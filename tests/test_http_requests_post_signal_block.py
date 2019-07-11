from threading import Event
from unittest.mock import patch, MagicMock

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..http_requests_post_signal_block import HTTPRequestsPostSignal


class TestHTTPRequestsPostSignal(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.event = Event()

    def signals_notified(self, block, signals, output_id):
        super().signals_notified(block, signals, output_id)
        self.event.set()
        self.event.clear()

    def test_post(self):
        url = "https://httpbin.org/post"
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "url": url,
        })
        block.start()
        block.process_signals(
            [Signal({'key1': 'value1', 'key2': 'value2'})]
        )
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[DEFAULT_TERMINAL][0].url)
        self.assertEqual(
            'value1', self.last_notified[DEFAULT_TERMINAL][0].json['key1'])
        self.assertEqual(
            'value2', self.last_notified[DEFAULT_TERMINAL][0].json['key2'])
        block.stop()

    def test_post2(self):
        url = "https://httpbin.org/post"
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "url": url,
        })
        block.start()
        block.process_signals([Signal({'string': 'text', 'int': 1})])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[DEFAULT_TERMINAL][0].url)
        self.assertEqual(
            'text', self.last_notified[DEFAULT_TERMINAL][0].json['string'])
        self.assertEqual(
            1, self.last_notified[DEFAULT_TERMINAL][0].json['int'])
        block.stop()
