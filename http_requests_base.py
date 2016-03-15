from nio.block.base import Block
from nio.signal.base import Signal
from nio.properties.holder import PropertyHolder
from nio.properties.select import SelectProperty
from nio.properties.string import StringProperty
from nio.properties import Property
from nio.properties.object import ObjectProperty
from nio.properties.bool import BoolProperty
from nio.properties.list import ListProperty
from enum import Enum
import requests
import json
from nio.block.mixins.enrich.enrich_signals import EnrichSignals, EnrichProperties


class Header(PropertyHolder):
    header = Property(title='Header', allow_none=True)
    value = Property(title='Value', allow_none=True)


class BasicAuthCreds(PropertyHolder):
    username = StringProperty(title='Username', allow_none=True)
    password = StringProperty(title='Password', allow_none=True)


class HTTPMethod(Enum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    HEAD = 'head'
    OPTIONS = 'options'


class HTTPRequestsBase(EnrichSignals, Block):

    """ A base for Blocks that makes HTTP Requests.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
    """

    url = Property(title='URL Target',
                   default="http://127.0.0.1:8181")
    basic_auth_creds = ObjectProperty(BasicAuthCreds,
                                      title='Credentials (BasicAuth)',
                                      default=BasicAuthCreds())
    http_method = SelectProperty(
        HTTPMethod,
        default=HTTPMethod.GET,
        title='HTTP Method'
    )
    headers = ListProperty(Header, title="Headers", default=[])
    require_json = BoolProperty(title="Require JSON Response", default=False)
    verify = BoolProperty(
        title="Verify host's SSL certificate", default=True, visible=False)

    # TODO: remove this when mixin in framework is fixed
    enrich = ObjectProperty(EnrichProperties,
                            title='Signal Enrichment',
                            default=EnrichProperties())

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
            self.logger.warning(
                "Failed to evaluate url {}: {}".format(url, e)
            )
            return
        auth = self._create_auth()
        payload = self._create_payload(signal)
        headers = self._create_headers(signal)

        try:
            r = self._execute_request(url, auth, payload, headers)
        except Exception as e:
            self.logger.warning("Bad Http Request: {0}".format(e))
            return

        if 200 <= r.status_code < 300:
            return self._process_response(r, signal)
        else:
            self.logger.warning(
                "{} request to {} returned with response code: {}".format(
                    self.http_method(),
                    url,
                    r.status_code
                )
            )
            return [signal]

    def _execute_request(self, url, auth, data, headers):
        try:
            method_name = self.http_method().value
        except:
            method_name = HTTPMethod.GET.value
            self.logger.debug(
                "Invalid HTTP method selection. Defaulting to GET."
            )
        finally:
            method = getattr(requests, method_name)

        return method(url, auth=auth, data=data, headers=headers,
                      verify=self.verify())

    def _process_response(self, response, signal):
        result = []
        try:
            data = response.json()

            # if the response is a dictionary, build a signal
            if isinstance(data, dict):
                result = [self.get_output_signal(data, signal)]

            # if the response is a list, build a signal for each element
            elif isinstance(data, list):
                sigs = []
                for s in data:
                    sigs.append(
                        self.get_output_signal(s, signal))
                if sigs:
                    result = sigs

            # otherwise, no dice on parsing the response body
            else:
                self.logger.warning("Response body could not be parsed into "
                                     "Signal(s): {}".format(data))
                result = [signal]
        except ValueError:
            if not self.require_json():
                result = [self.get_output_signal(
                    {'raw': response.text}, signal)]
            else:
                self.logger.warning(
                    "Request was successful, but response was not "
                    "valid JSON. No response signal was created."
                )
                result = [signal]
        except Exception as e:
            self.logger.warning(
                "Request was successful but "
                "failed to create response signal: {}".format(e)
            )
            result = [signal]
        finally:
            # Add the rest of the Response information to the signal
            for sig in result:
                try:
                    sig._resp = response.__dict__
                except:
                    self.logger.warning("Response failed to save to signal")
            return result

    def _create_auth(self):
        if self.basic_auth_creds().username() is not None:
            return requests.auth.HTTPBasicAuth(
                self.basic_auth_creds().username(),
                self.basic_auth_creds().password()
            )

    def _create_payload(self, signal):
        return json.dumps(signal.to_dict())

    def _create_headers(self, signal):
        headers = {}
        for header in self.headers():
            header_header = header.header(signal)
            header_value = header.value(signal)
            if header_header and header_value:
                headers[header_header] = header_value
        return headers
