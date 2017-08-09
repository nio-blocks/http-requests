HTTPRequests
============
A Block that makes HTTP requests.  One request is made for every input signal. For each successful request, an output signal is created with the url that was hit.

Properties
----------
- **basic_auth_creds**: 
- **data**: 
- **enrich**: 
- **headers**: 
- **http_method**: 
- **require_json**: 
- **retry_options**: 
- **timeout**: 
- **url**: 
- **verify**: 

Inputs
------
- **default**: Any list of signals. Signal attributes can be used for `url` and `data`.

Outputs
-------
- **default**: If the response body is json, then the body is output as a new Signal.  If the response body is a list of json, then a list is output with a new Signal for each json dict in the body.  If the response body is not json, then the raw text of the response is output on a new Signal as `raw`.

Commands
--------

Dependencies
------------
-   [requests](https://pypi.python.org/pypi/requests/)

Example Usage
-------------
**Trigger block commands.** Set the url to
```
http://{{$host}}:{{$port}}/services/{{$service_name}}/{{$block_name}}/{{$command_name}}
```
and make sure to set the Basic Authentication for your nio instance. Anytime a signal is input to this block, the command will be called. One use case is to reset a counter block on a given interval.
NOTE: This example is superseded by the [NioCommand](https://github.com/nio-blocks/nio_command) block.

Example Output
-------------
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

HTTPRequestsPostSignal
======================


Properties
----------
- **basic_auth_creds**: When making a request that needs Basic Authentication, enter the username and password.
- **enrich**: If true, the output signal will include the original signal sent into the block
- **headers**: Custom Headers. Keys and Values are Expression Properties.
- **http_method**: HTTP Method (e.g. GET|POST|PUT|DELETE).
- **require_json**: If `True` and response is not json, log warning and do not emit a signals. If `False` and response is not json, emit a signal of format `{'raw': response.text}`.
- **retry_options**: How many times to retry to HTTP request
- **timeout**: Timeout in seconds for each request, if empty or 0 then requests will not time out.
- **url**: URL to make request to.
- **verify**: For https, check a host's SSL certificate. Default value for the block is `True`, the same as the requests library.

Inputs
------
- **default**: Any list of signals. Signal attributes can be used for `url` and `data`.

Outputs
-------
- **default**: If the response body is json, then the body is output as a new Signal.  If the response body is a list of json, then a list is output with a new Signal for each json dict in the body.  If the response body is not json, then the raw text of the response is output on a new Signal as `raw`.

Commands
--------

