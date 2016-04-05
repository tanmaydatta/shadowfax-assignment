from flask import Flask

app = Flask(__name__)
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.flushall()
from app import views
