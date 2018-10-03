# chargeflask [![Build Status](https://travis-ci.org/ritstudentgovernment/chargeflask.svg?branch=master)](https://travis-ci.org/ritstudentgovernment/chargeflask) [![codecov](https://codecov.io/gh/ritstudentgovernment/chargeflask/branch/master/graph/badge.svg)](https://codecov.io/gh/ritstudentgovernment/chargeflask) 



Flask implementation of **RIT Charge Tracker** server.

The web client for this project can be found at [chargevue.](https://github.com/ritstudentgovernment/chargevue)



### Building Containers

Prerequisites: Flask and PostgreSQL

1. Install [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/install/)
2. Pull project from this repo.
3. Copy the `template.env` file at the root of the project to `.env` and fill out the environment variables.
4.  Run `docker-compose up` from the root project directory. 


**If you have a Mac, you will have to create the folders `/chargeflaskdata`, `chargeflaskdata/postgres-data`, `chargeflaskdata/redis-data` and give Docker permission to these folders.**



To ensure that all the containers are running, simply run `docker ps` you should have an output similar to the following:

```bash
CONTAINER ID        IMAGE                     COMMAND                  CREATED             STATUS              PORTS                    NAMES
0c2e1f4c7cb7        chargeflask_huey_worker   "sh -c 'python postg…"   39 seconds ago      Up 38 seconds                                chargeflask_huey_worker_1
db670f5e1f39        chargeflask_flask         "sh -c 'python postg…"   25 hours ago        Up 38 seconds       0.0.0.0:5000->5000/tcp   chargeflask_flask_1
cd810b6790c1        redis:alpine              "docker-entrypoint.s…"   27 hours ago        Up About an hour    6379/tcp                 redis
dc1320d2b173        chargeflask_postgres_db   "docker-entrypoint.s…"   27 hours ago        Up About an hour    5432/tcp                 postgres
```



