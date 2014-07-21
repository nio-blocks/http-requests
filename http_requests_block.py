from nio.common.block.base import Block
from nio.common.signal.base import Signal
from nio.common.versioning.dependency import DependsOn
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.object import ObjectProperty

import requests


class BasicAuthCreds(PropertyHolder):
    username = StringProperty(title='Username')
    password = StringProperty(title='Password')


@Discoverable(DiscoverableType.block)
class HTTPRequests(Block):

    """ A Block that makes HTTP Requests.

    Properties:
        url (str): URL to make request to.
        basic_auth_creds (obj): Basic Authentication credentials.

    """

    url = StringProperty(title='URL Target', default="http://127.0.0.1:8181")
    basic_auth_creds = ObjectProperty(BasicAuthCreds, title='Credentials (BasicAuth)')

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
            auth = self._create_auth()
            r = self._get(auth, signal)
            new_signal = Signal()
            new_signal.url = r.url
            return new_signal
        except Exception as e:
            self._logger.warning("Bad Http Request: {0}".format(e))

    def _get(self, auth, signal):
        return requests.get(self.url, auth=auth)

    def _create_auth(self):
        if self.basic_auth_creds.username:
            return requests.auth.HTTPBasicAuth(
                self.basic_auth_creds.username,
                self.basic_auth_creds.password
            )
