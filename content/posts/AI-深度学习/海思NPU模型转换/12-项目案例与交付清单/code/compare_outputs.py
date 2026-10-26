"""按 benchmark 日志的名称、shape、stride 将原始 FP32 输出与 NPZ 基准对齐。"""
import argparse
import json
from pathlib import Path
import re
import numpy as np

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--log', required=True, type=Path)
    parser.add_argument('--prefix', required=True, type=Path, help='对应 PREFIX_0.bin 等文件')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--atol', type=float, help='可选逐元素绝对误差门槛，不提供时只报告差异')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('请使用新的报告路径')
    if args.atol is not None and (not np.isfinite(args.atol) or args.atol < 0):
        parser.error('atol 必须为非负有限数')
    pattern = r'^output index=(\d+) name=(\S+) bytes=(\d+) stride=(\d+) type=(\d+) dims=([\d,]+)$'
    descriptors = re.findall(pattern, args.log.read_text(), re.MULTILINE)
    if not descriptors:
        raise ValueError('日志中没有 benchmark 输出描述')
    rows, seen = [], set()
    with np.load(args.reference, allow_pickle=False) as reference:
        for idx, name, size, stride, kind, dims in descriptors:
            if name not in reference.files or name in seen:
                raise ValueError(f'缺少或重复的参考输出名称：{name}')
            seen.add(name)
            shape = tuple(int(x) for x in dims.split(',') if x)
            size, stride = int(size), int(stride)
            if int(kind) != 0 or not shape or min(shape) <= 0:
                raise ValueError('仅支持此 SDK type=0 的 FP32 固定形状输出')
            count = int(np.prod(shape[:-1], dtype=np.int64))
            width = shape[-1] * 4
            raw = Path(f'{args.prefix}_{idx}.bin').read_bytes()
            if len(raw) != size or width > stride or count * stride > size:
                raise ValueError('输出文件字节数或 stride 与日志不一致')
            compact = b''.join(raw[i * stride:i * stride + width] for i in range(count))
            actual = np.frombuffer(compact, dtype='<f4').reshape(shape).astype(np.float64)
            expected = reference[name].astype(np.float64)
            if actual.shape != expected.shape or not np.isfinite(actual).all() or not np.isfinite(expected).all():
                raise ValueError('输出 shape 不一致或存在非有限值')
            delta = actual - expected
            norm = np.linalg.norm(actual.ravel()) * np.linalg.norm(expected.ravel())
            rows.append({'name': name, 'shape': list(shape), 'mae': float(np.mean(np.abs(delta))),
                         'rmse': float(np.sqrt(np.mean(delta ** 2))), 'max_abs': float(np.max(np.abs(delta))),
                         'cosine': float(np.dot(actual.ravel(), expected.ravel()) / norm) if norm > 0 else None})
        if seen != set(reference.files):
            raise ValueError('基准与输出张量集合不一致')
    passed = None if args.atol is None else all(x['max_abs'] <= args.atol for x in rows)
    report = {'outputs': rows, 'atol': args.atol, 'within_atol': passed,
              'note': '数值比较不包含检测解码、NMS 和任务准确率；没有通用的量化验收阈值。'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if passed is False:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
