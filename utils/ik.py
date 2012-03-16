import maya.cmds as mc
import glTools.utils.mathUtils
import glTools.utils.matrix

class UserInputError(Exception): pass

def getAffectedJoints(ikHandle):
	'''
	Get a list of joints affected by a specified ikHandle
	@param ikHandle: IK Handle to query affected joints for
	@type ikHandle: str
	'''
	# Check ikHandle
	if not mc.objExists(ikHandle): raise UserInputError('IK handle '+ikHandle+' does not exist!')
	if mc.objectType(ikHandle) != 'ikHandle': raise UserInputError('Object '+ikHandle+' is not a valid ikHandle!')
	
	# Get startJoint
	startJoint = mc.listConnections(ikHandle+'.startJoint',s=True,d=False)[0]
	# Get endEffector
	endEffector = mc.listConnections(ikHandle+'.endEffector',s=True,d=False)[0]
	endJoint = mc.listConnections(endEffector+'.translateX',s=True,d=False)[0]
	
	# Get list of joints affected by ikHandle
	ikJoints = [endJoint]
	while ikJoints[-1] != startJoint:
		ikJoints.append(mc.listRelatives(ikJoints[-1],p=True)[0])
	# Reverse joint list
	ikJoints.reverse()
	
	# Return ik joints list
	return ikJoints

def poleVectorPosition(ikHandle,poleVectorType='free',distanceFactor=1.0):
	'''
	Determine a poleVector position for specified ikHandle based on the input arguments
	@param ikHandle: IK Handle to calculate poleVector position for
	@type ikHandle: str
	@param poleVectorType: Type of poleVector to setup. Accepted values are "free" and "fixed"
	@type poleVectorType: str
	@param distanceFactor: The relative distance from the joints to place the poleVector
	@type distanceFactor: float
	'''
	# Check ikHandle
	if mc.objectType(ikHandle) != 'ikHandle': raise UserInputError('Object "'+ikHandle+'" is not a valid IK Handle!!')
	if mc.listConnections(ikHandle+'.ikSolver',s=True,d=False)[0] != 'ikRPsolver':
		raise UserInputError('IK Handle "'+ikHandle+'" does not use a pole vector!!')
	
	# Get IK chain details
	ikJoints = getAffectedJoints(ikHandle)
	poleVector = mc.getAttr(ikHandle+'.poleVector')[0]
	poleVector = glTools.utils.mathUtils.normalizeVector(poleVector)
	# Transform poleVector to worldSpace
	ikParent = mc.listRelatives(ikHandle,p=True)
	if ikParent:
		ikMatrix = glTools.utils.matrix.buildMatrix(transform=ikParent[0])
		poleVector = glTools.utils.matrix.vectorMatrixMultiply(poleVector,ikMatrix,transformAsPoint=False,invertMatrix=False)
	
	# Get start/end joint positions
	startPos = mc.xform(ikJoints[0],q=True,ws=True,rp=True)
	endPos = mc.xform(ikJoints[-1],q=True,ws=True,rp=True)
	
	# Calculate poleVector position
	# ==
	# FREE
	if poleVectorType == 'free':
		# Calculate poleVector distance
		pvDist = glTools.utils.mathUtils.distanceBetween(startPos,endPos)*distanceFactor
		# Single Joint Elbow
		if len(ikJoints) == 3:
			elbowPos = mc.xform(ikJoints[1],q=True,ws=True,rp=True)
		# Double Joint Elbow
		elif len(ikJoints) == 4:
			mid1Pos = mc.xform(ikJoints[1],q=True,ws=True,rp=True)
			mid2Pos = mc.xform(ikJoints[2],q=True,ws=True,rp=True)
			elbowPos = ((mid1Pos[0]+mid2Pos[0])*0.5,(mid1Pos[1]+mid2Pos[1])*0.5,(mid1Pos[2]+mid2Pos[2])*0.5)
		pvPos = (elbowPos[0]+(poleVector[0]*pvDist),elbowPos[1]+(poleVector[1]*pvDist),elbowPos[2]+(poleVector[2]*pvDist))
	# FIXED
	elif poleVectorType == 'fixed':
		elbowPos = mc.xform(ikJoints[1],q=True,ws=True,rp=True)
		pvDist = glTools.utils.mathUtils.distanceBetween(startPos,elbowPos)*distanceFactor
		pvPos = (startPos[0]+(poleVector[0]*pvDist),startPos[1]+(poleVector[1]*pvDist),startPos[2]+(poleVector[2]*pvDist))
	else:
		raise UserInputError('Invalid poleVector type supplied ("'+poleVectorType+'")!! Specify "free" or "fixed"!')
	
	# Return position
	return pvPos
