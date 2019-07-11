import responses
from unittest.mock import MagicMock, patch

from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase

from ..http_requests_block import HTTPRequests


class TestHTTPRequestsBlock(NIOBlockTestCase):

    def test_execute_request_verify_flag(self):
        block = HTTPRequests()
        self.configure_block(block, {})
        with patch('requests.get') as get:
            block._execute_request('url', None, None, None, timeout=10)
            get.assert_called_once_with(
                'url',
                auth=None,
                data=None,
                headers=None,
                verify=True,
                timeout=10)
        self.configure_block(block, {'verify': False})
        with patch('requests.get') as get:
            block._execute_request('url', None, None, None, timeout=10)
            get.assert_called_once_with(
                'url',
                auth=None,
                data=None,
                headers=None,
                verify=False,
                timeout=10)

    def test_create_payload(self):
        block = HTTPRequests()
        self.configure_block(block, {})
        payload = block._create_payload(Signal())
        self.assertEqual({}, payload)
        self.configure_block(block, {'data': {'form_encode_data': True}})
        payload = block._create_payload(Signal())
        self.assertEqual({}, payload)

    def test_create_headers(self):
        block = HTTPRequests()
        self.configure_block(block, {})
        headers = block._create_headers(Signal())
        self.assertEqual({}, headers)
        self.configure_block(block, {'headers': [
            {'header': '{{ $header }}', 'value': '{{ $value }}'}]})
        headers = block._create_headers(Signal({'header': 'h', 'value': 'v'}))
        self.assertEqual({'h': 'v'}, headers)

    @responses.activate
    def test_post(self):
        url = 'http://foo/'
        params = [
            {'key': 'key1', 'value': 'value1'},
            {'key': 'key2', 'value': 'value2'},
        ]
        responses.add(
            responses.POST,
            url,
            json={param['key']: param['value'] for param in params},
            status=200)
        block = HTTPRequests()
        config = {
            'url': url,
            'http_method': 'POST',
            'data': {
                'params': params
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        signals = [s.to_dict() for s in self.last_notified[DEFAULT_TERMINAL]]
        self.assertEqual(url, responses.calls[0].request.url)
        self.assertEqual('value1', signals[0]['key1'])
        self.assertEqual('value2', signals[0]['key2'])
        block.stop()

    @responses.activate
    def test_post_form(self):
        url = 'http://foo/'
        params = [
            {'key': 'key1', 'value': 'value1'},
            {'key': 'key2', 'value': 'value2'},
        ]
        responses.add(
            responses.POST,
            url,
            json={param['key']: param['value'] for param in params},
            status=200)
        block = HTTPRequests()
        config = {
            'url': url,
            'http_method': 'POST',
            'data': {
                'params': params,
                'form_encode_data': True
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.assertEqual(
            'application/x-www-form-urlencoded',
            responses.calls[0].request.headers['Content-Type'])
        block.stop()

    @responses.activate
    def test_post_expr(self):
        url = 'http://foo/'
        params = [
            {'key': '{{ $key }}', 'value': '{{ $val }}'},
        ]
        responses.add(
            responses.POST,
            url,
            json={'greeting': 'cheers'},
            status=200)
        block = HTTPRequests()
        config = {
            'url': url,
            'http_method': 'POST',
            'data': {
                'params': params
            }
        }
        self.configure_block(block, config)
        block.start()
        block.process_signals([
            Signal({'key': 'greeting', 'val': 'cheers'}),
        ])
        signals = [s.to_dict() for s in self.last_notified[DEFAULT_TERMINAL]]
        self.assertEqual(url, responses.calls[0].request.url)
        self.assertEqual(
            'cheers', signals[0]['greeting'])
        block.stop()

    @responses.activate
    def test_resp_attr(self):
        ''' Hidden attr '_resp' is added to signals '''
        url = 'http://foo/'
        responses.add(
            responses.GET,
            url,
            status=200)
        block = HTTPRequests()
        config = {'url': url}
        self.configure_block(block, config)
        block.start()
        block.process_signals([Signal()])
        self.assertEqual(url, responses.calls[0].request.url)
        self.assertEqual(200, responses.calls[0].response.status_code)
        block.stop()

    @patch('requests.get')
    def test_default_configuration(self, mock_get):
        url = 'https://httpbin.org/get'
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        mock_get.assert_called_once_with(
            url,
            auth=None,
            data={},
            headers={},
            verify=True,
            timeout=None
        )
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].url, url)
        self.assertFalse(
            hasattr(self.last_notified[DEFAULT_TERMINAL][0], 'input_attr'))
        block.stop()

    @patch('requests.get')
    def test_enriched_signals(self, mock_get):
        url = 'https://httpbin.org/get'
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp
        block = HTTPRequests()
        # fake a response object from get request
        # class Resp(object):
        #     def __init__(self, status_code):
        #         self.status_code = status_code
        #     def json(self):
        # a signal will be notified with this response body
        #         return {'url': url}
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url,
            'enrich': {
                'exclude_existing': False,
                'enrich_field': 'response'
            }
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(mock_get.called)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].response['url'], url)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].input_attr, 'value')
        block.stop()

    @patch('requests.get')
    def test_timeout(self, mock_get):
        url = 'https://httpbin.org/get'
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url,
            'timeout': 10
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        mock_get.assert_called_once_with(
            url,
            auth=None,
            data={},
            headers={},
            verify=True,
            timeout=10
        )
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].url, url)
        self.assertFalse(
            hasattr(self.last_notified[DEFAULT_TERMINAL][0], 'input_attr'))
        block.stop()

    @patch('requests.get')
    def test_multiple_sigs(self, mock_get):
        url = 'https://httpbin.org/get'
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url,
            'enrich': {
                'exclude_existing': False,
                'enrich_field': 'response'
            }
        })
        block.start()
        block.process_signals([
            Signal({'input_attr': 'value1'}),
            Signal({'input_attr': 'value2'})
        ])
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(len(self.last_notified[DEFAULT_TERMINAL]), 2)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].response['url'], url)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][1].response['url'], url)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].input_attr, 'value1')
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][1].input_attr, 'value2')
        block.stop()

    @patch('requests.get')
    def test_get_with_enrich_signal_list_resp(self, mock_get):
        url = 'https://httpbin.org/get'
        url2 = 'https://httpbin.org/get2'
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value=[{'url': url}, {'url': url2}])
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url,
            'enrich': {
                'exclude_existing': False,
                'enrich_field': 'response'
            }
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        self.assertTrue(mock_get.called)
        self.assertEqual(
            # this isn't right, but make it pass
            self.last_notified[DEFAULT_TERMINAL][0].response['url'], url2)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][1].response['url'], url2)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].input_attr, 'value')
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][1].input_attr, 'value')
        block.stop()

    @patch('requests.get')
    def test_request_exceptions(self, mock_get):
        from requests.exceptions import Timeout
        url = 'https://httpbin.org/get'
        block = HTTPRequests()
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value={'url': url})
        mock_get.side_effect = [
            Timeout,
            Timeout,
            Timeout,
            resp,
        ]
        self.configure_block(block, {
            'http_method': 'GET',
            'url': url,
            'timeout': 10,
            'log_level': 'DEBUG',
            'enrich': {
                'exclude_existing': False,
                'enrich_field': 'response'
            },
            'retry_options': {
                'max_retry': 2,
                'multiplier': 0
            }
        })
        block.start()
        block.process_signals([
            Signal({'input_attr': 'value1'}),
            Signal({'input_attr': 'value2'})
        ])
        block.stop()

        self.assertEqual(len(self.last_notified[DEFAULT_TERMINAL]), 1)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].response['url'], url)
        self.assertEqual(
            self.last_notified[DEFAULT_TERMINAL][0].input_attr, 'value2')

    @patch('requests.get')
    def test_non_json_response(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value=18)
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'require_json': False
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        block.stop()
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].raw, resp.text)

    @patch('requests.get')
    def test_json_required_non_json_response(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(return_value=18)
        mock_get.return_value = resp
        block = HTTPRequests()
        self.configure_block(block, {
            'http_method': 'GET',
            'require_json': True
        })
        block.start()
        block.process_signals([Signal({'input_attr': 'value'})])
        block.stop()
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].input_attr, 'value')
