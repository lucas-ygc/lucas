#!/usr/bin/env python3
"""只读检查 TLUPG002 包的签名、身份、长度及组件哈希；不安装、不升级设备。"""
import argparse
import hashlib
from pathlib import Path
import re
import struct
import subprocess
import tempfile

LIMITS = (8 * 1024 * 1024, 184 * 126976)


def check(package, public_key, model, hardware):
    size = package.stat().st_size
    if not 768 <= size <= 768 + sum(LIMITS):
        raise ValueError("文件长度超出当前包格式范围")
    data = package.read_bytes()
    # 只接受公钥文件。正式密钥路径不属于这个工具的输入。
    key_info = subprocess.run(["openssl", "rsa", "-pubin", "-in", str(public_key), "-text", "-noout"],
                              capture_output=True, text=True)
    if key_info.returncode or not re.search(r"Public-Key:\s*\(2048 bit\)", key_info.stdout):
        raise ValueError("需要 RSA-2048 公钥")
    with tempfile.TemporaryDirectory(prefix="package-check-") as directory:
        header, signature = Path(directory) / "header.bin", Path(directory) / "signature.bin"
        header.write_bytes(data[:512])
        signature.write_bytes(data[512:768])
        result = subprocess.run(["openssl", "dgst", "-sha256", "-verify", str(public_key),
                                 "-signature", str(signature), str(header)], capture_output=True)
        if result.returncode:
            raise ValueError("描述头签名无效，或公钥不匹配")

    magic, version, header_bytes, model_bytes, hardware_bytes, release = struct.unpack_from("<8sII32s32sQ", data)
    if magic != b"TLUPG002" or version != 1 or header_bytes != 768 or release == 0:
        raise ValueError("不支持的包描述头")
    def name(raw):
        if b"\0" not in raw:
            raise ValueError("身份字段未终止")
        return raw.split(b"\0", 1)[0].decode("ascii")
    if name(model_bytes) != model or name(hardware_bytes) != hardware:
        raise ValueError("产品或硬件与指定值不匹配")
    if any(data[200:512]):
        raise ValueError("保留字段非零")
    offset, present, components = 768, 0, []
    for index, label in enumerate(("kernel", "app")):
        kind, length, component_version, minimum, digest = struct.unpack_from("<IIQQ32s", data, 88 + index * 56)
        if kind != index or length > LIMITS[index]:
            raise ValueError(f"{label} 类型或长度无效")
        if length:
            if component_version == 0 or offset + length > len(data):
                raise ValueError(f"{label} 版本无效或数据截断")
            image = data[offset:offset + length]
            if hashlib.sha256(image).digest() != digest:
                raise ValueError(f"{label} SHA-256 不匹配")
            if index == 0 and (length < 8 or image[:4] != b"\xd0\x0d\xfe\xed" or struct.unpack_from(">I", image, 4)[0] != length):
                raise ValueError("kernel 不是长度匹配的完整 FIT")
            if index == 1 and (length < 96 or image[:4] != b"hsqs"):
                raise ValueError("app 不是预期 SquashFS 输入")
            present += 1
            components.append(f"{label}: bytes={length}, version={component_version}, sha256={digest.hex()}")
        offset += length
    if not present or offset != len(data):
        raise ValueError("空包、截断或多余尾部数据")
    return [f"PASS: {model} / {hardware}, release={release}", *components,
            "仅通过离线内容检查；不代表设备可安装、可启动或业务正常。"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--public-key", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--hardware", required=True)
    args = parser.parse_args()
    try:
        print("\n".join(check(args.package, args.public_key, args.model, args.hardware)))
    except (OSError, ValueError, struct.error) as exc:
        parser.exit(1, f"检查失败：{exc}\n")


if __name__ == "__main__":
    main()
