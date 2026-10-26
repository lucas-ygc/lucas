"""只读审计 ONNX 的接口和算子；不判断海思算子支持与精度。"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import onnx

def describe(value):
    tensor = value.type.tensor_type
    shape = [d.dim_value if d.HasField('dim_value') else d.dim_param or '?' for d in tensor.shape.dim]
    return {'name': value.name, 'dtype': onnx.TensorProto.DataType.Name(tensor.elem_type), 'shape': shape}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('model', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('输出已存在，请使用新的审计文件')
    model = onnx.load(str(args.model))
    onnx.checker.check_model(model)
    constants = {x.name for x in model.graph.initializer}
    report = {'model': str(args.model), 'bytes': args.model.stat().st_size,
              'main_file_sha256': hashlib.sha256(args.model.read_bytes()).hexdigest(),
              'ir_version': model.ir_version,
              'opsets': [{'domain': x.domain, 'version': x.version} for x in model.opset_import],
              'inputs': [describe(x) for x in model.graph.input if x.name not in constants],
              'outputs': [describe(x) for x in model.graph.output],
              'operators': dict(sorted(Counter((x.domain + '::' if x.domain else '') + x.op_type for x in model.graph.node).items())),
              'notes': ['checker 通过不等于 ATC 支持。', 'external data 模型还需单独保存和校验其外部权重文件。']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
