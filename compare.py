#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import subprocess
import re
import collections

EACH_ITEM = collections.namedtuple('EACH_ITEM','FILE_NAME TOTAL_LINES CHANGE_LINES NEW_LINES')

def get_file_list(dir,file_list):
	'''
	获取目录dir下的所有文件名(文件路径)
	略过隐藏的特殊文件
	支持子目录
	'''
	try:
		new_dir = dir
		if os.path.isfile(dir):
			file_list.append(dir)
		elif os.path.isdir(dir):
			for s in os.listdir(dir):
				#略过特殊字符开头的文件或者文件夹
				if not s[0].isdigit() and not s[0].isalpha():
					logger.warning("Hidden file:%s"%(s))
					#logger.warning("Hidden file:{}".format(s))
					if s != '.':
						continue
				new_dir = os.path.join(dir,s)
				get_file_list(new_dir,file_list)
		else:
			pass
	except Exception as e:
		logger.warning(e)

	return file_list

def compare_single(base_file_path, latest_file_path):
	#count only non whitespace lines
	#lines_cmd = ['wc','-l',base_file_path]
	total_line = ''
	change_line = ''
	new_line = ''

	lines_cmd = ['grep','-c','-P',"'\S'",base_file_path]
	p2 = subprocess.Popen(lines_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
	stderr=subprocess.PIPE, shell=False)
	p2.wait()
	out = p2.stdout.read()
	err = p2.stderr.read()
	if err != '' and not err.startswith(b'cygwin warning') and err != b'':
		print("p2 error encounted: ",err)
	else:
		total_line = out.decode('utf-8').strip().strip('\n').split(' ')[0]

	cmd = ['diff','-B',base_file_path,latest_file_path]
	p1 = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
	stderr=subprocess.PIPE, shell=False)
	out,err = p1.communicate('')
	out  = str(out)
	if err != '' and not err.startswith(b'cygwin warning') and err != b'':
		print("p1 error encounted:",err)
	else:
		change_line = str(out.count('<'))
		#count the new line by z-y +1 from 'xay,z' diff result
		rule = r'^\d+a\d+,?[\d]*'
		comp = re.compile(rule)
		new_line = 0
		for line in out.split('\n'):
			res = comp.findall(line)
			if len(res) == 1:
				r = res[0].split('a')
				if len(r) == 2:
					rr = r[1].split(',')
					if len(rr) == 2:
						new_line += int(rr[1])-int(rr[0])+1
					elif len(rr) == 1:
						new_line += 1
					else:
						pass
	each_result = EACH_ITEM(os.path.basename(base_file_path), total_line, change_line, new_line)
	return each_result


def file_line(file_name):
    with open(file_name) as f:
    	#for non-blank lines counting
        lengths = [len(line) for line in (line.rstrip() for line in f.readlines()) if line]
    return len(lengths)

def compare(base,latest):

	#base_files = os.listdir(base)
	base_files = []

	get_file_list(base,base_files)

	result = []
	i = 0	
	for base_file_path in base_files:
		i += 1
		#each_result = []
		#each_result = EACH_ITEM(file_name, total_line, change_line, new_line)
		total_line = 0
		change_line = 0
		new_line = 0
		file_name = os.path.basename(base_file_path)

		#latest_file_path = os.path.join(latest,file_name)
		latest_file_path = os.path.join(os.path.dirname(base_file_path).replace('base','latest'), file_name)

		print("{0}.{1}".format(i,base_file_path))
		err =''

		'''	
		#count only non whitespace lines
		#lines_cmd = ['wc','-l',base_file_path]
		lines_cmd = ['grep','-c','-P',"'\S'",base_file_path]
		p2 = subprocess.Popen(lines_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
		stderr=subprocess.PIPE, shell=False)
		p2.wait()
		out = p2.stdout.read()
		err = p2.stderr.read()
		if err != '' and err != b'':
			print("p2 error encounted: ",err)
			continue
		else:
			#total_line = str(p2.stdout.read()).strip().split(' ')[0]
			total_line = out.decode('utf-8').strip().strip('\n').split(' ')[0]
			#each_result.append(total_line)
			#print "finished total line = ",total_line
		'''

		total_line = file_line(base_file_path)

		cmd = ['diff','-B',base_file_path,latest_file_path]
		p1 = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
		stderr=subprocess.PIPE, shell=False)

		out,err = p1.communicate('')
		out  = str(out)

		if err != '' and err != b'':
			print("p1 error encounted:",err)
			continue
		else:
			#out = p1.stdout.readline(100)
			change_line = str(out.count('<'))
			#each_result.append(change_line)
			#print "change counting finshed:",change_line
			#feature1: newlines counting begin
			rule = r'^\d+a\d+,?[\d]*'
			comp = re.compile(rule)
			new_line = 0
			for line in out.split('\n'):
				res = comp.findall(line)
				if len(res) == 1:
					r = res[0].split('a')
					if len(r) == 2:
						rr = r[1].split(',')
						if len(rr) == 2:
							new_line += int(rr[1])-int(rr[0])+1
						elif len(rr) == 1:
							new_line += 1
						else:
							pass
			#each_result.append(new_line)
			#feature1: newlines counting end

		each_result = EACH_ITEM(file_name, total_line, change_line, new_line)
		result.append(each_result)	
		print("finished")
		
	return result

def printl(s,result='result.txt'):
	with open(result,'a') as f:
		print(s)
		f.write(s)
		f.write('\n')


if __name__ == '__main__':

	base = os.path.join(os.getcwd(),'base')
	latest = os.path.join(os.getcwd(),'latest')
	
	re = compare(base,latest)

	printl("")
	s = "Summary"
	printl(s)
	s = "%-5s"%("INDEX") + "%-30s"%(" FILE_NAME") + "%-12s"%(" TOTAL_LINES") + "%-12s"%(" CHANGE_LINES")\
	+ "%-12s"%(" NEW_LINES")
	printl(s)

	'''
	print "Summary"
	print "%-5s"%("INDEX"),
	print "%-25s"%("FILE_NAME"),
	print "%-12s"%("TOTAL_LINES"),
	print "%-12s"%("CHANGE_LINES"),
	print "%-12s"%("NEW_LINES")
	'''
	
	index = 0
	all_total_line = 0
	for item in re:
		s = ''
		index +=1
		s = "%-5s"%(str(index)) + " %-30s"%(item.FILE_NAME) + " %-12s"%(item.TOTAL_LINES) + \
		" %-12s"%(item.CHANGE_LINES) + " %-12s"%(item.NEW_LINES) 
		printl(s)
		all_total_line += int(item.TOTAL_LINES)


		'''
		print "%-5s"%(str(index)),
		print "%-25s"%(item.FILE_NAME),
		print "%-12s"%(item.TOTAL_LINES),
		print "%-12s"%(item.CHANGE_LINES),
		print "%-12s"%(item.NEW_LINES)
		'''

	'''
	i = 0
	with open('result','w') as f:

		f.write('INDEX FILE_NAME TOTAL_LINES CHANGES NEW_LINES\n')
		for item in re:
			i+= 1
			f.write(str(i)+' '+item[0] + ' ' + item[1] + ' ' + item[2] + ' ' + str(item[3]))
			f.write('\n')
	'''

	printl("All the files sumed total lines = %d"%all_total_line)
	print("'Please also see the result.txt to copy the data.'")

	a = input()
