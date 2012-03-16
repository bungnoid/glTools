import os
import os.path

def searchAndReplaceFilename(path,search,replace):
	'''
	'''
	# Check path
	if not os.path.isdir(path):
		raise Exception('Invalid path!!')
	
	# Get dir list
	fileList = os.listdir(path)
	fileList.sort()
	
	for file in fileList:
		if file.count(search):
			newfile = file.replace(search,replace)
			os.rename(path+'/'+file,path+'/'+newfile)
