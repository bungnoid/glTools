import maya.cmds as mc
import maya.cmds as mm

import glTools.utils.reference

import ika.maya.sgxml

import os
import datetime

def getNodes(filePath,stripNS=False):
	'''
	'''
	# Check File
	if not os.path.isfile(filePath):
		raise Exception('Invalid file path! No file at location - '+filePath)
	
	# Get Nodes
	nodes = []
	if filePath.endswith('.pose'): nodes = getPoseNodes(filePath,stripNS)
	if filePath.endswith('.anim'): nodes = getAnimNodes(filePath,stripNS)
	
	# Return Result
	return nodes

def getPoseNodes(poseFile,stripNS=False):
	'''
	'''
	# Check File
	if not os.path.isfile(poseFile):
		raise Exception('Invalid file path! No file at location - '+poseFile)
	
	# Read Files
	f = open(poseFile,'r')
	
	# Get Nodes
	nodes = []
	for i, line in enumerate(f):
		node = line.split('.')[0]
		if stripNS: node = node.split(':')[-1]
		if not node in nodes: nodes.append(node)
	
	# Close File
	f.close()
	
	# Return Result
	return nodes

def getAnimNodes(animFile,stripNS=False):
	'''
	'''
	# Check File
	if not os.path.isfile(animFile):
		raise Exception('Invalid file path! No file at location - '+animFile)
	
	# Read Files
	f = open(animFile,'r')
	
	# Get Nodes
	nodes = []
	for i, line in enumerate(f):
		lineItem = line.split('')
		if lineItem[0] == 'static' or lineItem[0] == 'anim':
			node = lineItem[3]
			if stripNS: node = node.split(':')[-1]
			if not node in nodes: nodes.append(node)
	
	# Close File
	f.close()
	
	# Return Result
	return nodes

def loadPose(poseFile,targetNS=''):
	'''
	Load pose file to the specified target namespace
	@param poseFile: Pose file path
	@type poseFile: str
	@param targetNS: Target namespace to apply the pose to
	@type targetNS: str
	'''
	# Check File
	if not os.path.isfile(poseFile):
		raise Exception('Invalid file path! No file at location - '+poseFile)
	
	# Read Files
	f = open(poseFile,'r')
	
	# Read Lines
	for i, line in enumerate(f):
		
		# Get Line Data
		poseData = line.split()
		poseAttr = targetNS+':'+poseData[0].split(':')[-1]
		poseVal = float(poseData[1])
		
		# Check Target Attribute
		if not mc.objExists(poseAttr):
			print('Attribute "'+poseAttr+'" does not exist!! Skipping...')
			return False
		if not mc.getAttr(poseAttr,se=True):
			print('Attribute "'+poseAttr+'" is not settable!! Skipping...')
			return False
		
		# Apply Static Value
		mc.setAttr(poseAttr,poseVal)
	
	# Close File
	f.close()
		
	# Return Result
	return True

def loadAnim(animFile,targetNS,frameOffset=0,infinityOverride=None,applyEulerFilter=False):
	'''
	Load anim file to the specified target namespace
	@param animFile: Anim file path
	@type animFile: str
	@param targetNS: Target namespace to apply the anim to
	@type targetNS: str
	@param frameOffset: Frame offset to apply to the loaded animation data
	@type frameOffset: int or float
	@param infinityOverride: Force infinity mode for loaded animation data.
	@type infinityOverride: str or None
	@param applyEulerFilter: Apply euler filter to rotation channels in targetNS.
	@type applyEulerFilter: bool
	'''
	# Check File
	if not os.path.isfile(animFile):
		raise Exception('Invalid file path! No file at location - '+animFile)
	
	# Read Files
	f = open(animFile,'r')
	
	# Read Lines
	for i, line in enumerate(f):
		
		# Get Channel Mode
		lineItem = line.split()
		if not lineItem: continue
		if lineItem[0] == 'static': loadStaticData(line,targetNS)
		if lineItem[0] == 'anim': loadAnimData(animFile,i,targetNS,frameOffset,infinityOverride)
	
	# Close File
	f.close()
	
	# Filter Rotation Anim
	if applyEulerFilter:
		rotateChannels = mc.ls(targetNS+':*',type='animCurveTA')
		mc.filterCurve(rotateChannels)
	
	# Return Result
	return True

def loadStaticData(line,targetNS):
	'''
	Apply static anim data from anim file
	@param line: Static data line from the source anim file
	@type line: str
	@param targetNS: Target namespace to apply the static data to
	@type targetNS: str
	'''
	# Parse Line Data
	lineItem = line.split()
	attr = lineItem[2]
	obj = lineItem[3].split(':')[-1]
	attrPath = targetNS+':'+obj+'.'+attr
	value = float(lineItem[5])
	
	# Check Target Attribute
	if not mc.objExists(attrPath):
		print('Attribute "'+attrPath+'" does not exist!! Skipping...')
		return False
	if not mc.getAttr(attrPath,se=True):
		print('Attribute "'+attrPath+'" is not settable!! Skipping...')
		return False
	
	# Apply Static Value
	try: mc.setAttr(attrPath,value)
	except Exception, e: print('AnimLib: Load Static Data: Error setting attribute "'+attrPath+'" to value '+str(value)+'! Exception Msg: '+str(e))
	
	# Return Result
	return True

def loadAnimData(animFile,lineID,targetNS,frameOffset=0,infinityOverride=None):
	'''
	Apply anim data from anim file
	@param animFile: Anim file path
	@type animFile: str
	@param lineID: Line ID (number) which marks the start of the node.attr anim data
	@type lineID: int
	@param targetNS: Target namespace to apply the static data to
	@type targetNS: str
	@param frameOffset: Frame offset to apply to the loaded animation data
	@type frameOffset: int or float
	@param infinityOverride: Force infinity mode override for loaded animation data.
	@type infinityOverride: str or None
	'''
	# Initialize Target Attribute
	attrPath = ''
	animData = []
	
	# =============
	# - Read File -
	# =============
	
	f = open(animFile,'r')
	for i, line in enumerate(f):
	
		# Skip to relevant line items
		if i < lineID: continue
		
		# Get Anim Data Header
		if i == lineID:
			
			lineItem = line.split()
			attr = lineItem[2]
			obj = lineItem[3].split(':')[-1]
			attrPath = targetNS+':'+obj+'.'+attr
			
			# Check Target Attribute
			if not mc.objExists(attrPath):
				print('Attribute "'+attrPath+'" does not exist!! Skipping...')
				return False
			if not mc.getAttr(attrPath,se=True):
				print('Attribute "'+attrPath+'" is not settable!! Skipping...')
				return False
			
			# Proceed to Next Line
			continue
		
		# Check Anim Data End
		if '}' in line: break
		
		# Build Anim Data
		animData.append(line)
	
	# ===================
	# - Apply Anim Data -
	# ===================
	
	# Get Curve Data
	weighted = bool(animData[1].split()[-1][:-1])
	preInf = animData[2].split()[-1][:-1]
	postInf = animData[3].split()[-1][:-1]
	
	# Check Infinity Mode Override
	if infinityOverride:
		
		# Check Valid Infinity Mode
		if not infinityOverride in ['constant','linear','cycle','cycleRelative','oscillate']:
			print('Invalid infinity mode "'+infinityOverride+'"! Using stored values...')
		else:
			preInf = infinityOverride
			postInf = infinityOverride
	
	# Load Animation Data
	for data in animData[5:]:
		
		# Clean Data Line
		data = data.replace(';','')
		
		# Split Data Items
		dataItem = data.split()
		
		# Apply Time Offset
		time = float(dataItem[0])+frameOffset
		value = float(dataItem[1])
		ittype = dataItem[2]
		ottype = dataItem[3]
		lock = bool(dataItem[4])
		bd = bool(int(dataItem[6][0]))
		
		mc.setKeyframe(attrPath,t=time,v=value)
		mc.keyTangent(attrPath,e=True,weightedTangents=weighted)
		mc.keyTangent(attrPath,e=True,t=(time,time),lock=lock,itt=ittype,ott=ottype)
		mc.keyframe(attrPath,e=True,t=(time,time),breakdown=bd)
		if weighted: mc.keyTangent(attrPath,weightLock=1)
		
		if len(dataItem) == 11:
			inAn = float(dataItem[7])
			inWt = float(dataItem[8])
			otAn = float(dataItem[9])
			otWt = float(dataItem[10])
			mc.keyTangent(	attrPath,
							e=True,
							t=(time,time),
							inAngle=inAn,
							inWeight=inWt,
							outAngle=otAn,
							outWeight=otWt	)
	
	# Set Curve Infinity
	mc.setInfinity(attrPath,pri=preInf,poi=postInf)
	
	# Return Result
	return True

def applyAnim(targetNS,char,animType,anim):
	'''
	Apply an animation clip to a specified target namespace.
	@param targetNS: Target namespace to apply a animation clip to.
	@type targetNS: str
	@param char: The character library to apply the pose from.
	@type char: str
	@param animType: The animation clip type (sub-directory) to apply.
	@type animType: str
	@param anim: The anim clip to apply.
	@type anim: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if not mc.namespace(ex=targetNS):
		raise Exception('Target namespace "'+targetNS+'" does not exist!')
	
	# Determine Pose
	animFile = animLibRoot()+'/'+char+'/'+animType+'/'+anim+'.anim'
	
	# Check Anim File
	if not os.path.isfile(animFile):
		raise Exception('Anim clip file "'+animFile+'" does not exist! Unable to load animation.')
	
	# ===================
	# - Apply Hand Pose -
	# ===================
	
	loaded = loadAnim(animFile,targetNS)
	if not loaded:
		raise Exception('Problem applying animation clip "'+anim+'" to namespace "'+targetNS+'"!')
	
	# =================
	# - Return Result -
	# =================
	
	return loaded

def applyPose(targetNS,char,poseType,pose,key=False):
	'''
	Apply a hand pose to a specified target namespace.
	@param targetNS: Target namespace to apply a hand pose to.
	@type targetNS: str
	@param char: The character library to apply the pose from.
	@type char: str
	@param poseType: The pose type (sub-directory) to apply.
	@type poseType: str
	@param pose: The pose to apply.
	@type pose: str
	@param key: Set keyframes for pose.
	@type key: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if not mc.namespace(ex=targetNS):
		raise Exception('Target namespace "'+targetNS+'" does not exist!')
	
	# Determine Pose
	poseFile = animLibRoot()+'/'+char+'/'+poseType+'/'+pose+'.pose'
	
	# Check Pose File
	if not os.path.isfile(poseFile):
		raise Exception('Pose file "'+poseFile+'" does not exist! Unable to load pose.')
	
	# ===================
	# - Apply Hand Pose -
	# ===================
	
	loaded = loadPose(poseFile,targetNS)
	if not loaded:
		raise Exception('Problem applying pose "'+pose+'" to namespace "'+targetNS+'"!')
	
	# =================
	# - Set Pose Keys -
	# =================
	
	if key:
		poseNodes = [targetNS+':'+i for i in getPoseNodes(poseFile,stripNS=True)]
		mc.setKeyframe(poseNodes)
	
	# =================
	# - Return Result -
	# =================
	
	return loaded

def applyHandPose(targetNS,side,char=None,pose=None,key=False):
	'''
	Apply a hand pose to a specified target namespace.
	@param targetNS: Target namespace to apply a hand pose to.
	@type targetNS: str
	@param side: The hand to apply the pose to. Accepted values are "lf" or "rt".
	@type side: str
	@param char: The character library to apply the pose from. If empty, get character from reference path context ("asset").
	@type char: str
	@param pose: The hand pose to apply. If empty, choose pose randomly from available pose files.
	@type pose: str
	@param key: Set keyframes for pose.
	@type key: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if not mc.namespace(ex=targetNS):
		raise Exception('Target namespace "'+targetNS+'" does not exist!')
	
	# Check Character
	if not char:
		targetCtx = glTools.utils.reference.contextFromNsReferencePath(targetNS)
		if not dict(targetCtx).has_key('asset'):
			raise Exception('Unable to determine asset from reference path')
		char = targetCtx['asset']
	
	# Check Pose
	poseDir = animLibRoot()+'/'+char+'/Hands'
	if not pose:
		poseList = [i for i in os.listdir(poseDir) if i.endswith('_'+side+'.pose')]
		if not poseList:
			raise Exception('No available pose files in directory "'+poseDir+'"! (*_'+side+'.pose)')
		poseInd = int(random.random()*len(poseList))
		pose = poseDir+'/'+poseList[poseInd]
	else:
		pose = poseDir+'/'+pose+'_'+side+'.pose'
	
	# Check Pose File
	if not os.path.isfile(pose):
		raise Exception('Pose file "'+pose+'" does not exist! Unable to load pose.')
	
	# ===================
	# - Apply Hand Pose -
	# ===================
	
	loaded = loadPose(pose,targetNS)
	if not loaded:
		raise Exception('Problem applying pose "'+pose+'" to namespace "'+targetNS+'"!')
	
	# =================
	# - Set Pose Keys -
	# =================
	
	if key:
		poseNodes = [targetNS+':'+i for i in getPoseNodes(pose,stripNS=True)]
		mc.setKeyframe(poseNodes)
	
	# =================
	# - Return Result -
	# =================
	
	return loaded

def applyHandAnim(targetNS,side,char=None,anim=None):
	'''
	Apply a hand pose to a specified target namespace.
	@param targetNS: Target namespace to apply a hand anim to.
	@type targetNS: str
	@param side: The hand to apply the anim to. Accepted values are "lf" or "rt".
	@type side: str
	@param char: The character library to apply the anim from. If empty, get character from reference path context ("asset").
	@type char: str
	@param anim: The hand animation to apply. If empty, choose animation randomly from available anim files.
	@type anim: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if not mc.namespace(ex=targetNS):
		raise Exception('Target namespace "'+targetNS+'" does not exist!')
	
	# Check Character
	if not char:
		targetCtx = glTools.utils.reference.contextFromNsReferencePath(targetNS)
		if not dict(targetCtx).has_key('asset'):
			raise Exception('Unable to determine asset from reference path')
		char = targetCtx['asset']
	
	# Check Anim
	animDir = animLibRoot()+'/'+char+'/Hands'
	if not anim:
		animList = [i for i in os.listdir(animDir) if i.endswith('_'+side+'.anim')]
		if not animList:
			raise Exception('No available anim files in directory "'+animDir+'"! (*_'+side+'.anim)')
		animInd = int(random.random()*len(animList))
		anim = animDir+'/'+animList[animInd]
	else:
		pose = animDir+'/'+anim+'_'+side+'.anim'
	
	# Check Pose File
	if not os.path.isfile(anim):
		raise Exception('Animation file "'+anim+'" does not exist! Unable to load anim.')
	
	# ===================
	# - Apply Hand Anim -
	# ===================
	
	loaded = loadAnim(anim,targetNS)
	
	# =================
	# - Return Result -
	# =================
	
	return loaded

def applyFacePose(targetNS,char=None,pose=None,key=False):
	'''
	Apply a face pose to a specified target namespace.
	@param targetNS: Target namespace to apply a pose to.
	@type targetNS: str
	@param char: The character library to apply the pose from. If empty, get character from reference path context ("asset").
	@type char: str
	@param pose: The pose to apply. If empty, choose pose randomly from available pose files.
	@type pose: str
	@param key: Set keyframes for pose.
	@type key: bool
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if not mc.namespace(ex=targetNS):
		raise Exception('Target namespace "'+targetNS+'" does not exist!')
	
	# Check Character
	if not char:
		targetCtx = glTools.utils.reference.contextFromNsReferencePath(targetNS)
		if not dict(targetCtx).has_key('asset'):
			raise Exception('Unable to determine asset from reference path')
		char = targetCtx['asset']
	
	# Check Pose
	poseDir = animLibRoot()+'/'+char+'/Face_Exp'
	if not pose:
		poseList = [i for i in os.listdir(poseDir) if i.endswith('.pose')]
		if not poseList:
			raise Exception('No available pose files in directory "'+poseDir+'"! (*.pose)')
		poseInd = int(random.random()*len(poseList))
		pose = poseDir+'/'+poseList[poseInd]
	else:
		pose = poseDir+'/'+pose+'.pose'
	
	# Check Pose File
	if not os.path.isfile(pose):
		raise Exception('Pose file "'+pose+'" does not exist! Unable to load pose.')
	
	# ===================
	# - Apply Face Pose -
	# ===================
	
	loaded = loadPose(pose,targetNS)
	if not loaded:
		raise Exception('Problem applying pose "'+pose+'" to namespace "'+targetNS+'"!')
	
	# =================
	# - Set Pose Keys -
	# =================
	
	if key:
		poseNodes = getPoseNodes(pose)
		mc.setKeyframe(poseNodes)
	
	# =================
	# - Return Result -
	# =================
	
	return loaded

def savePose(poseFile,poseNodes=[],poseNote=None,poseImg=None):
	'''
	'''
	pass

def saveAnim(animFile,animNodes=[],animNote=None,animImg=None):
	'''
	'''
	# ===================
	# - Check Anim Path -
	# ===================
	
	# File Extension
	if not animFile.endswith('.anim'):
		raise Exception('Incorrect anim file extension! Expected anim file extension ".anim"...')
	
	# Get Path Directory
	pathDir = os.path.dirname(animFile)
	
	# Create File Directory if Needed
	if not os.path.exists(pathDir): os.makedirs(pathDir)
	
	# ===================
	# - Save Anim Notes -
	# ===================
	
	if animNote:
		noteFile = animFile.replace('.anim','.notes')
		writeNotes(noteFile,note=animNote)
	
	# ======================
	# - Save Anim Snapshot -
	# ======================
	
	if not animImg:
		pass
		#animLib_snapShot($path,$name,"anim");
	
	# ==================
	# - Save Anim File -
	# ==================
	
	writeAnimFile(animFile,animNodes=animNodes)

def writePoseFile(poseFile,poseNodes=[]):
	'''
	Write pose data to file.
	@param poseFile: Destination pose file
	@type poseFile: str
	@param poseNodes: List of nodes to save pose data for
	@type poseNodes: list
	'''
	# Open File for Writing
	print('\nWriting Animation Curves...\n')
	f = open(poseFile,'w')
	
	for poseNode in poseNodes:
		
		# Get Settable Attrs
		attrs = []
		attrs.extend(mc.listAttr(poseNode,k=True) or [])
		attrs.extend(mc.listAttr(poseNode,cb=True) or [])
		
		# Remove Locked Attrs
		lock_attrs = mc.listAttr(poseNode,l=True)
		attrs = list(set(attrs)-set(lock_attrs))
		
		# Build poseData
		for at in attrs:
			
			# Check Settable
			if not mc.getAttr(poseNode+'.'+at,se=True): continue
			v = mc.getAttr(poseNode+'.'+at)
			if v < 0.000001: v = 0
			f.write(poseNode+'.'+at+' '+str(v))
	
	# Close File
	f.close()
	
	# Return Result
	print '\nDone Writing Pose Data\n'
	return poseFile

def writeAnimFile(animFile,animNodes=[]):
	'''
	Write pose data to file.
	@param poseFile: Destination pose file
	@type poseFile: str
	@param poseNodes: List of nodes to save pose data for
	@type poseNodes: list
	'''
	# Initialize First Frame Value
	firstKeyTime = 1000000
	
	# Open File for Writing
	print('\nWriting Animation Curves...\n')
	f = open(animFile,'w')
	f.write('# Generated by VFX animLib\n#\n')
	f.write('# dkAnim written by Daniel Kramer MOD by Mark Behm\n#\n')
	f.write('# Source workfile: '+mc.file(q=True,sn=True)+'\n#\n\n')
	
	for item in animNodes:
		
		# Get Animated Channels
		channels = mc.listConnections(item,s=True,d=False,p=True,c=True,type='animCurve')
		for i in range(0,len(channels),2):
			
			chan = mc.ls(channels[i],o=True)[0]
			node = mc.ls(channels[i+1],o=True)[0]
			attr = channels[i+1].split('.')[-1]
			attrName = channels[i+1]
			
			parent = 0
			nodeParent = mc.listRelatives(node,p=True)
			if nodeParent: parent = 1
			
			# Infinity
			infValue = ['constant','linear','constant','cycle','cycleRelative','oscillate']
			preIn = infValue[mc.getAttr(chan+'.preInfinity')]
			postInf = infValue[mc.getAttr(chan+'.postInfinity')]
			
			# Weighted
			weighted = int(mc.getAttr(chan+'.weightedTangents'))
			
			# ====================
			# - Write Curve Data -
			# ====================
			
			f.write('anim '+attr+' '+attr+' '+node+' '+parent+' 0 0;\n')
			f.write('animData {\n')
			f.write('  weighted '+str(weighted)+';\n')
			f.write('  preInfinity '+preIn+';\n')
			f.write('  postInfinity '+postIn+';\n')
			f.write('  keys {\n')
			
			# ==================
			# - Write Key Data -
			# ==================
			
			# Get Key Data
			keys = mc.keyframe(chan,q=True)
			values = mc.keyframe(chan,q=True,vc=True)
			inTan = mc.keyTangent(chan,q=True,itt=True)
			outTan = mc.keyTangent(chan,q=True,ott=True)
			tanLock = mc.keyTangent(chan,q=True,lock=True)
			weightLock = mc.keyTangent(chan,q=True,weightLock=True)
			breakDown = mc.keyframe(chan,q=True,breakdown=True)
			inAngle = mc.keyTangent(chan,q=True,inAngle=True)
			outAngle = mc.keyTangent(chan,q=True,outAngle=True)
			inWeight = mc.keyTangent(chan,q=True,inWeight=True)
			outWeight = mc.keyTangent(chan,q=True,outWeight=True)
			
			# Write Key Data
			for i in range(len(keys)):
				
				# Get Breakdown Status
				bd = int(bool(keys[i] in breakDown))
				
				# First Key
				if keys[i] < firstKeyTime: firstKeyTime = keys[i]

				# Write Key Data to File
				f.write('    '+str(keys[i])+' '+str(values[i])+' '+inTan[i]+' '+outTan[i]+' '+str(tanLock[i])+' '+str(weightLock[i])+' '+str(bd))
				if inTan[i] == 'fixed': f.write(' '+str(inAngle[i])+' '+str(inWeight[i]))
				if outTan[i] == 'fixed': f.write(' '+str(outAngle[i])+' '+str(outWeight[i]))
				f.write(';\n')
				
			f.write('  }\n}\n')
		
		# =========================
		# - Write Static Channels -
		# =========================
		
		staticChans = mc.listAnimatable(item)
		for staticChan in staticChans:
			
			node = mc.ls(staticChan,o=True)[0]
			attr = staticChan.split('.')[-1]

			parent = 0
			nodeParent = mc.listRelatives(node,p=True)
			if nodeParent: parent = 1
			
			#staticChan = node+'.'+attr
			keys = mc.keyframe(staticChan,q=True)
			connected = mc.listConnections(staticChan,s=True)
			
			if not keys and not connected:
				f.write('static '+attr+' '+attr+' '+node+' '+parent+' '+str(mc.getAttr(staticChan))+'\n')

	# Record First Key Offset
	f.write('firstKeyTime '+str(firstKeyTime))
	
	# Close File
	f.close()
	
	# =================
	# - Return Result -
	# =================
	
	print '\nDone Writing Animation Curves\n'
	
	return animFile

def writeNotes(noteFile,note=None):
	'''
	'''
	# Open File for Writing
	f = open(noteFile,'w')
	
	# Write Note to File
	if not note:
		f.write('author: '+os.environ['USER'])
		day = ['Mon','Tues','Wed','Thur','Fri','Sat','Sun']
		dt = datetime.datetime.now()
		f.write('date:   '+day[datetime.datetime.weekday(dt)]+' '+dt.month+' '+dt.day+' '+dt.hour+':'+dt.minute+':'+dt.second+' PST '+dt.year)
	else:
		f.write(note)
	
	# Close File
	f.close()

