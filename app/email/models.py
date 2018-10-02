"""
filename: models.py
description: Models for email.
created by: Omar De La Hoz (oed7416@rit.edu)
created on: 09/27/18
"""

from huey import RedisHuey
import os

huey = RedisHuey(host=os.environ.get('REDIS_URL', 'redis://localhost:6379/?db=1'))
