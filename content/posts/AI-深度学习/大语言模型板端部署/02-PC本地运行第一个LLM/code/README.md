# 在 PC 上运行第一个本地 LLM

目标：Linux PC 上用 CPU 加载官方 Qwen3-0.6B-Q8_0 GGUF，完成单轮问答、流式显示、取消和运行记录。无需训练、PyTorch 或云端 API 密钥。

## 准备与启动

需要 Python 3.10+、C/C++ 编译器、CMake、curl、tar、sha256sum；如缺失，请先使用系统包管理器安装。预留数 GB 磁盘空间用于源码、编译和模型，运行内存不能只按模型文件大小估算。

在本代码目录执行：

```bash
bash setup.sh
python3 serve.py
```

`setup.sh` 会联网下载固定版本源码与模型、校验 SHA-256，并以 4 个编译任务构建 CPU 版本。只写入本目录 `.runtime/`，不安装系统软件，不修改系统 PATH。首次准备可能较慢；模型文件 639446688 字节（约 639 MB / 610 MiB）。已有文件通过校验会复用，下载中断保留 `.part` 供续传。校验失败时不要跳过检查，应重新获取文件。

- llama.cpp：`v0.7.0`，源码归档 SHA-256 `ebe5fe11eb89011e7e5db1481f37c1b31a9d7c1968ce44fc775aea1100302cf9`。
- 模型：`Qwen/Qwen3-0.6B-GGUF`，revision `23749fefcc72300e3a2ad315e1317431b06b590a`。
- 文件：`Qwen3-0.6B-Q8_0.gguf`，SHA-256 `9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031`。

固定 Linux CPU 基线：单请求槽位、上下文 2048、4 个 CPU 线程、GPU 层数 0，仅监听 127.0.0.1:18080，关闭思考模式。GGUF 内的聊天模板由服务器应用。当前源码构建不启用 HTTPS 下载能力；模型已由 curl 下载，本地 HTTP 推理不受影响。

## 发送问题

保持终端一的服务运行，在终端二进入同一代码目录：

```bash
python3 client.py --no-stream
python3 client.py
python3 client.py --prompt '请用一句话解释 PCM 音频。'
python3 inspect_input.py
```

省略 `--prompt` 时读取本目录 `prompt.txt`。每次是独立单轮请求，不保存对话历史。流式请求中按 Ctrl+C 关闭连接并保存部分结果，退出码为 130。客户端退出后服务仍可继续使用；关闭服务请在终端一按 Ctrl+C。

短输出上限实验：

```bash
python3 client.py --max-tokens 8
```

观察 `finish_reason=length` 与正常 `stop` 的区别，不要把截断当成完整回答。默认采样值固定为 temperature=0.7、top_p=0.8、top_k=20、min_p=0、presence_penalty=1.5、seed=7；同一 seed 不保证跨机器或版本完全一致。

## 记录含义

`outputs/` 中保存服务日志、服务运行 JSON 和每次请求 JSON（包括问题与回答）。不需要安装第三方 Python 包。

- `first_content_seconds`：客户端从发请求到首段非空可见文本的时间；包括排队、HTTP、模板、分词和提示处理等开销，不是纯计算 TTFT。
- 非流式请求的首段延迟为 null，不拿完整响应时间冒充首 token 时间。
- `total_seconds`：客户端整个请求耗时，不含已独立完成的模型加载。
- `usage`、`server_timings`：保留服务端提供的真实计数与耗时；缺失时不自行用汉字数或事件数猜 token 数。
- `process_hwm_kib`：Linux `/proc` 中服务进程的 RSS 高水位；不是整个系统占用、不是 GPU 内存，也不包含编译过程。
- `max_sampled_rss_kib`：每 250 ms 采样的最大 RSS，可能漏掉瞬时峰值。

`--timeout` 是网络操作超时，并非整个请求的硬性总时限；请求还受输出 Token 上限控制。

客户端设置 `cache_prompt=false`，用于降低重复输入复用缓存对入门比较的影响；冷热状态、采样、线程数仍需一起记录。停止客户端只是关闭连接，服务端释放任务是否及时要从日志与后续请求验证，不能据此宣称板端取消延迟已验收。

## 已有模型或自定义路径

```bash
python3 serve.py --server /你的路径/llama-server --model /你的路径/Qwen3-0.6B-Q8_0.gguf --out /tmp/llm-records
python3 client.py --out /tmp/llm-records
```

启动脚本的默认文件路径相对于脚本，不依赖当前工作目录。换模型需重新确认模板、采样参数与思考模式，不能只改文件名就沿用所有假设。

## 回归检查

```bash
python3 test_client.py
```

这组检查不加载模型，只验证协议和取消处理。真实推理与构建验证情况以 `verification.md` 为准。小模型的回答需要人工核对，不应自动当作设备控制指令。

## 官方资料

- [llama.cpp 固定版本](https://github.com/ggml-org/llama.cpp/tree/v0.7.0)
- [服务器接口](https://github.com/ggml-org/llama.cpp/blob/v0.7.0/tools/server/README.md)
- [官方模型仓库](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF)

本篇代码包不携带模型、第三方源码或编译产物。模型许可证见官方仓库，llama.cpp 许可证见其源码归档。

源码构建默认针对当前 PC 的 CPU 特性优化；这份二进制不能直接当作 ARM 板端版本复制过去。板端需重新选择目标工具链与后端。
