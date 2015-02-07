import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim

import glTools.utils.base
import glTools.utils.matrix

import ast

def buildMatrix(mat):
	'''
	Build MMatrix From Matrix Cache List
	'''
	matrix = OpenMaya.MMatrix()
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 0, mat[0][0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 1, mat[0][1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[0], 2, mat[0][2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 0, mat[1][0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 1, mat[1][1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[1], 2, mat[1][2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 0, mat[2][0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 1, mat[2][1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[2], 2, mat[2][2])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 0, mat[3][0])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 1, mat[3][1])
	OpenMaya.MScriptUtil.setDoubleArray(matrix[3], 2, mat[3][2])
	return matrix

def loadMatrixCache(cacheFile,agent='',targetNS=''):
	'''
	'''
	# Initialize Frame No.
	frame = 0
	
	# Check NS
	if targetNS: targetNS+=':'
	
	# Open File
	f = open(cacheFile,'r')
	lines = f.readlines()
	
	# Load Cache
	for line in lines:
		
		# Get Frame
		if line.startswith('# frame'):
			frame = line.split(' ')[-1]
			print frame
			continue
		
		# Get Matrix
		seg = line.split(' ')[0]
		mat = ast.literal_eval(line.replace(seg+' ',''))
		matrix = buildMatrix(mat)
		
		# Check Agent
		if agent and seg == 'Agent': seg = agent
		
		# ===================
		# - Get Translation -
		# ===================
		
		pos = OpenMaya.MTransformationMatrix(matrix).getTranslation(OpenMaya.MSpace.kTransform)
		t = [pos[0],pos[1],pos[2]]
		
		# ================
		# - Get Rotation -
		# ================
		
		# Factor in Joint Orientation
		if mc.objectType(seg) == 'joint':
			segObj = glTools.utils.base.getMObject(seg)
			segFn = OpenMayaAnim.MFnIkJoint(segObj)
			segOri = OpenMaya.MQuaternion()
			segFn.getOrientation(segOri)
			matrix *= segOri.asMatrix().inverse()
		
		# Get Rotation
		rot = OpenMaya.MTransformationMatrix(matrix).eulerRotation()
		rad = mm.eval('rad_to_deg(1)')
		r = [rot.x*rad,rot.y*rad,rot.z*rad]
		
		# =================
		# - Set Keyframes -
		# =================
		
		mc.setKeyframe(targetNS+seg,at='tx',v=t[0],t=float(frame))
		mc.setKeyframe(targetNS+seg,at='ty',v=t[1],t=float(frame))
		mc.setKeyframe(targetNS+seg,at='tz',v=t[2],t=float(frame))
		mc.setKeyframe(targetNS+seg,at='rx',v=r[0],t=float(frame))
		mc.setKeyframe(targetNS+seg,at='ry',v=r[1],t=float(frame))
		mc.setKeyframe(targetNS+seg,at='rz',v=r[2],t=float(frame))
	
	# ==============
	# - Close File -
	# ==============
	
	f.close()

def loadAgentData(dataFile):
	'''
	'''
	# Get Radian Conversion Factor
	rad = mm.eval('rad_to_deg(1)')
	
	# Open File
	f = open(dataFile,'r')
	lines = f.readlines()
	
	# Build Matrices
	agent_matrix = OpenMaya.MTransformationMatrix(buildMatrix(ast.literal_eval(lines[0])))
	segment_matrix = OpenMaya.MTransformationMatrix(buildMatrix(ast.literal_eval(lines[1])))
	
	# AGENT
	a = mc.spaceLocator(n='agent')[0]
	b = mc.spaceLocator(n='Hips')[0]
	mc.parent(b,a)
	
	# Agent Position
	pos = agent_matrix.getTranslation(OpenMaya.MSpace.kTransform)
	t = [pos[0],pos[1],pos[2]]
	mc.setAttr(a+'.t',*t)
	
	# Agent Rotation
	rot = agent_matrix.eulerRotation()
	r = [rot.x*rad,rot.y*rad,rot.z*rad]
	mc.setAttr(a+'.r',*r)
	
	# Hip Position
	pos = segment_matrix.getTranslation(OpenMaya.MSpace.kTransform)
	t = [pos[0],pos[1],pos[2]]
	mc.setAttr(b+'.t',*t)
	
	# Return Result
	return [a,b]

def printAgentData(dataFile):
	'''
	'''
	# Get Radian Conversion Factor
	rad = mm.eval('rad_to_deg(1)')
	
	# Open File
	f = open(dataFile,'r')
	lines = f.readlines()
	
	# Build Matrices
	agent_matrix = OpenMaya.MTransformationMatrix(buildMatrix(ast.literal_eval(lines[0])))
	segment_matrix = OpenMaya.MTransformationMatrix(buildMatrix(ast.literal_eval(lines[1])))
	
	# AGENT
	
	# Position
	pos = agent_matrix.getTranslation(OpenMaya.MSpace.kTransform)
	t = [pos[0],pos[1],pos[2]]
	print('Agent Translate: '+str(t))
	
	rot = agent_matrix.eulerRotation()
	r = [rot.x*rad,rot.y*rad,rot.z*rad]
	print('Agent Rotate: '+str(r))
	
	scaleUtil = OpenMaya.MScriptUtil()
	scaleUtil.createFromDouble(0,0,0)
	scalePtr = scaleUtil.asDoublePtr()
	agent_matrix.getScale(scalePtr,OpenMaya.MSpace.kTransform)
	s = [	OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,0),
			OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,1),
			OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,2)	]
	print('Agent Scale: '+str(s))
	
	# SEGMENT
	
	# Position
	pos = segment_matrix.getTranslation(OpenMaya.MSpace.kTransform)
	t = [pos[0],pos[1],pos[2]]
	print('Segment Translate: '+str(t))
	
	rot = segment_matrix.eulerRotation()
	r = [rot.x*rad,rot.y*rad,rot.z*rad]
	print('Segment Rotate: '+str(r))
	
	scaleUtil = OpenMaya.MScriptUtil()
	scaleUtil.createFromDouble(0,0,0)
	scalePtr = scaleUtil.asDoublePtr()
	segment_matrix.getScale(scalePtr,OpenMaya.MSpace.kTransform)
	s = [	OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,0),
			OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,1),
			OpenMaya.MScriptUtil().getDoubleArrayItem(scalePtr,2)	]
	print('Segment Scale: '+str(s))
	
	
