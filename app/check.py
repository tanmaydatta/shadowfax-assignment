from functools import wraps
from flask import session, request, redirect, url_for
import ipdb

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# ipdb.set_trace()
		# return f(*args, **kwargs)
		try:
			if session['logged_in'] != kwargs['filename']:
				print 'error'
				return redirect('/')
			# return redirect('/')
			return f(*args, **kwargs)
		except:
			return redirect('/')
	return decorated_function
