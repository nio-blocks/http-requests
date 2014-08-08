HTTPRequests
===========

A Block that makes HTTP requests.

One request is made for every input signal. For each successful request, an output signal is created with the url that was hit.

Properties
--------------

-   **url**: URL to make request to. Expression property.
-   **basic_auth_creds**: When making a request that needs Basic Authentication, enter the username and password.


Dependencies
----------------

-   [requests](https://pypi.python.org/pypi/requests/)

Commands
----------------
None

Input
-------
Any list of signals. No attributes of the signal are used. They simply act as a trigger to make the request.

Output
---------
One output signal is created for each successful http request. The signal contains the *url* that was hit.

Example Usage
-------------
**Trigger block commands.** Set the url to `http://{{$host}}:{{$port}}/services/{{$service_name}}/{{$block_name}}/{{$command_name}}` and make sure to set the Basic Authentication for your nio instance. Anytime a signal is input to this block, the command will be called. One use case is to reset a counter block on a given interval.
