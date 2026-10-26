"""生成 YuNet 320 的输入、浮点基准及 input255 等价图；不运行 ATC。"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import cv2
import numpy as np
import onnx
from onnx import numpy_helper
import onnxruntime as ort

OUTPUT_NAMES = [f'{kind}_{stride}' for kind in ('cls', 'obj', 'bbox', 'kps') for stride in (8, 16, 32)]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fixed_yunet(path):
    model = onnx.load(str(path))
    if [x.name for x in model.graph.output] != OUTPUT_NAMES:
        raise ValueError('仅支持本系列所述 YuNet 2023mar 十二输出模型')
    if len(model.graph.input) != 1 or model.graph.input[0].name != 'input':
        raise ValueError('YuNet 输入接口不匹配')
    dims = model.graph.input[0].type.tensor_type.shape.dim
    if len(dims) != 4:
        raise ValueError('输入必须为四维')
    for dim, value in zip(dims, (1, 3, 320, 320)):
        dim.ClearField('dim_param')
        dim.dim_value = value
    # 该 YuNet 为全卷积路径；同步修正 640 输入遗留的输出声明。
    del model.graph.value_info[:]
    channels = {'cls': 1, 'obj': 1, 'bbox': 4, 'kps': 10}
    for output in model.graph.output:
        kind, stride = output.name.rsplit('_', 1)
        dims = output.type.tensor_type.shape.dim
        if len(dims) != 3:
            raise ValueError('YuNet 输出必须为三维')
        for dim, value in zip(dims, (1, (320 // int(stride)) ** 2, channels[kind])):
            dim.ClearField('dim_param')
            dim.dim_value = value
    onnx.checker.check_model(model)
    return model

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--container-output', required=True, help='输出目录在转换容器内的绝对路径')
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('--images', nargs='+', type=Path, help='真实头部 ROI 图片，按左上对齐缩放到 320')
    sources.add_argument('--synthetic', action='store_true', help='仅验证数值与文件格式，不用于模型质量或生产校准')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('输出目录必须不存在，避免覆盖旧实验')
    if not args.container_output.startswith('/'):
        parser.error('container-output 必须是绝对路径')
    original = fixed_yunet(args.model)
    scaled = copy.deepcopy(original)
    first = scaled.graph.node[0]
    if first.op_type != 'Conv':
        raise ValueError('首节点不是预期 Conv')
    for item in scaled.graph.initializer:
        if item.name == first.input[1]:
            value = numpy_helper.to_array(item).astype(np.float32) * np.float32(255)
            item.CopyFrom(numpy_helper.from_array(value, item.name))
            break
    else:
        raise ValueError('首卷积权重不是预期 initializer')
    onnx.checker.check_model(scaled)
    args.output.mkdir(parents=True)
    original_path = args.output / 'yunet320_reference.onnx'
    scaled_path = args.output / 'yunet320_input255.onnx'
    onnx.save(original, original_path)
    onnx.save(scaled, scaled_path)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    a = ort.InferenceSession(str(original_path), sess_options=options, providers=['CPUExecutionProvider'])
    b = ort.InferenceSession(str(scaled_path), sess_options=options, providers=['CPUExecutionProvider'])
    if args.synthetic:
        y, x = np.indices((240, 300))
        image = np.stack(((x * 3 + y) % 256, (x + y * 2) % 256, (x * 2 + y * 3) % 256), axis=-1).astype(np.uint8)
        inputs = [('synthetic-pattern', image)]
    else:
        inputs = [(str(path), cv2.imread(str(path), cv2.IMREAD_COLOR)) for path in args.images]
    report = {'source_model_sha256': digest(args.model), 'onnx_sha256': digest(scaled_path),
              'synthetic': args.synthetic, 'input': {'name': 'input', 'shape': [1, 3, 320, 320],
              'runtime_dtype': 'uint8', 'layout': 'BGR_PLANAR', 'geometry': 'top-left / black padding / bilinear'},
              'versions': {'numpy': np.__version__, 'opencv': cv2.__version__, 'onnx': onnx.__version__, 'onnxruntime': ort.__version__},
              'samples': []}
    calibration = []
    for index, (name, image) in enumerate(inputs):
        if image is None or not image.size:
            raise ValueError(f'无法读取图像：{name}')
        h, w = image.shape[:2]
        scale = 320 / max(h, w)
        rw, rh = max(1, round(w * scale)), max(1, round(h * scale))
        canvas = np.zeros((320, 320, 3), dtype=np.uint8)
        canvas[:rh, :rw] = cv2.resize(image, (rw, rh), interpolation=cv2.INTER_LINEAR)
        image_path = args.output / f'prepared_{index}.png'
        if not cv2.imwrite(str(image_path), canvas):
            raise IOError('PNG 写出失败')
        planar = np.ascontiguousarray(canvas.transpose(2, 0, 1))
        input_path = args.output / f'input_{index}.bgr'
        planar.tofile(input_path)
        assert input_path.stat().st_size == 307200
        floats = planar[None].astype(np.float32)
        ra = a.run(OUTPUT_NAMES, {'input': floats})
        rb = b.run(OUTPUT_NAMES, {'input': floats / np.float32(255)})
        diffs = []
        for output, original_values, scaled_values in zip(OUTPUT_NAMES, ra, rb):
            if not (np.isfinite(original_values).all() and np.isfinite(scaled_values).all()):
                raise ValueError('浮点参考出现非有限值')
            np.testing.assert_allclose(scaled_values, original_values, rtol=1e-3, atol=1e-3)
            diffs.append({'name': output, 'shape': list(original_values.shape),
                          'max_abs': float(np.max(np.abs(original_values - scaled_values))),
                          'mae': float(np.mean(np.abs(original_values - scaled_values)))})
        np.savez(args.output / f'reference_{index}.npz', **dict(zip(OUTPUT_NAMES, ra)))
        np.savez(args.output / f'input255_{index}.npz', **dict(zip(OUTPUT_NAMES, rb)))
        report['samples'].append({'source': name, 'source_size': [w, h], 'resized_size': [rw, rh],
                                  'input_file': input_path.name, 'input_sha256': digest(input_path),
                                  'prepared_sha256': digest(image_path), 'outputs': diffs})
        calibration.append(args.container_output.rstrip('/') + '/' + image_path.name)
    (args.output / 'calibration.txt').write_text('\n'.join(calibration) + '\n')
    (args.output / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
