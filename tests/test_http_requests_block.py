from ..http_requests_block import HTTPRequests
from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from unittest.mock import MagicMock
from nio.modules.threading import Event


class EventBlock(HTTPRequests):

    def __init__(self, event):
        super().__init__()
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

    def test_get_with_response_body(self):
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # a signal will be notified with this response body
                return {'url': url}
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].url, url)
        block.stop()

    def test_get_no_response_body(self):
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # no signal will be notified by get request worked
                raise Exception('bad json')
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block._logger.warning = MagicMock()
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified, [])
        block._logger.warning.assert_called_once_with(
            'Request was successfull but '
            'failed to create ResponseSignal: bad json'
        )
        block.stop()

    def test_get_bad_status(self):
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
        # get request will return 400
        block._get = MagicMock(return_value=Resp(400))
        config = {
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block._logger.warning = MagicMock()
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified, [])
        block._logger.warning.assert_called_once_with(
            'HTTPMethod.GET request to http://httpbin.org/get '
            'returned with response code: 400'
        )
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
