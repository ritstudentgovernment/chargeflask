# chargeflask [![Build Status](https://travis-ci.org/ritstudentgovernment/chargeflask.svg?branch=master)](https://travis-ci.org/ritstudentgovernment/chargeflask) [![codecov](https://codecov.io/gh/ritstudentgovernment/chargeflask/branch/master/graph/badge.svg)](https://codecov.io/gh/ritstudentgovernment/chargeflask) 



Flask implementation of **RIT Charge Tracker** server.

The web client for this project can be found at [chargevue.](https://github.com/ritstudentgovernment/chargevue)



### Development Setup

Prerequisites: Flask and PostgreSQL

1. Pull project from this repo.
2. Install and create [virtual environment](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/).
3. Create a database for the project.
4. Specify the ``SQLALCHEMY_DATABASE_URI`` in the ``config.py`` file with the database path.
5. Activate virtual environment.
6. Execute `pip install -r requirements.txt`
7. Run ``python run.py``



