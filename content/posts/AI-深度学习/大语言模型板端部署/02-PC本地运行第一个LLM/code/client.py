"""Python 标准库客户端：单轮本地问答、SSE 流式输出、取消和记录。"""
import argparse
from datetime import datetime, timezone
import json
import http.client
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent


def sse_events(lines):
    """按 SSE 空行分隔事件；一条 data 行/事件不等于一个 token。"""
    data = []
    for raw in lines:
        line = raw.decode("utf-8").rstrip("\r\n")
        if not line:
            if data:
                yield "\n".join(data)
                data = []
        elif line.startswith("data:"):
            data.append(line[5:].removeprefix(" "))
    # 未以空行终止的事件视为不完整，不将断流伪装成成功。


def ask(base_url, prompt, streaming=True, max_tokens=192, timeout=120, emit=print):
    request_body = {
        "model": "local-qwen", "messages": [
            {"role": "system", "content": "你是嵌入式设备助手，请用简短中文回答。不确定时明确说明。"},
            {"role": "user", "content": prompt}],
        "stream": streaming, "max_tokens": max_tokens,
        "temperature": 0.7, "top_p": 0.8, "top_k": 20, "min_p": 0.0,
        "presence_penalty": 1.5, "seed": 7,
        "cache_prompt": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if streaming:
        request_body["stream_options"] = {"include_usage": True}
    record = {"created_at": datetime.now(timezone.utc).isoformat(),
              "endpoint": base_url, "request": request_body, "status": "running",
              "answer": "", "first_content_seconds": None, "total_seconds": None,
              "finish_reason": None, "usage": None, "server_timings": None}
    started = time.perf_counter()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(base_url.rstrip("/") + "/v1/chat/completions",
                                    data=json.dumps(request_body).encode("utf-8"),
                                    headers={"Content-Type": "application/json"})
    try:
        with opener.open(request, timeout=timeout) as response:
            if streaming:
                if "text/event-stream" not in response.headers.get("Content-Type", ""):
                    raise ValueError("服务没有返回 SSE 流，请核对服务与版本")
                done = False
                for event in sse_events(response):
                    if event == "[DONE]":
                        done = True
                        break
                    payload = json.loads(event)
                    if "error" in payload:
                        raise ValueError(str(payload["error"]))
                    if payload.get("usage"):
                        record["usage"] = payload["usage"]
                    if payload.get("timings"):
                        record["server_timings"] = payload["timings"]
                    for choice in payload.get("choices", []):
                        content = choice.get("delta", {}).get("content") or ""
                        if content:
                            if record["first_content_seconds"] is None:
                                record["first_content_seconds"] = time.perf_counter() - started
                            record["answer"] += content
                            emit(content)
                        if choice.get("finish_reason") is not None:
                            record["finish_reason"] = choice["finish_reason"]
                if not done or record["finish_reason"] is None:
                    raise ValueError("响应提前断流，缺少结束标记或结束原因")
            else:
                payload = json.load(response)
                choice = payload["choices"][0]
                record["answer"] = choice["message"].get("content") or ""
                record["finish_reason"] = choice.get("finish_reason")
                record["usage"] = payload.get("usage")
                record["server_timings"] = payload.get("timings")
                emit(record["answer"])
            if not record["answer"].strip():
                raise ValueError("没有可见回答，请检查聊天模板、思考模式和长度上限")
            record["status"] = "truncated" if record["finish_reason"] == "length" else "completed"
    except KeyboardInterrupt:
        record["status"] = "cancelled"
    except (OSError, ValueError, KeyError, IndexError, http.client.HTTPException, urllib.error.URLError) as error:
        record["status"] = "failed"
        record["error"] = str(error)
    finally:
        record["total_seconds"] = time.perf_counter() - started
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:18080")
    parser.add_argument("--prompt", help="省略时读取本目录 prompt.txt")
    parser.add_argument("--no-stream", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=192)
    parser.add_argument("--timeout", type=float, default=120)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs")
    args = parser.parse_args()
    if args.max_tokens < 1 or not 0 < args.timeout < float("inf"):
        parser.error("max-tokens 与有限超时时间必须为正")
    prompt = args.prompt if args.prompt is not None else (ROOT / "prompt.txt").read_text()
    if not prompt.strip():
        parser.error("问题不能为空")
    args.out.mkdir(parents=True, exist_ok=True)
    record = ask(args.url, prompt, not args.no_stream, args.max_tokens, args.timeout,
                 emit=lambda text: print(text, end="", flush=True))
    path = args.out / (datetime.now().strftime("request-%Y%m%d-%H%M%S-%f") + ".json")
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(f"\n\n状态: {record['status']}，finish_reason={record['finish_reason']}")
    print(f"首段可见文本秒数: {record['first_content_seconds']}；总耗时: {record['total_seconds']:.3f}s")
    if record["usage"]:
        print("服务端 token 计数:", record["usage"])
    if record["server_timings"]:
        print("服务端计时:", record["server_timings"])
    print("记录:", path)
    if record["status"] == "failed":
        print(record["error"], file=sys.stderr)
        raise SystemExit(2)
    if record["status"] == "cancelled":
        raise SystemExit(130)


if __name__ == "__main__":
    main()
