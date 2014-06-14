from unittest.mock import patch
from http_requests.http_requests_block import HTTPRequests
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from unittest.mock import MagicMock


class TestHTTPRequests(NIOBlockTestCase):

    def test_get(self):
        url = "http://google.comm"
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
