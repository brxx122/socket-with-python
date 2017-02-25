#!/usr/bin/python
# -*- coding:utf-8 -*-
import socket,sys
import struct
import os
from flask import flash
import base64
import time


MAXBUF = 1024
M = ['ADD', 'DELETE', 'MODIFY', 'CHECK', 'GET', 'UPLOAD', 'DOWNLOAD', 'DIR', 'REMOVE', 'ALL']

def create_request(argv, content):	#dict
	request_msg = ""
	if argv.has_key('Method') and argv['Method'] in M:
		request_msg += argv['Method'] + " "
	else:
		print "There is not valid Method!"
	
	if (argv.has_key('URI')):
		request_msg += argv['URI'] + " "
	else:
		print "There is not valid URI!"
	
	request_msg += 'MyHTTP' + '\r\n'
	
	request_buf = ""
	for key in argv.keys():
		if key == 'Method' or key == 'URI':
			continue
		request_buf += key + ':' + argv[key] + '\r\n'
	request_buf += '\r\n'
	request_buf += content
	
	length = len(request_buf) + len(request_msg)
	request_msg += 'Length:' + str(length) + '\r\n'
	request_msg += request_buf

	return request_msg
	
def client_recv(s):
	buf = s.recv(MAXBUF)
	begin_buf = buf.split('\r\n')[0]
	begin = begin_buf.split(' ')
	Version = begin[0]
	Status = begin[1]
	Pharse = ' '.join(begin[2:])
	error_str = ''
	state_str =  Status + ' ' + Pharse
	
	if Version != 'MyHTTP':
		error_str += 'The Version is not valid!'
		return state_str, error_str, buf
	if state_str.startswith('4'):
		return state_str, error_str, buf
	
	# get all of the repo
	argv = {}
	remain_buf = buf[len(begin_buf + '\r\n'):]
	Length = remain_buf.split('\r\n')[0]
	[key, value] = Length.split(':')
	argv[key] = value
	if 'Length' not in Length:
		error_str +=  'Lost length!'
		return state_str, error_str, buf
	if int(argv['Length']) > len(buf):
		length = int(argv['Length'])
		had_recv = len(buf)
		while had_recv < length:
			buf += s.recv(MAXBUF)
			had_recv += MAXBUF
	
	return state_str, error_str, buf
	
def check_record(s):
	buf = s.recv(MAXBUF)
	begin_buf = buf.split('\r\n')[0]
	begin = begin_buf.split(' ')
	Version = begin[0]
	Status = begin[1]
	Pharse = ' '.join(begin[2:])
	
	error_str = ''
	state_str =  Status + ' ' + Pharse
	info = {}
	
	if Version != 'MyHTTP':
		error_str +=  'The Version is not valid!'
		return state_str, error_str, info, buf
	if state_str.startswith('4'):
		return state_str, error_str, info, buf
	
	# get all of the content
	argv = {}
	remain_buf = buf[len(begin_buf + '\r\n'):]
	Length = remain_buf.split('\r\n')[0]
	[key, value] = Length.split(':')
	argv[key] = value
	if 'Length' not in Length:
		error_str += 'Lost length!'
		return state_str, error_str, info, buf
		
	if int(argv['Length']) > len(buf):
		length = int(argv['Length'])
		had_recv = len(buf)
		while had_recv < length:
			remain_buf += s.recv(MAXBUF)
			time.sleep(0.001)
			had_recv += MAXBUF
	[head, content] = remain_buf.split('\r\n\r\n')
	print "actu len:" + str(length)
	print "recv len: " + str(len(remain_buf) + len(begin_buf + '\r\n'))
	head_lines = head.split('\r\n')
	for line in head_lines:
		[key, value] = line.split(':')
		argv[key] = value
	
	buf = buf[:len(begin_buf + '\r\n')] + remain_buf
	
	# get the info
	if argv.has_key('ID'):
		info['ID'] = argv['ID']
	else:
		error_str += 'Lost ID!'
		return state_str, error_str, info, buf
	if argv.has_key('Name'):
		info['Name'] = argv['Name']
	else:
		error_str += 'Lost Name!'
		return state_str, error_str, info, buf
	if argv.has_key('Picture'):
		Picture = argv['Picture']
	else:
		error_str += 'Lost Picture!'
		return state_str, error_str, info, buf

	# restore the file
	filename = argv['fhead']
	info['Picture'] = 'new_' + filename
	filename = 'static\\temp\\new_' + filename
	fp = open(filename, 'wb')
	filedata = content
	fp.write(filedata)
	fp.close()
	
	return state_str, error_str, info, buf 

def check_dir(s):
	buf = s.recv(MAXBUF)
	begin_buf = buf.split('\r\n')[0]
	begin = begin_buf.split(' ')
	Version = begin[0]
	Status = begin[1]
	Pharse = ' '.join(begin[2:])
	
	error_str = ''
	state_str =  Status + ' ' + Pharse
	info = {}
	
	if Version != 'MyHTTP':
		error_str +=  'The Version is not valid!'
		return state_str, error_str, info, buf
	if state_str.startswith('4'):
		return state_str, error_str, info, buf
	
	# get all of the content
	argv = {}
	remain_buf = buf[len(begin_buf + '\r\n'):]
	Length = remain_buf.split('\r\n')[0]
	[key, value] = Length.split(':')
	argv[key] = value
	if 'Length' not in Length:
		error_str += 'Lost length!'
		return state_str, error_str, info, buf
		
	if int(argv['Length']) > len(buf):
		length = int(argv['Length'])
		had_recv = len(buf)
		while had_recv < length:
			remain_buf += s.recv(MAXBUF)
			time.sleep(0.001)
			had_recv += MAXBUF
	[head, content] = remain_buf.split('\r\n\r\n')
	print "actu len:" + str(int(argv['Length']))
	print "recv len: " + str(len(remain_buf) + len(begin_buf + '\r\n'))
	head_lines = head.split('\r\n')
	for line in head_lines:
		[key, value] = line.split(':')
		argv[key] = value
	
	buf = buf[:len(begin_buf + '\r\n')] + head
	
	return state_str, error_str, content, buf 
	
def send_image(s, fname, requ_argv, path):
	p = os.path.abspath(path)
	
	requ_content = ""
	filename = p.split('\\')[-1]
	if 'ID' in requ_argv.keys():
		requ_argv['fhead'] = requ_argv['ID'] + '.' + filename.split('.')[-1]
	elif 'RID' in requ_argv.keys():
		requ_argv['fhead'] = requ_argv['RID'] + '.' + filename.split('.')[-1]
	elif 'SID'  in requ_argv.keys():
		requ_argv['fhead'] = requ_argv['SID'] + '.' + filename.split('.')[-1]
	ft = open(p, 'rb')
	
	while 1:
		filedata = ft.read(MAXBUF)
		if not filedata:
			break
		requ_content += filedata
	ft.close()
	
	if 'ID' in requ_argv.keys():
		requ_argv['Picture'] = 'image\\head\\' + requ_argv['ID'] + '.' + fname.split('.')[-1]
	elif 'RID' in requ_argv.keys():
		requ_argv['Picture'] = 'image\\head\\' + requ_argv['RID'] + '.' + fname.split('.')[-1]
	elif 'SID'  in requ_argv.keys():
		requ_argv['Picture'] = 'image\\head\\' + requ_argv['SID'] + '.' + fname.split('.')[-1]
	
	
	# create requ_msg
	request_msg = ""
	if requ_argv.has_key('Method') and requ_argv['Method'] in M:
		request_msg += requ_argv['Method'] + " "
	else:
		print "There is not valid Method!"
	if (requ_argv.has_key('URI')):
		request_msg += requ_argv['URI'] + " "
	else:
		print "There is not valid URI!"
	request_msg += 'MyHTTP' + '\r\n'
	request_buf = ""
	for key in requ_argv.keys():
		if key == 'Method' or key == 'URI':
			continue
		request_buf += key + ':' + requ_argv[key] + '\r\n'
	request_buf += '\r\n'
	#request_buf += requ_content
	
	length = len(request_buf) + len(request_msg) + len(requ_content)
	request_msg += 'Length:' + str(length) + '\r\n'
	request_msg += request_buf
	
	s.send(request_msg)
	s.send(requ_content)

def send_file(s, fname, requ_argv, path):
	p = os.path.abspath(path)
	
	requ_content = ""
	filename = p.split('\\')[-1]
	ft = open(p, 'rb')
	
	while 1:
		filedata = ft.read(MAXBUF)
		if not filedata:
			break
		requ_content += filedata
	ft.close()
	
	# create requ_msg
	request_msg = ""
	if requ_argv.has_key('Method') and requ_argv['Method'] in M:
		request_msg += requ_argv['Method'] + " "
	else:
		print "There is not valid Method!"
	if (requ_argv.has_key('URI')):
		request_msg += requ_argv['URI'] + " "
	else:
		print "There is not valid URI!"
	request_msg += 'MyHTTP' + '\r\n'
	request_buf = ""
	for key in requ_argv.keys():
		if key == 'Method' or key == 'URI':
			continue
		request_buf += key + ':' + requ_argv[key] + '\r\n'
	request_buf += '\r\n'
	#request_buf += requ_content
	
	length = len(request_buf) + len(request_msg) + len(requ_content)
	request_msg += 'Length:' + str(length) + '\r\n'
	request_msg += request_buf
	
	s.send(request_msg)
	s.send(requ_content)
	
def down_file(s):
	buf = s.recv(MAXBUF)
	begin_buf = buf.split('\r\n')[0]
	begin = begin_buf.split(' ')
	Version = begin[0]
	Status = begin[1]
	Pharse = ' '.join(begin[2:])
	
	error_str = ''
	state_str =  Status + ' ' + Pharse
	info = {}
	
	if Version != 'MyHTTP':
		error_str +=  'The Version is not valid!'
		return state_str, error_str, info, buf
	if state_str.startswith('4'):
		return state_str, error_str, info, buf
	
	# get all of the content
	argv = {}
	remain_buf = buf[len(begin_buf + '\r\n'):]
	Length = remain_buf.split('\r\n')[0]
	[key, value] = Length.split(':')
	argv[key] = value
	if 'Length' not in Length:
		error_str += 'Lost length!'
		return state_str, error_str, info, buf
		
	if int(argv['Length']) > len(buf):
		length = int(argv['Length'])
		had_recv = len(buf)
		while had_recv < length:
			remain_buf += s.recv(MAXBUF)
			time.sleep(0.001)
			had_recv += MAXBUF
	[head, content] = remain_buf.split('\r\n\r\n')
	print "actu len:" + str(int(argv['Length']))
	print "recv len: " + str(len(remain_buf) + len(begin_buf + '\r\n'))
	head_lines = head.split('\r\n')
	for line in head_lines:
		[key, value] = line.split(':')
		argv[key] = value
	
	buf = buf[:len(begin_buf + '\r\n')] + 'I have received your request!'
	
	# restore the file
	filename = 'static\\temp\\download_' + argv['fhead']
	fp = open(filename, 'wb')
	filedata = content
	fp.write(filedata)
	fp.close()
	
	return state_str, error_str, buf 


'''
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = '127.0.0.1'
PORT = 8000
s.connect((HOST,PORT)) 	#server ip
print 'Client has been assigned socket name', s.getsockname()
requ_argv = {}
requ_argv['ID'] = '50'
requ_argv['Method'] = 'CHECK'
requ_argv['URI'] = 'document\student.txt'
request_msg = create_request(requ_argv, 'Hello')
s.send(request_msg)
state_str, error_str, info, buf = check_record(s)
s.close()'''

