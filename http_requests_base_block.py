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
from simplejson.scanner import JSONDecodeError


class ResponseSignal(Signal):

    def __init__(self, data):
        super().__init__()
        for k in data:
            setattr(self, k, data[k])


class Header(PropertyHolder):
    header = StringProperty(title='Header')
    value = StringProperty(title='Value')


class BasicAuthCreds(PropertyHolder):
    username = StringProperty(title='Username')
    password = StringProperty(title='Password')


class HTTPMethod(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    HEAD = 'head'
    OPTIONS = 'options'


class HTTPRequestsBase(Block):

    """ A base for Blocks that makes HTTP Requests.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
    """

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
    require_json = BoolProperty(title="Require JSON Response", default=False)

    def process_signals(self, signals):
        new_signals = []
        for signal in signals:
            new_sigs = self._make_request(signal)
            if new_sigs:
                new_signals.extend(new_sigs)
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
            r = self._execute_request(url, auth, payload, headers)
        except Exception as e:
            self._logger.warning("Bad Http Request: {0}".format(e))
            return
        
        if 200 <= r.status_code < 300:
            return self._process_response(r)
        else:
            self._logger.warning(
                "{} request to {} returned with response code: {}".format(
                    self.http_method,
                    url,
                    r.status_code
                )
            )

    def _execute_request(self, url, auth, data, headers):
        try:
            method_name = self.http_method.value
        except:
            method_name = HTTPMethod.GET.value
            self._logger.debug(
                "Invalid HTTP method selection. Defaulting to GET."
            )
        finally:
            method = getattr(requests, method_name)

        return method(url, auth=auth, data=data, headers=headers)


    def _process_response(self, response):
        result = None
        try:
            data = response.json()

            # if the response is a dictionary, build a signal
            if isinstance(data, dict):
                result = [ResponseSignal(data)]

            # if the response is a list, build a signal for each element
            elif isinstance(data, list):
                sigs = []
                for s in data:
                    sigs.append(ResponseSignal(s))
                if sigs:
                    result = sigs

            # otherwise, no dice on parsing the response body
            else:
                self._logger.warning("Response body could not be parsed into "
                                     "Signal(s): {}".format(data))
        except JSONDecodeError:
            if not self.require_json:
                result = [ResponseSignal({'raw': response.text})]
            else:
                self._logger.warning(
                    "Request was successful, but response was not "
                    "valid JSON. No ResponseSignal was created."
                )
        except Exception as e:
            self._logger.warning(
                "Request was successful but "
                "failed to create ResponseSignal: {}".format(e)
            )
        finally:
            return result


            
    def _create_auth(self):
        if self.basic_auth_creds.username:
            return requests.auth.HTTPBasicAuth(
                self.basic_auth_creds.username,
                self.basic_auth_creds.password
            )

    def _create_payload(self, signal):
        return json.dumps(signal.to_dict())

    def _create_headers(self, signal):
        headers = {}
        for header in self.headers:
            header_header = header.header
            header_value = header.value
            if header_header and header_value:
                headers[header_header] = header_value
        return headers
