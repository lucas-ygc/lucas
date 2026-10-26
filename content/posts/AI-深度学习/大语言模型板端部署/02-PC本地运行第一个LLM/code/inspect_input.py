"""读取服务的真实聊天模板展开结果与 token ID；不把 ID 当作向量。"""
import argparse
import json
from pathlib import Path
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:18080')
    args = parser.parse_args()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def post(route, body):
        request = urllib.request.Request(args.url.rstrip('/') + route,
                                         data=json.dumps(body).encode(),
                                         headers={'Content-Type': 'application/json'})
        with opener.open(request, timeout=30) as response:
            return json.load(response)

    prompt = (Path(__file__).resolve().parent/'prompt.txt').read_text()
    messages = [{'role': 'system', 'content': '你是嵌入式设备助手，请用简短中文回答。不确定时明确说明。'},
                {'role': 'user', 'content': prompt}]
    rendered = post('/apply-template', {'messages': messages})['prompt']
    tokens = post('/tokenize', {'content': rendered, 'add_special': False})['tokens']
    print('聊天模板展开后的真实文本：\n' + rendered)
    print('Token 数:', len(tokens))
    print('前 24 个 Token ID:', tokens[:24])
    print('这些是编号，不是 Embedding；生成请求的最终计数以服务端 usage 为准。')


if __name__ == '__main__':
    main()
