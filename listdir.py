#!/usr/bin/env python
# --*-- coding:utf-8 --*--
#author Felix, fancyzzy@163.com

from Tkinter import *
import tkMessageBox 
import dnd
import os
import compare

MY_COLOR_BLUE = '#%02x%02x%02x' % (51,153,255)
MY_COLOR_BLUE_OFFICE ='#%02x%02x%02x' % (43,87,154) 
MY_COLOR_GREEN = '#%02x%02x%02x' % (192,233,17)

class DirList(object):
	def __init__(self, initdir=None):
		self.top = Tk()
		self.top.geometry('500x550+200+180')
		self.top.wm_title("VC2.0")

		Label(self.top, text='').pack()
		fm_title = Frame(self.top)
		self.label_title = Label(fm_title, text='Version Compare v2.0',\
			font = ('Helvetica', 16, 'bold'), fg =MY_COLOR_BLUE_OFFICE)
		self.label_title.pack()
		fm_title.pack()
		#self.top.iconbitmap(icon_path)

		fm_listbox = Frame(self.top)

		##############################
		fm_listbox_base = Frame(fm_listbox)
		'''
		self.listbox_baseby = Scrollbar(fm_listbox_base)
		self.listbox_baseby.pack(side=RIGHT, fill=Y)
		self.listbox_basebx = Scrollbar(fm_listbox_base,orient=HORIZONTAL)
		self.listbox_basebx.pack(side=BOTTOM, fill=X)
		'''

		self.list_base_v = StringVar()
		#selectmode=EXTENDED,BROWSE,MULTIPLE,SINGLE
		#exportselection is used to enable "ctrl+c" to copy the content selected 
		#in the listbox into the windows clipboard when =1
		self.listbox_base = Listbox(fm_listbox_base, height=20, width=34, selectmode=BROWSE,\
			exportselection=1,listvariable=self.list_base_v)
		'''
		self.listbox_base['yscrollcommand'] = self.listbox_baseby.set
		self.listbox_baseby.config(command=self.listbox_base.yview)
		self.listbox_base['xscrollcommand'] = self.listbox_basebx.set
		self.listbox_basebx.config(command=self.listbox_base.xview)
		'''
		Label(fm_listbox_base, text = 'BASE').pack()
		self.listbox_base.pack()

		self.base_file_list = []
		self.ptext_base = StringVar()
		self.ptext_base.set("")
		self.label_info_base = Label(fm_listbox_base, textvariable=self.ptext_base,justify='left')
		self.label_info_base.pack()

		fm_listbox_base.grid(row=0,column=0)

		############################
		label_compare = Label(fm_listbox, text="diff").grid(row=0,column=1)
		############################

		fm_listbox_latest = Frame(fm_listbox)
		self.list_latest_v = StringVar()
		self.listbox_latest = Listbox(fm_listbox_latest, height=20, width=34, selectmode=BROWSE,\
			exportselection=1,listvariable=self.list_latest_v)
		Label(fm_listbox_latest, text='LATEST').pack()
		self.listbox_latest.pack()

		self.latest_file_list = []
		self.ptext_latest = StringVar()
		self.ptext_latest.set("")
		self.label_info_latest = Label(fm_listbox_latest, textvariable=self.ptext_latest,justify='left')
		self.label_info_latest.pack()
		fm_listbox_latest.grid(row=0,column=2)
		############################

		fm_listbox.pack()

		fm_compare = Frame(self.top)
		self.button_compare = Button(fm_compare, text="Compare", command=self.compare_files,\
			height=2,width=12)
		self.button_compare.pack()
		fm_compare.pack()

		self.dnd_enable(self.listbox_base, self.ptext_base, self.base_file_list)
		self.dnd_enable(self.listbox_latest, self.ptext_latest, self.latest_file_list)


	def show_result(self, result):
		compare.printl("")
		compare.printl("Summary")
		s = "%-5s"%("INDEX") + "%-65s"%(" FILE_NAME") + "%-12s"%(" TOTAL_LINES") + "%-12s"%(" CHANGE_LINES")\
		+ "%-12s"%(" NEW_LINES")
		compare.printl(s)
		index = 0
		all_total_line = 0
		for item in result:
			s = ''
			index +=1
			s = "%-5s"%(str(index)) + " %-65s"%(item.FILE_NAME) + " %-12s"%(item.TOTAL_LINES) + \
			" %-12s"%(item.CHANGE_LINES) + " %-12s"%(item.NEW_LINES) 
			compare.printl(s)
			all_total_line += int(item.TOTAL_LINES)


	def compare_files(self):
		#d_latest = {'file_name':'file_path'}
		d_latest = {os.path.basename(item):item for item in self.latest_file_list}

		#EACH_ITEM = collections.namedtuple('EACH_ITEM','FILE_NAME TOTAL_LINES CHANGE_LINES NEW_LINES')
		result = []
		i = 0 
		for base_file_path in self.base_file_list:
			base_file_name = os.path.basename(base_file_path)
			i+=1
			print("{0}.{1}".format(i,base_file_path))
			if d_latest.has_key(base_file_name):
				single_re = compare.compare_single(base_file_path, d_latest.get(base_file_name))
			else:
				#latest files not include the base file, just compare itself to get the total line
				single_re = compare.compare_single(base_file_path, base_file_path)
			print("finished")

			result.append(single_re)

		#print("DEBUG result=",result)
		self.show_result(result)
		tkMessageBox.showinfo(title='Diff Result', message="Diff result has been saved in 'result.txt'.")


	###############Drag and Drop feature:########################
	def dnd_enable(self, widget,string_var,file_list):
		dd = dnd.DnD(self.top)
		def drag(action, actions, type, win, X, Y, x, y, data):
			return action
		def drag_enter(action, actions, type, win, X, Y, x, y, data):
			widget.focus_force()
			return action
		def drop(action, actions, type, win, X, Y, x, y, data):
			widget.delete(0, END)
			os_sep = os.path.sep
			refined_data = self.refine_data(data)
			
			ln = len(refined_data)
			file_list[:] = []
			path_list = []
			for i in range(ln):
				if refined_data[i].startswith('{'):
					refined_data[i] = refined_data[i][1:-1]
				refined_data[i] = refined_data[i].replace(r'/', os_sep)
				widget.insert('end',refined_data[i])
				path_list.append(refined_data[i])
				if os.path.isdir(refined_data[i]):
					widget.itemconfig(END, fg = MY_COLOR_BLUE)
				else:
					pass

			#print("DEBUG after refined_data=",refined_data)
			#print("DEBUG file_list=",file_list)

			#get all the files path
			for path in path_list:
				compare.get_file_list(path,file_list)
			#print("DEBUG now, file_list=",file_list)
			string_var.set("%s items added"%(len(file_list)))

		dd.bindtarget(widget, 'text/uri-list', '<Drag>', drag, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
		dd.bindtarget(widget, 'text/uri-list', '<DragEnter>', drag_enter, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D'))
		dd.bindtarget(widget, 'text/uri-list', '<Drop>', drop, ('%A', '%a', '%T', '%W', '%X', '%Y', '%x', '%y', '%D')) #Drag and Drop

	def refine_data(self, data):
		flag = 0
		for i in range(len(data)):
			if data[i] == '{':
				flag += 1
			elif data[i] == '}':
				flag -= 1
			
			if data[i] == ' ' and flag == 0:
				#print "DEBUG data[:i-1]",data[:i]
				data = data[:i] + "," + data[i+1:]
		l = data.split(',')
		return l
	###############Drag and Drop feature:########################


def main():
	d = DirList()
	d.top.mainloop()


if __name__ == '__main__':
	main()
	'''
	import sys
	try:
		main()		
	except Exception as e:
		showerror(title='Error', message="Error occured!\n %s \n CB.corefile saved"%e)
		with open(os.path.join(WORKING_PATH,'CB.corefile'), 'a') as fobj:
			stime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			fobj.write('Core dump happened at %s\n'%stime)
			fobj.write('blackbox info: %s\n\n'%e)
	'''


