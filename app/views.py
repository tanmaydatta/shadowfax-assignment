from app import app
import ipdb
from flask import Flask, request,render_template, redirect, session
from check import login_required
from server import *
import redis
from app import r
import os
import soldier
import thread
from server import queue_data


@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html')

	elif request.method == 'POST':
		# ipdb.set_trace()
		filename = request.form['filename']
		passwd = request.form['pass']
		# ipdb.set_trace()
		try:
			# check if file already exists
			# if doesnt exists then create a new file and enter details in redis
			if not r.exists(filename) or r.exists == None:
				r.hmset(filename,{request.remote_addr:filename})
				r.set(filename+'pass',passwd)
				a=soldier.run('touch app/files/' + filename)
				# start queue for sending data to clients 
				start_queue(filename)
			# if exists check for password
			else:
				if r.exists(filename+'pass'):
					if r.get(filename+'pass')!=passwd:
						return redirect('/')
		except:
			# exception will be if file is not present hence create the file
			r.hmset(filename,{request.remote_addr:filename})
			r.set(filename+'pass',passwd)
			a=soldier.run('touch app/files/' + filename)
			# start queue for sending data to clients 
			start_queue(filename)
			if r.get(filename+'pass')!=passwd:
				return redirect('/')

		# add filename to curr ip and vice versa in redis
		ip_file_map = r.hgetall(filename)
		ip_file_map[request.remote_addr] = filename
		r.hmset(filename,ip_file_map)
		r.set(request.remote_addr, filename)
		# store that user is logged in 
		session['logged_in'] = filename
		return redirect('/edit/' + filename)


@app.route('/edit/<filename>/', methods=['GET'])
@login_required
def edit(filename):
	if request.method == 'GET':
		try:
			f = open('app/files/' + filename, 'r')
		except:
			return 'Invalid File'
		data = f.read()
		f.close()
		ip=os.popen("ip route get 8.8.8.8 | awk '{print $NF; exit}'").read()
		print ip.split()[0]
		return render_template('file.html', data=data,ip=ip.split()[0])


