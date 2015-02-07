import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.mesh

import math

def validatePoints(obj):
	'''
	'''
	# Initiate check
	check = 0
	
	# Get points
	pArray = glTools.utils.base.getMPointArray(obj,worldSpace=False)
	
	# Check points
	for i in range(pArray.length()):
		
		# Check point values
		for val in [pArray[i].x,pArray[i].y,pArray[i].z,pArray[i].w]:
			
			# Check NaN
			if math.isnan(val):
				print('Found NaN : '+obj+'.p['+str(i)+']')
				check += 1
			# Check INF
			if math.isinf(val):
				print('Found INF : '+obj+'.p['+str(i)+']')
				check += 1
	
	# Return result
	return check

def validateNormals(mesh):
	'''
	'''
	# Initiate check
	check = 0
	
	# Get points
	nArray = glTools.utils.mesh.getNormals(mesh,worldSpace=False)
	
	# Check points
	for i in range(nArray.length()):
		
		# Check point values
		for val in [nArray[i].x,nArray[i].y,nArray[i].z]:
			
			# Check NaN
			if math.isnan(val):
				print('Found NaN : '+mesh+'.n['+str(i)+']')
				check += 1
			# Check INF
			if math.isinf(val):
				print('Found INF : '+mesh+'.n['+str(i)+']')
				check += 1
	
	# Return result
	return check

def validateUVs(mesh):
	'''
	'''
	# Initiate check
	check = 0
	
	# Get meshFn
	meshFn = glTools.utils.mesh.getMeshFn(mesh)
	
	# Get UV Sets
	uvSetList = mc.polyUVSet(mesh,q=True,allUVSets=True)
	if not uvSetList:
		print('No UV Set : '+mesh)
		check += 1
	
	for uvSet in uvSetList:
		
		# Get UV values
		uArray = OpenMaya.MFloatArray()
		vArray = OpenMaya.MFloatArray()
		meshFn.getUVs(uArray,vArray,uvSet)
		
		# Check empty UV set
		if not uArray.length() and not vArray.length():
			print('Empty UV Set : '+mesh+' - '+uvSet)
			check += 1
		
		# Check U values
		for i in range(uArray.length()):
			if math.isnan(uArray[i]):
				print('Found NaN : '+mesh+'.uv['+str(i)+']')
				check += 1
			if math.isinf(uArray[i]):
				print('Found INF : '+mesh+'.uv['+str(i)+']')
				check += 1
		
		# Check V values
		for i in range(vArray.length()):
			if math.isnan(vArray[i]):
				print('Found NaN : '+mesh+'.uv['+str(i)+']')
				check += 1
			if math.isinf(vArray[i]):
				print('Found INF : '+mesh+'.uv['+str(i)+']')
				check += 1
	
	# Return result
	return check

def validateAttr(attr):
	'''
	'''
	# Initiate check
	check = 0
	
	# Check Attr
	if not mc.objExists(attr):
		raise Exception('Attribute "'+attr+'" does not exist!')
	
	# Get Attribute type
	val = mc.getAttr(attr)
	
	# Check value
	if type(val) == list:
		
		for i in val:
			
			if type(i) == list or type(i) == tuple:
				for n in i:
					if math.isnan(n):
						print('Found NaN : '+attr+'['+str(i)+']['+str(n)+']')
						check += 1
					if math.isinf(n):
						print('Found INF : '+attr+'['+str(i)+']['+str(n)+']')
						check += 1
			else:
				if math.isnan(i):
					print('Found NaN : '+attr+'['+str(i)+']')
					check += 1
				if math.isinf(i):
					print('Found INF : '+attr+'['+str(i)+']')
					check += 1
	else:
		if math.isnan(val):
			print('Found NaN : '+attr)
			check += 1
		if math.isinf(val):
			print('Found INF : '+attr)
			check += 1

	# Return result
	return check
