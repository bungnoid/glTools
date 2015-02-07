import maya.mel as mm
import maya.cmds as mc

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.matrix

def createCurve(pt,start=None,end=None,inc=1):
	'''
	Create motion path curves for the specified list of points.
	@param pt: Object to create motion path from
	@type pt: str
	@param start: Start frame for motion path curve. If None, use first frame from timeline.
	@type start: int or None
	@param end: Start frame for motion path curve. If None, use last frame from timeline.
	@type end: int or None
	@param inc: Frame increment for motion path curve. Values will be clamped to a minimum of 1.
	@type inc: int or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not pt:
		raise Exception('No valid point provided! Unable to create motion path...')
	
	# Check Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	if end < start:
		raise Exception('Invalid time range! Start is greater than end.')
	
	# Check Increment
	if inc < 1: inc = 1
	if inc > (end-start):
		raise Exception('Frame increment is greater than the time range!')
	
	# =====================
	# - Build Motion Path -
	# =====================
	
	hasEndPt = False
	
	# Initialize Motion Paths
	mc.currentTime(start)
	pos = glTools.utils.base.getPosition(pt)
	crv = mc.curve(p=[pos],d=1)
	crv = mc.rename(crv,pt+'_curve')
	
	# Track Paths
	for i in range(start+inc,end+1,inc):
		mc.currentTime(i)
		if i == end: hasEndPt = True
		pos = glTools.utils.base.getPosition(pt)
		mc.curve(crv,a=True,p=pos)
	
	# Ensure End Point
	if not hasEndPt:
		mc.currentTime(end)
		pos = glTools.utils.base.getPosition(pt)
		mc.curve(crv,a=True,p=pos)
		
	# Rebuild Motion Paths
	mc.rebuildCurve(crv,ch=False,rpo=True,rt=0,end=1,kr=2,kcp=True,kep=True)
	
	# ======================
	# - Encode Motion Data -
	# ======================
	
	# Encode Source Object Name
	mc.addAttr(crv,ln='sourceObject',dt='string')
	mc.setAttr(crv+'.sourceObject',pt,type='string')
	
	# Encode Motion Start/End
	mc.addAttr(crv,ln='motionStart')
	mc.setAttr(crv+'.motionStart',start)
	mc.addAttr(crv,ln='motionEnd')
	mc.setAttr(crv+'.motionEnd',end)
	
	# =================
	# - Return Result -
	# =================
	
	return crv

def createCurves(ptList,start=None,end=None,inc=1):
	'''
	Create motion path curves for the specified list of points.
	@param ptList: List of objects to create motion paths from
	@type ptList: list
	@param start: Start frame for motion path curve. If None, use first frame from timeline.
	@type start: int or None
	@param end: Start frame for motion path curve. If None, use last frame from timeline.
	@type end: int or None
	@param inc: Frame increment for motion path curve. Values will be clamped to a minimum of 1.
	@type inc: int or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not ptList:
		raise Exception('No valid point list provided! Unable to creat motion path...')
	
	# Check Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	if end < start:
		raise Exception('Invalid time range! Start is greater than end.')
	
	# Check Increment
	if inc < 1: inc = 1
	if inc > (end-start):
		raise Exception('Frame increment is greater than the time range!')
	
	# ======================
	# - Build Motion Paths -
	# ======================
	
	hasEndPt = False
	
	# Initialize Motion Paths
	crvList = []
	mc.currentTime(start)
	for pt in ptList:
		
		# Create Motion Path Curves
		pos = glTools.utils.base.getPosition(pt)
		crv = mc.curve(p=[pos],d=1)
		crv = mc.rename(crv,pt+'_curve')
		crvList.append(crv)
		
		# Encode Source Object Name
		mc.addAttr(crv,ln='sourceObject',dt='string')
		mc.setAttr(crv+'.sourceObject',pt,type='string')
		
		# Encode Motion Start/End
		mc.addAttr(crv,ln='motionStart')
		mc.setAttr(crv+'.motionStart',start)
		mc.addAttr(crv,ln='motionEnd')
		mc.setAttr(crv+'.motionEnd',end)
	
	# Track Paths
	for i in range(start+inc,end+1,inc):
		mc.currentTime(i)
		if i == end: hasEndPt = True
		for n in range(len(ptList)):
			pos = glTools.utils.base.getPosition(ptList[n])
			mc.curve(crvList[n],a=True,p=pos)
	
	# Ensure End Point
	if not hasEndPt:
		mc.currentTime(end)
		for n in range(len(ptList)):
			pos = glTools.utils.base.getPosition(ptList[n])
			mc.curve(crvList[n],a=True,p=pos)
		
	# Rebuild Motion Paths
	for crv in crvList:
		mc.rebuildCurve(crv,ch=False,rpo=True,rt=0,end=1,kr=2,kcp=True,kep=True)
	
	# =================
	# - Return Result -
	# =================
	
	return crvList

def createAverageCurve(xformList,start=None,end=None,inc=1,prefix=''):
	'''
	Create a motion path curve for the specified list of transforms.
	The resulting curves will track the average positions of all specified transforms.
	@param xformList: Transforms to create average motion math curve from
	@type xformList: list
	@param start: Start frame for motion path curve. If None, use first frame from timeline.
	@type start: int or None
	@param end: Start frame for motion path curve. If None, use last frame from timeline.
	@type end: int or None
	@param inc: Frame increment for motion path curve. Values will be clamped to a minimum of 1.
	@type inc: int or None
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Xform list
	xformList = mc.ls(xformList,transforms=True) or []
	if not xformList: raise Exception('No valid transforms specified!')
	
	# Prefix
	if not prefix: prefix = 'motionPath#'
	
	# ======================
	# - Create Motion Path -
	# ======================
	
	# Create Average Locator
	loc = mc.group(em=True,n=prefix)
	mc.pointConstraint(xformList,loc,mo=False)
	
	# Create Motion Path
	crv = createCurve(loc,start,end,inc)
	
	# Cleanup
	mc.delete(loc)
	
	# =================
	# - Return Result -
	# =================
	
	return crv

def motionPathToKeys(path,obj=None,start=None,end=None):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Path
	if not mc.objExists(path):
		raise Exception('Motion path curve "'+path+'" does not exist!')
	if not glTools.utils.curve.isCurve(path):
		raise Exception('Motion path curve "'+path+'" is not a valid curve!')
	
	# Check Keyframe Object
	if not obj:
		if not mc.attributeQuery('sourceObject',n=path,ex=True):
			raise Exception('No keyframe object specified!')
		else:
			obj = mc.getAttr(path+'.sourceObject')
			if not mc.objExists(path):
				raise Exception('Motion path curve "'+path+'" does not exist!')
	
	# Check Start/End
	if start == None:
		if mc.attributeQuery('motionStart',n=path,ex=True):
			start = mc.getAttr(path+'.motionStart')
		else:
			start = mc.playbackOptions(q=True,min=True)
	if end == None:
		if mc.attributeQuery('motionEnd',n=path,ex=True):
			end = mc.getAttr(path+'.motionEnd')
		else:
			end = mc.playbackOptions(q=True,max=True)
	
	# ==================================
	# - Set Keyframes from Motion Path -
	# ==================================
	
	# Get Target Space (Matrix)
	objMatrix = glTools.utils.matrix.fromList(mc.getAttr(obj+'.parentMatrix'))
	
	for i in range(start,end):
		
		# ===
		print i
		

def motionPathAimRotation(path,obj,upVector=None,start=None,end=None):
	'''
	'''
	pass

def motionPathResample(path,startId,endId,method='linear'):
	'''
	'''
	pass
