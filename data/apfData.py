import maya.cmds as mc

import os
import data

class ApfData( data.Data ):
	'''
	Apf data class definition
	'''
	
	def __init__(self,apfFile=''):
		'''
		Apf data class initializer
		@param apfFile: Apf file to load.
		@type apfFile: str
		'''
		# Execute Super Class Initilizer
		super(ApfData, self).__init__()
		
		# Initialize Data Type
		self.dataType = 'ApfData'
		
		if apfFile: self.read(apfFile)
		
		self.apfChan = ['tx','ty','tz','rx','ry','rz']
	
	def read(self,apfFile):
		'''
		@param apfFile: Apf file to load.
		@type apfFile: str
		'''
		# Check File
		if not os.path.isfile(apfFile):
			raise Exception('Apf file "'+apfFile+'" is not a valid path!')
		
		# Read File
		f = open(apfFile,'r')
		
		# Sort Data
		char = ''
		for line in f:
			
			# Get Line Data
			lineData = line.split()
			
			# Skip Empty Lines
			if not lineData: continue
			
			# Check BEGIN
			if lineData[0] == 'BEGIN':
				char = lineData[1]
				self._data[char] = {}
				continue
			
			# Check Character
			if not char: continue
			
			# Parse Line Data
			lineObj = lineData[0]
			lineVal = [float(i) for i in lineData[1:]]
			self._data[char][lineObj] = lineVal	

def processDir(srcDir):
	'''
	Convert all apf files in a specified directory to ApfData object files (*.bpf)
	@param srcDir: Source directory to process apf files for.
	@type srcDir: str
	'''
	# Check Source Directory
	if not os.path.isdir(srcDir):
		raise Exception('Source directory "'+srcDir+'" is not a valid path!')
	
	# Start Timer
	timer = mc.timerX()
	
	# Find all APF files
	apfFiles = [i for i in os.listdir(srcDir) if i.endswith('.apf')]
	apfFiles.sort()
	bpfFiles = []
	for apfFile in apfFiles:
		
		# Check File
		srcFile = srcDir+'/'+apfFile
		if not os.path.isfile(srcFile):
			raise Exception('Apf file "'+srcFile+'" is not a valid path!')
		
		print apfFile
		
		apfData = ApfData(srcFile)
		bpfFile = apfData.save(srcFile.replace('.apf','.bpf'))
		bpfFiles.append(bpfFile)
	
	# Print Result
	totalTime = mc.timerX(st=timer)
	print 'Total time: '+str(totalTime)
	
	# Return Result
	return bpfFiles

def loadAnim(srcDir,agentNS):
	'''
	Load animation from apf file data
	@param srcDir: Source directory to load bpf files from.
	@type srcDir: str
	@param agentNS: Agent namespace to apply animation to.
	@type agentNS: str
	'''
	# Check Source Directory
	if not os.path.isdir(srcDir):
		raise Exception('Source directory "'+srcDir+'" is not a valid path!')
	
	# Start Timer
	timer = mc.timerX()
	
	# Load Agent Animation
	bpfFiles = [i for i in os.listdir(srcDir) if i.endswith('.bpf')]
	bpfIndex = [int(i.split('.')[1]) for i in bpfFiles]
	bpfIndex.sort()
	
	# For Each File
	apfChan = ['tx','ty','tz','rx','ry','rz']
	for ind in bpfIndex:
		data = ApfData().load(srcDir+'/frame.'+str(ind)+'.bpf')
		if data._data.has_key(agentNS):
			for item in data._data[agentNS].iterkeys():
				
				# Check Agent:Item Exists
				if not mc.objExists(agentNS+':'+item): continue
				
				# Load Anim Channels
				if item == 'Hips':
					for i in range(3):
						mc.setKeyframe(agentNS+':'+item,at=apfChan[i],t=ind,v=data._data[agentNS][item][i])
				for i in range(3,6):
					mc.setKeyframe(agentNS+':'+item,at=apfChan[i],t=ind,v=data._data[agentNS][item][i])
				
	
	# Print Result
	totalTime = mc.timerX(st=timer)
	print 'Total time: '+str(totalTime)
