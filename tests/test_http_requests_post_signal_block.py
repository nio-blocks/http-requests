import json
import responses
from unittest.mock import patch, MagicMock

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

    @responses.activate
    def test_post_signal_list(self):
        """ Disable option to make one request per signal."""
        sigs = [
            {'host': 'http://foo/', 'arbitrary': 1},
            {'host': 'http://foo/', 'arbitrary': 2},
            {'host': 'http://bar/', 'arbitrary': 3},
        ]
        responses.add(
            responses.POST,
            'http://foo/',
            status=200)
        responses.add(
            responses.POST,
            'http://bar/',
            status=200)
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            'one_request_per_signal': False,
            'url': '{{ $host }}',
        })
        block.start()
        block.process_signals([Signal(sig) for sig in sigs])
        self.assertEqual(2, len(responses.calls))
        self.assertEqual('http://foo/', responses.calls[0].request.url)
        self.assertEqual('http://bar/', responses.calls[1].request.url)
        self.assertEqual(
            sigs[:2],
            json.loads(responses.calls[0].request.body))
        self.assertEqual(
            sigs[-1:],
            json.loads(responses.calls[1].request.body))
        block.stop()

    @patch('requests.post')
    def test_signal_list_headers(self, mock_post):
        """ When posting multiple signals in one request, the first is used
        to determine headers, timeout, etc.
        """
        mock_post.return_value = MagicMock(status_code=200)
        sigs = [
            {'host': 'foo', 'timeout': 7,},
            {'host': 'foo', 'timeout': None},
            {'host': 'bar', 'timeout': 3},
        ]
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            'one_request_per_signal': False,
            'headers': [
                {
                    'header': '{{ $host }}',
                    'value': '{{ $timeout }}',
                }
            ],
            'timeout': '{{ $timeout }}',
            'url': '{{ $host }}',
        })
        block.start()
        block.process_signals([Signal(sig) for sig in sigs])

        self.assertEqual(2, mock_post.call_count)
        self.assertEqual(7, mock_post.call_args_list[0][1]['timeout'])
        self.assertDictEqual(
            {sigs[0]['host']: sigs[0]['timeout']},
            mock_post.call_args_list[0][1]['headers'])

        self.assertEqual(3, mock_post.call_args_list[1][1]['timeout'])
        self.assertDictEqual(
            {sigs[2]['host']: sigs[2]['timeout']},
            mock_post.call_args_list[1][1]['headers'])
        block.stop()
