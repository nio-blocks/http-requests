from .http_requests_base import HTTPRequestsBase, HTTPMethod
from nio.properties import SelectProperty
from nio.util.discovery import discoverable


@discoverable
class HTTPRequestsPostSignal(HTTPRequestsBase):

    """ A Block that makes HTTP Requests.

    Makes the configured request with a payload consisting of the json-
    serialized incoming signal.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
    """

    http_method = SelectProperty(
        HTTPMethod,
        default=HTTPMethod.POST,
        title='HTTP Method',
        visible=False
    )
