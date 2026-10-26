#!/usr/bin/env python3
"""离线签名实验，仅在临时目录生成教学密钥，不读取项目密钥或访问设备。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def run(*args, ok=True):
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if ok and result.returncode:
        raise RuntimeError(f"命令失败：{args[0]} {args[1]}\n{result.stderr}")
    return result.returncode == 0


def require(value, message):
    if not value:
        raise RuntimeError(message)
    print("PASS:", message)


def main():
    if not shutil.which("openssl"):
        raise SystemExit("需要 OpenSSL 命令行工具")
    # 临时目录位于实验目录内；正常退出及 Python 异常退出时自动清理。
    with tempfile.TemporaryDirectory(prefix=".signature-demo-", dir=Path(__file__).resolve().parent) as directory:
        work = Path(directory)
        for name in ("publisher", "other"):
            private, public = work / f"{name}-private.pem", work / f"{name}-public.pem"
            run("openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(private))
            private.chmod(0o600)
            run("openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public))
        image = work / "firmware.bin"
        image.write_bytes(b"teaching firmware v1\n")
        metadata = {"model": "DEMO_ONLY", "version": 1,
                    "size": image.stat().st_size,
                    "sha256": hashlib.sha256(image.read_bytes()).hexdigest()}
        header = work / "manifest.json"
        header.write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
        original_header, original_image = header.read_bytes(), image.read_bytes()
        signature = work / "manifest.sig"

        def sign(name, dest):
            run("openssl", "dgst", "-sha256", "-sign", str(work / f"{name}-private.pem"),
                "-out", str(dest), str(header))

        def verify(name, sig):
            return run("openssl", "dgst", "-sha256", "-verify", str(work / f"{name}-public.pem"),
                       "-signature", str(sig), str(header), ok=False)

        def matches():
            info = json.loads(header.read_text(encoding="utf-8"))
            data = image.read_bytes()
            return len(data) == info["size"] and hashlib.sha256(data).hexdigest() == info["sha256"]

        sign("publisher", signature)
        require(verify("publisher", signature) and matches(), "原始签名和镜像哈希均通过")
        require(not verify("other", signature), "错误公钥不能验证发布方签名")
        image.write_bytes(original_image.replace(b"v1", b"v2"))
        require(verify("publisher", signature) and not matches(), "只改镜像时，头签名仍通过，但镜像哈希拒绝")
        metadata["sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        header.write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
        require(matches() and not verify("publisher", signature), "镜像与哈希一起改，旧签名仍然拒绝")
        alternate_signature = work / "other.sig"
        sign("other", alternate_signature)
        require(verify("other", alternate_signature) and not verify("publisher", alternate_signature),
                "替换包内公钥可自洽，但不能通过已有可信公钥验证")
        header.write_bytes(original_header)
        image.write_bytes(original_image)
        header.write_bytes(original_header + b" ")
        require(not verify("publisher", signature), "即使 JSON 语义相同，改动签名字节仍使验签失败")
    print("完成：教学临时密钥已清理；没有生成可刷写固件。")


if __name__ == "__main__":
    main()
