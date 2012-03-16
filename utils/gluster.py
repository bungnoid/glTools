###########################################################################################
#<OPEN>
#<KEEP_FORMAT>
#<FILE NAME>
#			rig_gluster.py
#</FILE NAME>
#
#<VERSION HISTORY>
#			02/20/08 : Grant Laker : Initial release
#</VERSION HISTORY>
#
#<DESCRIPTION>
#			Utility methods for working with the gluster deformer
#</DESCRIPTION>
#
#<USAGE>
#
#</USAGE>
#
#<DEPARTMENTS>
#			<+> rig
#			<+> cfin
#</DEPARTMENTS>
#
#<KEYWORDS>
#			<+> gluster
#			<+> utility
#</KEYWORDS>
#
#<APP>
#			Maya
#</APP>
#
#<APP VERSION>
#			2008
#</APP VERSION>
#<CLOSE>
###########################################################################################

import maya.cmds as mc
import maya.mel as mm

import glTools.common.componentUtilities

###########################################################
#<OPEN>
#<PROC NAME>
#			setup
#</PROC NAME>
#
#<USAGE>
#			setup()
#</USAGE>
#<CLOSE>
###########################################################

def setup( control_obj, bpm_obj, surface, gluster, prefix="", volume=1):
	
	componentUtils = glTools.common.componentUtilities.ComponentUtilities()
	
	#declare variables
	return_list = []
	gls=[]
	
	#check for gluster
	if not mc.objExists(gluster):
		gls = mc.deformer( surface, type="gluster", n=(prefix+"_gls") )
	else:
		gls.append( gluster )
	return_list.append(gls[0])
	
	
	index = getNextIndex(gluster)
	makeConnections( control_obj=control_obj, bpm_obj=bpm_obj, gluster=gls[0], index=index)
	
	if (volume): ramp_loc = addVolumeControl(control_obj=control_obj, gluster=gls[0], index=index, prefix=prefix)
		
	shape = mc.listRelatives(surface, s=1 )
	numVtx = []
	if ( mc.objectType( shape[0], isType='nurbsSurface' ) ):
		numVtx.append( componentUtils.getComponentCount( surface ) )
	else:
		numVtx.append( mc.polyEvaluate( surface,v=1 ) )
	
	'''
	stupid Autodesk!
	cmd = ('mc.setAttr( "'+ gls[0] +'.influenceWeight[0]",')
	for i in range( numVtx[0]-1 ):
		cmd+= " 1.0"
		if i != numVtx[0]-2: cmd+= ","
		else: cmd+= ', type="doubleArray", '+ str(numVtx[0]-1) +' )'
	
	print cmd
	eval(cmd)
	'''
	
	cmd = ('setAttr '+ gls[0] +'.influenceWeight['+str(index)+'] -type "doubleArray" '+ str(numVtx[0]) )
	for i in range( numVtx[0] ):
		if volume == 1:
			cmd+= " 1.0"
		else:
			cmd+= " 1.0"
	mm.eval(cmd)
	print cmd
	return return_list

###########################################################
#<OPEN>
#<PROC NAME>
#			getNextIndex
#</PROC NAME>
#
#<USAGE>
#			getNextIndex()
#</USAGE>
#<CLOSE>
###########################################################

def getNextIndex(gluster):
	index = mc.getAttr(gluster+".matrix", s=1)
	return index

###########################################################
#<OPEN>
#<PROC NAME>
#			makeConnections
#</PROC NAME>
#
#<USAGE>
#			makeConnections()
#</USAGE>
#<CLOSE>
###########################################################

def makeConnections( control_obj, bpm_obj, gluster, index):
	mc.connectAttr( (control_obj+".worldMatrix[0]"), (gluster+".matrix["+str(index)+"]") )
	mc.connectAttr( (bpm_obj+".worldInverseMatrix[0]"), (gluster+".bindPreMatrix["+str(index)+"]") )
	mc.connectAttr( (control_obj+".message"), (gluster+".paintTrans"), f=1 )

###########################################################
#<OPEN>
#<PROC NAME>
#			addVolumeControl
#</PROC NAME>
#
#<USAGE>
#			addVolumeControl()
#</USAGE>
#<CLOSE>
###########################################################

def addVolumeControl(control_obj, gluster, index, prefix=""):
	return_list=[]
	ramp_loc = mc.createNode( "rampLocator", p=control_obj, n=prefix+"_rmp" )
	return_list.append(ramp_loc)
	mc.connectAttr( (ramp_loc+".width"), (gluster+".volumeWidth["+str(index)+"]") )
	mc.connectAttr( (ramp_loc+".offset"), (gluster+".volumeOffset["+str(index)+"]") )
	mc.connectAttr( (ramp_loc+".falloffMessage"), (gluster+".falloff["+str(index)+"]") )
	mc.connectAttr( (ramp_loc+".message"), (control_obj+".specifiedManipLocation") )
	mc.setAttr( (control_obj+".showManipDefault"), 7)
	return return_list

###########################################################
#<OPEN>
#<PROC NAME>
#			setupMultipleGlusters
#</PROC NAME>
#
#<USAGE>
#			setupMultipleGlusters()
#</USAGE>
#<CLOSE>
###########################################################

def setupMultipleGlusters(control_obj, bpm_obj, surface, gluster, prefix="", volume=1):
	gluster_data=[]
	for i in range( len(control_obj)):
		gluster_data.extend( setup_gluster( control_obj[i], bpm_obj[i], surface, gluster, prefix, volume))

###########################################################
#<OPEN>
#<PROC NAME>
#			reorderInfluence
#</PROC NAME>
#
#<USAGE>
#			reorderInfluence()
#</USAGE>
#<CLOSE>
###########################################################

def reorderInfluence(glusterNode):
	
	influenceList = mc.listConnections(glusterNode+'.matrix',s=1,d=0)
	bindPreMatrixList = mc.listConnections(glusterNode+'.bindPreMatrix',s=1,d=0)
	indexArray = range(len(influenceList))
	indexArray.reverse()
	
	popWeightList = mc.getAttr(glusterNode + '.influenceWeight[' + str(indexArray[0]) + ']')
	
	for ind in indexArray:
		if ind:
			copyWeightList = mc.getAttr(glusterNode + '.influenceWeight[' + str(ind-1) + ']')
			mc.setAttr(glusterNode + '.influenceWeight[' + str(ind) + ']',copyWeightList,type='doubleArray')
			mc.connectAttr(influenceList[(ind-1)]+'.worldMatrix[0]',glusterNode+'.matrix['+str(ind)+']',f=1)
			mc.connectAttr(bindPreMatrixList[(ind-1)]+'.worldInverseMatrix[0]',glusterNode+'.bindPreMatrix['+str(ind)+']',f=1)
		else:
			mc.setAttr(glusterNode + '.influenceWeight[' + str(ind) + ']',popWeightList,type='doubleArray')
			mc.connectAttr(influenceList[indexArray[0]]+'.worldMatrix[0]',glusterNode+'.matrix[0]',f=1)
			mc.connectAttr(bindPreMatrixList[indexArray[0]]+'.worldInverseMatrix[0]',glusterNode+'.bindPreMatrix[0]',f=1)
		
	

###########################################################
#<OPEN>
#<PROC NAME>
#			skinToGluster
#</PROC NAME>
#
#<USAGE>
#			skinToGluster()
#</USAGE>
#<CLOSE>
###########################################################

def skinToGluster(obj):
	
	# Verify object
	if not mc.objExists(obj):
		print('Object ' + skinCluster + ' does not exist!')
		return
	skinCluster = mm.eval('findRelatedSkinCluster("'+obj+'")')
	
	# Verify skinCluster
	if not mc.objExists(skinCluster):
		print('skinCluster ' + skinCluster + ' does not exist!')
		return
	else:
		if mc.objectType(skinCluster) != 'skinCluster':
			print('Object ' + skinCluster + ' is not a valid skinCluster!')
			return
	
	# Get skinCluster influenceList
	influenceList = mc.skinCluster(skinCluster,q=1,inf=1)
	
	# Get number of affected components
	shape = obj
	if mc.objectType(obj) == 'transform':
		shapeList = mc.listRelatives(obj,s=1,ni=1)
		shape = shapeList[0]
	compCnt = 0
	if mc.objectType(shape) == 'mesh':
		compCnt = mc.polyEvaluate(shape,v=1)
	
	# Build weight array structure (dictionary)
	weights = {}
	for inf in influenceList:
		weights[inf] = []
	for i in range(compCnt):
		ptWtList = mc.skinPercent( skinCluster, shape+'.vtx['+str(i)+']', q=1, v=1 )
		for w in range(len(influenceList)):
			weights[influenceList[w]].append(ptWtList[w])
	
	# Create Gluster deformer
	glusterName = skinCluster + '_gls'
	nameElem = skinCluster.split('_')
	elemCnt = len(nameElem)
	if elemCnt > 1:
		glusterName = skinCluster.replace(nameElem[(elemCnt-1)],'gls')
	
	gluster = mc.deformer(obj,type='gluster',n=glusterName)
	mc.setAttr(gluster[0]+'.combineMethod',1)
	
	for i in range(len(influenceList)):
		# Connect influece object to deformer
		mc.connectAttr(influenceList[i]+'.worldMatrix[0]',gluster[0]+'.matrix['+str(i)+']',f=1)
		# Create base influence object
		base = influenceList[i]+'_bpm'
		if mc.objExists(influenceList[i]+'.bpmXform'):
			base = mc.getAttr(inf+'.bpmXform')
		else:
			nameElem = influenceList[i].split('_')
			elemCnt = len(nameElem)
			if elemCnt > 1:
				base = influenceList[i].replace(nameElem[(elemCnt-1)],'bpm')
			base = mc.createNode('transform',n=base)
			# Add bindPreMatrix (xform name) attribute to skinCluster influence
			mc.addAttr(influenceList[i],ln='bpmXform',dt='string')
			mc.setAttr(influenceList[i]+'.bpmXform',base,type='string')
			# Position and Orient base influence
			mc.delete(mc.parentConstraint(influenceList[i],base))
			mc.delete(mc.scaleConstraint(influenceList[i],base))
		# Connect influece base to deformer
		mc.connectAttr(base+'.worldInverseMatrix[0]',gluster[0]+'.bindPreMatrix['+str(i)+']',f=1)
		# Apply influence weights
		mc.setAttr(gluster[0] + '.influenceWeight[' + str(i) + ']',weights[influenceList[i]],type='doubleArray')
	

###########################################################
#<OPEN>
#<PROC NAME>
#			normalizeWeights
#</PROC NAME>
#
#<USAGE>
#			normalizeWeights()
#</USAGE>
#<CLOSE>
###########################################################

def normalizeWeights(glusterNode):
	
	# Verify gluster
	if not mc.objExists(glusterNode):
		print('gluster ' + glusterNode + ' does not exist!')
		return
	else:
		if mc.objectType(glusterNode) != 'gluster':
			print('Object ' + glusterNode + ' is not a valid gluster!')
			return()
	
	influence = mc.listConnections(glusterNode+'.matrix',s=1,d=0)
	
	weights = {}
	
	for i in range(len(influence)):
		weights[influence[i]] = mc.getAttr(glusterNode + '.influenceWeight[' + str(i) + ']')
		print(weights[influence[i]][120])
	
	for n in range(len(weights[influence[0]])):
		weightSum = 0.0
		for i in range(len(influence)):
			weightSum += weights[influence[i]][n]
		#print('weightSum = ' + str(weightSum))
		if weightSum != 1.0:
			normalFactor = 1.0/weightSum
			#print('normalFactor = ' + str(normalFactor)
			for i in range(len(influence)):
				weights[influence[i]][n] *= normalFactor
	
	for i in range(len(influence)):
		mc.setAttr(glusterNode + '.influenceWeight[' + str(i) + ']',weights[influence[i]],type='doubleArray')
	
