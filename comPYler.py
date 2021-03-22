#!/usr/bin/python3
import os
import time
import math
import yaml
import pathlib as p

#   Simple Debugging functionalitites below
DEBUG = True
def log(s):
	if DEBUG == True:
		print(s)

#   Class for ease of use in iteration of main loop
#   Cumbursome dual list no longer necessary if using this.
class FileTimeData:
	#   Initialize from the file_name
	def __init__(self, filename):
		self.filename = filename
		# self.file_statistics = os.stat(self.file_name)
		self.time_checked = os.stat(self.filename).st_mtime

	#	Functions that will be most often used from outside
	def get_time_checked(self):
		return self.time_checked

	def change_happened(self):
		return not math.isclose(self.time_checked, os.stat(self.filename).st_mtime)


	def set_time_checked(self):
		self.time_checked = os.stat(self.filename).st_mtime



class CompWatcher:

	def __init__(self, config_filename = "compyler.yaml"):
		#	Backup section
		self.document = {} 
		
		#	CMD section
		self.cmd = ""
		self.command = ""
		self.config_file = config_filename
		self.main = ""
		self.files = []
		self.options = []
		self.target = ""

		#	Program Config section
		self.delay = 0
		self.error_display = 0

		#	Program Section
		self.watching = True
		# self.config_read = False

		self.config()

	#	This will be called automatically when the object is being created.
	#	It may be called when a change happens in the config file while
	#	it is running.
	def config(self, config_change = False):
		print('Change detected in config file...') if config_change else print('Configuration start...')

		
		#	Check if config exists
		if(not p.Path(self.config_file).is_file()):
			self.create_config()

		#	Read the yaml file here
		with open(str(self.config_file), 'r') as f:
			self.document = yaml.load(f, Loader=yaml.FullLoader)

			#	Set up the command of the compilation
			self.command = self.document['cmd']['command']

			#	Set up the files found as paths
			self.files = [file for file in self.document['cmd']['files']]

			#	Set up main as a path and append to files
			self.main = self.document['cmd']['main']
			self.files.append(self.main)

			#	Set up all options as found in yaml file
			self.options = [option for option in self.document['cmd']['options']]

			#	Set up the target
			self.target = self.document['cmd']['target']

			#	Combine the information found into a command
			self.cmd = self.command + " "

			for option in self.options:
				self.cmd += str(option) + " "

			for file in self.files:
				self.cmd += str(file) + " "

			self.cmd += "-o " + self.target

			#	Read in the config seciton of program parameters
			self.delay = self.document['config']['check_delay']
			self.error_display = self.document['config']['error_display']

		print('Configuration reloaded...') if config_change else print('Configuration end...')


	def compile(self):
		print('File change detected. Running compiler...')

		print(self.cmd)

		result = os.system(self.cmd)

		print(result)

		print('Compilation complete...')

	#	If no config file is found, a standard one is created based on
	#	default settings and found files in the current folder.
	def create_config(self):
		#	May check for extra things but mostly just write to a file

		#	Create a dictionary defining the standard config file
		standard = { 	'cmd' : 
						{ 
							'command' : 'clang++', 
							'main' : 'main.cpp',
							'files' : [],
							'options' : [],
							'target' : 'a.out'
						},

						'config' :
						{
							'check_delay' : 1,
							'error_display' : 5
						}
					}

		#	Open a file for writing based on pathname
		#	Dump dictionary in file using yaml dump method
		with open(str(self.config_file), 'w') as file:
			doc = yaml.dump(standard, file)

		log(doc)

	#	This is the main loop of the program
	#	In here the files received from config file will be checked for changes
	#	and will be compiled if change is met. 
	#	Will also check for changes in the config file used.
	def watch(self):
		print('Initiating watcher...')
		#	Create the time data for checking changes
		
		time_data = [FileTimeData(file) for file in self.files]
		config_data = FileTimeData(self.config_file)
		change = False

		#	Loop for as long as watcher is meant to run
		#	This is here for future subprocess adddition
		print('Watcher started!')
		while(self.watching):
			time.sleep(self.delay)

			#	Check every file for a change if a change happened flip switch
			for data_index in range(len(time_data)):
				if(time_data[data_index].change_happened()):
					change = True
					time_data[data_index].set_time_checked()


			if (change is True):
				change = False
				self.compile()

			if(config_data.change_happened()):
				self.config(config_change = True)

# #	Configure the autocompiler based on  
# def test_config():
#	 print('Test configuration start...')
#	 #   TODO: make a configuration file that has all necessary files and 
#	 #		 read from that configuration file (look into yaml config files)
#	 #	Main command
#	 command = 'clang++'

#	 #   Name of file that contains the main function
#	 main_file = 'testCPP/main.cpp'

#	 #   The name of extra cpp files needed for complete compilation of program
#	 extra_files = []

#	 extra_files_str = ""

#	 for file in extra_files:
#		 extra_files_str += file + ' '

#	 #	Options to be used in command TODO FOR LATER
#	 options = []

#	 #	Final concatinated command
#	 line_cmd = command + ' ' + main_file + ' ' + extra_files_str

#	 log('Configured command: ' + line_cmd)

#	 print('Configuration done!')

#	 extra_files.append(main_file)

#	 log('Inside config main_file var: ' + main_file)
#	 log('Inside config extra_files var: ' + str(extra_files))

#	 return (line_cmd, extra_files)


# def main():
#	 print("Begin checking program...")

#	 cmd, list_of_files = test_config()

#	 log('Inside main cmd var: ' + cmd)
#	 log('Inside main list_of_files var: ' + str(list_of_files))

#	 #   Create os.stat objects for each file to keep track of the timestamps
#	 files_stats = [FileTimeData(file) for file in list_of_files]

#	 #   Create a list of the current time stamps, used for noticing changes
#	 #   files_old_timestamps = [file.st_mtime for file in files_stats]

#	 log('Inside main program_structure var: ' + str(files_stats))

#	 while(True):
#		 time.sleep(1)
#		 log('DEBUG:   Checking file...')

#		 for file_index in range(len(files_stats)):

#			 if (files_stats[file_index].change_happened()):
#				 #   If not close that means file changed.
#				 #   Run the compilation steps and make the old_time into the new time
#				 print('File change detected. Running compiler!')

#				 result = os.system(cmd)

#				 print("Result of compilation: " + str(result))

#				 files_stats[file_index].reset_permanent_time()
#				 print('Compilation complete!')

	
	#	Check this line below / if statement should be different
if (__name__ == '__main__'):
	watcher = CompWatcher()
	watcher.watch()
