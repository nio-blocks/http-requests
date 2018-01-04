HTTPRequests
============
The HTTPRequests block sends an HTTP request for each incoming signal. If the incoming signal is a list of multiple signals, a request will be made for each item in the list. For each successful request, an outgoing signal is emitted that includes the response from the request.

Properties
----------
- **basic_auth_creds**: When making a request that needs Basic Authentication, enter the username and password.
- **data**: URL parameters are key-value pairs that can appear in a URL path. Keys and values can be either simple strings or expression properties that use incoming signals.
- **enrich**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **headers**: Create custom header content. Headers and values can be either simple strings or expression properties that use incoming signals.
- **http_method**: HTTP request method (e.g., GET|POST|PUT|DELETE).
- **require_json**: If `True` and response is not json, log a warning and do not emit a signal. If `False` and response is not json, emit a signal with the format `{'raw': response.text}`.
- **retry_options**: A selection of options to choose from when retrying to make a connection.
- **timeout**: Amount of time, in seconds, to wait for a response. If empty or 0, requests will never time out.
- **url**: Target URL for the request.
- **verify**: A hidden property. For HTTPS, determines whether to check a host's SSL certificate. Default value for the block is `True`.

Inputs
------
- **default**: Any list of signals. Signal attributes can be used for `url` and `data`.

Outputs
-------
- **default**: If the response body is json, then the body is output as a new signal. If the response body is a list of json, then a list is output with each json dict in the body acting as a new signal. If the response body is not json, then the raw text of the response is included in the outgoing signal as the value of the key `raw`.

Commands
--------
None

Dependencies
------------
-   [requests](https://pypi.python.org/pypi/requests/)

Example Output
--------------
```python
{
  'raw': '<html>Raw html page... boring</html>',
}
```
The request's [requests.Response](http://docs.python-requests.org/en/latest/api/#requests.Response) is appended to each output signal as a dictionary in the hidden attribute `_resp`. TODO: Make this a configurable attribute with the EnrichSignals mixin.
Example `_resp` for `requests.Response().__dict__`:
```python
{
  '_resp': {
    'status_code': None,
    'history': [],
    'reason': None,
    'raw': None,
    '_content_consumed': False,
    'elapsed': datetime.timedelta(0),
    '_content': False,
    'headers': CaseInsensitiveDict({}),
    'url': None,
    'cookies': <<class 'requests.cookies.RequestsCookieJar'>[]>,
    'encoding': None
  }
}
```

Example Usage
-------------
**Trigger block commands.** Set the url to
```
http://{{$host}}:{{$port}}/services/{{$service_name}}/{{$block_name}}/{{$command_name}}
```
and make sure to set the Basic Authentication for your nio instance. Anytime a signal is input to this block, the command will be called. One use case is to reset a counter block on a given interval.
NOTE: This example is superseded by the [NioCommand](https://github.com/nio-blocks/nio_command) block.

HTTPRequestsPostSignal
======================
The HTTPRequestsPostSignal block is similar to the [HTTPRequests](https://blocks.n.io/HTTPRequests) block. One request is made for every signal input. The input signal will be used as the body of the post request.

Properties
----------
- **basic_auth_creds**: When making a request that needs Basic Authentication, enter the username and password.
- **enrich**: If checked (true), the attributes of the incoming signal will be excluded from the outgoing signal. If unchecked (false), the attributes of the incoming signal will be included in the outgoing signal.
- **headers**: Create custom header content. Headers and values can be either simple strings or expression properties that use incoming signals.
- **http_method**: HTTP request method (e.g., GET|POST|PUT|DELETE).
- **require_json**: If `True` and response is not json, log a warning and do not emit a signal. If `False` and response is not json, emit a signal with the format `{'raw': response.text}`.
- **retry_options**: How many times to retry to HTTP request
- **timeout**: Amount of time, in seconds, to wait for a response. If empty or 0, requests will never time out.
- **url**: Target URL for the request.
- **verify**: A hidden property. For HTTPS, determines whether to check a host's SSL certificate. Default value for the block is `True`.

Inputs
------
- **default**: Any list of signals. Signal attributes can be used for `url` and `data`.

Outputs
-------
- **default**: If the response body is json, then the body is output as a new signal. If the response body is a list of json, then a list is output with each json dict in the body acting as a new signal. If the response body is not json, then the raw text of the response is included in the outgoing signal as the value of the key `raw`.

Commands
--------
None

