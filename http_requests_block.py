from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.common.versioning.dependency import DependsOn
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.select import SelectProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.object import ObjectProperty
from nio.metadata.properties.bool import BoolProperty
from nio.metadata.properties.list import ListProperty

from enum import Enum
import requests
import json


class ResponseSignal(Signal):

    def __init__(self, data):
        super().__init__()
        for k in data:
            setattr(self, k, data[k])


class Param(PropertyHolder):
    key = ExpressionProperty(title='URL Parameter Key')
    value = ExpressionProperty(title='Value')

class Header(PropertyHolder):
    header = StringProperty(title='Header')
    value = StringProperty(title='Value')


class BasicAuthCreds(PropertyHolder):
    username = StringProperty(title='Username')
    password = StringProperty(title='Password')


class HTTPMethod(Enum):
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3
    HEAD = 4
    OPTIONS = 5


@Discoverable(DiscoverableType.block)
class HTTPRequests(Block):

    """ A Block that makes HTTP Requests.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
        data (obj): URL Parameters.
        headers (list(dict)): Custom headers.

    """
    params = ListProperty(Param, title="Parameters")
    form_encode_data = BoolProperty(default=False,
                                    title="Form-Encode Data?")
    url = ExpressionProperty(title='URL Target',
                             default="http://127.0.0.1:8181")
    basic_auth_creds = ObjectProperty(BasicAuthCreds,
                                      title='Credentials (BasicAuth)')
    http_method = SelectProperty(
        HTTPMethod,
        default=HTTPMethod.GET,
        title='HTTP Method'
    )
    headers = ListProperty(Header, title="Headers")

    def process_signals(self, signals):
        new_signals = []
        for signal in signals:
            new_signal = self._make_request(signal)
            if new_signal:
                new_signals.append(new_signal)
        if new_signals:
            self.notify_signals(new_signals)

    def _make_request(self, signal):
        try:
            url = self.url(signal)
        except Exception as e:
            self._logger.warning(
                "Failed to evaluate url {}: {}".format(url, e)
            )
            return
        auth = self._create_auth()
        payload = self._create_payload(signal)
        headers = self._create_headers(signal)
        try:
            if self.http_method == HTTPMethod.GET:
                r = self._get(url, auth, payload, headers)
            elif self.http_method == HTTPMethod.POST:
                r = self._post(url, auth, payload, headers)
            elif self.http_method == HTTPMethod.PUT:
                r = self._put(url, auth, payload, headers)
            elif self.http_method == HTTPMethod.DELETE:
                r = self._delete(url, auth, payload, headers)
            elif self.http_method == HTTPMethod.HEAD:
                r = self._head(url, auth, payload, headers)
            elif self.http_method == HTTPMethod.OPTIONS:
                r = self._options(url, auth, payload, headers)
            else:
                # default to GET
                r = self._get(url, auth, payload, headers)
        except Exception as e:
            self._logger.warning("Bad Http Request: {0}".format(e))
            return
        if 200 <= r.status_code < 300:
            try:
                sig = ResponseSignal(r.json())
                return sig
            except Exception as e:
                self._logger.warning(
                    "Request was successfull but "
                    "failed to create ResponseSignal: {}".format(e)
                )
                return
        else:
            self._logger.warning("{} request to {} returned with "
                                    "response code: {}".format(
                                        self.http_method,
                                        url,
                                        r.status_code
                                    )
            )

    def _get(self, url, auth, payload, headers):
        return requests.get(
            url, auth=auth, data=payload, headers=headers
        )

    def _post(self, url, auth, payload, headers):
        return requests.post(
            url, auth=auth, data=payload, headers=headers
        )

    def _put(self, url, auth, payload, headers):
        return requests.put(
            url, auth=auth, data=payload, headers=headers
        )

    def _delete(self, url, auth, payload, headers):
        return requests.delete(
            url, auth=auth, data=payload, headers=headers
        )

    def _head(self, url, auth, payload, headers):
        return requests.head(
            url, auth=auth, data=payload, headers=headers
        )

    def _options(self, url, auth, payload, headers):
        return requests.options(
            url, auth=auth, data=payload, headers=headers
        )

    def _create_auth(self):
        if self.basic_auth_creds.username:
            return requests.auth.HTTPBasicAuth(
                self.basic_auth_creds.username,
                self.basic_auth_creds.password
            )

    def _create_payload(self, signal):
        payload = {}
        for param in self.params:
            try:
                param_key = param.key(signal)
            except Exception as e:
                param_key = None
            try:
                param_value = param.value(signal)
            except Exception as e:
                param_value = None
            if param_key and param_value:
                payload[param_key] = param_value
        if not self.form_encode_data:
            payload = json.dumps(payload)
        return payload

    def _create_headers(self, signal):
        headers = {}
        for header in self.headers:
            header_header = header.header
            header_value = header.value
            if header_header and header_value:
                headers[header_header] = header_value
        return headers
