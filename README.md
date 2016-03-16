# DataUSA API
To learn more about the API, visit the [DataUSA API Wiki page](https://github.com/DataUSA/datausa-api/wiki) or visit the [DataUSA Quick Start Guide](http://beta.datausa.io/about/api/).

#Installation

**DataUSA** is a web platform built using Flask, an open source Python library for interacting with HTTP. this installation guide is written assuming a Linux or Linux-like environment. The following software is required to be installed locally in order to get DataViva running:

*   Python
*   Postgres

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

5.  Set environment variables
        
        export DATAUSA_DB_NAME=db_name
        export DATAUSA_DB_USER=postgres_user
        export DATAUSA_DB_PW=postgres_pw
        export DATAUSA_DB_HOST=127.0.0.1

6.  Run api
