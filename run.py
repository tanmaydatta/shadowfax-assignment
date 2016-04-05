from app import app
import thread
import os
# from app.views import socket_thread
from app.server import *

app.secret_key = 'super secret key'

# start socket thread to accept socket connections
thread.start_new_thread(socket_thread, ())

ip=os.popen("ip route get 8.8.8.8 | awk '{print $NF; exit}'").read()

app.run(host=ip.split()[0],debug=True,use_reloader=False)
