from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties import StringProperty
import json
from .http_requests_block import HTTPRequests


@Discoverable(DiscoverableType.block)
class HTTPRequestsEnrichSignal(HTTPRequests):

    """ A Block that makes HTTP Requests and enriches the input signal
    with the resulting response. If the property *enrich_signal_attr* is set,
    then the response signal that normally would be output, is instead placed
    into this attribute on the original input signal

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.
        http_method (select): HTTP method (ex. GET, POST,
            PUT, DELETE, etc).
        data (obj): URL Parameters.
        headers (list(dict)): Custom headers.
        enrich_signal_attr (str): If specified, the response Signal is placed
            inside this attribute on the original input Signal.

    """

    enrich_signal_attr = StringProperty(title='Enrich Signal - Attribute Name',
                                        default='')

    def process_signals(self, signals):
        new_signals = []
        for signal in signals:
            new_sigs = self._make_request(signal)
            if new_sigs:
                if self.enrich_signal_attr:
                    for new_sig in new_sigs:
                        sig = Signal(signal.to_dict())
                        setattr(sig, self.enrich_signal_attr, new_sig.to_dict())
                        new_signals.append(sig)
                else:
                    new_signals.extend(new_sigs)
        if new_signals:
            self.notify_signals(new_signals)
