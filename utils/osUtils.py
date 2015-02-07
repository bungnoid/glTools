import os
import os.path

def getFileList(path,filesOnly=False):
	'''
	Return a list of files from a specified directory path.
	@param path: Directory path to get the file list from.
	@type path: str
	@param filesOnly: Return only files (exclude directories).
	@type filesOnly: bool
	'''
	# Check path
	if not os.path.isdir(path):
		raise Exception('Invalid path! ("'+path+'")')
	
	# Get file list
	fileList = os.listdir(path)
	
	# Filter
	if filesOnly:
		fileList = [i for i in fileList if not os.path.isdir(path+'/'+i)]
	
	# Return Result
	return fileList

def searchAndReplaceFilename(path,search,replace):
	'''
	'''
	# Check path
	if not os.path.isdir(path):
		raise Exception('Invalid path! ("'+path+'")')
	
	# Get dir list
	fileList = os.listdir(path)
	fileList.sort()
	
	for file in fileList:
		if file.count(search):
			newfile = file.replace(search,replace)
			os.rename(path+'/'+file,path+'/'+newfile)

def viewSource(module):
	'''
	View the source of the specified python module
	@param module: Python module to view source of
	@type module: module
	'''
	try:
		filepath = module.__file__
		os.system('gedit '+filepath[:-1]+' &')
	except:
		pass
