import maya.cmds as mc

import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mathUtils

def build(attachments=4,sections=9,sectionsSpans=8,minRadius=0.0,maxRadius=1.0,startPt=[0.0,0.0,6.0],endPt=[0.0,0.0,-6.0],prefix='muscle'):
	'''
	Build muscle primitive based on the input argument values between the start and end points
	
	@param attachments: Number of attachments points
	@type attachments: int
	@param sections: Number of profile curves
	@type sections: int
	@param sectionSpans: Number of spans for profile curves
	@type sectionSpans: int
	@param minRadius: Minimum radius for muscle profile curves
	@type minRadius: float
	@param maxRadius: Maximum radius for muscle profile curves
	@type maxRadius: float
	@param startPt: Start point of the muscle
	@type startPt: list
	@param endPt: End point of the muscle
	@type endPt: list
	@param prefix: Name prefix for muscle primitive
	@type prefix: str
	
	@return: Muscle mesh
	@returnType: str
	'''
	# Checks
	
	# Get start, end and distance values
	startPoint = glTools.utils.base.getMPoint(startPt)
	endPoint = glTools.utils.base.getMPoint(endPt)
	startEndOffset = endPoint - startPoint
	startEndDist = startEndOffset.length()
	startEndInc = startEndDist / (attachments - 1)
	
	# Calculate attachment point positions
	attachPoints = []
	for i in range(attachments):
		attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * i))
		# Start Tangent
		if not i:
			attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * 0.5))
		# End Tangent
		if i == (attachments-2):
			attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * (i+0.5)))
	attachPts = [[pt.x,pt.y,pt.z] for pt in attachPoints]
	# Resize attachments value to accomodate for tangent points
	attachments = len(attachPts)
	
	# ------------------------
	# - Build base hierarchy -
	# ------------------------
	
	# Create groups
	muscleGrp = mc.createNode('transform',n=prefix+'_group')
	muscleAttachGrp = mc.createNode('transform',n=prefix+'_attachment_group')
	muscleProfileGrp = mc.createNode('transform',n=prefix+'_profile_group')
	
	# Build hierarchy
	mc.parent(muscleAttachGrp,muscleGrp)
	mc.parent(muscleProfileGrp,muscleGrp)
	
	
	# ----------------------
	# - Build Muscle Curve -
	# ----------------------
	
	# Build muscle base curve
	muscleCurve = mc.rename(mc.curve(d=1,p=attachPts,k=range(len(attachPts))),prefix+'_curve')
	mc.rebuildCurve(muscleCurve,ch=0,rpo=1,rt=0,end=1,kr=0,kcp=1,kep=1,kt=1,s=0,d=1)
	muscleCurveShape = mc.listRelatives(muscleCurve,s=True)[0]
	mc.parent(muscleCurve,muscleAttachGrp)
	
	# Add muscle attributes
	mc.addAttr(muscleCurve,ln='muscle',at='message')
	mc.addAttr(muscleCurve,ln='muscleObjectType',dt='string')
	mc.setAttr(muscleCurve+'.muscleObjectType','spline',type='string',l=True)
	
	# Connect curve to attachment locators
	attachLocators = glTools.utils.curve.locatorCurve(muscleCurve,locatorScale=0.1,freeze=False,prefix=prefix)
	# Rename attachment locators and add muscle attibutes
	for i in range(len(attachLocators)):
		# Add muscle attibutes
		mc.addAttr(attachLocators[i],ln='muscle',at='message')
		mc.addAttr(attachLocators[i],ln='muscleObjectType',dt='string')
		mc.setAttr(attachLocators[i]+'.muscleObjectType','attachment',type='string',l=True)
		
		# Rename attachment locators
		if not i:
			attachLocators[i] = mc.rename(attachLocators[i],prefix+'_attachStart_locator')
		elif i == 1:
			attachLocators[i] = mc.rename(attachLocators[i],prefix+'_attachStartTangent_locator')
			mc.setAttr(attachLocators[i]+'.muscleObjectType',l=False)
			mc.setAttr(attachLocators[i]+'.muscleObjectType','attachmentTangent',type='string',l=True)
		elif i == (attachments-2):
			attachLocators[i] = mc.rename(attachLocators[i],prefix+'_attachEndTangent_locator')
			mc.setAttr(attachLocators[i]+'.muscleObjectType',l=False)
			mc.setAttr(attachLocators[i]+'.muscleObjectType','attachmentTangent',type='string',l=True)
		elif i == (attachments-1):
			attachLocators[i] = mc.rename(attachLocators[i],prefix+'_attachEnd_locator')
		else:
			attachLocators[i] = mc.rename(attachLocators[i],prefix+'_attachMid'+str(i-1)+'_locator')
	
	# Group attachment locators
	attachLocGroup = []
	[attachLocGroup.append(glTools.utils.base.group(loc)) for loc in attachLocators]
	mc.parent(attachLocGroup,muscleAttachGrp)
	
	# Create spline rebuild curve
	splineCurve = mc.rebuildCurve(muscleCurve,ch=1,rpo=0,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=5,d=3)
	splineRebuild = mc.rename(splineCurve[1],prefix+'_spline_rebuildCurve')
	splineCurveShape = mc.rename(mc.listRelatives(splineCurve[0],s=True)[0],prefix+'_spline_curveShape')
	mc.parent(splineCurveShape,muscleCurve,s=True,r=True)
	mc.delete(splineCurve[0])
	
	# Create tangent rebuild curve
	tangentCurve = mc.rebuildCurve(muscleCurve,ch=1,rpo=0,rt=0,end=1,kr=0,kcp=0,kep=1,kt=1,s=2,d=3)
	tangentRebuild = mc.rename(tangentCurve[1],prefix+'_tangent_rebuildCurve')
	tangentCurveShape = mc.rename(mc.listRelatives(tangentCurve[0],s=True)[0],prefix+'_tangent_curveShape')
	mc.parent(tangentCurveShape,muscleCurve,s=True,r=True)
	mc.delete(tangentCurve[0])
	
	# Create curve visibility attributes
	mc.addAttr(muscleCurve,ln='attachment',at='enum',en='Off:On:')
	mc.setAttr(muscleCurve+'.attachment',k=False,cb=True)
	mc.connectAttr(muscleCurve+'.attachment',muscleCurveShape+'.v')
	
	mc.addAttr(muscleCurve,ln='spline',at='enum',en='Off:On:')
	mc.setAttr(muscleCurve+'.spline',k=False,cb=True)
	mc.connectAttr(muscleCurve+'.spline',splineCurveShape+'.v')
	
	mc.addAttr(muscleCurve,ln='tangent',at='enum',en='Off:On:')
	mc.setAttr(muscleCurve+'.tangent',k=False,cb=True)
	mc.connectAttr(muscleCurve+'.tangent',tangentCurveShape+'.v')
	
	mc.setAttr(muscleCurve+'.attachment',0)
	mc.setAttr(muscleCurve+'.spline',1)
	mc.setAttr(muscleCurve+'.tangent',1)
	
	# Setup start tangent toggle
	mc.addAttr(attachLocators[0],ln='tangentControl',at='enum',en='Off:On:')
	mc.setAttr(attachLocators[0]+'.tangentControl',k=False,cb=True)
	mc.connectAttr(attachLocators[0]+'.tangentControl',attachLocGroup[1]+'.v',f=True)
	startTangentBlend = mc.createNode('blendColors',n=prefix+'_startTangent_blendColors')
	mc.connectAttr(attachLocators[1]+'.worldPosition[0]',startTangentBlend+'.color1',f=True)
	mc.connectAttr(attachLocators[2]+'.worldPosition[0]',startTangentBlend+'.color2',f=True)
	mc.connectAttr(attachLocators[0]+'.tangentControl',startTangentBlend+'.blender',f=True)
	mc.connectAttr(startTangentBlend+'.output',muscleCurve+'.controlPoints[1]',f=True)
	# Setup end tangent toggle
	mc.addAttr(attachLocators[-1],ln='tangentControl',at='enum',en='Off:On:')
	mc.setAttr(attachLocators[-1]+'.tangentControl',k=False,cb=True)
	mc.connectAttr(attachLocators[-1]+'.tangentControl',attachLocGroup[-2]+'.v',f=True)
	endTangentBlend = mc.createNode('blendColors',n=prefix+'_endTangent_blendColors')
	mc.connectAttr(attachLocators[-2]+'.worldPosition[0]',endTangentBlend+'.color1',f=True)
	mc.connectAttr(attachLocators[-3]+'.worldPosition[0]',endTangentBlend+'.color2',f=True)
	mc.connectAttr(attachLocators[-1]+'.tangentControl',endTangentBlend+'.blender',f=True)
	mc.connectAttr(endTangentBlend+'.output',muscleCurve+'.controlPoints['+str(attachments-2)+']',f=True)
	
	
	# -------------------------------
	# - Build Muscle Profile Curves -
	# -------------------------------
	
	# Initialize profile list
	profileList = []
	profileGrpList = []
	profileFollowList = []
	
	# Iterate through profiles
	profileInc = 1.0/(sections-1)
	for i in range(sections):
		
		# Create profile curve
		profile = mc.circle(ch=0,c=(0,0,0),nr=(0,0,1),sw=360,r=1,d=3,ut=0,tol=0.01,s=sectionsSpans,n=prefix+'_profile'+str(i+1)+'_curve')[0]
		profileList.append(profile)
		
		# Add muscle profile attribute
		mc.addAttr(profile,ln='muscle',at='message')
		mc.addAttr(profile,ln='muscleObjectType',dt='string')
		mc.setAttr(profile+'.muscleObjectType','profile',type='string',l=True)
		
		# Group profile curve
		profileGrp = glTools.utils.base.group(profile)
		profileGrpList.append(profileGrp)
		
		# Skip start/end profiles
		if (not i) or (i ==(sections-1)): continue
		
		# Add curve parameter attribute
		mc.addAttr(profile,ln='uValue',min=0.0,max=1.0,dv=profileInc*i)
		mc.setAttr(profile+'.uValue',k=False,cb=True)
		
		# Create profile pointOnCurveInfo node
		profileCurveInfo = mc.createNode('pointOnCurveInfo',n=prefix+'_profile'+str(i+1)+'_pointOnCurveInfo')
		
		# Attach profile group to point on muscle spline curve
		mc.connectAttr(splineCurveShape+'.worldSpace[0]',profileCurveInfo+'.inputCurve',f=True)
		mc.connectAttr(profile+'.uValue',profileCurveInfo+'.parameter',f=True)
		mc.connectAttr(profileCurveInfo+'.position',profileGrp+'.translate',f=True)
		
		# Create profile follow group
		profileFollowGrp = mc.createNode('transform',n=prefix+'_profileFollow'+str(i+1)+'_group')
		profileFollowList.append(profileFollowGrp)
		mc.connectAttr(profileCurveInfo+'.position',profileFollowGrp+'.translate',f=True)
	
	mc.parent(profileGrpList,muscleProfileGrp)
	mc.parent(profileFollowList,muscleProfileGrp)
	
	
	# ------------------------------------
	# - Create profile orientation setup -
	# ------------------------------------
	
	oddProfile = sections % 2
	intProfile = int(sections * 0.5)
	midProfile = intProfile + oddProfile
	intIncrement = 1.0/intProfile
	
	# Create mid profile orientConstraint
	if oddProfile:
		midPointObject = profileFollowList[midProfile-2]
	else:
		midPointObject = mc.createNode('transform',n=prefix+'_midPointFollow_group')
		mc.parent(midPointObject,muscleProfileGrp)
	midOrientCon = mc.orientConstraint([attachLocators[0],attachLocators[-1]],midPointObject,n=prefix+'_midPoint_orientConstraint')
	
	# Create intermediate profile orientConstraints
	for i in range(intProfile):
		
		# Skip start/end profiles
		if not i: continue
		
		# Create orientConstraints
		startMidOriCon = mc.orientConstraint([attachLocators[0],midPointObject],profileFollowList[i-1])[0]
		endMidOriCon = mc.orientConstraint([attachLocators[-1],midPointObject],profileFollowList[-(i)])[0]
		startMidOriWt = mc.orientConstraint(startMidOriCon,q=True,weightAliasList=True)
		endMidOriWt = mc.orientConstraint(endMidOriCon,q=True,weightAliasList=True)
		
		# Set constraint weights
		mc.setAttr(startMidOriCon+'.'+startMidOriWt[0],1.0-(intIncrement*i))
		mc.setAttr(startMidOriCon+'.'+startMidOriWt[1],(intIncrement*i))
		mc.setAttr(endMidOriCon+'.'+endMidOriWt[0],1.0-(intIncrement*i))
		mc.setAttr(endMidOriCon+'.'+endMidOriWt[1],(intIncrement*i))
		
		# Add constraint weight attribute to profile
		mc.addAttr(profileList[i],ln='twist',min=0,max=1,dv=1.0-(intIncrement*i),k=True)
		mc.addAttr(profileList[-(i+1)],ln='twist',min=0,max=1,dv=1.0-(intIncrement*i),k=True)
		
		# Connect twist attribite to constraint weights
		startMidOriRev = mc.createNode('reverse',n=profileList[i].replace('_curve','_reverse'))
		endMidOriRev = mc.createNode('reverse',n=profileList[-(i+1)].replace('_curve','_reverse'))
		mc.connectAttr(profileList[i]+'.twist',startMidOriRev+'.inputX',f=True)
		mc.connectAttr(profileList[i]+'.twist',startMidOriCon+'.'+startMidOriWt[0],f=True)
		mc.connectAttr(startMidOriRev+'.outputX',startMidOriCon+'.'+startMidOriWt[1],f=True)
		mc.connectAttr(profileList[-(i+1)]+'.twist',endMidOriRev+'.inputX',f=True)
		mc.connectAttr(profileList[-(i+1)]+'.twist',endMidOriCon+'.'+endMidOriWt[0],f=True)
		mc.connectAttr(endMidOriRev+'.outputX',endMidOriCon+'.'+endMidOriWt[1],f=True)
	
	# Create Profile tangent constraints
	tangentConList = []
	for i in range(len(profileGrpList)):
		# Determine world up object
		if not i:
			# start profile
			worldUpObject = attachLocators[0]
		elif i == (len(profileGrpList)-1):
			# end profile
			worldUpObject = attachLocators[-1]
		else:
			worldUpObject = profileFollowList[i-1]
		# Create constraint
		tangentCon = mc.tangentConstraint(tangentCurveShape,profileGrpList[i],aim=[0,0,-1],u=[0,1,0],wu=[0,1,0],wut='objectrotation',wuo=worldUpObject)
		tangentConList.append(tangentCon)
	
	# -----------------------------
	# - Set profile radius values -
	# -----------------------------
	
	# Set default profile radius values
	radiusList = glTools.utils.mathUtils.distributeValue(midProfile,rangeStart=minRadius,rangeEnd=maxRadius)
	radiusList = [glTools.utils.mathUtils.smoothStep(i,minRadius,maxRadius,0.5) for i in radiusList]
	for i in range(midProfile):
		mc.setAttr(profileList[i]+'.scale',radiusList[i],radiusList[i],radiusList[i])
		mc.setAttr(profileList[-(i+1)]+'.scale',radiusList[i],radiusList[i],radiusList[i])
	
	# ----------------------------
	# - Generate Muscle Geometry -
	# ----------------------------
	
	# Loft mesh between profile curves
	loft = mc.loft(profileList,u=0,c=0,d=3,ch=1,po=1)
	muscleMesh = mc.rename(loft[0],prefix)
	muscleLoft = mc.rename(loft[1],prefix+'_loft')
	muscleTess = mc.listConnections(muscleLoft+'.outputSurface',s=False,d=True,type='nurbsTessellate')[0]
	muscleTess = mc.rename(muscleTess,prefix+'_nurbsTessellate')
	mc.parent(muscleMesh,muscleGrp)
	
	# Set nurbsTessellate settings
	mc.setAttr(muscleTess+'.format',2)
	mc.setAttr(muscleTess+'.polygonType',1)
	mc.setAttr(muscleTess+'.uType',1)
	mc.setAttr(muscleTess+'.vType',1)
	mc.setAttr(muscleTess+'.uNumber',20)
	mc.setAttr(muscleTess+'.vNumber',10)
	
	# Add muscle mesh attributes
	mc.addAttr(muscleMesh,ln='precision',at='long',min=1,dv=5)
	mc.setAttr(muscleMesh+'.precision',k=False,cb=True)
	mc.addAttr(muscleMesh,ln='tangentPrecision',at='long',min=1,dv=2)
	mc.setAttr(muscleMesh+'.tangentPrecision',k=False,cb=True)
	
	mc.addAttr(muscleMesh,ln='uDivisions',at='long',min=4,dv=20)
	mc.setAttr(muscleMesh+'.uDivisions',k=False,cb=True)
	mc.addAttr(muscleMesh,ln='vDivisions',at='long',min=3,dv=10)
	mc.setAttr(muscleMesh+'.vDivisions',k=False,cb=True)
	
	mc.addAttr(muscleMesh,ln='restLength',at='float',min=0,dv=startEndDist)
	mc.setAttr(muscleMesh+'.restLength',k=False,cb=True)
	mc.addAttr(muscleMesh,ln='currentLength',at='float',min=0,dv=startEndDist)
	mc.setAttr(muscleMesh+'.currentLength',k=True)
	mc.addAttr(muscleMesh,ln='lengthScale',at='float',min=0,dv=1)
	mc.setAttr(muscleMesh+'.lengthScale',k=True)
	
	mc.addAttr(muscleMesh,ln='muscleMessage',at='message')
	mc.addAttr(muscleMesh,ln='muscleSpline',at='message')
	mc.addAttr(muscleMesh,ln='attachment',at='message',m=True)
	mc.addAttr(muscleMesh,ln='profile',at='message',m=True)
	
	mc.addAttr(muscleMesh,ln='muscleObjectType',dt='string')
	mc.setAttr(muscleMesh+'.muscleObjectType','geo',type='string',l=True)
	
	# Connect muscle mesh attributes
	mc.connectAttr(muscleCurve+'.message',muscleMesh+'.muscleSpline',f=True)
	for i in range(len(attachLocators)):
		mc.connectAttr(attachLocators[i]+'.message',muscleMesh+'.attachment['+str(i)+']',f=True)
		mc.connectAttr(muscleMesh+'.message',attachLocators[i]+'.muscle',f=True)
	for i in range(len(profileList)):
		mc.connectAttr(profileList[i]+'.message',muscleMesh+'.profile['+str(i)+']',f=True)
		mc.connectAttr(muscleMesh+'.message',profileList[i]+'.muscle',f=True)
	
	# Connect muscle mesh attributes to curve rebuild settings
	mc.connectAttr(muscleMesh+'.precision',splineRebuild+'.spans',f=True)
	musclePreCondition = mc.createNode('condition',n=prefix+'_precision_condition')
	mc.setAttr(musclePreCondition+'.operation',4) # Less Than
	mc.connectAttr(muscleMesh+'.precision',musclePreCondition+'.firstTerm',f=True)
	mc.connectAttr(muscleMesh+'.tangentPrecision',musclePreCondition+'.secondTerm',f=True)
	mc.connectAttr(muscleMesh+'.precision',musclePreCondition+'.colorIfTrueR',f=True)
	mc.connectAttr(muscleMesh+'.tangentPrecision',musclePreCondition+'.colorIfFalseR',f=True)
	mc.connectAttr(musclePreCondition+'.outColorR',tangentRebuild+'.spans',f=True)
	
	# Connect musle mesh attributes to nurbsTessellate settings
	mc.connectAttr(muscleMesh+'.uDivisions',muscleTess+'.uNumber',f=True)
	mc.connectAttr(muscleMesh+'.vDivisions',muscleTess+'.vNumber',f=True)
	
	# Setup length calculation
	muscleLenCurveInfo = mc.createNode('curveInfo',n=prefix+'_length_curveInfo')
	mc.connectAttr(splineCurveShape+'.worldSpace[0]',muscleLenCurveInfo+'.inputCurve',f=True)
	mc.connectAttr(muscleLenCurveInfo+'.arcLength',muscleMesh+'.currentLength',f=True)
	muscleLenDiv = mc.createNode('multiplyDivide',n=prefix+'_length_multiplyDivide')
	mc.setAttr(muscleLenDiv+'.operation',2) # Divide
	mc.setAttr(muscleLenDiv+'.input1',1,1,1)
	mc.setAttr(muscleLenDiv+'.input2',1,1,1)
	mc.connectAttr(muscleLenCurveInfo+'.arcLength',muscleLenDiv+'.input1X',f=True)
	mc.connectAttr(muscleMesh+'.restLength',muscleLenDiv+'.input2X',f=True)
	mc.connectAttr(muscleLenDiv+'.outputX',muscleMesh+'.lengthScale',f=True)
	
	# -----------
	# - Cleanup -
	# -----------
	
	# Parent start/end tangent locators
	mc.parent(attachLocGroup[1],attachLocators[0])
	mc.parent(attachLocGroup[-2],attachLocators[-1])
	
	# Parent start/end profiles
	mc.parent(profileGrpList[0],attachLocators[0])
	mc.setAttr(profileGrpList[0]+'.t',0.0,0.0,0.0)
	mc.setAttr(profileGrpList[0]+'.r',0.0,0.0,0.0)
	mc.setAttr(profileGrpList[0]+'.s',1.0,1.0,1.0)
	
	mc.parent(profileGrpList[-1],attachLocators[-1])
	mc.setAttr(profileGrpList[-1]+'.t',0.0,0.0,0.0)
	mc.setAttr(profileGrpList[-1]+'.r',0.0,0.0,0.0)
	mc.setAttr(profileGrpList[-1]+'.s',1.0,1.0,1.0)
	
	# Setup start/end profile scale compensation
	attachStartScaleCompNode = mc.createNode('multiplyDivide',n=prefix+'_attachStart_multiplyDivide')
	mc.setAttr(attachStartScaleCompNode+'.input1',1,1,1)
	mc.setAttr(attachStartScaleCompNode+'.operation',2)
	mc.connectAttr(attachLocators[0]+'.scale',attachStartScaleCompNode+'.input2',f=True)
	mc.connectAttr(attachStartScaleCompNode+'.output',profileGrpList[0]+'.scale',f=True)
	attachEndScaleCompNode = mc.createNode('multiplyDivide',n=prefix+'_attachEnd_multiplyDivide')
	mc.setAttr(attachEndScaleCompNode+'.input1',1,1,1)
	mc.setAttr(attachEndScaleCompNode+'.operation',2)
	mc.connectAttr(attachLocators[-1]+'.scale',attachEndScaleCompNode+'.input2',f=True)
	mc.connectAttr(attachEndScaleCompNode+'.output',profileGrpList[-1]+'.scale',f=True)
	
	# Lock transforms
	mc.setAttr(muscleGrp+'.inheritsTransform',0)
	mc.setAttr(muscleGrp+'.t',l=True,cb=True)
	mc.setAttr(muscleGrp+'.r',l=True,cb=True)
	mc.setAttr(muscleGrp+'.s',l=True,cb=True)
	
	# Return result
	return muscleMesh

def isMuscle(muscle):
	'''
	Check if input object (muscle) is a valid muscle object
	@param muscle: Object to query
	@type muscle: str
	'''
	# Check obect exists
	if not mc.objExists(muscle):
		print('Object "'+muscle+'" does not exis!')
		return False
		
	# Check muscle message attribute
	if not mc.objExists(muscle+'.muscleMessage'):
		print('Object "'+muscle+'" is not a valid muscle!')
		return False
	
	# Return result
	return True

def getMuscleObjectType(muscleObject):
	'''
	Get muscle object type of the specified muscleObject
	@param muscleObject: Muscle object to query
	@type muscleObject: str
	'''
	# Check muscleObject exists
	if not mc.objExists(muscleObject):
		raise Exception('Muscle object "'+muscleObject+'" does not exist!')
	
	# Check muscleObjectType attribute
	if not mc.objExists(muscleObject+'.muscleObjectType'):
		raise Exception('Object "'+muscleObject+'" is not connected to a valid muscle!')
	
	# Get muscle object type
	muscleObjType = mc.getAttr(muscleObject+'.muscleObjectType')
	
	# Return result
	return muscleObjType

def getMuscle(muscleObject):
	'''
	Get muscle connected to the specified muscleObject
	@param muscleObject: Muscle object to query
	@type muscleObject: str
	'''
	# Get muscle object type
	muscleObjType = getMuscleObjectType(muscleObject)
	
	# Get muscle
	muscle = ''
	if muscleObjType == 'geo':
		muscle = muscleObject
	elif (muscleObjType == 'profile') or (muscleObjType == 'attachment') or (muscleObjType == 'spline'):
		muscleConn = mc.listConnections(muscleObject+'.muscle',s=True,d=False)
		if not muscleConn:
			raise Exception('Unable to determine muscle connection from muscleObject "'+muscleObject+'"!')
		muscle = muscleConn[0]
	elif (muscleObjType == 'attachmentTangent'):
		muscleObjParent = mc.listRelatives(muscleObject,p=True)[0]
		muscleConn = mc.listConnections(muscleObjParent+'.muscle',s=True,d=False)
		if not muscleConn:
			raise Exception('Unable to determine muscle connection from muscleObject "'+muscleObject+'"!')
		muscle = muscleConn[0]
	else:
		raise Exception('Invalid muscleObjectType value: "'+muscleObjType+'"!')
	
	# Return result
	return muscle

def getAttachments(muscleObject):
	'''
	Get muscle attachments associated with the specified muscleObject
	@param muscleObject: Muscle object to query
	@type muscleObject: str
	'''
	# Get muscle
	muscle = getMuscle(muscleObject)
	
	# Get attachments
	attachments = mc.listConnections(muscle+'.attachment',s=True,d=False)
	if not attachments:
		raise Exception('No valid muscle attachments associated with muscleObject "'+muscleObject+'"!')
	
	# Return result
	return attachments

def getProfiles(muscleObject):
	'''
	Get muscle profile curves associated with the specified muscleObject
	@param muscleObject: Muscle object to query
	@type muscleObject: str
	'''
	# Get muscle
	muscle = getMuscle(muscleObject)
	
	# Get profile curves
	profiles = mc.listConnections(muscle+'.profile',s=True,d=False)
	if not profiles:
		raise Exception('No valid muscle profiles associated with muscleObject "'+muscleObject+'"!')
	
	# Return result
	return profiles

def getSpline(muscleObject):
	'''
	Get muscle spline associated with the specified muscleObject
	@param muscleObject: Muscle object to query
	@type muscleObject: str
	'''
	# Get muscle
	muscle = getMuscle(muscleObject)
	
	# Get profile curves
	spline = mc.listConnections(muscle+'.muscleSpline',s=True,d=False)
	if not spline:
		raise Exception('No valid muscle spline associated with muscleObject "'+muscleObject+'"!')
	
	# Return result
	return spline[0]

def setRestLength(muscle):
	'''
	Set muscle rest length to be equal to the current muscle length.
	@param muscle: Muscle set rest length for
	@type muscle: str
	'''
	# Check muscle
	if not isMuscle(muscle):
		raise Exception('Object "'+muscle+'" is not a valid muscle!')
	# Get current length
	length = mc.getAttr(muscle+'.currentLength')
	# Set rest length
	mc.setAttr(muscle+'.restLength',length)

def insertProfile(muscle,uValue):
	'''
	'''
	pass

def deleteProfile(profile):
	'''
	'''
	pass
