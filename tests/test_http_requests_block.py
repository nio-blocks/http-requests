from nio.common.signal.base import Signal
from nio.modules.threading import Event
from nio.util.support.block_test_case import NIOBlockTestCase
from ..http_requests_block import HTTPRequests


class TestHTTPRequests(NIOBlockTestCase):

    def setUp(self):
        super().setUp()
        self.last_notified = []
        self.event = Event()

    def signals_notified(self, signals, output_id='default'):
        self.last_notified = signals
        self.event.set()
        self.event.clear()

    def test_create_payload(self):
        block = HTTPRequests()
        self.configure_block(block, {})
        payload = block._create_payload(Signal())
        self.assertEqual({}, payload)
        self.configure_block(block, {'data': {'form_encode_data': True}})
        payload = block._create_payload(Signal())
        self.assertEqual({}, payload)

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

    def test_post2(self):
        url = "http://httpbin.org/post"
        block = HTTPRequests()
        config = {
            "url": url,
            "http_method": "POST",
            "data": {
                "params": [
                    {"key": "string", "value": "text"},
                    {"key": "int", "value": "{{int(1)}}"}
                ]
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual('text', self.last_notified[0].json['string'])
        self.assertEqual(1, self.last_notified[0].json['int'])
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

    def test_resp_attr(self):
        ''' Hidden attr '_resp' is added to signals '''
        url = "http://httpbin.org/get"
        block = HTTPRequests()
        config = {"url": url}
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.event.wait(2)
        self.assertEqual(url, self.last_notified[0].url)
        self.assertEqual(200, self.last_notified[0]._resp['status_code'])
        block.stop()
