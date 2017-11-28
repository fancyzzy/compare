#!/usr/bin/env python
#-*-coding=utf-8-*-

import os
import subprocess
import re

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

def compare(base,latest):

	#base_files = os.listdir(base)
	base_files = []

	get_file_list(base,base_files)
	print "DEBUG base_files=",base_files

	result = []
	i = 0	
	for file in base_files:
		#print "DEBUG basename = ",os.path.basename(file)
		i += 1
		each_result = []
		del_cha_number = 0
		total_line = 0
		each_result.append(os.path.basename(file))
		print "{0}.{1}".format(i,file)
		err =''

		lines_cmd = ['wc','-l',os.path.join(base,file)]
		p2 = subprocess.Popen(lines_cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
		stderr=subprocess.PIPE, shell=False)
		p2.wait()
		err = p2.stderr.read()
		if err != '':
			print "error encounted!"
			continue
		else:
			total_line = p2.stdout.read().strip().split(' ')[0]
			each_result.append(total_line)
			#print "finished total line = ",total_line

		cmd = ['diff','-B',os.path.join(base,file),os.path.join(latest,file)]
		p1 = subprocess.Popen(cmd,stdin=subprocess.PIPE, stdout=subprocess.PIPE,\
		stderr=subprocess.PIPE, shell=False)

		out,err = p1.communicate('')

		if err != '':
			print "error encounted!"
			continue
		else:
			#out = p1.stdout.readline(100)
			del_cha_number = str(out.count('<'))
			each_result.append(del_cha_number)
			#print "change counting finshed:",del_cha_number
			#feature1: newlines counting begin
			rule = r'^\d+a\d+,?[\d]*'
			comp = re.compile(rule)
			add_number = 0
			for line in out.split('\n'):
				res = comp.findall(line)
				if len(res) == 1:
					r = res[0].split('a')
					if len(r) == 2:
						rr = r[1].split(',')
						if len(rr) == 2:
							add_number += int(rr[1])-int(rr[0])+1
						elif len(rr) == 1:
							add_number += 1
						else:
							pass
			each_result.append(add_number)
			#feature1: newlines counting end

		result.append(each_result)	
		print "finished"
		
	return result
if __name__ == '__main__':

	base = os.path.join(os.getcwd(),'base')
	latest = os.path.join(os.getcwd(),'latest')
	
	re = compare(base,latest)

	print "Summary"
	print "%-5s"%("INDEX"),
	print "%-25s"%("FILE_NAME"),
	print "%-12s"%("TOTAL_LINE"),
	print "%-12s"%("CHANGES"),
	print "%-12s"%("NEW_LINES")

	
	index = 0
	for item in re:
		index +=1
		print "%-5s"%(str(index)),
		print "%-25s"%(item[0]),
		print "%-12s"%(item[1]),
		print "%-12s"%(item[2]),
		print "%-12s"%(item[3])


	i = 0
	with open('result','w') as f:

		f.write('INDEX FILE_NAME TOTAL_LINES CHANGES NEW_LINES\n')
		for item in re:
			i+= 1
			f.write(str(i)+' '+item[0] + ' ' + item[1] + ' ' + item[2] + ' ' + str(item[3]))
			f.write('\n')


	wa = raw_input()