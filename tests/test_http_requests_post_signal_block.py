from unittest.mock import patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from unittest.mock import MagicMock
from nio.modules.threading import Event

from ..http_requests_post_signal_block import HTTPRequestsPostSignal


def create_signal(val1='value1', val2='value2'):
    return Signal({'key1': val1, 'key2': val2})


# class EventBlock(HTTPRequests):
#     def __init__(self, event):
#         super().__init__()
#         self.event = event


class TestHTTPRequestsPostSignal(NIOBlockTestCase):
    BLOCK = HTTPRequestsPostSignal

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
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].url, url)
        block.stop()

    def test_get_with_list_response_body(self):
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
            "url": url
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.assertTrue(block._get.called)
        self.assertEqual(self.last_notified[0].url, url)
        self.assertEqual(self.last_notified[1].url, url2)
        block.stop()

    def test_get_no_response_body(self):
        url = "http://httpbin.org/get"
        block = self.BLOCK()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
            def json(self):
                # no signal will be notified by get request worked
                raise Exception('bad json')
        block._get = MagicMock(return_value=Resp(200))
        config = {
            "http_method": "GET",
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
        block = self.BLOCK()
        # fake a response object from get request
        class Resp(object):
            def __init__(self, status_code):
                self.status_code = status_code
        # get request will return 400
        block._get = MagicMock(return_value=Resp(400))
        config = {
            "http_method": "GET",
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
        block = self.BLOCK()
        config = {
            "http_method": "POST",
            "url": url,
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([create_signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        print()
        print(self.last_notified[0].json)
        self.assertEqual('value1', self.last_notified[0].json['key1'])
        self.assertEqual('value2', self.last_notified[0].json['key2'])
        block.stop()
