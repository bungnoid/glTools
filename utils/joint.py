import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.channelState
import glTools.utils.mathUtils
import glTools.utils.matrix
import glTools.utils.skinCluster
import glTools.utils.stringUtils
import glTools.utils.transform

import math

def isJoint(joint):
	'''
	Check if the specified object is a valid joint
	@param joint: Object to check
	@type joint: str
	'''
	# Check object exists
	if not mc.objExists(joint): return False
	
	# Check joint
	if not mc.ls(type='joint').count(joint): return False
	
	# Return result
	return True

def getJointList(startJoint,endJoint):
	'''
	Get list of joints between and including a specified start and end joint
	@param startJoint: Start joint of joint list
	@type startJoint: str
	@param endJoint: End joint of joint list
	@type endJoint: str
	'''
	# Check joints
	if not mc.objExists(startJoint):
		raise Exception('Start Joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End Joint "'+endJoint+'" does not exist!')
	
	# Check hierarchy
	decendantList = mc.ls(mc.listRelatives(startJoint,ad=True),type='joint')
	if not decendantList.count(endJoint):
		raise Exception('End joint "'+endJoint+'" is not a decendant of start joint "'+startJoint+'"!')
	
	# Build joint list
	jntList = [endJoint]
	while(jntList[-1] != startJoint):
		pJnt = mc.listRelatives(jntList[-1],p=True,pa=True)
		if not pJnt: raise Exception('Found root joint while searching for start joint "'+startJoint+'"!')  
		jntList.append(pJnt[0])
	
	# Reverse list
	jntList.reverse()
	
	# Return result
	return jntList
	
def length(joint):
	'''
	Get length of specified joint
	@param joint: Joint to query length from
	@type joint: str
	'''
	# Check joint
	if not mc.objExists(joint): raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get child joints
	cJoints = mc.ls(mc.listRelatives(joint,c=True),type='joint')
	if not cJoints: return 0.0
	
	# Get length
	maxLength = 0.0
	for cJoint in cJoints:
		pt1 = glTools.utils.base.getPosition(joint)
		pt2 = glTools.utils.base.getPosition(cJoint)
		offset = glTools.utils.mathUtils.offsetVector(pt1,pt2)
		length = glTools.utils.mathUtils.mag(offset)
		if length > maxLength: maxLength = length
	
	# Return result
	return maxLength

def createFromPointList(ptList,orient=False,side='cn',part='chain',suffix='jnt'):
	'''
	Create joint chain from a list of point positions
	@param ptList: List of points to create joint chain from
	@type ptList: list
	@param orient: Orient joints
	@type orient: bool
	@param side: Joint side name prefix
	@type side: str
	@param part: Joint part name
	@type part: str
	@param suffix: Joint name suffix
	@type suffix: str
	'''
	# Clear selection
	mc.select(cl=True)
	
	# Create joint chain
	jntList = []
	for i in range(len(ptList)):
		jnt = mc.joint(p=ptList[i],n=side+'_'+part+str(i+1)+'_'+suffix)
		if i and orient: mc.joint(jntList[-1],e=True,zso=True,oj='xyz',sao='yup')
		jntList.append(jnt)
	
	# Return result
	return jntList

def orient(joint,aimAxis='x',upAxis='y',upVec=(0,1,0)):
	'''
	Orient joints based on user defined vectors
	@param joint: Joints to orient
	@type joint: str
	@param aimAxis: Axis to be aligned down the length of the joint
	@type aimAxis: str
	@param upAxis: Axis to be aligned withe the world vector specified by upVec
	@type upAxis: str
	@param upVec: World vector to align upAxis to
	@type upVec: tuple
	'''
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get joint child list
	childList = mc.listRelatives(joint,c=1)
	childJointList = mc.listRelatives(joint,c=1,type='joint',pa=True)
	
	# Unparent children
	if childList: childList = mc.parent(childList,w=True)
	
	# Orient joint
	if not childJointList:
		
		# End joint - Zero out joint orient
		mc.setAttr(joint+'.jo',0,0,0)
		
	else:
		
		# Get parent joint matrix
		pMat = OpenMaya.MMatrix()
		pJoint = mc.listRelatives(joint,p=True,pa=True)
		if pJoint: pMat = glTools.utils.matrix.getMatrix(pJoint[0])
		
		# Calculate aim vector
		p1 = glTools.utils.base.getPosition(joint)
		p2 = glTools.utils.base.getPosition(childJointList[0])
		aimVec = glTools.utils.mathUtils.offsetVector(p1,p2)
		
		# Build target matrix
		tMat = glTools.utils.matrix.buildRotation(aimVec,upVec,aimAxis,upAxis)
		
		# Calculate orient matrix
		oriMat = tMat * pMat.inverse()
		
		# Extract joint orient values
		rotOrder = mc.getAttr(joint+'.ro')
		oriRot = glTools.utils.matrix.getRotation(oriMat,rotOrder)
		
		# Reset joint rotation and orientation
		mc.setAttr(joint+'.r',0,0,0)
		mc.setAttr(joint+'.jo',oriRot[0],oriRot[1],oriRot[2])
		
	# Reparent children
	if childList: mc.parent(childList,joint)

def orient_old(joints,aimAxis=(1,0,0),upAxis=(0,1,0),upVec=(0,1,0)):
	'''
	Orient joints based on user defined vectors
	
	@param joints: List of joints to orient
	@type joints: list
	@param aimAxis: Axis to be aligned down the length of the joint
	@type aimAxis: tuple
	@param upAxis: Axis to be aligned withe the world vector specified by upVec
	@type upAxis: tuple
	@param upVec: World vector to align upAxis to
	@type upVec: tuple
	'''
	if not joints: joints = []
	for joint in joints:
		
		# Get child list
		childList = mc.listRelatives(joint,c=1)
		childJointList = mc.listRelatives(joint,c=1,type='joint',pa=True)
		if not childJointList:
			mc.setAttr(joint+'.jo',0,0,0)
			continue
		# Unparent children
		childList = mc.parent(childList,w=True)
		
		# Reset joint rotation and orientation
		mc.setAttr(joint+'.r',0,0,0)
		mc.setAttr(joint+'.jo',0,0,0)
		mc.makeIdentity(joint,apply=True,t=1,r=1,s=1,n=0,jointOrient=True)
		
		# Move transform to joint
		parent = mc.listRelatives(joint,p=True,pa=True)
		trans = mc.group(em=True,n=joint+'_ORIENT')
		if parent: mc.parent(trans,parent[0])
		mc.delete(mc.pointConstraint(joint,trans))
		
		# Match rotation order
		mc.setAttr(trans+'.ro',mc.getAttr(joint+'.ro'))
		
		# Derive orientation
		mc.aimConstraint(childJointList[0],trans,aimVector=aimAxis,upVector=upAxis,worldUpType='vector',worldUpVector=upVec)
		rot = mc.getAttr(trans+'.r')[0]
		mc.setAttr(joint+'.jo',rot[0],rot[1],rot[2])
		mc.delete(trans)
		
		# Reparent children
		mc.parent(childList,joint)

def orientTo(joint,target):
	'''
	Match specified joint orientation to a target transform
	@param joint: Joint to set orientation for
	@type joint: str
	@param target: Transform to match joint orientation to
	@type target: str
	'''
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	# Check target
	if not mc.objExists(target):
		raise Exception('Target transform "'+target+'" does not exist!')
	if not glTools.utils.transform.isTransform(target):
		raise Exception('Target "'+target+'" is not a valid transform!')
	
	# Unparent children
	childList = mc.listRelatives(joint,c=1,type=['joint','transform'])
	if childList: childList = mc.parent(childList,w=True)
	
	# Get parent joint matrix
	pMat = OpenMaya.MMatrix()
	pJoint = mc.listRelatives(joint,p=True,pa=True)
	if pJoint: pMat = glTools.utils.matrix.getMatrix(pJoint[0])
	
	# Get target matrix
	tMat = glTools.utils.matrix.getMatrix(target)
	
	# Calculate orient matrix
	oriMat = tMat * pMat.inverse()
	
	# Extract joint orient values
	rotOrder = mc.getAttr(joint+'.ro')
	oriRot = glTools.utils.matrix.getRotation(oriMat,rotOrder)
	
	# Reset joint rotation and orientation
	mc.setAttr(joint+'.r',0,0,0)
	mc.setAttr(joint+'.jo',oriRot[0],oriRot[1],oriRot[2])
	
	# Reparent children
	if childList:
		mc.parent(childList,joint)

def flipOrient(joint,target='',axis='x'):
	'''
	Flip the spcified joint orient across a given axis.
	Apply the flipped orientation to a target joint, or the original joint if no target is specified
	@param joint: Joint to flip the orientation of
	@type joint: str
	@param target: Target joitn to apply flipped orientation to.
	@type target: str
	@param axis: Axis to flip orientation across
	@type axis: str
	'''
	# Check joint
	if not isJoint(joint):
		raise Exception('Joint "'+joint+'" is not a valid joint')
	
	# Check target
	if not target: target = joint
	if not isJoint(target):
		raise Exception('Target "'+target+'" is not a valid joint!')
	
	# Get joint matrix
	jMat = glTools.utils.matrix.getMatrix(joint)
	
	# Build flip matrix
	flipMat = None
	if axis == 'x': flipMat = glTools.utils.matrix.buildMatrix(xAxis=(-1,0,0))
	if axis == 'y': flipMat = glTools.utils.matrix.buildMatrix(yAxis=(0,-1,0))
	if axis == 'z': flipMat = glTools.utils.matrix.buildMatrix(zAxis=(0,0,-1))
	
	tMat = OpenMaya.MTransformationMatrix(jMat * flipMat.inverse())
	flipRot = tMat.eulerRotation()
	
	# Set target joint orientation
	radToDeg = 180.0 / math.pi
	mc.setAttr(target+'.jo',flipRot.x*radToDeg,flipRot.y*radToDeg,flipRot.z*radToDeg)
	
	# Return result
	return (flipRot.x*radToDeg,flipRot.y*radToDeg,flipRot.z*radToDeg)

def influenceIndex(joint,skinCluster):
	'''
	'''
	# Check Joint
	if not isJoint(joint):
		raise Exception('"'+joint+'" is not a valid joint!')
	
	# Check SkinCluster
	if not glTools.utils.skinCluster.isSkinCluster(skinCluster):
		raise Exception('"'+skinCluster+'" is not a valid skinCluster!')
	
	# Get skinCluster influence list
	infList = mc.skinCluster(skinCluster,q=True,inf=True)
	if not infList.count(joint):
		raise Exception('Joint "'+joint+'" is not an influence of skinCluster "'+skinCluster+'"')
	infInd = glTools.utils.skinCluster.getInfluenceIndex(skinCluster,joint)

def rebuild(joints, prefix='', suffix='jjj', replaceOriginal=0, orient='xyz'):
	'''
	Regenerate or redraw a list of joints
	
	example:
	 import glTools.utils.joint
	 glTools.utils.joint.rebuild()
	
	keyword:
	 rig
	 joint
	 rebuild
	
	@param joints: List of joints to rebuild
	@type joints: list
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	@param suffix: Name suffix for newly created nodes
	@type suffix: str
	@param replaceOriginal: Replace original joints, or create a new ones.
	@type replaceOriginal: bool
	@param orient: Oriention for new joints. If empty string, keep original orientation
	@type orient: str
	'''
	# Check Joints
	if not joints: 
		raise Exception('Invalid joint list provided!!')
	if not replaceOriginal and not prefix:
		raise Exception('You must provide a valid prefix!!')
	
	# Adjust Hierarchy
	parent = mc.listRelatives(joints[0],p=1)
	if len(parent): mc.select(parent[0])
	else: mc.select(cl=1)
	
	# Iterate through joints
	ind=0
	j=0
	jjj=[]
	for i in joints:
		inc = str(j+1)
		if j < 9: inc = ('0' + inc)
		name = (prefix+'_xx'+inc+'_'+suffix)
		if replaceOriginal: 
			name = 'joint'
		# get current joint info
		pos = mc.xform(i, q=1, ws=1, t=1)
		rad = mc.getAttr(i+'.radius')
		orientList = mc.getAttr(i+'.jointOrient')
		prefAngleList=[]
		prefAngleList.append(mc.getAttr(i+'.preferredAngleX'))
		prefAngleList.append(mc.getAttr(i+'.preferredAngleY'))
		prefAngleList.append(mc.getAttr(i+'.preferredAngleZ'))
		
		if orient=='':
			jjj.append( mc.joint( p=( pos[0], pos[1], pos[2] ), n=name+str(j), o=orientList[0] ) )
		else:
			jjj.append( mc.joint( p=( pos[0], pos[1], pos[2] ), n=name+str(j) ) )
		
		mc.setAttr( ( jjj[j]+ '.radius'), rad )
		mc.setAttr( ( jjj[j]+ '.preferredAngle'), prefAngleList[0], prefAngleList[1], prefAngleList[2], type='double3' )
		ind+=3
		j+=1
	
	# Orient Joints
	if orient: mc.joint( jjj, e=1, oj=orient, sao='xup', ch=1, zso=1)
	
	# Replace original
	if replaceOriginal:
		mc.delete(joints)
		for i in range(len(joints)):
			mc.rename(jjj[i],joints[i])
	
	# Return result
	return jjj

def connectInverseScale(joint,invScaleObj=''):
	'''
	Connect joints inverseScale attribute
	@param joint: Joint to connect inverseScale for
	@type joint: str
	@param invScaleObj: Object whose scale attribute will be connected to joints inverseScale. Defaults to joints parent transform
	@type invScaleObj: str
	'''
	if not mc.objExists(joint): raise Exception('Joint '+joint+' does not exists!')
	if mc.objectType(joint) != 'joint': raise Exception('Object '+joint+' is not a valid joint!')
	if not len(invScaleObj): invScaleObj = mc.listRelatives(joint,p=True)[0]
	# Connect inverseScale
	try: mc.connectAttr(invScaleObj+'.scale',joint+'.inverseScale',f=True)
	except: pass

def curveIntersectJoints(curve,intersectCurveList,jointAtBase=True,jointAtTip=True,useDirection=False,intersectDirection=(0,0,1),prefix=''):
	'''
	Create joints along a curve at the points of intersection with a list of secondary curves
	@param curve: Curve to create joints along
	@type curve: list
	@param intersectCurveList: List of intersection curves
	@type intersectCurveList: list
	@param jointAtBase: Create a joint at the base of the curve
	@type jointAtBase: bool
	@param jointAtTip: Create a joint at the tip of the curve
	@type jointAtTip: bool
	@param useDirection: Project the curves in a specified direction before intersecting
	@type useDirection: bool
	@param intersectDirection: The direction to project the curves before intersecting
	@type intersectDirection: tuple or list
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Check curve
	if not mc.objExists(curve):
		raise Exception('Curve object '+curve+' does not exist!')
	
	# Check intersect curve list
	for i in range(len(intersectCurveList)):
		if not mc.objExists(intersectCurveList[i]):
			raise Exception('Object '+intersectCurveList[i]+' is not a valid curve!')
	
	# Check prefix
	if not prefix: prefix = glTools.utils.stringUtils.stripSuffix(curve)
	
	# Get curve Range
	minU = mc.getAttr(curve+'.minValue')
	maxU = mc.getAttr(curve+'.maxValue')
	
	# Initialize return list
	mc.select(cl=True)
	jointList = []
	
	# Create Base Joint
	if jointAtBase:
		# Get curve point position
		pos = mc.pointOnCurve(curve,pr=minU,p=True)
		# Create joint
		ind = '01'
		jjj = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
		jjj = mc.joint(p=pos,n=jjj)
		jointList.append(jjj)
	
	# Create joints at curve intersections
	for n in range(len(intersectCurveList)):
		# Get string index
		ind = str(n+1+int(jointAtBase))
		if i < (9-int(jointAtBase)): ind = '0'+ind
		# Get curve intersections
		uList = mc.curveIntersect(curve,intersectCurveList[n],ud=useDirection,d=intersectDirection)
		if not uList: continue
		uList = uList.split(' ')
		
		# Create joints
		for u in range(len(uList)/2):
			# Get curve point position
			pos = mc.pointOnCurve(curve,pr=float(uList[u*2]),p=True)
			# Create joint
			jjj = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
			jjj = mc.joint(p=pos,n=jjj)
			jointList.append(jjj)
	
	# Create Tip Joint
	if jointAtTip:
		# Get string index
		ind = str(len(intersectCurveList)+int(jointAtBase)+1)
		if len(intersectCurveList) < (9-int(jointAtBase)): ind = '0'+ind
		# Get curve point position
		pos = mc.pointOnCurve(curve,pr=maxU,p=True)
		# Create joint
		jjj = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
		jjj = mc.joint(p=pos,n=jjj)
		jointList.append(jjj)
	
	# Return result
	return jointList

def group(joint,indexStr='A'):
	'''
	Create a joint buffer transform (joint).
	@param joint: Joint to create buffer group for
	@type joint: str
	@param indexStr: Name index string
	@type indexStr: str
	'''
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get name prefix
	prefix = glTools.utils.stringUtils.stripSuffix(joint)
	
	# Create joint group
	grp = mc.duplicate(joint,po=True,n=prefix+'Con'+indexStr+'_jnt')[0]
	mc.parent(joint,grp)
	
	# Delete user attrs
	udAttrList = mc.listAttr(grp,ud=True)
	if udAttrList:
		for attr in udAttrList: mc.deleteAttr(grp+'.'+attr)
	
	# Set display overrides
	mc.setAttr(joint+'.overrideEnabled',1)
	mc.setAttr(joint+'.overrideLevelOfDetail',0)
	mc.setAttr(grp+'.overrideEnabled',1)
	mc.setAttr(grp+'.overrideLevelOfDetail',0)
	
	# Return result
	return grp

def duplicateChain(startJoint,endJoint,parent='',skipJnt='*_Con*_jnt',search='',replace='',prefix=''):
	'''
	Duplicate a joint chain based on start and end joint conditions.
	@param startJoint: Start joint of chain
	@type startJoint: str
	@param endJoint: End joint of chain
	@type endJoint: str
	@param parent: Parent transform for new chain
	@type parent: str
	'''
	# Check joints
	if not mc.objExists(startJoint):
		raise Exception('Start Joint "'+startJoint+'" does not exist!')
	if not mc.objExists(endJoint):
		raise Exception('End Joint "'+endJoint+'" does not exist!')
	
	# Check name
	rename = True
	if not prefix and not search and not replace:
		rename = False
		
	# Check parent
	if parent and not mc.objExists(parent): parent = ''
	
	# Get joint list
	joints = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Define transform attributes
	transAttr = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
	
	# Duplicate joint
	dupChain = []
	for i in range(len(joints)):
		
		# Naming index
		ind = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		if (i == (len(joints)-1)): ind = 'End'
		
		# Duplicate
		jnt = mc.duplicate(joints[i],po=True)[0]
		
		# Rename joint
		if rename:
			if prefix: jnt = mc.rename(jnt,prefix+ind+'_jnt')
			else: jnt = mc.rename(jnt,joints[i].replace(search,replace))
		
		# Unlock transforms
		for attr in transAttr: mc.setAttr(jnt+'.'+attr,l=False)
		
		# Parent joint
		if not i:
			if not parent: mc.parent(jnt,w=True)
			else: mc.parent(jnt,parent)
		else:
			mc.parent(jnt,dupChain[-1])
			mc.connectAttr(dupChain[-1]+'.scale',jnt+'.inverseScale',f=True)
		
		# Append to list
		dupChain.append(jnt)
	
	# Return Result
	return dupChain


