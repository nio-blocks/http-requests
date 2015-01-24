from unittest.mock import patch, MagicMock
from ..http_requests_enrich_signal_block import HTTPRequestsEnrichSignal
from nio.modules.threading import Event
from nio.common.signal.base import Signal
from nio.util.support.block_test_case import NIOBlockTestCase


class TestHTTPRequestsEnrichSignal(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.last_notified = []
        self.event = Event()

    def signals_notified(self, signals, output_id='default'):
        self.last_notified = signals
        self.event.set()
        self.event.clear()

    @patch('requests.get')
    def test_get_with_enrich_signal_empty(self, mock_get):
        url = "http://httpbin.org/get"
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp

        block = HTTPRequestsEnrichSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].url, url)
        self.assertFalse(hasattr(self.last_notified[0], 'input_attr'))
        block.stop()

    @patch('requests.get')
    def test_get_with_enrich_signal(self, mock_get):
        url = "http://httpbin.org/get"

        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp

        block = HTTPRequestsEnrichSignal()
        # # fake a response object from get request
        # class Resp(object):
        #     def __init__(self, status_code):
        #         self.status_code = status_code
        #     def json(self):
        #         # a signal will be notified with this response body
        #         return {'url': url}
        config = {
            "http_method": "GET",
            "url": url,
            "enrich_signal_attr": "response"
        }
        self.configure_block(block, {
            "http_method": "GET",
            "url": url,
            "enrich_signal_attr": "response"
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].response['url'], url)
        self.assertEqual(self.last_notified[0].input_attr, 'value')
        block.stop()

    @patch('requests.get')
    def test_get_with_enrich_signal_list_resp(self, mock_get):
        url = "http://httpbin.org/get"
        url2 = "http://httpbin.org/get2"

        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value=[{'url': url}, {'url': url2}])
        mock_get.return_value = resp

        block = HTTPRequestsEnrichSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url,
            "enrich_signal_attr": 'response'
        })
        
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].response['url'], url)
        self.assertEqual(self.last_notified[1].response['url'], url2)
        self.assertEqual(self.last_notified[0].input_attr, 'value')
        self.assertEqual(self.last_notified[1].input_attr, 'value')
        block.stop()
