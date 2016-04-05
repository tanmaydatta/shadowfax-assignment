import base64
import hashlib
import os
import socket
import thread
import ipdb
from app import r
import json
import collections
import soldier
from ast import literal_eval
import time

ip=os.popen("ip route get 8.8.8.8 | awk '{print $NF; exit}'").read()
HOST = ip.split()[0]
PORT = 8887
MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
HSHAKE_RESP = "HTTP/1.1 101 Switching Protocols\r\n" + \
			"Upgrade: websocket\r\n" + \
			"Connection: Upgrade\r\n" + \
			"Sec-WebSocket-Accept: %s\r\n" + \
			"\r\n"


#unicode keys to str
def convert(data):
	if isinstance(data, basestring):
		return str(data)
	elif isinstance(data, collections.Mapping):
		return dict(map(convert, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		return type(data)(map(convert, data))
	else:
		return data


def queue_data(filename):
	global clients_set
	print 'queue data for ===== ' + filename
	while True:
		# print 'inloop'
		time.sleep(0.1)
		x = r.lpop(filename+'queue')
		if x:
			y = r.lpop(filename+'enqueue')
			z = r.lpop(filename+'ip')
			# ipdb_set_trace()
			print 'inloop ' + x + "=====" + y
			# print literal_eval(x)
			f=open('app/files/' + filename,'r')
			data = f.read()
			f.close()
			cursor = int(x.split('$$$')[1])
			val = int(x.split('$$$')[0])
			if val!=46 and val != 8:
				data = data[:cursor-1] + chr(val) + data[cursor-1:]
			elif val == 8:
				data = data[:cursor-2] + data[cursor-1:]
			else:
				data = data[:cursor] + data[cursor+1:]

			print 'write ' + data
			f=open('app/files/' + filename,'w')
			f.write(data);
			f.close()
			for con,addr in clients_set:
				print con,addr
				if r.get(addr[0]) == filename and addr[0]!=z:
					try:
						con.send(encode_data(y))
						print 'sent'
					except:
						print 'error'
						pass


		


def start_server(host, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print port
	# s.bind((host, port))
	# s.listen(5)
	return s

def encode_data(data_to_encode):
	resp = bytearray([0b10000001, len(data_to_encode)])
	for d in bytearray(data_to_encode):
		resp.append(d)
	return resp

def decode_data(data_to_decode):
	databyte = bytearray(data_to_decode)
	datalen = (0x7F & databyte[1])
	if(datalen > 0):
		mask_key = databyte[2:6]
		masked_data = databyte[6:(6+datalen)]
		unmasked_data = [masked_data[i] ^ mask_key[i%4] for i in range(len(masked_data))]
		data_from_client = str(bytearray(unmasked_data))
	return data_from_client or data_to_decode

def handle_client_handshake(conn):
	data = conn.recv(4096)
	# print decode_data(data)
	headers = {}
	lines = data.splitlines()
	for l in lines:
		# print l
		parts = l.split(": ", 1)
		if len(parts) == 2:
			headers[parts[0]] = parts[1]
	headers['code'] = lines[len(lines) - 1]
	key = headers['Sec-WebSocket-Key']
	resp_data = HSHAKE_RESP % ((base64.b64encode(hashlib.sha1(key+MAGIC).digest()),))
	conn.send(resp_data)

def send_to_client(data, conn, ad,data_recv):
	# ipdb.set_trace()
	global clients_set
	filename = r.get(ad[0])
	while r.get(filename+'lock') == 1:
		pass
	r.set(filename+'lock',1)
	f=open('app/files/' + filename,'w')
	f.write(data_recv['value']);
	f.close()
	for con,addr in clients_set:
		print con,addr
		if r.get(addr[0]) == filename and addr[0]!=ad[0]:
			try:
				con.send(data)
				print 'sent'
			except:
				print 'error'
				pass
	r.set(filename+'lock',0)
	# try:
	#     conn.sendall(data)
	# except:
	#     print("error sending to a client")




def new_client(conn, addr, clients_set, files_mapping):
	clients_set.add((conn,addr))
	handle_client_handshake(conn)
	# send_file_string(conn)
	filename = r.get(addr[0])
	print addr[0] + "testing" 
	print 'new client'
	while 1:
		ip = addr[0]
		print ip
		data_recv = conn.recv(4096)
		if not data_recv:
			break
		print "data received ======= " + data_recv
		try:
			# ipsb.set_trace()
			print 'decoding'
			data_from_client = decode_data(data_recv)
			data_from_client = json.loads(data_from_client)
			print 'decoded ====== ' + data_from_client['value']
			# send_to_client(encode_data(str(convert(data_from_client))), conn, addr,data_from_client)
			r.rpush(filename+'queue', data_from_client['value']+'$$$'+str(data_from_client['cursor']))
			r.rpush(filename+'enqueue', str(convert(data_from_client)))
			r.rpush(filename+'ip', ip)
		except Exception as e:
			print str(e)
		# if ".txt" in data_from_client:
		# open_file_name = store_mapping_and_send_file_data(conn, data_from_client, files_mapping)
		# else:
			# save_to_file(data_from_client, open_file_name)
			# send_updated_file(data_from_client, open_file_name, clients_set, files_mapping)

	print "exit"
# if __name__ == "__main__":
#     clients_set = set()
#     files_mapping = {}
#     s = start_server(HOST, PORT)

	# while 1:
	#     conn, addr = s.accept()
	#     thread.start_new_thread(new_client, (conn, addr, clients_set, files_mapping))

def socket_thread():
	global clients_set
	global files_mapping
	global s
	s.bind((HOST, PORT))
	s.listen(5)
	print "starting socket server"
	while 1:
		conn, addr = s.accept()
		thread.start_new_thread(new_client, (conn, addr, clients_set, files_mapping))

def start_queue(filename):
	thread.start_new_thread(queue_data, (filename,))

# if __name__ == "__main__":
clients_set = set()
files_mapping = {}
s = start_server(HOST, PORT)