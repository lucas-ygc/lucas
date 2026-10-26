#!/usr/bin/env bash
# Linux 本机 CPU 构建；下载固定模型并校验，不安装系统软件。
set -euo pipefail
TASK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
TASK_RUNTIME="$TASK_DIR/.runtime"
mkdir -p "$TASK_RUNTIME"
for command in curl cmake c++ tar sha256sum; do
    command -v "$command" >/dev/null || { echo "缺少工具：$command" >&2; exit 2; }
done

fetch_checked() {
    local url="$1" destination="$2" digest="$3"
    if [ -f "$destination" ] && echo "$digest  $destination" | sha256sum --check --status; then
        echo "校验通过，复用：$destination"
        return
    fi
    curl --fail --location --retry 3 --retry-all-errors --continue-at - --output "$destination.part" "$url"
    echo "$digest  $destination.part" | sha256sum --check
    mv -- "$destination.part" "$destination"
}

fetch_checked 'https://api.github.com/repos/ggml-org/llama.cpp/tarball/v0.7.0' \
    "$TASK_RUNTIME/llama.cpp-v0.7.0.tar.gz" \
    'ebe5fe11eb89011e7e5db1481f37c1b31a9d7c1968ce44fc775aea1100302cf9'
mkdir -p "$TASK_RUNTIME/llama.cpp"
tar -xzf "$TASK_RUNTIME/llama.cpp-v0.7.0.tar.gz" -C "$TASK_RUNTIME/llama.cpp" --strip-components=1
cmake -S "$TASK_RUNTIME/llama.cpp" -B "$TASK_RUNTIME/llama.cpp/build" \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_BUILD_RPATH_USE_ORIGIN=ON -DGGML_CUDA=OFF -DGGML_VULKAN=OFF \
    -DLLAMA_OPENSSL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF \
    -DLLAMA_BUILD_APP=OFF -DLLAMA_BUILD_UI=OFF
cmake --build "$TASK_RUNTIME/llama.cpp/build" --target llama-server -j 4

fetch_checked 'https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/23749fefcc72300e3a2ad315e1317431b06b590a/Qwen3-0.6B-Q8_0.gguf' \
    "$TASK_RUNTIME/Qwen3-0.6B-Q8_0.gguf" \
    '9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031'
echo '准备完成。终端一：python3 serve.py；终端二：python3 client.py'
