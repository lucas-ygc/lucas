#!/usr/bin/env python3
"""只查询 PTZ 状态或配置，不发送运动、停止或写配置命令。"""
import argparse
import json
import socket
import struct
import time
import uuid

MAX_FRAME = 64 * 1024


def receive_exact(sock, size, deadline):
    data = bytearray()
    while len(data) < size:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("等待设备应答超时")
        sock.settimeout(remaining)
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise ConnectionError("设备在一帧接收完成前关闭连接")
        data.extend(chunk)
    return bytes(data)


def query(host, port, command):
    if command not in ("ptz_status", "ptz_get_config"):
        raise ValueError("此工具仅允许状态和配置查询")
    query_id = "tutorial_" + uuid.uuid4().hex
    request = {"magic": "TL_PROD", "cmd": command,
               "params": {"query_id": query_id}}
    payload = json.dumps(request, separators=(",", ":")).encode("utf-8")
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(struct.pack("!I", len(payload)) + payload)
        deadline = time.monotonic() + 10
        while True:
            size = struct.unpack("!I", receive_exact(sock, 4, deadline))[0]
            if not 0 < size <= MAX_FRAME:
                raise ValueError(f"非法帧长度：{size}")
            reply = json.loads(receive_exact(sock, size, deadline).decode("utf-8"))
            if not isinstance(reply, dict):
                raise ValueError("应答不是 JSON 对象")
            if reply.get("magic") != "TL_PROD" or reply.get("cmd") != command + "_ack":
                continue
            if reply.get("query_id") not in (None, "", query_id):
                continue
            if reply.get("phase") == "accepted":
                continue
            return reply


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("command", choices=("status", "get-config"))
    parser.add_argument("--port", type=int, default=8899)
    args = parser.parse_args()
    command = "ptz_status" if args.command == "status" else "ptz_get_config"
    try:
        reply = query(args.host, args.port, command)
        print(json.dumps(reply, ensure_ascii=False, indent=2))
        return 0 if reply.get("result") == "ok" else 1
    except (OSError, ValueError, ConnectionError) as exc:
        parser.exit(1, f"查询失败：{exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
