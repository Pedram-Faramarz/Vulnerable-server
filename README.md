Project summary

This project is a small example web server made with Flask.
It intentionally contains three security problems so you can learn how to find and fix them:

Internal information exposure — server shows stack trace or internal details on error.

Hard-coded secrets & secrets in repo — API keys and passwords are stored in files and code.

Unsafe deserialization — server unpickles data from user input, which allows code execution.

The lab shows how to reproduce each problem, explains the risk, and includes a pull request (PR) that fixes them without changing the app behavior
