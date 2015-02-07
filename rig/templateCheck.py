import maya.cmds as mc

import glTools.utils.joint
import glTools.utils.lib
import glTools.utils.mathUtils
import glTools.utils.transform

def checkTemplateElements(template):
	'''
	Check if every component item of a template exists.
	@param template: A dictionary of template component and items.
	@type template: dict
	'''
	# =================================
	# - Check Template Elements Exist -
	# =================================
	
	for key in template.iterkeys():
		
		# Get template component list
		templateList = template[key]
		for item in templateList:
			
			# Check template item exists
			if not mc.objExists(item):
				raise Exception('Template component "'+str(key)+'" item "'+item+'" does not exist!')

def checkJointAxis(joint,axis='x',vector='x',warnThreshold=0.5,errorThreshold=0.0):
	'''
	Check a specified joint axis against a world vector.
	Print warning or raise error if past a given threshold value
	@param joint: The joint to check the axis direction for
	@type joint: str
	@param axis: The joint axis (as a string) to check the direction of
	@type axis: str
	@param vector: The world vector (as a string) to compare to the joint axis
	@type vector: str
	@param warnThreshold: If the vector comparison value (dot product) falls below this value, display a warning
	@type warnThreshold: float
	@param errorThreshold: If the vector comparison value (dot product) falls below this value, raise an error (Exception)
	@type errorThreshold: float
	'''
	# Check Joint
	if not mc.objExists(joint):
		raise Exception('Joint "'+joint+'" does not exist!')
	
	# Get Joint Axis as World Vector
	axisVec = glTools.utils.transform.axisVector(joint,axis,normalize=True)
	# Get Camparison World Vector
	refVec = glTools.utils.lib.axis_dict()[vector]
	
	# Compare Vectors
	dot = glTools.utils.mathUtils.dotProduct(axisVec,refVec)
	
	# Check Thresholds
	if dot < errorThreshold:
		print ('Template Check ERROR: Joint "'+joint+'" axis "'+axis+'" is below the maximum comparison threshold to its target world vector ('+str(refVec)+')!')
	if dot < warnThreshold:
		print ('Template Check Warning: Joint "'+joint+'" axis "'+axis+'" is below the recommended comparison threshold to its target world vector ('+str(refVec)+')!')

def checkZeroJointOrient(joint,fix=False):
	'''
	Check zero joint orients for the specified joint
	@param joint: The joint to check the zero joint orients for
	@type joint: str
	@param fix: Set zero joint orients if check fails
	@type fix: bool
	'''
	# Check Joint Orient
	jointOri = mc.getAttr(joint+'.jo')
	if (jointOri[0] + jointOri[1] + jointOri[2]) > 0.001:
		
		# Print Warning
		print('Template Check Warning: Joint "'+joint+'" has non zero joint orients! ('str(jointOri[0])'+'str(jointOri[1])'+'str(jointOri[2])')')
		
		# Zero Joint Orient
		if fix:
			mc.setAttr(joint+'.jo',0,0,0)
			print('Template Check: Joint "'+joint+'" orients have been zeroed out')

def checkInverseScaleConnection(joint,fix=False):
	'''
	Check joint inverse scale connection to parent joint scale.
	@param joint: The joint to check inverse scale connections for
	@type joint: str
	@param fix: Connect inverse scale to parent joint scale check fails
	@type fix: bool
	'''
	# Get Joint Parent
	parentJoint = mc.listRelatives(joint,p=True)
	if not parentJoint: return
	if not mc.objectType(parentJoint[0]) == 'joint': return
	
	# Get Existing Inverse Scale Connection
	invScalConn = mc.listConnections(joint+'.inverseScale',s=True,d=False)
	if not invScalConn: invScalConn = []
	if not invScalConn.count(parentJoint[0]):
		print('Template Check Warning: Joint "'+joint+'" inverse scale is not connected to its parent joint "'+parentJoint[0]+'" scale attribute!')

def checkJointTranslation(joint,offsetAxis='',ignoreMultipleSibling=False):
	'''
	Check joint translation relative to its parent joint.
	@param joint: The joint to check translation values for
	@type joint: str
	@param offsetAxis: The joint offset axis that is expected to have non zero translations.
	@type offsetAxis: str
	@param ignoreMultipleSibling: Ignore joints that have one or more siblings directly under the parent joint/transform.
	@type ignoreMultipleSibling: bool
	'''
	# Get Joint Parent
	parentJoint = mc.listRelatives(joint,p=True)
	if not parentJoint: return
	if not mc.objectType(parentJoint[0]) == 'joint':
		print('Template Check: Parent transform ("'+parentJoint[0]+'") of joint ("'+joint+'") is not a joint! Offset axis is being ignored for translation check.')
		offsetAxis=''
	
	# Get List of Joint Siblings
	jointSiblings = mc.ls(mc.listRelatives(parentJoint[0],c=True,pa=True),type='joint')
	jointSiblings.remove(joint)
	if jointSiblings and ignoreMultipleSibling:
		print('Template Check: Joint ("'+joint+'") has one or more joint siblings! Joint translation is expected for joints with siblings. Skipping check...')
		return
	
	# Check Joint Translation
	tSum = 0
	t = mc.getAttr(joint+'.t')[0]
	if not offsetAxis.count('x'): tSum += t[0]
	if not offsetAxis.count('y'): tSum += t[1]
	if not offsetAxis.count('z'): tSum += t[2]
	if tSum > 0.0001:
		print('Template Check Warning: Joint "'+joint+'" has non zero translate values!')

def checkBipedTemplate(fix=False):
	'''
	'''
	# ============================
	# - Define Template Elements -
	# ============================
	
	template = {}
	template['body'] = ['cn_bodyA_jnt','cn_bodyEnd_jnt']
	template['spine'] = ['cn_spineA_jnt','cn_spineB_jnt','cn_spineC_jnt','cn_spineEnd_jnt']
	template['neck'] = ['cn_neckA_jnt','cn_neckEnd_jnt']
	template['head'] = ['cn_headA_jnt','cn_headB_jnt','cn_headEnd_jnt']
	template['lf_clav'] = ['lf_clavicleA_jnt','lf_clavicleEnd_jnt']
	template['rt_clav'] = ['rt_clavicleA_jnt','rt_clavicleEnd_jnt']
	template['lf_arm'] = ['lf_armA_jnt','lf_armB_jnt','lf_armEnd_jnt']
	template['rt_arm'] = ['rt_armA_jnt','rt_armB_jnt','rt_armEnd_jnt']
	template['lf_hand'] = ['lf_handA_jnt']
	template['rt_hand'] = ['lf_handA_jnt']
	template['lf_index'] = ['lf_indexA_jnt','lf_indexB_jnt','lf_indexC_jnt','lf_indexEnd_jnt']
	template['lf_middle'] = ['lf_middleA_jnt','lf_middleB_jnt','lf_middleC_jnt','lf_middleEnd_jnt']
	template['lf_ring'] = ['lf_ringA_jnt','lf_ringB_jnt','lf_ringC_jnt','lf_ringEnd_jnt']
	template['lf_pinky'] = ['lf_pinkyA_jnt','lf_pinkyB_jnt','lf_pinkyC_jnt','lf_pinkyEnd_jnt']
	template['lf_thumb'] = ['lf_thumbA_jnt','lf_thumbB_jnt','lf_thumbC_jnt','lf_thumbEnd_jnt']
	template['rt_index'] = ['rt_indexA_jnt','rt_indexB_jnt','rt_indexC_jnt','rt_indexEnd_jnt']
	template['rt_middle'] = ['rt_middleA_jnt','rt_middleB_jnt','rt_middleC_jnt','rt_middleEnd_jnt']
	template['rt_ring'] = ['rt_ringA_jnt','rt_ringB_jnt','rt_ringC_jnt','rt_ringEnd_jnt']
	template['rt_pinky'] = ['rt_pinkyA_jnt','rt_pinkyB_jnt','rt_pinkyC_jnt','rt_pinkyEnd_jnt']
	template['rt_thumb'] = ['rt_thumbA_jnt','rt_thumbB_jnt','rt_thumbC_jnt','rt_thumbEnd_jnt']
	template['lf_leg'] = ['lf_legA_jnt','lf_legB_jnt','lf_legEnd_jnt']
	template['rt_leg'] = ['rt_legA_jnt','rt_legB_jnt','rt_legEnd_jnt']
	template['lf_foot'] = ['lf_footA_jnt','lf_footB_jnt','lf_footEnd_jnt']
	template['rt_foot'] = ['rt_footA_jnt','rt_footB_jnt','rt_footEnd_jnt']
	template['lf_foot_loc'] = ['lf_foot_loc', 'lf_heel_loc', 'lf_toe_loc', 'lf_footInner_loc', 'lf_footOuter_loc']
	template['rt_foot_loc'] = ['rt_foot_loc', 'rt_heel_loc', 'rt_toe_loc', 'rt_footInner_loc', 'rt_footOuter_loc']
	
	# =================================
	# - Check Template Elements Exist -
	# =================================
	
	checkTemplateElements(template)
	
	# =======================
	# - Check Joint Orients -
	# =======================
	
	# Body
	for joint in template['body'][:-1]:
		checkJointAxis(joint=joint,axis='z',vector='z',warnThreshold=0.999,errorThreshold=0.9)
		checkJointAxis(joint=joint,axis='y',vector='y',warnThreshold=0.999,errorThreshold=0.9)
	
	# Spine
	for joint in template['spine'][:-1]:
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.999,errorThreshold=0.9)
		checkJointAxis(joint=joint,axis='x',vector='y',warnThreshold=0.8,errorThreshold=0.5)
	
	# Neck
	for joint in template['neck'][:-1]:
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.999,errorThreshold=0.9)
		checkJointAxis(joint=joint,axis='x',vector='y',warnThreshold=0.5,errorThreshold=0.0)
	
	# Head
	for joint in template['head'][:-1]:
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.999,errorThreshold=0.9)
		checkJointAxis(joint=joint,axis='x',vector='y',warnThreshold=0.8,errorThreshold=0.5)
	
	# Clavicles
	for joint in template['lf_clav'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='-y',warnThreshold=0.9,errorThreshold=0.8)
	for joint in template['rt_clav'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='y',warnThreshold=0.9,errorThreshold=0.8)
	
	# Arms
	for joint in template['lf_arm'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='-y',warnThreshold=0.9,errorThreshold=0.8)
	for joint in template['rt_arm'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='y',warnThreshold=0.9,errorThreshold=0.8)
	
	# Legs
	for joint in template['lf_leg'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='-y',warnThreshold=0.75,errorThreshold=0.5)
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.9,errorThreshold=0.8)
	for joint in template['rt_leg'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='y',warnThreshold=0.75,errorThreshold=0.5)
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.9,errorThreshold=0.8)
	
	# Feet
	for joint in template['lf_foot'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='z',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.9,errorThreshold=0.8)
	for joint in template['rt_foot'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='-z',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='x',warnThreshold=0.9,errorThreshold=0.8)
	
	# Hands
	for joint in template['lf_hand']:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='-y',warnThreshold=0.9,errorThreshold=0.8)
	for joint in template['rt_hand']:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.75,errorThreshold=0.25)
		checkJointAxis(joint=joint,axis='z',vector='y',warnThreshold=0.9,errorThreshold=0.8)
	
	# Fingers
	lf_fingerList = template['lf_index'] + template['lf_middle'] + template['lf_ring'] + template['lf_pinky']
	rt_fingerList = template['rt_index'] + template['rt_middle'] + template['rt_ring'] + template['rt_pinky']
	for joint in lf_fingerList:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.9,errorThreshold=0.5)
		checkJointAxis(joint=joint,axis='z',vector='-y',warnThreshold=0.75,errorThreshold=0.5)
	for joint in rt_fingerList:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.9,errorThreshold=0.5)
		checkJointAxis(joint=joint,axis='z',vector='y',warnThreshold=0.75,errorThreshold=0.5)
	for joint in template['lf_thumb'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.25,errorThreshold=0.0)
		checkJointAxis(joint=joint,axis='z',vector='-y',warnThreshold=0.25,errorThreshold=0.0)
	for joint in template['rt_thumb'][:-1]:
		checkJointAxis(joint=joint,axis='x',vector='x',warnThreshold=0.25,errorThreshold=0.0)
		checkJointAxis(joint=joint,axis='z',vector='y',warnThreshold=0.25,errorThreshold=0.0)
	
	# ==========================
	# - Check Joint Properties -
	# ==========================
	
	# For Each Joint
	for joint in mc.ls(type='joint'):
		
		# ==========================
		# - Zero End Joint Orients -
		# ==========================
		
		# Check End Joint
		if glTools.utils.joint.isEndJoint(joint):
			
			# Check Joint Orient
			checkZeroJointOrient(joint,fix=fix)
	
		# ===================================
		# - Check Inverse Scale Connections -
		# ===================================
		
		checkInverseScaleConnection(joint,fix=fix)
		
		# ==========================
		# - Check Joint Transforms -
		# ==========================
		
		checkJointTranslation(joint,'x',ignoreMultipleSibling=True)

def checkBoxtrollTemplate():
	'''
	'''
	# ============================
	# - Define Template Elements -
	# ============================
	
	template = {}
	template['body'] = ['cn_bodyA_jnt','cn_bodyEnd_jnt']
	template['box'] = ['cn_boxA_jnt','cn_boxEnd_jnt']
	template['lid'] = ['cn_lidA_jnt','cn_lidB_jnt','cn_lidEnd_jnt']
	template['head'] = ['cn_headA_jnt','cn_headB_jnt','cn_headEnd_jnt']
	template['lf_clav'] = ['lf_clavicleA_jnt','lf_clavicleEnd_jnt']
	template['rt_clav'] = ['rt_clavicleA_jnt','rt_clavicleEnd_jnt']
	template['lf_arm'] = ['lf_armA_jnt','lf_armB_jnt','lf_armEnd_jnt']
	template['rt_arm'] = ['rt_armA_jnt','rt_armB_jnt','rt_armEnd_jnt']
	template['lf_hand'] = ['lf_handA_jnt']
	template['rt_hand'] = ['lf_handA_jnt']
	template['lf_index'] = ['lf_indexA_jnt','lf_indexB_jnt','lf_indexC_jnt','lf_indexEnd_jnt']
	template['lf_middle'] = ['lf_middleA_jnt','lf_middleB_jnt','lf_middleC_jnt','lf_middleEnd_jnt']
	template['lf_pinky'] = ['lf_pinkyA_jnt','lf_pinkyB_jnt','lf_pinkyC_jnt','lf_pinkyEnd_jnt']
	template['lf_thumb'] = ['lf_thumbA_jnt','lf_thumbB_jnt','lf_thumbC_jnt','lf_thumbEnd_jnt']
	template['rt_index'] = ['rt_indexA_jnt','rt_indexB_jnt','rt_indexC_jnt','rt_indexEnd_jnt']
	template['rt_middle'] = ['rt_middleA_jnt','rt_middleB_jnt','rt_middleC_jnt','rt_middleEnd_jnt']
	template['rt_pinky'] = ['rt_pinkyA_jnt','rt_pinkyB_jnt','rt_pinkyC_jnt','rt_pinkyEnd_jnt']
	template['rt_thumb'] = ['rt_thumbA_jnt','rt_thumbB_jnt','rt_thumbC_jnt','rt_thumbEnd_jnt']
	template['lf_leg'] = ['lf_legA_jnt','lf_legB_jnt','lf_legEnd_jnt']
	template['rt_leg'] = ['rt_legA_jnt','rt_legB_jnt','rt_legEnd_jnt']
	template['lf_foot'] = ['lf_footA_jnt','lf_footB_jnt','lf_footEnd_jnt']
	template['rt_foot'] = ['rt_footA_jnt','rt_footB_jnt','rt_footEnd_jnt']
	template['lf_ear'] = ['lf_earA_jnt','lf_earB_jnt','lf_earEnd_jnt']
	template['rt_ear'] = ['rt_earA_jnt','rt_earB_jnt','rt_earEnd_jnt']
	template['lf_foot_loc'] = ['lf_foot_loc', 'lf_heel_loc', 'lf_toe_loc', 'lf_footInner_loc', 'lf_footOuter_loc']
	template['rt_foot_loc'] = ['rt_foot_loc', 'rt_heel_loc', 'rt_toe_loc', 'rt_footInner_loc', 'rt_footOuter_loc']
	
	# =================================
	# - Check Template Elements Exist -
	# =================================
	
	checkTemplateElements(template)
	
	# =======================
	# - Check Joint Orients -
	# =======================
	
		# Zero End Joint Orients
	
	# Check Inverse Scale Connections
	
	# Check Transforms
	
		# Translation in Single Axis for Lone Sibling
	
