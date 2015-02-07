import maya.cmds as mc

import maya.OpenMaya as OpenMaya

import glTools.utils.base
import glTools.utils.channelState
import glTools.utils.mathUtils
import glTools.utils.matrix
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

def isEndJoint(joint):
	'''
	Check if the specified joint is an end joint
	@param joint: Joint to check
	@type joint: str
	'''
	# Check Joint
	if not isJoint(joint):
		raise Exception('Object "'+joint+'" is not a valid joint!')
	
	# Check Child Joints
	jointDescendants = mc.ls(mc.listRelatives(joint,ad=True) or [],type='joint')
	if not jointDescendants: return True
	else: return False

def getEndJoint(startJoint,includeTransforms=False):
	'''
	Find the end joint of a chain from the specified start joint.
	@param joint: Joint to find end joint from
	@type joint: str
	@param includeTransforms: Include non-joint transforms in the chain.
	@type includeTransforms: bool
	'''
	# Check Start Joint
	if not mc.objExists(startJoint):
		raise Exception('Start Joint "'+startJoint+'" does not exist!')
	
	# Find End Joint
	endJoint = None
	nextJoint = startJoint
	while(nextJoint):
		
		# Get Child Joints
		childList = mc.listRelatives(nextJoint,c=True) or []
		childJoints = mc.ls(childList,type='joint') or []
		if includeTransforms:
			childJoints = list(set(childJoints + mc.ls(childList,transforms=True) or []))
		
		# Check End Joint
		if childJoints:
			nextJoint = childJoints[0]
		else:
			endJoint = nextJoint
			nextJoint = None
	
	# Return Result	
	return endJoint

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
	# Check Single Joint
	if startJoint == endJoint: return [startJoint]
	
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
	# Check Joint
	if not mc.objExists(joint): raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get Child Joints
	cJoints = mc.ls(mc.listRelatives(joint,c=True,pa=True) or [],type='joint')
	if not cJoints: return 0.0
	
	# Get Length
	maxLength = 0.0
	for cJoint in cJoints:
		pt1 = glTools.utils.base.getPosition(joint)
		pt2 = glTools.utils.base.getPosition(cJoint)
		offset = glTools.utils.mathUtils.offsetVector(pt1,pt2)
		length = glTools.utils.mathUtils.mag(offset)
		if length > maxLength: maxLength = length
	
	# Return Result
	return maxLength

def group(joint,indexStr='A'):
	'''
	Create a joint group (buffer) transform (joint).
	@param joint: Joint to create buffer group for
	@type joint: str
	@param indexStr: Name index string
	@type indexStr: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Check Index String
	if not indexStr:
		result = mc.promptDialog(	title='Index String',
									message='Joint Group Index:',
									text='A',
									button=['Create', 'Cancel'],
									defaultButton='Create',
									cancelButton='Cancel',
									dismissString='Cancel'	)
	
		if result == 'Create':
			indexStr = mc.promptDialog(q=True,text=True)
		else:
			print 'User canceled joint group creation...'
			return
	
	# Get Name Prefix
	prefix = glTools.utils.stringUtils.stripSuffix(joint)
	
	# ======================
	# - Create Joint Group -
	# ======================
	
	grp = mc.duplicate(joint,po=True,n=prefix+'Con'+indexStr+'_jnt')[0]
	mc.parent(joint,grp)
	
	# Set Joint Radius
	if mc.getAttr(grp+'.radius',se=True):
		try: mc.setAttr(grp+'.radius',0)
		except: pass
	
	# Connect Inverse Scale
	inverseScaleCon = mc.listConnections(joint+'.inverseScale',s=True,d=False)
	if not inverseScaleCon: inverseScaleCon = []
	if not inverseScaleCon.count(grp):
		try: mc.connectAttr(grp+'.scale',joint+'.inverseScale',f=True)
		except: pass
	
	# Delete User Attrs
	udAttrList = mc.listAttr(grp,ud=True)
	if udAttrList:
		for attr in udAttrList:
			if mc.objExists(grp+'.'+attr):
				mc.setAttr(grp+'.'+attr,l=False)
				mc.deleteAttr(grp+'.'+attr)
	
	# Set Display Overrides
	glTools.utils.base.displayOverride(joint,overrideEnable=1,overrideLOD=0)
	glTools.utils.base.displayOverride(grp,overrideEnable=1,overrideDisplay=2,overrideLOD=1)
	
	# =================
	# - Return Result -
	# =================
	
	return grp

def setDrawStyle(joints,drawStyle='bone'):
	'''
	Set joint draw style for the specified joints.
	@param joints: List of joints to set draw style for
	@type joints: list
	@param drawStyle: Draw style to apply to specified joints. Accepts "bone", "box" and "none"
	@type drawStyle: str
	'''
	# Check Joints
	if not joints:
		raise Exception('No joints specified!')
	
	# Check Draw Style
	drawStyle = drawStyle.lower()
	if not drawStyle in ['bone','box','none']:
		raise Exception('Invalid drawt style ("'+drawStyle+'")! Accepted values are "bone", "box" and "none"...')
	
	# For Each Joint
	for jnt in joints:
		
		# Check Joint
		if not isJoint(jnt): continue
		
		# Bone
		if drawStyle == 'bone': mc.setAttr(jnt+'.drawStyle',0)
		# Box
		if drawStyle == 'box': mc.setAttr(jnt+'.drawStyle',1)
		# None
		if drawStyle == 'none': mc.setAttr(jnt+'.drawStyle',2)
	
	# Return Result
	return joints

def duplicateJoint(joint,name=None):
	'''
	Duplicate a specified joint.
	@param joint: Joint to duplicate
	@type joint: str
	@param name: New name for duplicated joint. If None, leave as default.
	@type name: str or None
	'''
	# Check Joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	if not name: name = joint+'_dup'
	if mc.objExists(str(name)):
		raise Exception('Joint "'+name+'" already exist!')
	
	# Duplicate Joint
	dupJoint = mc.duplicate(joint,po=True)[0]
	if name: dupJoint = mc.rename(dupJoint,name)
	
	# Unlock Transforms
	for at in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v','radius']:
		mc.setAttr(dupJoint+'.'+at,l=False,cb=True)
	
	# Return Result
	return dupJoint

def duplicateChain(	startJoint,
					endJoint	= None,
					parent		= None,
					skipJnt		= '*_Con*_jnt',
					prefix		= None	):
	'''
	Duplicate a joint chain based on start and end joint.
	@param startJoint: Start joint of chain
	@type startJoint: str
	@param endJoint: End joint of chain. If None, use end of current chain.
	@type endJoint: str
	@param parent: Parent transform for new chain.
	@type parent: str or None
	@param skipJnt: Skip joints in chain that match name pattern.
	@type skipJnt: str or None
	@param prefix: New name prefix.
	@type prefix: str or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Joints
	if not mc.objExists(startJoint):
		raise Exception('Start Joint "'+startJoint+'" does not exist!')
	if endJoint and not mc.objExists(str(endJoint)):
		raise Exception('End Joint "'+endJoint+'" does not exist!')
	
	# Check Parent
	if parent:
		if not mc.objExists(parent):
			raise Exception('Specified parent transform "'+parent+'" does not exist!')
		if not glTools.utils.transform.isTransform(parent):
			raise Exception('Parent object "'+parent+'" is not a valid transform!')
	
	# =========================
	# - Duplicate Joint Chain -
	# =========================
	
	# Get Full Joint List
	if not endJoint: endJoint = getEndJoint(startJoint)
	joints = glTools.utils.joint.getJointList(startJoint,endJoint)
	
	# Get List of Skip Joints
	skipJoints = mc.ls(skipJnt) if skipJnt else []
	
	dupChain = []
	for i in range(len(joints)):
		
		# Skip Joints
		if joints[i] in skipJoints: continue
		
		# Rename Joint
		name = None
		if prefix:
			ind = glTools.utils.stringUtils.alphaIndex(i,upper=True)
			if (i == (len(joints)-1)): ind = 'End'
			name = prefix+ind+'_jnt'
			
		# Duplicate Joint
		jnt = duplicateJoint(joints[i],name)
		
		# Parent Joint
		if not i:
			if not parent:
				if mc.listRelatives(jnt,p=True):
					try: mc.parent(jnt,w=True)
					except: pass
			else:
				try: mc.parent(jnt,parent)
				except: pass
		else:
			try:
				mc.parent(jnt,dupChain[-1])
				if not mc.isConnected(dupChain[-1]+'.scale',jnt+'.inverseScale'):
					mc.connectAttr(dupChain[-1]+'.scale',jnt+'.inverseScale',f=True)
			except Exception, e:
				raise Exception('Error duplicating joint chain! Exception Msg: '+str(e))
			
		# Append to list
		dupChain.append(jnt)
	
	# =================
	# - Return Result -
	# =================
	
	return dupChain

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
	Flip the specified joint orient across a given axis.
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
	
	# Get Joint Matrix
	jMat = glTools.utils.matrix.getMatrix(joint)
	
	# Build flip matrix
	flipMat = None
	if axis == 'x': flipMat = glTools.utils.matrix.buildMatrix(xAxis=(-1,0,0))
	if axis == 'y': flipMat = glTools.utils.matrix.buildMatrix(yAxis=(0,-1,0))
	if axis == 'z': flipMat = glTools.utils.matrix.buildMatrix(zAxis=(0,0,-1))
	
	# Get Matrix Rotation
	tMat = OpenMaya.MTransformationMatrix(jMat * flipMat.inverse())
	flipRot = tMat.eulerRotation()
	
	# Set Target Joint Orientation
	radToDeg = 180.0 / math.pi
	mc.setAttr(target+'.jo',flipRot.x*radToDeg,flipRot.y*radToDeg,flipRot.z*radToDeg)
	
	# Return Result
	return (flipRot.x*radToDeg,flipRot.y*radToDeg,flipRot.z*radToDeg)

def mirrorOrient(joint,rollAxis):
	'''
	Reorient joint to replicate mirrored behaviour
	@param joint: Joint to mirror orientation for
	@type joint: str
	@param rollAxis: Axis to maintain orientation for
	@type rollAxis: str
	'''
	# Check Joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Check Roll Axis
	if not ['x','y','z'].count(rollAxis):
		raise Exception('Invalid roll axis "'+rollAxis+'"!')
	
	# UnParent Children
	childList = mc.listRelatives(joint,c=True)
	if childList: mc.parent(childList,w=True)
	
	# ReOrient Joint
	rt = [0,0,0]
	axisDict = {'x':0,'y':1,'z':2}
	rt[axisDict[rollAxis]] = 180
	mc.setAttr(joint+'.r',*rt)
	mc.makeIdentity(joint,apply=True,t=True,r=True,s=True)
	
	# Reparent children
	if childList: mc.parent(childList,joint)

def zeroOrient(joint):
	'''
	Zero joint orient of specified joint.
	@param joint: Joint to zero orientation for
	@type joint: str
	'''
	# Check joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Zero Joint Orient
	mc.setAttr(joint+'.jointOrient',0,0,0)

def connectInverseScale(joint,invScaleObj=None,force=False):
	'''
	Connect joints inverseScale attribute
	@param joint: Joint to connect inverseScale for
	@type joint: str
	@param invScaleObj: Object to connect to joint inverseScale attribute. If None, use joint parent.
	@type invScaleObj: str or None
	'''
	# Check Joint
	if not isJoint(joint):
		raise Exception('Object '+joint+' is not a valid joint!')
	
	# Check Inverse Scale Object
	if not invScaleObj:
		
		# Get Joint Parent
		parent = mc.listRelatives(joint,p=True) or []
		if parent and force: parent = mc.ls(parent, type='joint') or []
		if not parent:
			print('No source object specified and no parent joint found for joint "'+joint+'"! Skipping...')
			return None
		
		# Set Inverse Scale Object
		invScaleObj = parent[0]
	
	# Connect inverseScale
	invScaleCon = mc.listConnections(joint+'.inverseScale',s=True,d=False) or []
	if not invScaleObj in invScaleCon:
		try: mc.connectAttr(invScaleObj+'.scale',joint+'.inverseScale',f=True)
		except Exception, e: print('Error connecting "'+invScaleObj+'.scale" to "'+joint+'.inverseScale"! Exception msg: '+str(e))
	
	# Return Result
	return invScaleObj+'.scale'

def curveIntersectJoints(	curve,
							intersectCurveList,
							jointAtBase=True,
							jointAtTip=True,
							useDirection=False,
							intersectDirection=(0,0,1),
							prefix=''	):
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
		jnt = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
		jnt = mc.joint(p=pos,n=jnt)
		jointList.append(jnt)
	
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
			jnt = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
			jnt = mc.joint(p=pos,n=jnt)
			jointList.append(jnt)
	
	# Create Tip Joint
	if jointAtTip:
		# Get string index
		ind = str(len(intersectCurveList)+int(jointAtBase)+1)
		if len(intersectCurveList) < (9-int(jointAtBase)): ind = '0'+ind
		# Get curve point position
		pos = mc.pointOnCurve(curve,pr=maxU,p=True)
		# Create joint
		jnt = prefix+nameUtil.delineator+nameUtil.subPart['joint']+ind+nameUtil.delineator+nameUtil.node['joint']
		jnt = mc.joint(p=pos,n=jnt)
		jointList.append(jnt)
	
	# Return result
	return jointList

