from ..http_requests_block import HTTPRequests
from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from unittest.mock import MagicMock
from nio.modules.threading import Event

class EventBlock(HTTPRequests):
    def __init__(self, event):
        super().__init()
        self.event = event

class TestHTTPRequests(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.last_notified = []
        self.event = Event()

    def signals_notified(self, signals):
        self.last_notified = signals
        self.event.set()
        self.event.clear()

    def test_get_mock(self):
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        block._get = MagicMock()
        config = {
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        block.stop()

    def test_get(self):
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        config = {
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        block.stop()

    def test_post(self):
        url = "http://httpbin.org/post"
        block = HTTPRequests()
        config = {
            "url": url,
            "http_method": "POST",
            "data": {
                "params": [
                    {"key": "key1", "value": "value1"},
                    {"key": "key2", "value": "value2"}
                ]
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('value1', self.last_notified[0].json['key1'])
        self.assertEqual('value2', self.last_notified[0].json['key2'])
        block.stop()

    def test_post_form(self):
        url = "http://httpbin.org/post"
        block = HTTPRequests()
        config = {
            "url": url,
            "http_method": "POST",
            "data": {
                "params": [
                    {"key": "key1", "value": "value1"},
                    {"key": "key2", "value": "value2"}
                ],
                "form_encode_data": True
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('value1', self.last_notified[0].form['key1'])
        self.assertEqual('value2', self.last_notified[0].form['key2'])
        block.stop()

    def test_post_expr(self):
        url = "http://httpbin.org/post"
        block = HTTPRequests()
        config = {
            "url": url,
            "http_method": "POST",
            "data": {
                "params": [
                    {"key": "{{$key}}", "value": "{{$val}}"}
                ]
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal({'key': 'greeting',
                                       'val': 'cheers'})])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('cheers', self.last_notified[0].json['greeting'])
        block.stop()
