from unittest.mock import patch, MagicMock
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from nio.modules.threading import Event
from ..http_requests_post_signal_block import HTTPRequestsPostSignal
from simplejson.scanner import JSONDecodeError


class TestHTTPRequestsPostSignal(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.last_notified = []
        self.event = Event()

    def signals_notified(self, signals, output_id='default'):
        self.last_notified = signals
        self.event.set()
        self.event.clear()

    @patch('requests.get')
    def test_get_with_response_body(self, mock_get):
        url = "http://httpbin.org/get"
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].url, url)
        block.stop()

    @patch('requests.get')
    def test_get_with_non_json_resp(self, mock_get):
        url = "http://httpbin.org/get"
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(side_effect=JSONDecodeError('fail', 'data', 1))
        resp.text = 'not json'
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "log_level": "WARNING",
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].raw, 'not json')
        block.stop()
        
    @patch('requests.get')
    def test_get_with_non_json_resp_fail(self, mock_get):
        url = "http://httpbin.org/get"
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(side_effect=JSONDecodeError('fail', 'data', 1))
        resp.text = 'not json'
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url,
            "require_json": True
        })
        
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified, [])
        block.stop()

    @patch('requests.get')
    def test_get_with_list_response_body(self, mock_get):
        url = "http://httpbin.org/get"
        url2 = "http://httpbin.org/get2"
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value=[{'url': url}, {'url': url2}])
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified[0].url, url)
        self.assertEqual(self.last_notified[1].url, url2)
        block.stop()

    @patch('requests.get')
    def test_get_no_response_body(self, mock_get):
        url = "http://httpbin.org/get"

        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(side_effect=Exception('bad json'))
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block._logger.warning = MagicMock()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified, [])
        block._logger.warning.assert_called_once_with(
            'Request was successful but '
            'failed to create ResponseSignal: bad json'
        )
        block.stop()

    @patch('requests.get')
    def test_get_bad_status(self, mock_get):
        url = "http://httpbin.org/get"
        resp = MagicMock()
        resp.status_code = 400
        mock_get.return_value = resp

        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "GET",
            "url": url
        })
        
        block.start()
        block._logger.warning = MagicMock()
        block.process_signals([Signal()])
        self.assertTrue(mock_get.called)
        self.assertEqual(self.last_notified, [])
        block._logger.warning.assert_called_once_with(
            'HTTPMethod.GET request to http://httpbin.org/get '
            'returned with response code: 400'
        )
        block.stop()

    def test_post(self):
        url = "http://httpbin.org/post"
        
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "POST",
            "url": url,
        })
        
        block.start()
        block.process_signals(
            [Signal({'key1': 'value1', 'key2': 'value2'})]
        )
        
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('value1', self.last_notified[0].json['key1'])
        self.assertEqual('value2', self.last_notified[0].json['key2'])
        block.stop()

    def test_post2(self):
        url = "http://httpbin.org/post"
        
        block = HTTPRequestsPostSignal()
        self.configure_block(block, {
            "http_method": "POST",
            "url": url,
        })
        
        block.start()
        block.process_signals([Signal({'string': 'text', 'int': 1})])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('text', self.last_notified[0].json['string'])
        self.assertEqual(1, self.last_notified[0].json['int'])
        block.stop()
