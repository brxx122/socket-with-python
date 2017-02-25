#!/usr/bin/python
# -*- coding:utf-8 -*-
import socket	#socket
import os
import struct
import base64
import time

MAXBUF = 1024
M = ['ADD', 'DELETE', 'MODIFY', 'CHECK', 'UPLOAD', 'DOWNLOAD', 'DIR', 'REMOVE', 'ALL']
S = ['200', '201', '202','400','417']
P = ['OK']
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

HOST = '127.0.0.1'	#localhost
PORT = 8000

s.bind((HOST,PORT))		#server ip 
s.listen(1)			#recieve only one
print 'Listening at', s.getsockname()

def create_reponse(argv, content):	#dict
	reponse_msg = ""
	reponse_msg += 'MyHTTP' + ' '
	if argv.has_key('Status') and argv['Status'] in S:
		reponse_msg += argv['Status'] + " "
	else:
		print "There is not valid Status!"
	if argv.has_key('Pharse'):
		reponse_msg += argv['Pharse'] + " " + '\r\n'
	else:
		print "There is not valid Pharse!"

	reponse_buf = ""
	for key in argv.keys():
		if key == 'Status' or key == 'Pharse':
			continue
		reponse_buf += key + ':' + argv[key] + '\r\n'
	reponse_buf += '\r\n'
	reponse_buf += content
	
	length = len(reponse_buf) + len(reponse_msg)
	reponse_msg += 'Length:' + str(length) + '\r\n'
	reponse_msg += reponse_buf
	
	return reponse_msg

def send_file(sc, argv, content):
	reponse_msg = ""
	reponse_msg += 'MyHTTP' + ' '
	if argv.has_key('Status') and argv['Status'] in S:
		reponse_msg += argv['Status'] + " "
	else:
		print "There is not valid Status!"
	if argv.has_key('Pharse'):
		reponse_msg += argv['Pharse'] + " " + '\r\n'
	else:
		print "There is not valid Pharse!"

	reponse_buf = ""
	for key in argv.keys():
		if key == 'Status' or key == 'Pharse':
			continue
		reponse_buf += key + ':' + argv[key] + '\r\n'
	reponse_buf += '\r\n'
	#reponse_buf += content
	
	length = len(reponse_buf) + len(reponse_msg) + len(content)
	reponse_msg += 'Length:' + str(length) + '\r\n'
	reponse_msg += reponse_buf
	
	sc.send(reponse_msg)
	sc.send(content)
	
def recv_image(fname, content):
	filename = 'image\\head\\' + fname
	fp = open(filename, 'wb')
	filedata = content
	fp.write(filedata)
	fp.close()
	
def Add_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)
	
	f = open(path, 'r')
	flines = f.readlines()
	info = [line.strip().split('\t') for line in flines]
	IDs = [i[0] for i in info]
	Names = [i[1] for i in info]
	f.close()

	f = open(path, 'a')
	str = ''
	if 'ID' not in argv.keys():
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student ID!'
		return
	elif argv['ID'] in IDs:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Repeated ID!'
		return
	else:
		str += argv['ID'] + '\t'
	if 'Name' not in argv.keys():
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student Name!'
		return
	elif argv['Name'] in Names:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Repeated Name!'
		return
	else:
		str += argv['Name'] + '\t'
	if 'Picture' not in argv.keys():
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student Picture!'
		return
	else:
		str += argv['Picture'] + '\n'

	f.write(str)
	f.close()
	
	if 'fhead' in argv.keys():
		recv_image(argv['fhead'], content)
	
	repo_argv['Status'] = '201'
	repo_argv['Pharse'] = 'Create new record!'
	return
	
def Delete_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)

	f = open(path, 'r')
	flines = f.readlines()
	info = [line.strip().split('\t') for line in flines]
	length = len(flines)
	f.close()
	if 'ID' in argv.keys() and 'Name' in argv.keys():
		lines = [flines[i] for i in range(len(info)) if argv['ID'] != info[i][0] and argv['Name'] != info[i][1]]
		delete = [flines[i] for i in range(len(info)) if argv['ID'] == info[i][0] and argv['Name'] == info[i][1]]
	elif 'ID' in argv.keys():
		lines = [flines[i] for i in range(len(info)) if argv['ID'] != info[i][0]]
		delete = [flines[i] for i in range(len(info)) if argv['ID'] == info[i][0]]
	elif 'Name' in argv.keys():
		lines = [flines[i] for i in range(len(info)) if argv['Name'] != info[i][1]]
		delete = [flines[i] for i in range(len(info)) if argv['Name'] == info[i][1]]
	else:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student Name and ID!'
		return

	if length == len(lines):
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'There is no record!'
		return
	else:
		f = open(path, 'w')
		f.writelines(lines)
		path = os.path.abspath(delete[0].strip().split('\t')[-1])
		os.remove(delete[0].strip().split('\t')[-1])
		repo_argv['Status'] = '200'
		repo_argv['Pharse'] = 'Delete the record!'
		f.close()
	return

def replace_str(l, argv, repo_argv, IDs, Names):
	mflag = 0
	info = l.strip().split('\t')
	if 'RID' in argv.keys():
		if argv['RID']  != info[0] and argv['RID'] in IDs:
			repo_argv['Status'] = '417'
			repo_argv['Pharse'] = 'Repeated ID!'
			return -1, l, -1
		elif argv['RID']  != info[0]:
			info[0] = argv['RID']
			temp = 'image\\head\\' + argv['RID'] + '.' + info[2].split('.')[-1]
			os.rename(os.path.abspath(info[2]), os.path.abspath(temp))
			info[2] = temp + '\n'
			mflag = 1
	if 'RName' in argv.keys():
		if argv['RName']  != info[1] and argv['RName'] in Names:
			repo_argv['Status'] = '417'
			repo_argv['Pharse'] = 'Repeated Name!'
			return -1, l, -1
		elif argv['RName']  != info[1]:
			info[1] = argv['RName']
			mflag = 1
	if 'Picture' in argv.keys():
		os.remove(os.path.abspath(info[2].strip('\n')))
		info[2] = argv['Picture'] + '\n'
		mflag = 1

	l = '\t'.join(info)
	return 0, l, mflag

def Modify_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)

	flag = 0
	mflag = 0
	f = open(path, 'r')
	flines = f.readlines()
	info = [line.strip().split('\t') for line in flines]
	IDs = [i[0] for i in info]
	Names = [i[1] for i in info]
	if 'SID' in argv.keys() and 'SName' in argv.keys():
		for i in range(0, len(flines)):
			if argv['SID'] == info[i][0] and argv['SName'] == info[i][1]:
				flag = 1
				(s, flines[i], mflag) = replace_str(flines[i], argv, repo_argv, IDs,Names)
	elif 'SID' in argv.keys():
		for i in range(len(flines)):
			if argv['SID'] == info[i][0]:
				flag = 1
				(s, flines[i], mflag) = replace_str(flines[i], argv, repo_argv, IDs, Names)
	elif 'SName' in argv.keys():
		for i in range(len(flines)):
			if argv['SName'] == info[i][1]:
				flag = 1
				(s, flines[i], mflag) = replace_str(flines[i], argv, repo_argv, IDs, Names)
	else:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student Name and ID!'
		return
	f.close()

	if flag == 0:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'There is no record!'
		return
	if mflag == -1:
		return
	elif mflag == 0:
		repo_argv['Status'] = '202'
		repo_argv['Pharse'] = 'Nothing to modify!'
		return
	f = open(path, 'w')
	f.writelines(flines)
	
	if 'fhead' in argv.keys():
		recv_image(argv['fhead'], content)
	
	repo_argv['Status'] = '201'
	repo_argv['Pharse'] = 'Modify the record!'
	f.close()
	return

def Check_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)

	f = open(path, 'r')
	flines = f.readlines()
	info = [line.strip().split('\t') for line in flines]
	length = len(flines)
	f.close()
	if 'ID' in argv.keys() and 'Name' in argv.keys():
		lines = [info[i] for i in range(len(info)) if argv['ID']  == info[i][0] and argv['Name'] == info[i][1]]
	elif 'ID' in argv.keys():
		lines = [info[i] for i in range(len(info)) if argv['ID'] == info[i][0]]
	elif 'Name' in argv.keys():
		lines = [info[i] for i in range(len(info)) if argv['Name'] == info[i][1]]
	else:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Lost student Name and ID!'
		return 'ERROR'

	if len(lines) == 0:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'There is no record!'
		return 'ERROR'
	elif len(lines) > 1:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'More than one result!'
		return 'ERROR'

	repo_info = lines[0]
	repo_argv['ID'] = repo_info[0]
	repo_argv['Name'] = repo_info[1]
	repo_argv['Picture'] = repo_info[2]
	p = os.path.abspath(repo_info[2])

	repo_content = ""
	filename = p.split('\\')[-1]
	repo_argv['fhead'] = filename
	ft = open(p, 'rb')
	
	while 1:
		filedata = ft.read(MAXBUF)
		if not filedata:
			break
		repo_content += filedata
	ft.close()
	repo_argv['Status'] = '200'
	repo_argv['Pharse'] = 'transfer files succeed!'
	return repo_content
	
def All_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)

	f = open(path, 'r')
	repo_content = f.read()
	
	repo_argv['Status'] = '200'
	repo_argv['Pharse'] = 'transfer the list succeed!'
	return repo_content
	
def Upload_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)
	
	f = open('document\directory.txt','r')
	lines = f.readlines()
	re_lines = [l for l in lines if argv['fname'] in l]
	f.close()
	
	if len(re_lines) != 0:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'Repeated file name!'
		
	fp = open(os.path.join(path, argv['fhead']), 'wb')
	fp.write(content)
	fp.close()
	
	f = open('document\directory.txt', 'a')
	f.write('\t' + argv['fhead'] + '\n')
	f.close()
	
	repo_argv['Status'] = '201'
	repo_argv['Pharse'] = 'upload files succeed!'

def Dir_record(uri, argv, content, repo_argv):
	path = os.path.abspath(uri)

	f = open(path, 'r')
	repo_content = f.read()
	
	repo_argv['Status'] = '200'
	repo_argv['Pharse'] = 'transfer the dir succeed!'
	return repo_content
	
def Download_record(uri, argv, content, repo_argv):
	p = os.path.abspath(uri)

	f = open('document\directory.txt','r')
	lines = f.readlines()
	re_lines = [l for l in lines if argv['fname'] in l]
	f.close()
	
	if len(re_lines) == 0:
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'No such file!'
	
	path = os.path.join(p, argv['fname'])
	repo_content = ""
	filename = path.split('\\')[-1]
	repo_argv['fhead'] = filename
	ft = open(path, 'rb')
	
	while 1:
		filedata = ft.read(MAXBUF)
		if not filedata:
			break
		repo_content += filedata
	ft.close()
	repo_argv['Status'] = '200'
	repo_argv['Pharse'] = 'download files succeed!'
	return repo_content
	
def Remove_record(uri, argv, content, repo_argv):
	f = open('document\directory.txt','r')
	lines = f.readlines()
	re_lines = [l for l in lines if argv['fname'] not in l]
	f.close()
	
	if len(re_lines) == len(lines):
		repo_argv['Status'] = '417'
		repo_argv['Pharse'] = 'No such file!'
	
	p = os.path.abspath(uri)
	path = os.path.join(p, argv['fname'])
	os.remove(path)

	
	f = open('document\directory.txt','w')
	f.writelines(re_lines)
	f.close()
	
	
	repo_argv['Status'] = '200'
	repo_argv['Pharse'] = 'Remove files succeed!'
	
	
def server_listen():
	while 1:
		sc, addr = s.accept()
		print 'Connected by', addr
		print 'Socket connect', sc.getsockname(), 'and', sc.getpeername()

		buf = sc.recv(MAXBUF)
		print buf
		if buf == '':
			print "None!"
			sc.close()
			continue
		begin_buf = buf.split('\r\n')[0]
		begin = begin_buf.split(' ')
		Method = begin[0]
		URI = begin[1]
		Version = begin[2]

		repo_argv = {}
		if Version != 'MyHTTP':
			repo_argv['Status'] = '400'
			repo_argv['Pharse'] = 'The Version is not valid!'
			repo = create_reponse(repo_argv, repo_content)
			sc.send(repo)
			continue
		if Method not in M:
			repo_argv['Status'] = '400'
			repo_argv['Pharse'] = 'The Method is not valid!'
			repo = create_reponse(repo_argv, repo_content)
			sc.send(repo)
			continue

		#get all of the content
		argv = {}
		remain_buf = buf[len(begin_buf + '\r\n'):]
		Length = remain_buf.split('\r\n')[0]
		[key, value] = Length.split(':')
		argv[key] = value
		if 'Length' not in Length:
			repo_argv['Status'] = '400'
			repo_argv['Pharse'] = 'Lost length!'
			repo = create_reponse(repo_argv, repo_content)
			sc.send(repo)
			continue
		if int(argv['Length']) > len(buf):
			length = int(argv['Length'])
			had_recv = len(buf)
			while had_recv < length:
				remain_buf += sc.recv(MAXBUF)
				time.sleep(0.001)
				had_recv += MAXBUF
		print "actu len:" + str(int(argv['Length']))
		print "recv len: " + str(len(remain_buf) + len(begin_buf + '\r\n'))
		[head, content] = remain_buf.split('\r\n\r\n')
		head_lines = head.split('\r\n')
		for line in head_lines:
			[key, value] = line.split(':')
			argv[key] = value

		#implement the request
		if Method == 'ADD':
			Add_record(URI, argv, content, repo_argv)
			repo_content = 'I have receive your request!'
		elif Method == 'DELETE':
			Delete_record(URI, argv, content, repo_argv)
			repo_content = 'I have receive your request!'
		elif Method == 'MODIFY':
			Modify_record(URI, argv, content, repo_argv)
			repo_content = 'I have receive your request!'
		elif Method == 'CHECK':
			repo_content = Check_record(URI, argv, content, repo_argv)
			send_file(sc, repo_argv, repo_content)
			sc.close()
			continue
		elif Method == 'ALL':
			repo_content = All_record(URI, argv, content, repo_argv)
		elif Method == 'UPLOAD':
			Upload_record(URI, argv, content, repo_argv)
			repo_content = 'I have receive your request!'
		elif Method == 'DOWNLOAD':
			repo_content = Download_record(URI, argv, content, repo_argv)
			send_file(sc, repo_argv, repo_content)
			sc.close()
			continue
		elif Method == 'DIR':
			repo_content = Dir_record(URI, argv, content, repo_argv)
		elif Method == 'REMOVE':
			Remove_record(URI, argv, content, repo_argv)
			repo_content = 'I have receive your request!'
		else:
			repo_argv['Status'] = '200'
			repo_argv['Pharse'] = 'OK'
			repo_content = 'I have receive your request!'
		repo = create_reponse(repo_argv, repo_content)
		sc.send(repo)
		sc.close()
	

server_listen()