from unittest.mock import MagicMock
from nio.common.signal.base import Signal
from ..http_requests_enrich_signal_block import HTTPRequestsEnrichSignal
from .test_http_requests_block import TestHTTPRequests


class TestHTTPRequestsEnrichSignal(TestHTTPRequests):
    BLOCK = HTTPRequestsEnrichSignal

    def test_get_with_enrich_signal_empty(self):
        url = "http://httpbin.org/get"
        block = self.BLOCK()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # a signal will be notified with this response body
                return {'url': url}
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "http_method": "GET",
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].url, url)
        self.assertFalse(hasattr(self.last_notified[0], 'input_attr'))
        block.stop()

    def test_get_with_enrich_signal(self):
        url = "http://httpbin.org/get"
        block = self.BLOCK()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # a signal will be notified with this response body
                return {'url': url}
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "http_method": "GET",
            "url": url,
            "enrich_signal_attr": "response"
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].response['url'], url)
        self.assertEqual(self.last_notified[0].input_attr, 'value')
        block.stop()

    def test_get_with_enrich_signal_list_resp(self):
        url = "http://httpbin.org/get"
        url2 = "http://httpbin.org/get2"
        block = self.BLOCK()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # a signal will be notified with this response body
                return [{'url': url}, {'url': url2}]
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "http_method": "GET",
            "url": url,
            "enrich_signal_attr": 'response'
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].response['url'], url)
        self.assertEqual(self.last_notified[1].response['url'], url2)
        self.assertEqual(self.last_notified[0].input_attr, 'value')
        self.assertEqual(self.last_notified[1].input_attr, 'value')
        block.stop()
