# DataUSA API
API for access US data sets

#Installation

**DataUSA** is a web platform built using Flask, an open source Python library for interacting with HTTP. this installation guide is written assuming a Linux or Linux-like environment. The following software is required to be installed locally in order to get DataViva running:

*   Python
*   Postgres
*   Redis (at least version 2.8.6)

1.  Clone from Github
        git clone https://github.com/Datawheel/datausa-api.git
2.  [optional] Create a virtual environment. We suggest installing [virtualenv](https://pypi.python.org/pypi/virtualenv) with [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/) especially if the machine you are using is used for many other web projects. This allows python libraries to be installed easily and specifically on a per proeject basis.

    Once this is complete, run the following to initialize your datausa environment.

        mkvirtualenv datausa

3.  Install Prerequisites
        sudo apt-get install python-dev
        sudo apt-get install libpq-dev
4.  Install Python modules
        pip install -r requirements.txt

5.  Run api
