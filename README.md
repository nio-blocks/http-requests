HTTPRequests
===========

A Block that makes HTTP requests.

One request is made for every input signal. For each successful request, an output signal is created with the url that was hit.

Properties
--------------

-   **url**: URL to make request to.
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
