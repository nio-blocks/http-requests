import json

from .http_requests_base_block import HTTPRequestsBase, HTTPMethod
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import PropertyHolder, ExpressionProperty, \
    ObjectProperty, BoolProperty, ListProperty, SelectProperty


class Param(PropertyHolder):
    key = ExpressionProperty(title='URL Parameter Key')
    value = ExpressionProperty(title='Value')


class Data(PropertyHolder):
    params = ListProperty(Param, title="Parameters")
    form_encode_data = BoolProperty(default=False,
                                    title="Form-Encode Data?")


@Discoverable(DiscoverableType.block)
class HTTPRequests(HTTPRequestsBase):

    """ A Block that makes HTTP Requests.

    Makes the configured request with the configured data parameters,
    evaluated in the context of incoming signals.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
        data (obj): URL Parameters.
        headers (list(dict)): Custom headers.

    """

    data = ObjectProperty(Data, title="Parameters")

    http_method = SelectProperty(
        HTTPMethod,
        default=HTTPMethod.GET,
        title='HTTP Method'
    )

    def _create_payload(self, signal):
        payload = {}
        for param in self.data.params:
            try:
                param_key = param.key(signal)
            except Exception:
                param_key = None
            try:
                param_value = param.value(signal)
            except Exception:
                param_value = None
            if param_key and param_value:
                payload[param_key] = param_value
        if not self.data.form_encode_data:
            payload = json.dumps(payload)
        return payload
