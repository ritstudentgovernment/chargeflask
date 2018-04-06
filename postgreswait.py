import psycopg2
from urllib.parse import urlparse
import os
import time

url = os.environ.get("SQLALCHEMY_TEST_DATABASE_URI","")

result = urlparse(url)
stop = False

while not stop:
    try:
        connection = psycopg2.connect(database=result.path[1:],user=result.username,password=result.password,host=result.hostname)
        stop = True
        connection.close()
    except:
        print("Waiting for test database to be created")
        time.sleep(1)
