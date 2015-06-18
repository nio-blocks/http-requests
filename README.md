HTTPRequests
===========

A Block that makes HTTP requests.

One request is made for every input signal. For each successful request, an output signal is created with the url that was hit.

Properties
--------------

-   **url**: URL to make request to. Expression property.
-   **http_method**: HTTP Method (ex. GET, POST, PUT, DELETE, etc...).
-   **basic_auth_creds**: When making a request that needs Basic Authentication, enter the username and password.
-   **data**: URL Parameters. Keys and Values are Expression Properties.
-   **headers**: Custom Headers.
-   **require_json**: If `True` and response is not json, log warning and do not emit a signals. If `False` and response is not json, emit a signal of format {'raw': response.text}.


Dependencies
----------------

-   [requests](https://pypi.python.org/pypi/requests/)

Commands
----------------
None

Input
-------
Any list of signals. Signal attributes can be used for *url* and *data*.

Output
---------
One output signal is created for each successful http request. The requets Response object is place in the signal. Common attributes on the signal:

-   url
-   origin
-   data
-   json
-   form
-   args

Example Usage
-------------
**Trigger block commands.** Set the url to `http://{{$host}}:{{$port}}/services/{{$service_name}}/{{$block_name}}/{{$command_name}}` and make sure to set the Basic Authentication for your nio instance. Anytime a signal is input to this block, the command will be called. One use case is to reset a counter block on a given interval.

NOTE: This example is superseded by the [NioCommand](https://github.com/nio-blocks/nio_command) block.
