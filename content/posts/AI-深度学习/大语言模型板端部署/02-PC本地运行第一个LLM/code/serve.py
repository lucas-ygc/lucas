"""启动本地 CPU 服务，记录版本、命令、启动时间及 Linux 进程 RSS。"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent


def memory_kib(pid):
    path = Path(f"/proc/{pid}/status")
    try:
        fields = {}
        for line in path.read_text().splitlines():
            if line.startswith(("VmRSS:", "VmHWM:")):
                key, value, unit = line.split()
                fields[key.rstrip(":")] = int(value)
        return fields
    except OSError:
        return {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, default=ROOT / ".runtime/llama.cpp/build/bin/llama-server")
    parser.add_argument("--model", type=Path, default=ROOT / ".runtime/Qwen3-0.6B-Q8_0.gguf")
    parser.add_argument("--port", type=int, default=18080)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--ctx", type=int, default=2048)
    parser.add_argument("--startup-timeout", type=float, default=180)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    if not args.server.is_file() or not args.model.is_file():
        parser.error("缺少 llama-server 或模型；先按 README 准备，或指定 --server 和 --model")
    if args.threads < 1 or args.ctx < 256 or not 1 <= args.port <= 65535 or not 0 < args.startup_timeout < float("inf"):
        parser.error("请检查线程数、上下文、端口与启动超时")
    args.out.mkdir(parents=True, exist_ok=True)
    prefix = args.out / datetime.now().strftime("server-%Y%m%d-%H%M%S-%f")
    command = [str(args.server.resolve()), "-m", str(args.model.resolve()),
               "--host", "127.0.0.1", "--port", str(args.port), "--alias", "local-qwen",
               "-c", str(args.ctx), "-t", str(args.threads), "-ngl", "0", "-np", "1",
               "--jinja", "--chat-template-kwargs", '{"enable_thinking":false}']
    version = subprocess.run([str(args.server.resolve()), "--version"], capture_output=True, text=True, check=True)
    record = {"command": command, "version": version.stdout + version.stderr,
              "model_bytes": args.model.stat().st_size, "status": "starting",
              "startup_seconds": None, "max_sampled_rss_kib": 0, "process_hwm_kib": 0}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    # 提前拒绝已被占用的端口，避免把别的服务的 health 当成自己的就绪状态。
    import socket
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        probe.bind(("127.0.0.1", args.port))
    started = time.perf_counter()
    with prefix.with_suffix(".log").open("w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        record["pid"] = process.pid
        try:
            while process.poll() is None:
                memory = memory_kib(process.pid)
                record["max_sampled_rss_kib"] = max(record["max_sampled_rss_kib"], memory.get("VmRSS", 0))
                record["process_hwm_kib"] = max(record["process_hwm_kib"], memory.get("VmHWM", 0))
                if record["startup_seconds"] is None:
                    try:
                        with opener.open(f"http://127.0.0.1:{args.port}/health", timeout=1) as response:
                            healthy = json.load(response).get("status") == "ok"
                        if healthy and process.poll() is None:
                            record["startup_seconds"] = time.perf_counter() - started
                            record["status"] = "ready"
                            print(f"模型已就绪：http://127.0.0.1:{args.port}，启动 {record['startup_seconds']:.2f}s", flush=True)
                            print("在另一个终端运行 client.py；本终端 Ctrl+C 关闭服务。", flush=True)
                    except (OSError, ValueError, urllib.error.URLError):
                        pass
                    if record["startup_seconds"] is None and time.perf_counter() - started > args.startup_timeout:
                        raise TimeoutError("模型启动超时，请查看服务日志")
                prefix.with_suffix(".json").write_text(json.dumps(record, ensure_ascii=False, indent=2))
                time.sleep(0.25)
            raise RuntimeError(f"服务意外退出，退出码 {process.returncode}")
        except KeyboardInterrupt:
            record["status"] = "stopped"
        except (OSError, RuntimeError) as error:
            record["status"] = "failed"
            record["error"] = str(error)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            record["exit_code"] = process.returncode
            record["lifetime_seconds"] = time.perf_counter() - started
            prefix.with_suffix(".json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
            print("服务记录:", prefix.with_suffix(".json"), flush=True)
    if record["status"] == "failed":
        raise SystemExit(record["error"] + "；日志：" + str(prefix.with_suffix(".log")))


if __name__ == "__main__":
    main()
