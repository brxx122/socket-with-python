#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from time import sleep
import sys
from flask import Flask, render_template, session, request, redirect, flash, g,url_for
from werkzeug.utils import secure_filename
import json
import hashlib
import socket,sys
import struct
import os
import client_back as c

HOST = '127.0.0.1'
PORT = 8000
#s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.connect((HOST,PORT))

app = Flask(__name__)
app.secret_key ='123456'

@app.route("/")
def index():
	#return 'Hello world!'
    return render_template('indexLogin.html')

@app.route('/',methods=['POST'])
def Login():
	action = request.form['submit']
	localhost = request.form['localhost']
	port = request.form['port']
	if localhost.lower() == 'localhost':
		session['host'] = '127.0.0.1'
	else:
		session['host'] = localhost
	session['port'] = int(port)
	return redirect('/protocol')

@app.route("/protocol")
def protocol_page():
    return render_template('protocol.html')

@app.route("/file")
def file_page():
	return render_template('file.html',page="check")

@app.route('/file',methods=['POST'])
def file_operation():
	action = request.form['submit']
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((session['host'],session['port'])) 	#server ip   
	print ('Client has been assigned socket name', s.getsockname())
	if action == "check":
		ID = request.form['check_id']
		Name = request.form['check_name']
		requ_argv = {}
		requ_argv['Method'] = 'CHECK'
		requ_argv['URI'] = 'document\student.txt'
		requ_content = "Hello!"
		if ID == '' and Name == '':
			flash('Need ID or Name', 'error')
			s.close()
			return render_template('file.html', page='check')
		if ID:
			requ_argv['ID'] = ID
		if Name:
			requ_argv['Name'] = Name
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		state_str, error_str, info, buf = c.check_record(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
			return render_template('file.html', input = buf, page='check')
		if error_str:
			flash(error_str, 'error')
			return render_template('file.html', input = buf, page='check')
		else:
			path = url_for('static', filename = 'temp/' + info['Picture'])
			p = '''<img src=''' + path + ''' ''width = "200", height="220"/>'''
			info['P'] = p
			return render_template('file.html', stu_info = info, page='check')
	elif action == 'all_check':
		requ_argv = {}
		requ_argv['Method'] = 'ALL'
		requ_argv['URI'] = 'document\\student.txt'
		requ_content = "Hello!"
		
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		
		state_str, error_str, info, buf = c.check_dir(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
			return render_template('file.html', input = buf, page='check')
		if error_str:
			flash(error_str, 'error')
			return render_template('file.html', input = buf, page='check')
		return render_template('file.html', all = info.decode('utf8'),  input = buf, page='check')
	elif action == 'add':
		ID = request.form['add_id']
		Name = request.form['add_name']
		f = request.files['input_image']
		
		requ_argv = {}
		requ_argv['Method'] = 'ADD'
		requ_argv['URI'] = 'document\student.txt'
		requ_content = "Hello"
		if ID == '' or Name == '' or f.filename == '':
			flash('Need ID ,Name and Picture', 'error')
			s.close()
			return render_template('file.html', page='add')
		requ_argv['ID'] = ID
		requ_argv['Name'] = Name

		fname = secure_filename(f.filename)
		path = os.path.join('static/Uploads', fname)
		f.save(path)
		c.send_image(s, fname, requ_argv, path)

		state_str, error_str, buf = c.client_recv(s)
		if error_str:
			flash(error_str, 'error')
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		s.close()
		return render_template('file.html', input = buf, page='add')
	elif action == 'delete':
		ID = request.form['delete_id']
		Name = request.form['delete_name']
		requ_argv = {}
		requ_argv['Method'] = 'DELETE'
		requ_argv['URI'] = 'document\student.txt'
		requ_content = "Hello"
		if ID == '' and Name == '':
			flash('Need ID or Name', 'error')
			s.close()
			return render_template('file.html', page='delete')
		if ID:
			requ_argv['ID'] = ID
		if Name:
			requ_argv['Name'] = Name
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		state_str, error_str, buf = c.client_recv(s)
		if error_str:
			flash(error_str, 'error')
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		s.close()
		return render_template('file.html', input = buf, page='delete')
	elif action == 'modify':
		SID = request.form['modify_sid']
		SName = request.form['modify_sname']
		RID = request.form['modify_rid']
		RName = request.form['modify_rname']
		f = request.files['input_image2']
		
		requ_argv = {}
		requ_argv['Method'] = 'MODIFY'
		requ_argv['URI'] = 'document\student.txt'
		requ_content = "Hello"
		if SID == '' and SName == '':
			flash('Need ID or Name', 'error')
			s.close()
			return render_template('file.html', page='modify')
		if SID:
			requ_argv['SID'] = SID
		if SName:
			requ_argv['SName'] = SName
		if RID:
			requ_argv['RID'] = RID
		if RName:
			requ_argv['RName'] = RName
		if f.filename:
			fname = secure_filename(f.filename)
			path = os.path.join('static/Uploads', fname)
			f.save(path)
			c.send_image(s, fname, requ_argv, path)
		else:
			request_msg = c.create_request(requ_argv, requ_content)
			s.send(request_msg)
		
		state_str, error_str, buf = c.client_recv(s)
		if error_str:
			flash(error_str, 'error')
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		s.close()
		return render_template('file.html', input = buf, page='modify')
	return render_template('file.html', page='check')

	
@app.route("/transfer")
def tranfer_page():
    return render_template('transfer.html', page="upload")
		
@app.route('/transfer',methods=['POST'])
def file_send():
	action = request.form['submit']
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((session['host'],session['port'])) 	#server ip   
	print ('Client has been assigned socket name', s.getsockname())
	if action == "upload":
		requ_argv = {}
		requ_argv['Method'] = 'UPLOAD'
		requ_argv['URI'] = 'document\\'
		requ_content = "Hello!"
		
		f = request.files['upload_file']
		if f.filename == '':
			flash('Need upload file', 'error')
			s.close()
			return render_template('transfer.html', page="upload")
		fname = secure_filename(f.filename)
		requ_argv['fhead'] = f.filename
		path = os.path.join('static/Uploads', fname)
		f.save(path)
		c.send_file(s, fname, requ_argv, path)

		state_str, error_str, buf = c.client_recv(s)
		if error_str:
			flash(error_str, 'error')
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		s.close()
		return render_template('transfer.html', input = buf, page="upload")
	
	elif action == 'dir1':
		requ_argv = {}
		requ_argv['Method'] = 'DIR'
		requ_argv['URI'] = 'document\\directory.txt'
		requ_content = "Hello!"
		
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		
		state_str, error_str, info, buf = c.check_dir(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
			return render_template('transfer.html', input = buf, page="upload")
		if error_str:
			flash(error_str, 'error')
			return render_template('file.html', input = buf, page="upload")
		return render_template('transfer.html', dir = info.decode('utf8'),  input = buf, page="upload")
		
	elif action == 'dir2':
		requ_argv = {}
		requ_argv['Method'] = 'DIR'
		requ_argv['URI'] = 'document\\directory.txt'
		requ_content = "Hello!"
		
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		
		state_str, error_str, info, buf = c.check_dir(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
			return render_template('transfer.html', input = buf, page="download")
		if error_str:
			flash(error_str, 'error')
			return render_template('file.html', input = buf, page="download")
		return render_template('transfer.html', dir = info.decode('utf8'),  input = buf, page="download")
	
	elif action == 'dir3':
		requ_argv = {}
		requ_argv['Method'] = 'DIR'
		requ_argv['URI'] = 'document\\directory.txt'
		requ_content = "Hello!"
		
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		
		state_str, error_str, info, buf = c.check_dir(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
			return render_template('transfer.html', input = buf, page="remove")
		if error_str:
			flash(error_str, 'error')
			return render_template('file.html', input = buf, page="remove")
		return render_template('transfer.html', dir = info.decode('utf8'),  input = buf, page="remove")
		
	elif action == 'download':
		file_name = request.form['down_file']
		if file_name == '':
			flash('Need File name!', 'error')
			s.close()
			return render_template('transfer.html', page="download")
		
		requ_argv = {}
		requ_argv['Method'] = 'DOWNLOAD'
		requ_argv['URI'] = 'document\\'
		requ_argv['fname'] = file_name
		requ_content = "Hello!"
	
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		state_str, error_str, buf = c.down_file(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		if error_str:
			flash(error_str, 'error')
		return render_template('transfer.html', input = buf, page="download")
	
	elif action == 'remove':
		file_name = request.form['remove_file']
		if file_name == '':
			flash('Need File name!', 'error')
			s.close()
			return render_template('transfer.html', page="remove")
		
		requ_argv = {}
		requ_argv['Method'] = 'REMOVE'
		requ_argv['URI'] = 'document\\'
		requ_argv['fname'] = file_name
		requ_content = "Hello!"
	
		request_msg = c.create_request(requ_argv, requ_content)
		s.send(request_msg)
		state_str, error_str, buf = c.client_recv(s)
		s.close()
		if state_str.startswith('2'):
			flash(state_str, 'success')
		elif state_str.startswith('4'):
			flash(state_str, 'error')
		if error_str:
			flash(error_str, 'error')
		return render_template('transfer.html', input = buf, page="remove")
	
	else:
		return render_template('transfer.html', page="upload")

	
if __name__ == "__main__":
	#print('oh hello')
    #sleep(10)
    #sys.stdout.flush()
    #app.run(host="localhost", port = 5000)
	app.debug = True
	app.run()
