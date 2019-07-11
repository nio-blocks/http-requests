import json
import responses

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..http_requests_post_signal_block import HTTPRequestsPostSignal


class TestHTTPRequestsPostSignal(NIOBlockTestCase):

    @responses.activate
    def test_post(self):
        url = 'http://foo/'
        sig = {'key1': 'value1', 'key2': 'value2'}
        responses.add(
            responses.POST,
            url,
            json=sig,
            status=200)
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            'url': url,
        })
        block.start()
        block.process_signals([Signal(sig)])
        self.assertEqual(url, responses.calls[0].request.url)
        self.assertDictEqual(sig, json.loads(responses.calls[0].request.body))
        block.stop()

    @responses.activate
    def test_post2(self):
        url = 'http://foo/'
        sig = {'string': 'text', 'int': 1}
        responses.add(
            responses.POST,
            url,
            status=200)
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            'url': url,
        })
        block.start()
        block.process_signals([Signal(sig)])
        self.assertEqual(url, responses.calls[0].request.url)
        self.assertDictEqual(sig, json.loads(responses.calls[0].request.body))
        block.stop()
