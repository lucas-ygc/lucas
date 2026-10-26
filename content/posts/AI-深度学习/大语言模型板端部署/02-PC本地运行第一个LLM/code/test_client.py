"""无需下载模型的协议回归检查；真实模型结果另外记录。"""
import io
import json
import unittest
from unittest.mock import patch
from client import ask, sse_events


class Response(io.BytesIO):
    headers = {"Content-Type": "text/event-stream"}


def event(payload):
    return ("data: " + json.dumps(payload, ensure_ascii=False) + "\r\n\r\n").encode()


class ClientTests(unittest.TestCase):
    def run_request(self, data, emit=lambda text: None, streaming=True):
        with patch('client.urllib.request.build_opener') as opener:
            response = Response(data)
            if not streaming:
                response.headers = {"Content-Type": "application/json"}
            opener.return_value.open.return_value = response
            result = ask('http://127.0.0.1:18080', '测试', streaming=streaming, emit=emit)
            self.assertTrue(response.closed)
            return result

    def test_comments_and_multiline_sse(self):
        raw = b': heartbeat\r\n\r\nevent: message\r\ndata: one\r\ndata: two\r\n\r\ndata: incomplete'
        self.assertEqual(list(sse_events(io.BytesIO(raw))), ['one\ntwo'])

    def test_unicode_usage_and_empty_role(self):
        raw = event({'choices': [{'delta': {'role': 'assistant'}}]})
        raw += event({'choices': [{'delta': {'content': '你好，设备'}}]})
        raw += event({'choices': [{'delta': {}, 'finish_reason': 'stop'}]})
        raw += event({'choices': [], 'usage': {'completion_tokens': 4}})
        raw += b'data: [DONE]\n\n'
        output = []
        result = self.run_request(raw, output.append)
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(output, ['你好，设备'])
        self.assertEqual(result['usage']['completion_tokens'], 4)
        self.assertIsNotNone(result['first_content_seconds'])

    def test_early_disconnect(self):
        raw = event({'choices': [{'delta': {'content': '尚未结束'}}]})
        result = self.run_request(raw)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['answer'], '尚未结束')

    def test_cancel_closes_response(self):
        def interrupt(text):
            raise KeyboardInterrupt
        raw = event({'choices': [{'delta': {'content': '部分回答'}}]})
        result = self.run_request(raw, interrupt)
        self.assertEqual(result['status'], 'cancelled')
        self.assertEqual(result['answer'], '部分回答')
        self.assertIsNone(result['usage'])

    def test_length_is_not_normal_stop(self):
        raw = event({'choices': [{'delta': {'content': '截断'}, 'finish_reason': 'length'}]})
        result = self.run_request(raw + b'data: [DONE]\n\n')
        self.assertEqual(result['status'], 'truncated')

    def test_non_stream_does_not_claim_ttft(self):
        raw = json.dumps({'choices': [{'message': {'content': '回答'}, 'finish_reason': 'stop'}]}).encode()
        result = self.run_request(raw, streaming=False)
        self.assertEqual(result['status'], 'completed')
        self.assertIsNone(result['first_content_seconds'])

    def test_server_error_and_invalid_json(self):
        for raw in [event({'error': {'message': '上下文不足'}}), b'data: invalid\n\n']:
            self.assertEqual(self.run_request(raw)['status'], 'failed')


if __name__ == '__main__':
    unittest.main()
