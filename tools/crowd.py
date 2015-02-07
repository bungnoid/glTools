import maya.mel as mm
import maya.cmds as mc
import maya.app.general.pointOnPolyConstraint

#from glTools.rig import rig

from glTools.nrig.module import module

import glTools.tools.animLib
import glTools.tools.constraint
import glTools.tools.lookAt

import glTools.utils.boundingBox
import glTools.utils.mathUtils
import glTools.utils.namespace
import glTools.utils.reference
import glTools.utils.scenegraph
import glTools.utils.transform

import glTools.anim.mocap_utils
import glTools.anim.rig_utils
import glTools.anim.utils

import glTools.rig.mirrorAnim

import glTools.ui.utils

import ika.sgxml

import ika.editorial.cut
import ika.maya.file
import ika.maya.sgxml

import ika.context.util as ctx_util

import ika.glob as glob

import os
import random
import subprocess
import time

from glTools.data import data

from random import choice

# - chunkified -
#import chunkified.maya.crowd
#import chunkified.massive.file.callsheet as csh
#import chunkified.helper.alphanum as alpha

# ==============
# - Agents XML -
# ==============

def buildAgentsXmlUI():
	'''
	Build Agent XML UI
	'''
	# Window
	window = 'buildAgentXmlUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Build Crowd Agents Scenegraph',resizeToFitChildren=True)
	
	# UI Elements
	CL = mc.columnLayout()
	agentDirTFB = mc.textFieldButtonGrp('agentXml_agentDirTFB',label='XML Directory',buttonLabel='...')
	createB = mc.button(l='Create',c='import glTools.tools.crowd;reload(glTools.tools.crowd);glTools.tools.crowd.buildAgentsXmlFromUI()')
	mc.textFieldButtonGrp(agentDirTFB,e=True,bc='import glTools.ui.utils;reload(glTools.ui.utils);glTools.ui.utils.loadDirectoryPath("'+agentDirTFB+'")')
	
	# Show Window
	mc.showWindow(window)

def buildAgentsXmlFromUI():
	'''
	Build Agent XML from UI
	'''
	# Check Window
	window = 'buildAgentXmlUI'
	if not mc.window(window,q=True,ex=True):
		raise Exception('Build Agents XML UI not found! Unable to build agents XML file...')
	
	# Get Agent Directory
	agentDir = mc.textFieldButtonGrp('agentXml_agentDirTFB',q=True,text=True)
	if not os.path.isdir(agentDir):
		print('Build Agents XML: Invalid XML directory! Unable to build agents XML...')
		return
	if not agentDir.endswith('/'): agentDir += '/'
	
	# Get XML List
	xmlList = glob.glob(os.path.join(agentDir+'*', '*.base.xml'))
	if not xmlList: raise Exception('No base XML files found under root directory "'+agentDir+'"!')
	# Get Context from XML File - 
	# - Added hack (pop directory) to force context creation
	xmlfile = xmlList[0].replace('/'+xmlList[0].split('/')[-2],'')
	ctx = ika.context.util.getContext(*os.path.split(xmlfile))
	
	# Build Agents XML
	#ctx = ika.maya.file.getContext()
	xmlName = agentDir.split('/')[-2].split('.')[0]
	outFile = agentDir+ctx['sequence']+'.'+ctx['shot']+'.'+ctx['task']+'.'+xmlName+'.base.xml'
	outXml = buildAgentsXml(agentDir+'*',outFile)
	
	# Return Result
	return outXml

def buildAgentsXml(dirPattern, outFile):
	'''
	Builds sgxml file referencing all *.base.xml files in directories matching dirPattern.
	
	@param dirPattern: glob pattern defining which directories to search for *.base.xml files
	@param outFile: path to output xml file
	
	For example, to build a scene graph xml file name "female.xml" which references all
	female chars under seq/0800/sequence/crd:
	
	dirPattern = "/laika/jobs/hbm/vfx/seq/0800/sequence/crd/scene_graph/wip/*female*"
	buildAgentsXml(dirPattern, "/laika/jobs/hbm/vfx/seq/0800/sequence/crd/scene_graph/wip/female.xml")
	'''
	# Initialize Output XML File
	root = ika.sgxml.Root(xmlPath=outFile, channelRefFile="channels")
	
	# Get Agent XML Files
	for xmlRef in glob.glob(os.path.join(dirPattern, '*.base.xml')):
		name = os.path.basename(xmlRef).split('.')[-3]
		component = ika.sgxml.XmlReference(name, refFile=xmlRef)
		root.instanceList.append(component)
	
	# Export Agent XML
	root.writeAllXmlFiles()
	
	# Return Result
	if os.path.isfile(outFile):
		print('Created agent XML file "'+outFile+'"')
		return outFile
	else:
		print('ERROR creating XML file "'+outFile+'"!')
		return ''

def buildAgentsListXml(agentXmlList,outFile):
	'''
	Builds sgxml file referencing all specified agent XML files
	@param agentXmlList: list of agent base XML files
	@param outFile: path to output xml file
	'''
	# Initialize Output XML File
	root = ika.sgxml.Root(xmlPath=outFile,channelRefFile='channels')
	
	# Get Agent XML Files
	for xmlDir in agentXmlList:
		xmlRef = glob.glob(os.path.join(xmlDir, '*.base.xml'))
		if xmlRef:
			name = os.path.basename(xmlRef[0]).split('.')[-3]
			component = ika.sgxml.XmlReference(name, refFile=xmlRef[0])
			root.instanceList.append(component)
		else:
			print('Unable to find *.base.xml from agent directory "'+xmlDir+'"! Skipping...')
	
	# Export Agent XML
	root.writeAllXmlFiles()
	
	# Return Result
	if os.path.isfile(outFile):
		print('Created agent XML file "'+outFile+'"')
		return outFile
	else:
		print('ERROR creating XML file "'+outFile+'"!')
		return ''

# =========================
# - Agent Instance Bounds -
# =========================

def syncInstanceBounds(instance):
	'''
	Sync instance bounds animation based on GPU cache frame offset value.
	@param instance: Instance to sync bounding box geometry animation
	@type instance: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Instance
	if not mc.objExists(instance):
		raise Exception('Instance "'+instance+'" does not exist!')
	# Check frameOffset Attribute
	if not mc.attributeQuery('frameOffset',n=instance,ex=True):
		raise Exception('Instance "'+instance+'" has no "frameOffset" attribute!')
	
	# Check Instance Bounds
	instanceShapes = mc.listRelatives(instance,s=True,pa=True)
	if not instanceShapes:
		raise Exception('Instance "'+instance+'" has no shape children!')
	
	# Get Instance Bounds
	instanceName = instance.split('|')[-1]
	instanceBounds = None
	for shape in instanceShapes:
		if shape.endswith(instanceName+'BoundsShape'):
			instanceBounds = shape
	if not instanceBounds:
		raise Exception('Unable to determine bounds shape for instance "'+instance+'"!')
	
	# ========================
	# - Sync Instance Bounds -
	# ========================
	
	# Get Frame Offset
	frameOffset = mc.getAttr(instance+'.frameOffset')
	
	# Get Anim Curves
	animCrvs = mc.ls(mc.listConnections(instanceBounds+'.pnts',s=True,d=False) or [],type='animCurve')
	if not animCrvs: raise Exception('No incoming animation for instance bounds "'+instanceBounds+'"!')
	
	# Calculate Animation Offset
	startAttr = glTools.utils.scenegraph.ScenegraphXML().startAttr
	cacheStart = mc.getAttr(instance+'.'+startAttr)
	animStartCur = mc.keyframe(animCrvs[0],q=True,tc=True)[0]
	animStartNew = -cacheStart+frameOffset
	animOffset = animStartNew+animStartCur
	
	# Apply Anim Offset
	mc.keyframe(animCrvs,e=True,relative=True,option='over',tc=-animOffset)
	
	# =================
	# - Return Result -
	# =================
	
	return frameOffset

def buildAgentBounds(agentGeo,start=1,end=0,pad=0.001):
	'''
	Build agent bounds for selected geometry.
	Creates animated bounding box geometry based on the specified geoemtry or geometry group.
	@param agentGeo: Agent geometry to generate animated bounds for
	@type agentGeo: str
	@param start: Start frame
	@type start: int
	@param end: End frame
	@type end: int
	@param pad: Amout to pad the animated bounds geometry
	@type pad: float
	'''
	# ========================
	# - Check Agent Geometry -
	# ========================
	
	# Check Agent Geometry
	if not mc.objExists(agentGeo):
		raise Exception('Agent geometry "'+agentGeo+'" does not exist!')
	agentGeoList = mc.ls(mc.listRelatives(agentGeo,ad=True,pa=True),noIntermediate=True,geometry=True,visible=True)
	if not agentGeoList:
		raise Exception('Agent geometry "'+agentGeo+'" does not contain any visible geometry shapes!')
	
	# Check Agent Namespace
	agentNS = ''
	if ':' in agentGeo: agentNS = agentGeo.split(':')[0]
	
	# =====================
	# - Check Frame Range -
	# =====================
	
	if start > end:
		start = mc.playbackOptions(q=True,min=True)
		end = mc.playbackOptions(q=True,max=True)
	
	# ======================
	# - Build Agent Bounds -
	# ======================
	
	# Initialize Bounding Box
	bbox = mc.polyCube(w=pad,h=pad,d=pad,ch=0,n=agentNS+'__bounds')[0]
	bboxShape = mc.listRelatives(bbox,s=True,pa=True)[0]
	mc.setAttr(bboxShape+'.overrideEnabled',1)
	mc.setAttr(bboxShape+'.overrideShading',0)
	
	# For Each Frame
	for i in range(start,end+1):
		
		# Set Time
		mc.currentTime(i,u=True)
		
		# Get Bounds Channel Values
		b = glTools.utils.boundingBox.geometryBoundingBox(agentGeo,worldSpace=True,noIntermediate=True,visibleOnly=True)
		mn = b[:3]
		mx = b[3:]
		
		# Set Bounding Box
		mc.move(mn[0],mn[1],mx[2],bboxShape+'.vtx[0]',a=True)
		mc.move(mx[0],mn[1],mx[2],bboxShape+'.vtx[1]',a=True)
		mc.move(mn[0],mx[1],mx[2],bboxShape+'.vtx[2]',a=True)
		mc.move(mx[0],mx[1],mx[2],bboxShape+'.vtx[3]',a=True)
		mc.move(mn[0],mx[1],mn[2],bboxShape+'.vtx[4]',a=True)
		mc.move(mx[0],mx[1],mn[2],bboxShape+'.vtx[5]',a=True)
		mc.move(mn[0],mn[1],mn[2],bboxShape+'.vtx[6]',a=True)
		mc.move(mx[0],mn[1],mn[2],bboxShape+'.vtx[7]',a=True)
		
		# Key Bounds
		mc.setKeyframe(bboxShape+'.vtx[0:7]')
	
	# =================
	# - Return Result -
	# =================
	
	return 

def agentBoundsRig(agentBounds):
	'''
	Generate agent bounds rig for the specified animated bounding box geometry
	@param agentBounds: Agent bounds geometry to generate bounds rig for
	@type agentBounds: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Agent Bounds
	if not mc.objExists(agentBounds):
		raise Exception('Agent bounds object "'+agentBounds+'" does not exist!')
	
	# Check Agent Prefix
	agentPrefix = agentBounds.split('__')[0]
	agentPrefix = agentPrefix.split('|')[-1]
	
	# Get Agent Namespace
	agentNS = agentPrefix
	agentNSsuffix = agentNS.split('_')[-1]
	try: agentNSind = int(agentNSsuffix)
	except: agentNSind = 1
	else: agentNS = agentNS.replace('_'+agentNSsuffix,'')
	while mc.namespace(ex=agentNS+'_%03d' % agentNSind): agentNSind += 1
	agentNS = agentNS+'_%03d' % agentNSind
	
	mc.namespace(add=agentNS)
	
	# ==========================
	# - Build Agent Bounds Rig -
	# ==========================
	
	mc.select(cl=True)
	baseJnt = mc.joint(n=agentNS+':base_jnt')
	
	# Constrain Base Joint
	mc.select(agentBounds+'.f[3]')
	mc.select(baseJnt,tgl=True)
	#cmd = maya.app.general.pointOnPolyConstraint.assembleCmd()
	cmd = glTools.tools.constraint.pointOnPolyConstraintCmd(agentBounds+'.f[3]')
	# -------
	# !! Hack Fix !!
	# maya.app.general.pointOnPolyConstraint.assembleCmd() Returns invalid command parameters
	# Fixing by stripping down incorrect attribute names
	# -------
	while 'BoundsShape' in cmd: cmd = cmd.replace('BoundsShape','')
	if '|' in cmd: print cmd
	mm.eval('string $constraint[]=`pointOnPolyConstraint`'+cmd)
	
	# Disconnect Rotatation
	for r in ['.rx','.ry','.rz']:
		rConn = mc.listConnections(baseJnt+r,s=True,p=True)
		mc.disconnectAttr(rConn[0],baseJnt+r)
		mc.setAttr(baseJnt+r,0)
	
	# Constrain Corner Joints
	jntList = [baseJnt]
	for i in range(8):
		
		# Create Coner Joint
		mc.select(cl=True)
		jnt = mc.joint(n=agentNS+':corner_'+str(i)+'_jnt')
		jnt = mc.parent(jnt,baseJnt)[0]
		jntList.append(jnt)
		
		# Create Corner Constraint
		mc.select(agentBounds+'.vtx['+str(i)+']')
		mc.select(jntList[-1],tgl=True)
		#cmd = maya.app.general.pointOnPolyConstraint.assembleCmd()
		cmd = glTools.tools.constraint.pointOnPolyConstraintCmd(agentBounds+'.vtx['+str(i)+']')
		# -------
		# !! Hack Fix !!
		# maya.app.general.pointOnPolyConstraint.assembleCmd() Returns invalid command parameters
		# Fixing by stripping down incorrect attribute names
		# -------
		while 'BoundsShape' in cmd: cmd = cmd.replace('BoundsShape','')
		mm.eval('string $constraint[]=`pointOnPolyConstraint`'+cmd)
		
		# Disconnect Rotatation
		for r in ['.rx','.ry','.rz']:
			rConn = mc.listConnections(jntList[-1]+r,s=True,p=True)
			mc.disconnectAttr(rConn[0],jntList[-1]+r)
			mc.setAttr(jntList[-1]+r,0)
	
	# =================
	# - Return Result -
	# =================
	
	return agentNS

def agentBoundsRigList(agentBoundsList):
	'''
	Generate agent bounds rig for the list of specified animated bounding box geometries
	@param agentBoundsList: Agent bounds geometry to generate bounds rig for
	@type agentBoundsList: list
	'''
	pass

def bakeAgentBoundsRig(agentNS,start=1,end=0):
	'''
	Generate agent bounds rig for the specified agent.
	@param agentNS: Agent namespace to bake bounds rig for
	@type agentNS: str
	@param start: Start frame
	@type start: int
	@param end: End frame
	@type end: int
	'''
	# Check Start/End
	if start > end:
		start = mc.playbackOptions(q=True,min=True)
		end = mc.playbackOptions(q=True,max=True)
	
	# Get Joints to Bake
	jnts = [agentNS+':base_jnt']+[agentNS+':corner_'+str(i)+'_jnt' for i in range(8)]
	
	# Bake Results
	mc.refresh(suspend=True)
	mc.bakeResults(jnts,t=(start,end),at=['tx','ty','tz'],simulation=False)
	mc.refresh(suspend=False)
	
	# Delete Constraints
	delConst = mc.ls(mc.listRelatives(agentNS+':base_jnt',ad=True,pa=True),type='constraint')
	if delConst: mc.delete(delConst)

# ====================
# - Maya Agent Setup -
# ====================

def mayaAgentBuild(asset,agentSrcNS,agentNS,layoutNS='',rigSubtask='low',start=None,end=None):
	'''
	Generate agent animation cache given a layout workfile and an agent name.
	@param asset: Agent asset type
	@type asset: str
	@param agentSrcNS: Namespace of agent source/layout.
	@type agentSrcNS: str
	@param agentNS: Destination namespace of crowd agent to build.
	@type agentNS: str
	@param layoutNS: Layout workfile namespace, if applicable.
	@type layoutNS: str
	@param start: Start frame
	@type start: int
	@param end: End frame
	@type end: int
	'''
	# ====================
	# - Check Namespaces -
	# ====================
	
	# Layout NS
	if layoutNS: layoutNS+=':'
	
	# Check Agent NS
	if agentNS == agentSrcNS:
		mc.namespace(rename=[agentSrcNS,agentSrcNS+'_orig'])
		agentSrcNS += '_orig'
	
	# ==============================
	# - Define Source/Layout Nodes -
	# ==============================
	
	# Source/Layout All
	layout_all = agentSrcNS+':all'
	if not mc.objExists(layout_all): raise Exception('Source/Layout rig all node "'+layout_all+'" not found!')
	
	# Source/Layout AllTrans
	layout_allTrans = agentSrcNS+':allTransA'
	if not mc.objExists(layout_allTrans): raise Exception('Source/Layout rig allTrans node "'+layout_allTrans+'" not found!')
	
	# =================
	# - Set Start/End -
	# =================
	
	if start == None or end == None:
		cut = ika.editorial.cut.CutInfo()
		if start == None: start = cut.firstFrame
		if end == None: end = cut.lastFrame
	
	# Set Playback Range
	mc.playbackOptions(ast=start)
	mc.playbackOptions(min=start)
	mc.playbackOptions(max=end)
	mc.playbackOptions(aet=end)
	mc.currentTime(start)
	
	# ====================
	# - Load Agent Asset -
	# ====================
	
	print('>>> Referencing Agent Rig to Namespace "'+agentNS+'"...')
	
	# Set Agent Namespace
	charNS = agentNS
	
	# Determine Asset from Agent Name
	char = asset
	
	# Load Character/Agent Asset
	ika.maya.sgxml.loadAsset(	'char',
								char,
								task='rig',
								subtask=rigSubtask,
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=charNS,
								sgxmlType=None	)
	
	# Define Agent Nodes
	char_all = charNS+':all'
	if not mc.objExists(char_all): raise Exception('Agent rig all node "'+char_all+'" not found!')
	char_allTrans = charNS+':allTransA'
	if not mc.objExists(char_allTrans): raise Exception('Agent rig allTrans node "'+char_allTrans+'" not found!')
	
	# Position Agent
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# ====================================
	# - Apply Agent (Variation) Settings -
	# ====================================
	
	var_attrList = [	'var_costume',
						'var_costumeColour',
						'var_hair',
						'var_hairGroom',
						'var_hairColour',
						'var_groomColour',
						'var_hairTarget',
						
						'var_arsA_hat',
						'var_shpA_hat',
						'var_twnA_hat',
						'var_twnA_hatA',
						'var_twnA_hatB',
						'var_twnA_derbyHat',
						
						'var_wrkA_suspenders',
						'var_wrkA_waistcoat',
						
						'var_twnA_scarfA',
						'var_twnA_scarfB',
						'var_twnA_scarfC',
							
						'uniformScale'	]
	
	for var_attr in var_attrList:
		if mc.attributeQuery(var_attr,node=layout_all,ex=True):
			try: mc.setAttr(char_all+'.'+var_attr,mc.getAttr(layout_all+'.'+var_attr))
			except: print('Error setting rig variable attr "'+var_attr+'" for rig "'+charNS+'"!')
	
	# ================
	# - Apply Motion -
	# ================
	
	crowd_body_anim = None
	crowd_body_scale = None
	crowd_body_speed = None
	crowd_body_offset = None
	crowd_body_mirror = None
	crowd_body_infinity = None
	crowd_face_anim = None
	crowd_face_offset = None
	crowd_face_infinity = None
	crowd_lfHand_anim = None
	crowd_lfHand_offset = None
	crowd_lfHand_infinity = None
	crowd_rtHand_anim = None
	crowd_rtHand_offset = None
	crowd_rtHand_infinity = None
	
	if mc.objExists(layout_all+'.crowd_body_anim'): crowd_body_anim = mc.getAttr(layout_all+'.crowd_body_anim')
	if mc.objExists(layout_all+'.crowd_body_scale'): crowd_body_scale = mc.getAttr(layout_all+'.crowd_body_scale')
	if mc.objExists(layout_all+'.crowd_body_speed'): crowd_body_speed = mc.getAttr(layout_all+'.crowd_body_speed')
	if mc.objExists(layout_all+'.crowd_body_offset'): crowd_body_offset = int(mc.getAttr(layout_all+'.crowd_body_offset'))
	if mc.objExists(layout_all+'.crowd_body_mirror'): crowd_body_mirror = bool(mc.getAttr(layout_all+'.crowd_body_mirror'))
	if mc.objExists(layout_all+'.crowd_body_infinity'): crowd_body_infinity = mc.getAttr(layout_all+'.crowd_body_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_face_anim'): crowd_face_anim = mc.getAttr(layout_all+'.crowd_face_anim')
	if mc.objExists(layout_all+'.crowd_face_offset'): crowd_face_offset = int(mc.getAttr(layout_all+'.crowd_face_offset'))
	if mc.objExists(layout_all+'.crowd_face_infinity'): crowd_face_infinity = mc.getAttr(layout_all+'.crowd_face_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_lfHand_anim'): crowd_lfHand_anim = mc.getAttr(layout_all+'.crowd_lfHand_anim')
	if mc.objExists(layout_all+'.crowd_lfHand_offset'): crowd_lfHand_offset = int(mc.getAttr(layout_all+'.crowd_lfHand_offset'))
	if mc.objExists(layout_all+'.crowd_lfHand_infinity'): crowd_lfHand_infinity = mc.getAttr(layout_all+'.crowd_lfHand_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_rtHand_anim'): crowd_rtHand_anim = mc.getAttr(layout_all+'.crowd_rtHand_anim')
	if mc.objExists(layout_all+'.crowd_rtHand_offset'): crowd_rtHand_offset = int(mc.getAttr(layout_all+'.crowd_rtHand_offset'))
	if mc.objExists(layout_all+'.crowd_rtHand_infinity'): crowd_rtHand_infinity = mc.getAttr(layout_all+'.crowd_rtHand_infinity',asString=True)
	
	# Print Anim/Motion Details
	print('>>> APPLY POSE/ANIM: body anim = '+str(crowd_body_anim))
	print('>>> APPLY POSE/ANIM: body scale = '+str(crowd_body_scale))
	print('>>> APPLY POSE/ANIM: body speed = '+str(crowd_body_speed))
	print('>>> APPLY POSE/ANIM: body offset = '+str(crowd_body_offset))
	print('>>> APPLY POSE/ANIM: body mirror = '+str(crowd_body_mirror))
	print('>>> APPLY POSE/ANIM: body infinity = '+str(crowd_body_infinity))
	
	print('>>> APPLY POSE/ANIM: face anim = '+str(crowd_face_anim))
	print('>>> APPLY POSE/ANIM: face offset = '+str(crowd_face_offset))
	print('>>> APPLY POSE/ANIM: face infinity = '+str(crowd_face_infinity))
	
	print('>>> APPLY POSE/ANIM: lfHand anim = '+str(crowd_lfHand_anim))
	print('>>> APPLY POSE/ANIM: lfHand offset = '+str(crowd_lfHand_offset))
	print('>>> APPLY POSE/ANIM: lfHand infinity = '+str(crowd_lfHand_infinity))
	
	print('>>> APPLY POSE/ANIM: rtHand anim = '+str(crowd_rtHand_anim))
	print('>>> APPLY POSE/ANIM: rtHand offset = '+str(crowd_rtHand_offset))
	print('>>> APPLY POSE/ANIM: rtHand infinity = '+str(crowd_rtHand_infinity))
	
	# Apply Body
	if crowd_body_anim:
		isPose = crowd_body_anim.endswith('.pose')
		isAnim = crowd_body_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_body_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_body_anim,targetNS=charNS,frameOffset=crowd_body_offset*-1,infinityOverride=crowd_body_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading BODY anim "'+crowd_body_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
		
		# =========================
		# - Mirror Body Animation -
		# =========================
		
		if crowd_body_mirror: glTools.rig.mirrorAnim.mirrorBipedAnim(rigNS=charNS)
		
		# ========================
		# - Scale Body Animation -
		# ========================
		
		# Filter Curves
		glTools.anim.utils.eulerFilter(charNS+':cn_bodyA_jnt')
		# Scale Keys
		glTools.anim.utils.scaleKeyValues(	obj=charNS+':cn_bodyA_jnt',
											attrs=['rx','ry','rz','tx','ty','tz'],
											scale=crowd_body_scale,
											method='average'	)
		
		ctrlList = [	'cn_spineA_jnt',
						'cn_spineB_jnt',
						'cn_spineC_jnt',
						'cn_neckA_jnt',
						'cn_headA_jnt'	]
		
		for ctrl in ctrlList:
			
			# Filter Curves
			glTools.anim.utils.eulerFilter(charNS+':'+ctrl)
			
			# Scale Keys
			glTools.anim.utils.scaleKeyValues(	obj=charNS+':'+ctrl,
												attrs=['rx','ry','rz'], # 'tx','ty','tz',
												scale=crowd_body_scale,
												method='average'	)
		
		# Body Anim Speed
		if crowd_body_speed != None and crowd_body_speed != 1.0:
			glTools.anim.utils.scaleAnimTime(NS=charNS,scale=(1.0/crowd_body_speed),pivot=0.0)
	
	# Apply Face
	if crowd_face_anim:
		isPose = crowd_face_anim.endswith('.pose')
		isAnim = crowd_face_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_face_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_face_anim,targetNS=charNS,frameOffset=crowd_face_offset*-1,infinityOverride=crowd_face_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading FACE anim "'+crowd_face_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Apply Left Hand
	if crowd_lfHand_anim:
		isPose = crowd_lfHand_anim.endswith('.pose')
		isAnim = crowd_lfHand_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_lfHand_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_lfHand_anim,targetNS=charNS,frameOffset=crowd_lfHand_offset*-1,infinityOverride=crowd_lfHand_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading LEFT HAND anim "'+crowd_lfHand_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Apply Right Hand
	if crowd_rtHand_anim:
		isPose = crowd_rtHand_anim.endswith('.pose')
		isAnim = crowd_rtHand_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_rtHand_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_rtHand_anim,targetNS=charNS,frameOffset=crowd_rtHand_offset*-1,infinityOverride=crowd_rtHand_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading RIGHT HAND anim "'+crowd_rtHand_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Re-Position Agent
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# ===========
	# - Look At -
	# ===========
	
	crowd_lookAt = None
	crowd_lookAt_head = None
	crowd_lookAt_eyes = None
	crowd_lookAt_neck = None
	crowd_lookAt_chest = None
	crowd_lookAt_bake = True
	crowd_lookAt_offset = None
	crowd_lookAt_eyeOffset = None
	
	if mc.objExists(layout_all+'.crowd_lookAt'): crowd_lookAt = mc.getAttr(layout_all+'.crowd_lookAt')
	if mc.objExists(layout_all+'.crowd_lookAt_head'): crowd_lookAt_head = mc.getAttr(layout_all+'.crowd_lookAt_head')
	if mc.objExists(layout_all+'.crowd_lookAt_eyes'): crowd_lookAt_eyes = mc.getAttr(layout_all+'.crowd_lookAt_eyes')
	if mc.objExists(layout_all+'.crowd_lookAt_neck'): crowd_lookAt_neck = mc.getAttr(layout_all+'.crowd_lookAt_neck')
	if mc.objExists(layout_all+'.crowd_lookAt_chest'): crowd_lookAt_chest = mc.getAttr(layout_all+'.crowd_lookAt_chest')
	if mc.objExists(layout_all+'.crowd_lookAt_bake'): crowd_lookAt_bake = mc.getAttr(layout_all+'.crowd_lookAt_bake')
	if mc.objExists(layout_all+'.crowd_lookAt_offset'): crowd_lookAt_offset = mc.getAttr(layout_all+'.crowd_lookAt_offset')
	if mc.objExists(layout_all+'.crowd_lookAt_eyeOffset'): crowd_lookAt_eyeOffset = mc.getAttr(layout_all+'.crowd_lookAt_eyeOffset')
	
	# Create LookAt
	if crowd_lookAt:
		
		# Check LookAt Object
		crowd_lookAt = layoutNS+crowd_lookAt
		if not mc.objExists(crowd_lookAt):
			raise Exception('Agent lookAt object "'+crowd_lookAt+'" does not exist!')
		
		# Print LookAt Details
		print('>>> LOOKAT: target = '+crowd_lookAt)
		print('>>> LOOKAT: headWt = '+str(crowd_lookAt_head))
		print('>>> LOOKAT: eyesWt = '+str(crowd_lookAt_eyes))
		if crowd_lookAt_neck: print('>>> LOOKAT: neckWt = '+str(crowd_lookAt_neck))
		if crowd_lookAt_chest: print('>>> LOOKAT: chestWt = '+str(crowd_lookAt_chest))
		print('>>> LOOKAT: bakeAnim = '+str(bool(crowd_lookAt_bake)))
		print('>>> LOOKAT: offset = '+str(bool(crowd_lookAt_offset)))
		
		# Set SGXML Ignore
		ika.maya.sgxml.setIgnore([crowd_lookAt])
		
		# LookAt Setup
		lookAt_slaves = ['cn_headA_jnt','lf_eye_offset_jnt','rt_eye_offset_jnt']
		lookAt_weights = [crowd_lookAt_head,crowd_lookAt_eyes,crowd_lookAt_eyes]
		lookAt_aimUp = [('y','x'),('z','y'),('z','y')]
		
		# Neck LookAt
		if crowd_lookAt_neck:
			lookAt_slaves.insert(0,'cn_neckA_jnt')
			lookAt_weights.insert(0,crowd_lookAt_neck)
			lookAt_aimUp.insert(0,('y','x'))
		
		# Chest LookAt
		if crowd_lookAt_chest:
			lookAt_slaves.insert(0,'cn_spineC_jnt')
			lookAt_weights.insert(0,crowd_lookAt_chest)
			lookAt_aimUp.insert(0,('y','x'))
		
		# Setup Agent LookAt
		glTools.tools.lookAt.create(	target = crowd_lookAt,
									slaveList = [charNS+':'+i for i in lookAt_slaves],
									slaveAimUp=lookAt_aimUp,
									weightList=lookAt_weights,
									bakeAnim=crowd_lookAt_bake,
									bakeStartEnd=[start,end],
									offsetAnim=crowd_lookAt_offset,
									offset=(0,0,0)	)
		
		# Apply Eye Angle Offset
		if crowd_lookAt_eyeOffset:
			mc.keyframe(charNS+':lf_eye_offset_jnt.ry',e=True,relative=True,valueChange=crowd_lookAt_eyeOffset)
			mc.keyframe(charNS+':rt_eye_offset_jnt.ry',e=True,relative=True,valueChange=-crowd_lookAt_eyeOffset)
	
	# ===============================
	# - Apply Rig Control Overrides -
	# ===============================
	
	applyRigControlAttributeOverrides(agentSrcNS,charNS)
	
	# =====================
	# - Re-Position Agent -
	# =====================
	
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# =================
	# - Return Result -
	# =================
	
	return charNS

def mayaAgentBuildFromSel(rigSubtask='low',replace=False):
	'''
	'''
	# Get Agents from Current Selection
	agents = mc.ls(sl=1,transforms=True)
	NSlist = glTools.utils.namespace.getNSList(agents,topOnly=True)
	
	# Get Timeline Start/End
	start = mc.playbackOptions(q=True,min=True)
	end = mc.playbackOptions(q=True,max=True)
	
	# For Each Agent
	for agent in NSlist:
		
		# Get Agent Asset
		agentCtx = glTools.utils.reference.contextFromNsReferencePath(agent)
		agentAsset = dict(agentCtx)['asset']
		
		# Determine Build Asset Namespace
		agentNS = agent
		if not replace: agentNS += '_preview'
		
		# Build Agent
		mayaAgentBuild(	asset = agentAsset,
						agentSrcNS = agent,
						agentNS = agentNS,
						layoutNS = '',
						rigSubtask=rigSubtask,
						start = start,
						end = end	)

def mayaAgentSetup(workfile,agent,start=None,end=None,exportScenegraph=True,outName=None):
	'''
	Generate agent animation cache given a layout workfile and an agent name.
	@param workfile: Crowd layout workfile.
	@type workfile: str
	@param agent: Agent to setup for export
	@type agent: str
	@param start: Start frame
	@type start: int
	@param end: End frame
	@type end: int
	@param exportScenegraph: Export scenegraph and alembic cache
	@type exportScenegraph: bool
	@param outName: Target export sub-directory name
	@type outName: str or None
	'''
	# ========================
	# - Load Layout Workfile -
	# ========================
	
	# Check Layout Workfile
	if not os.path.isfile(workfile):
		raise Exception('Layout workfile "'+workfile+'" does not exist!')
	
	print('>>> Referencing Layout "'+workfile+'"...')
	
	# Get File Type
	fileType = {'.ma':'mayaAscii','.mb':'mayaBinary'}
	fileName, ext = os.path.splitext(workfile)
	
	# Reference Layout
	layoutNS = 'layout'
	mc.file(workfile,reference=True,type=fileType[ext],namespace=layoutNS,returnNewNodes=True)
	
	# Define Layout Nodes
	layout_all = layoutNS+':'+agent+':all'
	if not mc.objExists(layout_all): raise Exception('Layout rig all node "'+layout_all+'" not found!')
	layout_allTrans = layoutNS+':'+agent+':allTransA'
	if not mc.objExists(layout_allTrans): raise Exception('Layout rig allTrans node "'+layout_allTrans+'" not found!')
	
	# Cut Start/End
	if start == None or end == None:
		cut = ika.editorial.cut.CutInfo()
		if start == None: start = cut.firstFrame
		if end == None: end = cut.lastFrame
	
	# Set Playback Range
	mc.playbackOptions(ast=start)
	mc.playbackOptions(min=start)
	mc.playbackOptions(max=end)
	mc.playbackOptions(aet=end)
	mc.currentTime(start)
	
	# ====================
	# - Load Agent Asset -
	# ====================
	
	print('>>> Referencing Agent Rig to Namespace "'+agent+'"...')
	
	# Set Agent Namespace
	charNS = agent
	
	# Determine Asset from Agent Name
	char = agent.split(':')[0].replace('_'+agent.split('_')[-1],'')
	
	# Load Character/Agent Asset
	ika.maya.sgxml.loadAsset(	'char',
								char,
								task='rig',
								subtask='def',
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=charNS,
								sgxmlType=None	)
	
	# Define Agent Nodes
	char_all = charNS+':all'
	if not mc.objExists(char_all): raise Exception('Agent rig all node "'+char_all+'" not found!')
	char_allTrans = charNS+':allTransA'
	if not mc.objExists(char_allTrans): raise Exception('Agent rig allTrans node "'+char_allTrans+'" not found!')
	
	# Position Agent
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# ====================================
	# - Apply Agent (Variation) Settings -
	# ====================================
	
	var_attrList = [	'var_costume',
						'var_costumeColour',
						'var_hair',
						'var_hairGroom',
						'var_hairColour',
						'var_groomColour',
						'var_hairTarget',
						
						'var_arsA_hat',
						'var_shpA_hat',
						'var_twnA_hat',
						'var_twnA_hatA',
						'var_twnA_hatB',
						'var_twnA_derbyHat',
						
						'var_wrkA_suspenders',
						'var_wrkA_waistcoat',
						
						'var_twnA_scarfA',
						'var_twnA_scarfB',
						'var_twnA_scarfC',
							
						'uniformScale'	]
	
	for var_attr in var_attrList:
		if mc.attributeQuery(var_attr,node=layout_all,ex=True):
			try: mc.setAttr(char_all+'.'+var_attr,mc.getAttr(layout_all+'.'+var_attr))
			except: print('Problem setting rig variable attr "'+var_attr+'" for rig "'+charNS+'"!')
	
	# ================
	# - Apply Motion -
	# ================
	
	crowd_body_anim = None
	crowd_body_scale = None
	crowd_body_speed = None
	crowd_body_offset = None
	crowd_body_mirror = None
	crowd_body_infinity = None
	crowd_face_anim = None
	crowd_face_offset = None
	crowd_face_infinity = None
	crowd_lfHand_anim = None
	crowd_lfHand_offset = None
	crowd_lfHand_infinity = None
	crowd_rtHand_anim = None
	crowd_rtHand_offset = None
	crowd_rtHand_infinity = None
	
	if mc.objExists(layout_all+'.crowd_body_anim'): crowd_body_anim = mc.getAttr(layout_all+'.crowd_body_anim')
	if mc.objExists(layout_all+'.crowd_body_scale'): crowd_body_scale = mc.getAttr(layout_all+'.crowd_body_scale')
	if mc.objExists(layout_all+'.crowd_body_speed'): crowd_body_speed = mc.getAttr(layout_all+'.crowd_body_speed')
	if mc.objExists(layout_all+'.crowd_body_offset'): crowd_body_offset = int(mc.getAttr(layout_all+'.crowd_body_offset'))
	if mc.objExists(layout_all+'.crowd_body_mirror'): crowd_body_mirror = bool(mc.getAttr(layout_all+'.crowd_body_mirror'))
	if mc.objExists(layout_all+'.crowd_body_infinity'): crowd_body_infinity = mc.getAttr(layout_all+'.crowd_body_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_face_anim'): crowd_face_anim = mc.getAttr(layout_all+'.crowd_face_anim')
	if mc.objExists(layout_all+'.crowd_face_offset'): crowd_face_offset = int(mc.getAttr(layout_all+'.crowd_face_offset'))
	if mc.objExists(layout_all+'.crowd_face_infinity'): crowd_face_infinity = mc.getAttr(layout_all+'.crowd_face_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_lfHand_anim'): crowd_lfHand_anim = mc.getAttr(layout_all+'.crowd_lfHand_anim')
	if mc.objExists(layout_all+'.crowd_lfHand_offset'): crowd_lfHand_offset = int(mc.getAttr(layout_all+'.crowd_lfHand_offset'))
	if mc.objExists(layout_all+'.crowd_lfHand_infinity'): crowd_lfHand_infinity = mc.getAttr(layout_all+'.crowd_lfHand_infinity',asString=True)
	if mc.objExists(layout_all+'.crowd_rtHand_anim'): crowd_rtHand_anim = mc.getAttr(layout_all+'.crowd_rtHand_anim')
	if mc.objExists(layout_all+'.crowd_rtHand_offset'): crowd_rtHand_offset = int(mc.getAttr(layout_all+'.crowd_rtHand_offset'))
	if mc.objExists(layout_all+'.crowd_rtHand_infinity'): crowd_rtHand_infinity = mc.getAttr(layout_all+'.crowd_rtHand_infinity',asString=True)
	
	# Print Anim/Motion Details
	print('>>> APPLY POSE/ANIM: body anim = '+str(crowd_body_anim))
	print('>>> APPLY POSE/ANIM: body scale = '+str(crowd_body_scale))
	print('>>> APPLY POSE/ANIM: body speed = '+str(crowd_body_speed))
	print('>>> APPLY POSE/ANIM: body offset = '+str(crowd_body_offset))
	print('>>> APPLY POSE/ANIM: body mirror = '+str(crowd_body_mirror))
	print('>>> APPLY POSE/ANIM: body infinity = '+str(crowd_body_infinity))
	
	print('>>> APPLY POSE/ANIM: face anim = '+str(crowd_face_anim))
	print('>>> APPLY POSE/ANIM: face offset = '+str(crowd_face_offset))
	print('>>> APPLY POSE/ANIM: face infinity = '+str(crowd_face_infinity))
	
	print('>>> APPLY POSE/ANIM: lfHand anim = '+str(crowd_lfHand_anim))
	print('>>> APPLY POSE/ANIM: lfHand offset = '+str(crowd_lfHand_offset))
	print('>>> APPLY POSE/ANIM: lfHand infinity = '+str(crowd_lfHand_infinity))
	
	print('>>> APPLY POSE/ANIM: rtHand anim = '+str(crowd_rtHand_anim))
	print('>>> APPLY POSE/ANIM: rtHand offset = '+str(crowd_rtHand_offset))
	print('>>> APPLY POSE/ANIM: rtHand infinity = '+str(crowd_rtHand_infinity))
	
	# Apply Body
	if crowd_body_anim:
		
		isPose = crowd_body_anim.endswith('.pose')
		isAnim = crowd_body_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_body_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_body_anim,targetNS=charNS,frameOffset=crowd_body_offset*-1,infinityOverride=crowd_body_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading BODY anim "'+crowd_body_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
		
		# !!!!! - FIX BROKEN CHANT CLIPS - !!!!!
		mc.cutKey(charNS+':lf_arm_fkA_jnt',at=['sx','sy','sz'])
		mc.cutKey(charNS+':rt_arm_fkA_jnt',at=['sx','sy','sz'])
		if char == 'gen_male_a' or char == 'gen_male_c':
			mc.setAttr(charNS+':lf_arm_fkA_jnt.s',0.85,1.0,1.0)
			mc.setAttr(charNS+':rt_arm_fkA_jnt.s',0.85,1.0,1.0)
		else:
			mc.setAttr(charNS+':lf_arm_fkA_jnt.s',1.0,1.0,1.0)
			mc.setAttr(charNS+':rt_arm_fkA_jnt.s',1.0,1.0,1.0)
		
		# =========================
		# - Mirror Body Animation -
		# =========================
		
		if crowd_body_mirror: glTools.rig.mirrorAnim.mirrorBipedAnim(rigNS=charNS)
		
		# ========================
		# - Scale Body Animation -
		# ========================
		
		# Filter Curves
		glTools.anim.utils.eulerFilter(charNS+':cn_bodyA_jnt')
		# Scale Keys
		glTools.anim.utils.scaleKeyValues(	obj=charNS+':cn_bodyA_jnt',
											attrs=['rx','ry','rz','tx','ty','tz'],
											scale=crowd_body_scale,
											method='average'	)
		
		ctrlList = [	'cn_spineA_jnt',
						'cn_spineB_jnt',
						'cn_spineC_jnt',
						'cn_neckA_jnt',
						'cn_headA_jnt'	]
		
		for ctrl in ctrlList:
			
			# Filter Curves
			glTools.anim.utils.eulerFilter(charNS+':'+ctrl)
			
			# Scale Keys
			glTools.anim.utils.scaleKeyValues(	obj=charNS+':'+ctrl,
												attrs=['rx','ry','rz'],
												scale=crowd_body_scale,
												method='average'	)
		
		# Body Anim Speed
		if crowd_body_speed != None and crowd_body_speed != 1.0:
			glTools.anim.utils.scaleAnimTime(NS=charNS,scale=(1.0/crowd_body_speed),pivot=0.0)
	
	# Apply Face
	if crowd_face_anim:
		isPose = crowd_face_anim.endswith('.pose')
		isAnim = crowd_face_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_face_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_face_anim,targetNS=charNS,frameOffset=crowd_face_offset*-1,infinityOverride=crowd_face_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading FACE anim "'+crowd_face_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Apply Left Hand
	if crowd_lfHand_anim:
		isPose = crowd_lfHand_anim.endswith('.pose')
		isAnim = crowd_lfHand_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_lfHand_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_lfHand_anim,targetNS=charNS,frameOffset=crowd_lfHand_offset*-1,infinityOverride=crowd_lfHand_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading LEFT HAND anim "'+crowd_lfHand_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Apply Right Hand
	if crowd_rtHand_anim:
		isPose = crowd_rtHand_anim.endswith('.pose')
		isAnim = crowd_rtHand_anim.endswith('.anim')
		try:
			if isPose: glTools.tools.animLib.loadPose(crowd_rtHand_anim,targetNS=charNS)
			if isAnim: glTools.tools.animLib.loadAnim(crowd_rtHand_anim,targetNS=charNS,frameOffset=crowd_rtHand_offset*-1,infinityOverride=crowd_rtHand_infinity,applyEulerFilter=True)
		except Exception, e:
			print('MAYA_AGENT_SETUP: Problem loading RIGHT HAND anim "'+crowd_rtHand_anim+'" for agent "'+charNS+'"! Exception MSG: '+str(e))
	
	# Re-Position Agent
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# ===========
	# - Look At -
	# ===========
	
	crowd_lookAt = None
	crowd_lookAt_head = None
	crowd_lookAt_eyes = None
	crowd_lookAt_neck = None
	crowd_lookAt_chest = None
	crowd_lookAt_bake = True
	crowd_lookAt_offset = None
	crowd_lookAt_eyeOffset = None
	
	if mc.objExists(layout_all+'.crowd_lookAt'): crowd_lookAt = mc.getAttr(layout_all+'.crowd_lookAt')
	if mc.objExists(layout_all+'.crowd_lookAt_head'): crowd_lookAt_head = mc.getAttr(layout_all+'.crowd_lookAt_head')
	if mc.objExists(layout_all+'.crowd_lookAt_eyes'): crowd_lookAt_eyes = mc.getAttr(layout_all+'.crowd_lookAt_eyes')
	if mc.objExists(layout_all+'.crowd_lookAt_neck'): crowd_lookAt_neck = mc.getAttr(layout_all+'.crowd_lookAt_neck')
	if mc.objExists(layout_all+'.crowd_lookAt_chest'): crowd_lookAt_chest = mc.getAttr(layout_all+'.crowd_lookAt_chest')
	if mc.objExists(layout_all+'.crowd_lookAt_bake'): crowd_lookAt_bake = mc.getAttr(layout_all+'.crowd_lookAt_bake')
	if mc.objExists(layout_all+'.crowd_lookAt_offset'): crowd_lookAt_offset = mc.getAttr(layout_all+'.crowd_lookAt_offset')
	if mc.objExists(layout_all+'.crowd_lookAt_eyeOffset'): crowd_lookAt_eyeOffset = mc.getAttr(layout_all+'.crowd_lookAt_eyeOffset')
	
	# Create LookAt
	if crowd_lookAt:
		
		# Check LookAt Object
		crowd_lookAt = layoutNS+':'+crowd_lookAt
		if not mc.objExists(crowd_lookAt):
			raise Exception('Agent lookAt object "'+crowd_lookAt+'" does not exist!')
		
		# Print LookAt Details
		print('>>> LOOKAT: target = '+crowd_lookAt)
		print('>>> LOOKAT: headWt = '+str(crowd_lookAt_head))
		print('>>> LOOKAT: eyesWt = '+str(crowd_lookAt_eyes))
		if crowd_lookAt_neck: print('>>> LOOKAT: neckWt = '+str(crowd_lookAt_neck))
		if crowd_lookAt_chest: print('>>> LOOKAT: chestWt = '+str(crowd_lookAt_chest))
		print('>>> LOOKAT: bakeAnim = '+str(bool(crowd_lookAt_bake)))
		print('>>> LOOKAT: offset = '+str(bool(crowd_lookAt_offset)))
		
		# Set SGXML Ignore
		ika.maya.sgxml.setIgnore([crowd_lookAt])
		
		# LookAt Setup
		lookAt_slaves = ['cn_headA_jnt','lf_eye_offset_jnt','rt_eye_offset_jnt']
		lookAt_weights = [crowd_lookAt_head,crowd_lookAt_eyes,crowd_lookAt_eyes]
		lookAt_aimUp = [('y','x'),('z','y'),('z','y')]
		
		# Neck LookAt
		if crowd_lookAt_neck:
			lookAt_slaves.insert(0,'cn_neckA_jnt')
			lookAt_weights.insert(0,crowd_lookAt_neck)
			lookAt_aimUp.insert(0,('y','x'))
		
		# Chest LookAt
		if crowd_lookAt_chest:
			lookAt_slaves.insert(0,'cn_spineC_jnt')
			lookAt_weights.insert(0,crowd_lookAt_chest)
			lookAt_aimUp.insert(0,('y','x'))
		
		# Setup Agent LookAt
		glTools.tools.lookAt.create(	target = crowd_lookAt,
									slaveList = [charNS+':'+i for i in lookAt_slaves],
									slaveAimUp=lookAt_aimUp,
									weightList=lookAt_weights,
									bakeAnim=crowd_lookAt_bake,
									bakeStartEnd=[start,end],
									offsetAnim=crowd_lookAt_offset,
									offset=(0,0,0)	)
		
		# Apply Eye Angle Offset
		if crowd_lookAt_eyeOffset:
			mc.keyframe(charNS+':'+lookAt_slaves[1]+'.ry',e=True,relative=True,valueChange=crowd_lookAt_eyeOffset)
			mc.keyframe(charNS+':'+lookAt_slaves[2]+'.ry',e=True,relative=True,valueChange=-crowd_lookAt_eyeOffset)
	
	# ===============================
	# - Apply Rig Control Overrides -
	# ===============================
	
	applyRigControlAttributeOverrides(layoutNS+':'+agent,charNS)
	
	# =====================
	# - Re-Position Agent -
	# =====================
	
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	# =================
	# - Remove Layout -
	# =================
	
	layoutRef = glTools.utils.reference.getReferenceFromNamespace(layoutNS)
	glTools.utils.reference.removeReference(layoutRef)
	
	# =============================
	# - Save Agent Animation File -
	# =============================
	
	# Set Project To Current Working Directory
	workfileDir = os.path.join(os.environ['TASK_PATH'], 'workfile')
	mm.eval('setProject "%s"' % workfileDir)
	
	# Get Context to Save
	ctx = ctx_util.getContextByType('ShotWorkfile', workfileDir, overrides={'task':'anm', 'subtask':charNS, 'extension':'mb'})
	if outName: ctx = ctx_util.replaceFields(ctx,{'version':'001','workfileDir':ctx['workfileDir']+'/'+outName})
	savePath = os.path.normpath(ctx.getFullPath())
	saveCtx = ctx
	
	mc.file(rename=savePath)
	
	print('>>> Renamed Agent Animation Workfile ('+savePath+')...')
	#print('>>> Saved Agent Animation Workfile ('+savePath+')...')

	# ================
	# - Export Cache -
	# ================
	
	outDir = None
	if outName:
		overrides = {   'deptDir':'vfx',
						'seqDir':'seq',
						'sequence':saveCtx['sequence'],
						'shot':saveCtx['shot'],
						'task':'anm',
						'dataType':'scene_graph',
						'status':'wip',
						'subtask':outName+'/'+charNS,
						'name':'base',
						'version':'002',
						'extension':'xml'    }
		outCtx = ika.context.util.getContextByType('ShotSceneGraphXml',overrides=overrides)
		outDir = os.path.normpath(outCtx.getDir())
	
	if exportScenegraph:
		mayaAgentExport(	start=start,
							end=end,
							outDir=outDir,
							exportMayaScene=True	)
	
	print '>>> Maya Agent Cache Complete!'
	
	# =================
	# - Return Result -
	# =================
	
	return charNS

def mayaAgentSetupLaunch(agents=None,start=None,end=None,outName=None):
	'''
	Launch individual agent creation jobs and submit to the render farm.
	@param agents: List of agents to create animation cache for
	@type agents: list
	@param start: Start frame
	@type start: int or None
	@param end: End frame
	@type end: int or None
	@param outName: Target export sub-directory name
	@type outName: str or None
	'''
	# ====================
	# - Check Agent List -
	# ====================
	
	if not agents:
		print('Getting agents from current selection...')
		agents = mc.ls(sl=1,transforms=True)
	
	if not agents:
		print('Invalid or empty agent list!')
		return
	
	# Check OutName
	ctx = ika.maya.file.getContext()
	if not outName: outName = ctx['subtask']+'.'+ctx['version']
	
	# Check Existing Version
	overrides = {   'deptDir':'vfx',
					'seqDir':ctx['seqDir'],
					'sequence':ctx['sequence'],
					'shot':ctx['shot'],
					'task':ctx['task'],
					'dataType':'scene_graph',
					'status':'wip',
					'subtask':ctx['subtask'],
					'name':'base',
					'version':ctx['version'],
					'extension':'xml'    }
	
	outCtx = ika.context.util.getContextByType('ShotSceneGraphXml',overrides=overrides)
	outDir = os.path.normpath(outCtx.getDir())
	if os.path.isdir(outDir):
		confirm = mc.confirmDialog(title='Current Version Exists', message='Current version exists! Overwrite with new version?',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
		if confirm == 'Cancel':
			print('Export canceled! Version up workfile and try again...')
			return
		else:
			print('New version will overwrite existing crowd export! ('+outDir+')')
	
	# =================
	# - SAVE WORKFILE -
	# =================
	
	# Get Workfile File
	workfile = mc.file(q=True,sn=True)
	workdir = os.path.dirname(workfile)
	
	# Print MSG
	print('Saving workfile for export...')
	
	# Save
	mc.file(save=True)
	
	# ==================
	
	# Get Workfile Context
	ctx = ctx_util.getContext(*os.path.split(workfile))
	seq = ctx['sequence']
	shot = ctx['shot']
	
	# Get Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	# For Each Agent
	NSlist = glTools.utils.namespace.getNSList(agents,topOnly=True)
	for agent in NSlist:
		
		# Check Agent Layout Rig (Subtask)
		ctx = glTools.utils.reference.contextFromNsReferencePath(agent)
		if not dict(ctx)['subtask'] == 'layout':
			print('Agent namespace "'+agent+'" is not a valid asset layout rig! Unable to build agent cache. Skipping...')
			continue
		
		# Build Qube Job Command
		cmd = 'qbsub --name maya_agent_cache.'+seq+'.'+shot+'.'+agent+' --shell /bin/tcsh --cluster /ent/hbm/vfx --restrictions /ent/hbm/+ "set_show hbm_test;'
		cmd += 'cd '+workdir+';'
		cmd += 'start maya_2013 -o VFX_CODE_ROOT:/laika/home/g/glaker/dev/vfx_tools/build/Linux_17 -x mayapy -a /home/g/glaker/maya/bin/mayaAgentSetup.py" '+workfile+' '+agent+' '+str(int(start))+' '+str(int(end))
		if outName: cmd += ' '+outName
		
		# Launch Command
		qbsub = subprocess.Popen(cmd,shell=True).wait()
		if qbsub != None: print('maya_agent_cache.'+seq+'.'+shot+'.'+agent+'('+str(qbsub)+')')
		
		# Pause (0.1 second)
		time.sleep(0.1)
	
	# Return Result
	return NSlist

def mayaAgentSetupApf(	agent,
						callsheetFile='',
						animStart=None,
						animEnd=None,
						animOffset=0,
						loadRig=True,
						bakeAnim=False,
						saveScene=False,
						exportScenegraph=False,
						bpf=True	):
	'''
	Generate an agent animation workfile (massive->maya) from the specified agent APF file.
	@param agent: Agent to load
	@type agent: str
	@param callsheetFile: Crowd simulation callsheet.
	@type callsheetFile: str
	@param animStart: Import agent animation from this frame.
	@type animStart: int
	@param animEnd: Import agent animation from to frame.
	@type animEnd: int
	@param animOffset: Import agent animation with a frame offset.
	@type animOffset: int
	@param loadRig: Attach animation rig to agent animation.
	@type loadRig: bool
	@param bakeAnim: Bake agent animation to rig controls.
	@type bakeAnim: bool
	@param saveScene: Save workfile.
	@type saveScene: bool
	@param exportScenegraph: Export agent scenegraph from animation workfile.
	@type exportScenegraph: bool
	@param bpf: Load agent animation from bpf files, as opposed to ASCII apf files.
	@type bpf: bool
	'''
	# =============================
	# - Check Callsheet and Agent -
	# =============================
	
	# Check Callsheet
	if not callsheetFile:
		filePath = mc.fileDialog2(fileFilter="*.txt",dialogStyle=2,fileMode=1,caption='Load Callsheet',okCaption='Load')
		if not filePath: return
		callsheetFile = filePath[0]
	if not os.path.isfile(callsheetFile):
		raise Exception('Callsheet file "'+callsheetFile+'" does not exist!')
	
	# Check Agent
	callsheet = csh.Callsheet()
	callsheet.open( callsheetFile )
	if not callsheet.loaded():
		raise Exception('Unable to open callsheet!')
	else:
		# list of all agents in a callsheet
		# (this contains an alphabetical number sort/will add a sort by callsheet line)
		agents = callsheet.agents()
		if not agent in agents: raise Exception('Agent "" not found in callsheet!')
	
	# Get APF Path
	apfPath = os.path.dirname(callsheetFile)
	
	# Build CrowdHelper Object
	crowdHelper = chunkified.maya.crowd.CrowdHelper()
	
	# ========================
	# - Set Anim Frame Range -
	# ========================
	
	animFiles = os.listdir(apfPath)
	animFiles.sort(alpha.alphanum)
	animFiles = crowdHelper.clean_animList(animFiles,bpf=bpf)
	
	# Check Start/End
	if animStart == None:
		animStart = crowdHelper.frameFromAnim(animFiles[0])
	if animEnd == None:
		animEnd = crowdHelper.frameFromAnim(animFiles[-1])
	
	# Set Playback Range
	mc.playbackOptions(ast=animStart)
	mc.playbackOptions(min=animStart)
	mc.playbackOptions(max=animEnd)
	mc.playbackOptions(aet=animEnd)
	
	# ===================
	# - Load Agent Anim -
	# ===================
	
	print('>>> Loading Agent Animation ("'+agent+'"): '+str(animStart)+'-'+str(animEnd))
	
	# Load Agent Anim (buildAgent)
	timer = mc.timerX()
	crowdHelper.buildAgent(	agent=agent,
							crowdName='sim_grp',
							animFilePath=apfPath+'/'+animFiles[0],
							callsheetPath=callsheetFile,
							sf=animStart,
							ef=animEnd,
							offset=animOffset	)
	buildTime = mc.timerX(startTime=timer)
	
	print('>>> Agent Anim Build Time: '+str(buildTime))
	
	# Rename Agent Anim Namespace
	animNS = 'sim'
	mc.namespace(rename=[agent,animNS])
	if not mc.namespace(ex=animNS): raise Exception('Agent anim namespace')
	
	# Ignore sim_grp on Export
	sim_grp = 'sim_grp_MOB'
	if mc.objExists(sim_grp): ika.maya.sgxml.setIgnore([sim_grp])
	
	# ==================
	# - Load Agent Rig -
	# ==================
	
	if loadRig:
	
		print('>>> Referencing Agent Rig to Namespace "'+agent+'"...')
		
		charNS = agent
		char = agent.replace('_'+agent.split('_')[-1],'')
		ika.maya.sgxml.loadAsset(	'char',
									char,
									task='rig',
									subtask='def',
									name=None,
									version='latest',
									status='pub',
									xform=None,
									namespace=charNS,
									sgxmlType=None	)
		
		# ========================
		# - Apply Agent Settings -
		# ========================
		
		print('>>> Apply Agent Settings...')
		
		# Get Agent Variables
		agent_vars = callsheet.vars()
		if agent_vars.has_key(agent):
			
			attrList = [	'var_costume',			# [0]
							'var_costumeColour',	# [1]
							'var_hairGroom',		# [2]
							'var_hairColour',		# [3]
							'uniformScale'	]		# [4]
			
			if 'female' in char: attrList[2] = 'var_hair'
			
			# Check Agent Vars
			varList = ['costume_VAR','costume_colour_VAR','hair_colour_VAR','scale_VAR']
			for var in varList:
				if not agent_vars[agent].has_key(var):
					print('Agent variable "'+var+'" not found!')
				
			# Get Costume VARS ---------
			costumeVal = int(agent_vars[agent]['costume_VAR'])+1
			costumeCol = int(agent_vars[agent]['costume_colour_VAR'])
			
			# Apply Costume
			try: mc.setAttr(charNS+':all.'+attrList[0],costumeVal)
			except Exception, e: print('Error setting costume value of '+str(costumeVal)+' for "'+agent+'"! Exception msg: '+str(e))
			else: print('>>> === Costume VAR: '+str(costumeVal))
			
			# Apply Costume Colour
			try: mc.setAttr(charNS+':all.'+attrList[1],costumeCol)
			except Exception, e: print('Error setting costume colour value of '+str(costumeCol)+' for "'+agent+'"! Exception msg: '+str(e))
			else: print('>>> === Costume Colour VAR: '+str(costumeCol))
			
			# Get Groom VARS -----------
			hairVal = costumeVal # Costume Drives Hair/Groom
			hairCol = int(agent_vars[agent]['hair_colour_VAR'])
			
			# Apply Hair
			try: mc.setAttr(charNS+':all.'+attrList[2],costumeVal)
			except Exception, e: print('Error setting hair value of '+str(costumeVal)+' for "'+agent+'"! Exception msg: '+str(e))
			else: print('>>> === Hair VAR: '+str(hairVal))
			
			# Apply Hair Colour
			try: mc.setAttr(charNS+':all.'+attrList[3],hairCol)
			except Exception, e: print('Error setting hair colour value of '+str(hairCol)+' for "'+agent+'"! Exception msg: '+str(e))
			else: print('>>> === Hair Colour VAR: '+str(hairCol))
			
			# Scale
			# - Needs to be updated to use agent_vars when available
			#agentGrp = agent+'_AGENT'
			#if mc.objExists(agentGrp): agentScale = mc.getAttr(agentGrp+'.sx')
			#else: print('Agent group "'+agentGrp+'" not found! Unable to determine agent scale!')
			agentScale = agent_vars[agent]['scale_VAR']
			try: mc.setAttr(charNS+':all.'+attrList[4],agentScale)
			except Exception, e: print('Error setting agent scale value of '+str(agentScale)+' for "'+agent+'"! Exception msg: '+str(e))
			else: print('>>> === Agent Scale VAR: '+str(agentScale))
			
			# ====================
			# - Load Agent Props -
			# ====================
			
			# Get Prop IDs
			lf_propId = 0
			rt_propId = 0
			lf_propId = int(agent_vars[agent]['prop_L_VAR'])
			rt_propId = int(agent_vars[agent]['prop_R_VAR'])
			
			# Load Props
			if lf_propId: mayaAgentProp(animNS+':LeftHandProp',lf_propId)
			if rt_propId: mayaAgentProp(animNS+':RightHandProp',rt_propId)
			
		else:
			
			print('WARNING: Agent variable not found for "'+agent+'"! Using character defaults...')
		
		# ============================
		# - Attach Rig To Agent Anim -
		# ============================
		
		print('>>> Attach Rig...')
		
		# Attach Rig
		mc.currentTime(animStart)
		glTools.anim.mocap_utils.attachRigToMocap(mocapNS=animNS,rigNS=charNS)
		
		# Attach Hand Anim
		glTools.anim.mocap_utils.attachHandAnim(mocapNS=animNS,rigNS=charNS)
		
		# Bake Anim To Rig
		if bakeAnim:
			
			# Set Arms to FK Mode
			mc.setAttr(charNS+':config.lfArmIkFkBlend',1)
			mc.setAttr(charNS+':config.rtArmIkFkBlend',1)
			
			# ========== !!!!!!!!!! ==========
			# - Character Specific Arm Scale -
			# ========== !!!!!!!!!! ==========
			
			if (char == 'gen_male_a') or (char == 'gen_male_c'):
				
				mc.setAttr(charNS+':lf_arm_fkA_jnt.sx',0.85)
				mc.setAttr(charNS+':lf_arm_fkB_jnt.sx',0.85)
				mc.setAttr(charNS+':rt_arm_fkA_jnt.sx',0.85)
				mc.setAttr(charNS+':rt_arm_fkB_jnt.sx',0.85)
				mc.setAttr(charNS+':lf_handA_jnt.s',0.85,0.85,0.85)
				mc.setAttr(charNS+':rt_handA_jnt.s',0.85,0.85,0.85)
			
			# Bake Mocap and Hand Anim
			glTools.anim.mocap_utils.bakeMocapToRig(charNS,start=animStart,end=animEnd,bakeSim=True)
			glTools.anim.mocap_utils.bakeHandAnim(rigNS=charNS,start=animStart,end=animEnd)
		
			# Apply Default Hand Pose --- # Can only default hands after baked anim !!!!
			applyDefaultHands(charNS,poseThreshold=45)
	
			# ============================
			# - Scale Override Animation -
			# ============================
			
			scale = 1
			overrideList = [	'cn_bodyA_overrideTarget_grp',
								'cn_spineA_overrideTarget_grp',
								'cn_spineB_overrideTarget_grp',
								'cn_spineC_overrideTarget_grp',
								'cn_neckA_overrideTarget_grp',
								'cn_headA_overrideTarget_grp'	]
			
			for override in overrideList:
				
				# Filter Curves
				glTools.anim.utils.eulerFilter(charNS+':'+override)
				
				# Scale Keys
				glTools.anim.utils.scaleKeyValues(	obj=charNS+':'+override,
													attrs=['tx','ty','tz','rx','ry','rz'],
													scale=scale,
													method='average'	)
	
	# ========================
	# - Save Agent Anim File -
	# ========================
	
	if saveScene:
	
		# Set Project To Current Working Directory
		workfileDir = os.path.join(os.environ['TASK_PATH'], 'workfile')
		mm.eval('setProject "%s"' % workfileDir)
		
		# Get Context to Save
		ctx = ctx_util.getContextByType('ShotWorkfile', workfileDir, overrides={'task':'anm', 'subtask':charNS, 'extension':'mb'})
		saveCtx = ctx_util.getNewContextToSave(ctx)
		savePath = os.path.normpath(saveCtx.getFullPath())
		
		mc.file(rename=savePath)
		mc.file(save=True,type='mayaBinary')
		
		print('>>> Saved Anim Workfile ('+savePath+')...')
	
		# ================
		# - Export Cache - # Can only export cache for saved scene !!!!
		# ================
		
		if exportScenegraph: mayaAgentExport(animStart,animEnd)
	
	# =================
	# - Return Result -
	# =================
	
	print '>>> Maya Agent Setup Complete!'
	return charNS

def mayaAgentSetupFbx(	agentAnimFile='',
						simDataFile='',
						animStart=1,
						animEnd=0,
						bakeAnim=False,
						exportScenegraph=False	):
	'''
	Generate an agent animation workfile (massive->maya) from the specified agent animation file.
	@param agentAnimFile: Agent animation file from massive (.ma)
	@type agentAnimFile: str
	@param simDataFile: Simulation dat file from massive (.txt) which contains agent settings.
	@type simDataFile: str
	@param animStart: Export agent scenegraph from animation workfile.
	@type animStart: int
	@param animEnd: Export agent scenegraph from animation workfile.
	@type animEnd: int
	@param bakeAnim: Bake agent animation to rig controls.
	@type bakeAnim: bool
	@param exportScenegraph: Export agent scenegraph from animation workfile.
	@type exportScenegraph: bool
	'''
	# =========================
	# - Check Agent Anim File -
	# =========================
	
	# Check Agent Anim
	if not agentAnimFile:
		fileFilter = 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)'
		filePath = mc.fileDialog2(fileFilter=fileFilter,dialogStyle=2,fileMode=1,caption='Load Agent Animation',okCaption='Load')
		if not filePath: return
		agentAnimFile = filePath[0]
	if not os.path.isfile(agentAnimFile):
		raise Exception('Agent animation file "'+agentAnimFile+'" does not exist!')
	
	# Check Sim Data
	if not simDataFile:
		filePath = mc.fileDialog2(fileFilter="*.txt",dialogStyle=2,fileMode=1,caption='Load Sim Data',okCaption='Load')
		if not filePath: return
		simDataFile = filePath[0]
	if not os.path.isfile(simDataFile):
		raise Exception('Sim data file "'+simDataFile+'" does not exist!')
	
	# Parse File Path
	filename = os.path.basename(agentAnimFile)
	char, index, ext = filename.split('.')
	charNS = char+'_'+index
	animNS = 'sim'
	
	# ===================
	# - Load Agent Anim -
	# ===================
	
	print('>>> Referencing Agent Animation ("'+agentAnimFile+'")...')
	
	# Reference Animation File
	mc.file(agentAnimFile,r=True,namespace=animNS,prompt=False,force=True)
	
	# Create Sim Group
	sim_grp = mc.group(em=True,n='sim_grp')
	mc.parent(animNS+':Hips',sim_grp)
	ika.maya.sgxml.setIgnore([sim_grp])
	
	# Scale Animation
	# - Convert Meter to Centimeter (Massive->Maya units)
	mc.setAttr(sim_grp+'.s',0.01,0.01,0.01)
	
	# ========================
	# - Set Anim Frame Range -
	# ========================
	
	# Check Start/End
	if animStart > animEnd:
		keyTime = mc.keyframe(animNS+':Hips',q=True,tc=True)
		keyTime.sort()
		animStart = keyTime[0]
		animEnd = keyTime[-1]
	
	# Set Playback Range
	mc.playbackOptions(ast=animStart)
	mc.playbackOptions(min=animStart)
	mc.playbackOptions(max=animEnd)
	mc.playbackOptions(aet=animEnd)	
	
	# ==================
	# - Load Agent Rig -
	# ==================
	
	print('>>> Referencing Agent Rig...')
	
	ika.maya.sgxml.loadAsset(	'char',
								char,
								task='rig',
								subtask='def',
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=charNS,
								sgxmlType=None	)
	
	# ========================
	# - Apply Agent Settings -
	# ========================
	
	print('>>> Apply Agent Settings...')
	
	# Get Agent Data From File
	agentData = None
	simData = open(simDataFile,'r')
	for item in simData:
		elem = item.split()
		if elem[1] == charNS:
			agentData = str(item).split()
			break
	
	# Check Agent Data
	if not agentData: raise Exception('Unable to find agent entry in sim data file!')
	
	agentNum = agentData[0]
	agentName = agentData[1]
	agentMatrix = [float(i) for i in agentData[2:18]]
	agentFileType = agentData[18]
	agentFilePath = agentData[19]
	agentCostume = int(float(agentData[21]))+1
	agentScale = float(agentData[23])
	agentFromJet = bool(int(float(agentData[25])))
	
	# Costume
	mc.setAttr(charNS+':all.var_costume',agentCostume)
	mc.setAttr(charNS+':all.var_hairGroom',agentCostume)
	
	# Scale
	#mc.setAttr(charNS+':all.uniformScale',agentScale)
	
	# Close Data File
	simData.close()
	
	# =============================
	# - Reposition Agent (Height) -
	# =============================
	
	hipHeight = mc.xform(charNS+':cn_bodyA_jnt',q=True,ws=True,rp=True)[1]
	simHeight = mc.xform(animNS+':Hips',q=True,ws=True,rp=True)[1]
	simOffset = (hipHeight - simHeight)
	mc.move(0,simOffset,0,sim_grp,r=True)
	
	# ============================
	# - Attach Rig To Agent Anim -
	# ============================
	
	print('>>> Attach Rig...')
	
	# Attach Rig
	mc.currentTime(animStart)
	glTools.anim.mocap_utils.attachRigToMocap(mocapNS=animNS,rigNS=charNS)
	
	# Reset Anim Hips
	# - this is getting scaled to ~95 for some reason! WTF!!
	mc.setAttr(animNS+':Hips.s',1,1,1)
	
	# Bake Anim To Rig
	if bakeAnim: glTools.anim.mocap_utils.bakeMocapToRig(charNS,start=animStart,end=animEnd,bakeSim=True)
	
	# ========================
	# - Save Agent Anim File -
	# ========================
	
	# Get Anim Workfile Path via Context
	ctx = ika.maya.file.getContext()
	overrides = dict(ctx)
	overrides.update({'task':'anm','subtask':charNS})
	ctxType = ctx.__class__.__name__
	
	animCtx = ctx_util.getContextByType(ctxType,overrides=overrides)
	saveCtx = ctx_util.getNewContextToSave(animCtx)
	savePath = os.path.normpath(saveCtx.getFullPath())
	
	print('>>> Save Anim Workfile ('+savePath+')...')
	
	mc.file(rename=savePath)
	mc.file(save=True,type='mayaBinary')
	
	# ================
	# - Export Cache -
	# ================
	
	if exportScenegraph: mayaAgentExport(animStart,animEnd)
	
	# ================
	# - Print Result -
	# ================
	
	print '>>> Maya Agent Setup Complete!'

def mayaAgentPrelightCache(workfile,agentNS,exportScenegraph=True,outName=None):
	'''
	Generate agent prelight cache given a layout workfile and an agent name.
	@param workfile: Crowd layout workfile.
	@type workfile: str
	@param agentNS: Agent to load
	@type agentNS: str
	@param exportScenegraph: Export scenegraph and alembic cache
	@type exportScenegraph: bool
	@param outName: Target export sub-directory name
	@type outName: str or None
	'''
	# ========================
	# - Load Layout Workfile -
	# ========================
	
	# Check Layout Workfile
	if not os.path.isfile(workfile):
		raise Exception('Layout workfile "'+workfile+'" does not exist!')
	
	print('>>> Referencing Layout "'+workfile+'"...')
	
	# Get File Type
	fileType = {'.ma':'mayaAscii','.mb':'mayaBinary'}
	fileName, ext = os.path.splitext(workfile)
	
	# Reference Layout
	layoutNS = 'layout'
	mc.file(workfile,reference=True,type=fileType[ext],namespace=layoutNS,returnNewNodes=True)
	
	# ========================
	# - Set Anim Frame Range -
	# ========================
	
	# Set Playback Range
	mc.playbackOptions(ast=1)
	mc.playbackOptions(min=1)
	mc.playbackOptions(max=2)
	mc.playbackOptions(aet=2)
	
	# ====================
	# - Load Agent Asset -
	# ====================
	
	print('>>> Referencing Agent Rig to Namespace "'+agentNS+'"...')
	
	# Get Character Namespace
	charNS = agentNS
	char = charNS.replace('_'+charNS.split('_')[-1],'')
	
	ika.maya.sgxml.loadAsset(	'char',
								char,
								task='rig',
								subtask='def',
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=charNS,
								sgxmlType=None	)
	
	# Define Rig Nodes
	char_all = charNS+':all'
	if not mc.objExists(char_all): raise Exception('Agent rig all node "'+char_all+'" not found!')
	char_allTrans = charNS+':allTransA'
	if not mc.objExists(char_allTrans): raise Exception('Agent rig allTrans node "'+char_allTrans+'" not found!')
	layout_all = layoutNS+':'+agentNS+':all'
	if not mc.objExists(layout_all): raise Exception('Layout rig all node "'+layout_all+'" not found!')
	layout_allTrans = layoutNS+':'+agentNS+':allTransA'
	if not mc.objExists(layout_allTrans): raise Exception('Layout rig allTrans node "'+layout_allTrans+'" not found!')
	
	# ==============
	# - Pose Agent -
	# ==============
	
	# Position Agent
	glTools.utils.transform.match(char_allTrans,layout_allTrans)
	
	poseLoaded = glTools.tools.animLib.applyPose(	targetNS=charNS,
													char=char,
													poseType='Defaults',
													pose='default_pose',
													key=True	)
	
	# Check Pose
	if not poseLoaded: print('Problem loading default pose for agent "'+charNS+'"!')
	
	# ================================
	# - Apply Costume/Groom (Random) -
	# ================================
	
	var_attrList = [	'var_costume',
						'var_hairGroom',
						'var_hair',
						'var_costumeColour',
						'var_hairColour',
						'var_groomColour'	]
	
	for var_attr in var_attrList:
		if mc.attributeQuery(var_attr,node=layout_all,ex=True):
			try: mc.setAttr(char_all+'.'+var_attr,mc.getAttr(layout_all+'.'+var_attr))
			except: print('Error setting rig variable attr "'+var_attr+'" for rig "'+charNS+'"!')
	
	# =================
	# - Remove Layout -
	# =================
	
	layoutRef = glTools.utils.reference.getReferenceFromNamespace(layoutNS)
	glTools.utils.reference.removeReference(layoutRef)
	
	# ============================
	# - Save Agent Prelight File -
	# ============================
	
	# Set Project To Current Working Directory
	workfileDir = os.path.join(os.environ['TASK_PATH'], 'workfile')
	mm.eval('setProject "%s"' % workfileDir)
	
	# Get Context to Save
	ctx = ctx_util.getContextByType('ShotWorkfile', workfileDir, overrides={'task':'anm', 'subtask':charNS, 'extension':'mb'})
	if outName: ctx = ctx_util.replaceFields(ctx,{'version':'001','workfileDir':ctx['workfileDir']+'/'+outName})
	#saveCtx = ctx_util.getNewContextToSave(ctx)
	#savePath = os.path.normpath(saveCtx.getFullPath())
	savePath = os.path.normpath(ctx.getFullPath())
	saveCtx = ctx
	
	# Set Target Workfile Directory (OutName)
	#if outName:
	#	saveDir = workfileDir+'/'+outName
	#	#if not os.path.isdir(saveDir): os.makedirs(saveDir)
	#	savePath = savePath.replace(workfileDir,saveDir)
	
	mc.file(rename=savePath)
	#mc.file(save=True,type='mayaBinary')
	
	print('>>> Renamed Prelight Pose Workfile ('+savePath+')...')
	#print('>>> Saved Prelight Pose Workfile ('+savePath+')...')

	# ================
	# - Export Cache -
	# ================
	
	outDir = None
	if outName:
		overrides = {   'deptDir':'vfx',
						'seqDir':saveCtx['seqDir'],
						'sequence':saveCtx['sequence'],
						'shot':saveCtx['shot'],
						'task':saveCtx['task'],
						'dataType':'scene_graph',
						'status':'wip',
						'subtask':outName+'/'+charNS,
						'name':'base',
						'version':'001',
						'extension':'xml'    }
		
		outCtx = ika.context.util.getContextByType('ShotSceneGraphXml',overrides=overrides)
		outDir = os.path.normpath(outCtx.getDir())
	
	if exportScenegraph:
		mayaAgentExport(	start=1,
							end=2,
							outDir=outDir,
							exportMayaScene=True	)
	
	print '>>> Maya Agent Prelight Export Complete! Workfile saved to export directory ('+outDir+')'
	
	# =================
	# - Return Result -
	# =================
	
	return charNS

def mayaAgentPrelightCacheLaunch(agents=None,outName=None):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not agents:
		print('Getting agents from current selection...')
		agents = mc.ls(sl=1,transforms=True)
	
	if not agents:
		print('Invalid or empty agent list!')
		return
	
	# Check OutName
	ctx = ika.maya.file.getContext()
	if not outName: outName = ctx['subtask']+'.'+ctx['version']
	
	# Check Existing Version
	overrides = {   'deptDir':'vfx',
					'seqDir':'seq',
					'sequence':ctx['sequence'],
					'shot':ctx['shot'],
					'task':'anm',
					'dataType':'scene_graph',
					'status':'wip',
					'subtask':ctx['subtask'],
					'name':'base',
					'version':ctx['version'],
					'extension':'xml'    }
	
	outCtx = ika.context.util.getContextByType('ShotSceneGraphXml',overrides=overrides)
	outDir = os.path.normpath(outCtx.getDir())
	if os.path.isdir(outDir):
		confirm = mc.confirmDialog(title='Current Version Exists', message='Current version exists! Overwrite with new version?',button=['OK','Cancel'],defaultButton='OK',cancelButton='Cancel',dismissString='Cancel')
		if confirm == 'Cancel':
			print('Export canceled! Version up workfile and try again...')
			return
		else:
			print('New version will overwrite existing crowd export! ('+outDir+')')
	
	# =================
	# - SAVE WORKFILE -
	# =================
	
	# Get Workfile File
	workfile = mc.file(q=True,sn=True)
	workdir = os.path.dirname(workfile)
	
	# Print MSG
	print('Saving workfile for export...')
	
	# Save
	mc.file(save=True)
	
	# ==================
	
	# Get Workfile Context
	ctx = ctx_util.getContext(*os.path.split(workfile))
	seq = ctx['sequence']
	shot = ctx['shot']
	
	# For Each Agent
	NSlist = glTools.utils.namespace.getNSList(agents,topOnly=True)
	for agentNS in NSlist:
		
		# Check Agent Layout Rig (Subtask)
		ctx = glTools.utils.reference.contextFromNsReferencePath(agentNS)
		if not dict(ctx)['subtask'] == 'layout':
			print('Agent namespace "'+agentNS+'" is not a valid asset layout rig! Unable to build agent cache. Skipping...')
			continue
		
		# Build Qube Job Command
		cmd = 'qbsub --name maya_agent_cache.'+seq+'.'+shot+'.'+agentNS+' --shell /bin/tcsh --cluster /ent/hbm/vfx --restrictions /ent/hbm/+ "set_show hbm_test;'
		cmd += 'cd '+workdir+';'
		cmd += 'start maya_2013 -o VFX_CODE_ROOT:/laika/home/g/glaker/dev/vfx_tools/build/Linux_17 -x mayapy -a /home/g/glaker/maya/bin/mayaAgentPrelightCache.py" '+workfile+' '+agentNS+' '+outName
		
		# Launch Command
		qbsub = subprocess.Popen(cmd,shell=True).wait()
		if qbsub != None: print('maya_agent_cache.'+seq+'.'+shot+'.'+agentNS+'('+str(qbsub)+')')
		
		# Pause (0.1 second)
		time.sleep(0.1)

def mayaAgentProp(agentPropJnt,propId):
	'''
	Load and attach agent props.
	@param agentPropJnt: Agent prop joint to constrain prop rig to.
	@type agentPropJnt: str
	@param propId: Prop ID number. Load the prop rig for the corresponding prop ID.
	@type propId: int
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not propId:
		print('No prop to load! Prop ID = 0')
		return None
	
	if not mc.objExists(agentPropJnt):
		raise Exception('Agent prop joint "'+agentPropJnt+'" does not exist! Unable to constrain prop...')
	
	# ====================
	# - Define Prop List -
	# ====================
	
	propList = [	None,
					'crate_a',
					'apple_box_a',
					'box_bottle_a',
					'sack_grain_a',
					'barrel_a',
					'barrel_b',
					'barrel_c',
					'barrel_d',
					'bucket_a',
					'sack_gen_a',
					'sack_gen_b',
					'sack_gen_c',
					'sack_gen_d',
					'pitch_fork_a',
					'rake_a',
					'shovel_a',
					'shovel_b',
					'umbrella_a',
					'flower_bouquet',
					'carpet_roll_a'	]
	
	if not propId < len(propList):
		raise Exception('Invalid prop ID! Index out of range.')
	
	propName = propList[propId]
	propNS = propName
	
	# =============
	# - Load Prop -
	# =============
	
	print('>>> Referencing "'+propName+'" Prop Rig...')
	
	ika.maya.sgxml.loadAsset(	'prop',
								propName,
								task='rig',
								subtask='def',
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=propNS,
								sgxmlType=None	)
	
	# ==================
	# - Constrain Prop -
	# ==================
	
	print('>>> Constraining Prop Rig...')
	
	mc.parentConstraint(agentPropJnt,propNS+':allTransA')
	mc.scaleConstraint(agentPropJnt,propNS+':cn_rootA_jnt')
	
	# =================
	# - Return Result -
	# =================
	
	return propNS

def mayaAgentExport(start=None,end=None,outDir=None,exportMayaScene=False):
	'''
	Export agent animation scenegraph
	@param animStart: Animation export start frame. If empty, use timeline minimum.
	@type animStart: int
	@param animEnd: Animation export end frame. If empty, use timeline maximum.
	@type animEnd: int
	@param outDir: Override export location.
	@type outDir: str or None
	@param exportMayaScene: Export maya scene file.
	@type exportMayaScene: str or None
	'''
	# Check Start/End
	if start == None: start = mc.playbackOptions(q=True,min=True)
	if end == None: end = mc.playbackOptions(q=True,max=True)
	
	print('>>> Exporting Agent Cache (SceneGraph)')
	exporter = ika.maya.sgxml.SceneGraphExporter(	startFrame=start,
													endFrame=end,
													outDir=outDir,
													exportMayaScene=exportMayaScene	)
	exporter.export()
	print '>>> Agent cache exported from anim workfile ('+mc.file(q=True,sn=True)+')'
	
def applyDefaultHands(agentNS,poseThreshold=45):
	'''
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Target Namespace
	if agentNS and not mc.namespace(ex=agentNS):
		raise Exception('Agent namespace "'+agentNS+'" does not exist!')
	
	if agentNS: agentNS+=':'
	
	# =======================
	# - Check Existing Pose -
	# =======================
	
	for side in ['lf','rt']:
		
		# Get Hand Module
		handModule = agentNS+side+'_hand_module'
		if not mc.objExists(handModule):
			raise Exception('Hand module "'+handModule+'" does not exist!')
		
		# Get Hand Module Data
		handMod = module.Module()
		handMod.rebuildFromData(handModule)
		
		# Get Hand Joints
		handJnts = []
		for finger in ['thumb','index','middle','ring','pinky']:
			
			# Check Finger
			if not handMod.moduleData.has_key(side+'_handA_'+finger+'_ctrlList'):
				print('Finger module "'+side+'_handA_'+finger+'" not found! Skipping...')
			
			# Get Finger Joints
			[handJnts.append(str(i)) for i in handMod.moduleData[side+'_handA_'+finger+'_ctrlList']]
		
		# Check Joint Rotation (Pose)
		poseTotal = 0.0
		for jnt in handJnts:
			jntParent = mc.listRelatives(jnt,p=True,pa=True)[0]
			for xyz in 'xyz':
				for jntVal in mc.keyframe(jnt+'.r'+xyz,q=True,vc=True) or []:
					poseTotal += jntVal
		
		# Check Pose Total
		if abs(poseTotal) < abs(poseThreshold):
			
			# ==============
			# - Apply Pose -
			# ==============
			
			# Remove Existing Keys
			mc.cutKey(handJnts)
			
			# Load Pose
			glTools.tools.animLib.applyHandPose(	targetNS = agentNS[:-1],
												side = side,
												char = None,
												pose = 'relaxed',
												key = True	)
		
		else:
			
			# Hand Already Posed - Skipping!
			print('"'+side+'_hand" appears to be posed! Skipping...')
	
	# =================
	# - Return Result -
	# =================
	
	return

def applyRigControlAttributeOverrides(srcNS,dstNS):
	'''
	Apply rig control attribute overrides.
	@param srcNS: Crowd layout agent to apply rig control override attributes from.
	@type srcNS: str
	@param srcNS: Crowd anim agent to apply rig control override attributes to.
	@type srcNS: str
	'''
	# ======================
	# - Get Agent All Node -
	# ======================
	
	agent_all = srcNS+':all'
	if not mc.objExists(agent_all):
		print('Rig Control Attribute Override: Agent all node "'+agent_all+'" not found! Unable to apply rig control attribute overrides...')
		return None
	
	# ===============================
	# - Check Rig Control Overrides -
	# ===============================
	
	keyAttr = mc.listAttr(agent_all,k=True)
	if not keyAttr:
		print('Rig Control Attribute Override: No keyable attributes found on "'+agent_all+'"! Unable to apply rig control attribute overrides...')
		return None
	
	# ===============================
	# - Apply Rig Control Overrides -
	# ===============================
	
	overrideAttr = []
	for attr in keyAttr:
		
		# Check Override Attribute
		if not attr.startswith('crowd_override'): continue
		
		# Copy Keys to Clipboard
		keys = mc.copyKey(agent_all+'.'+attr)
		if not keys:
			print('Rig Control Attribute Override: No override keys on rig control override attribute "'+agent_all+'.'+attr+'"! Skipping...')
			continue
		
		# Split Attribute to Name Parts
		at = attr.split('__')
		
		# Check Rig Control
		rigNode = dstNS+':'+at[1]
		if not mc.objExists(rigNode):
			print('Rig Control Attribute Override: Rig control "'+rigNode+'" not found! Unable to apply rig control attribute override...')
			continue
		
		# Check Rig Control Attribute
		rigAttr = rigNode+'.'+at[2]
		if not mc.attributeQuery(at[2],n=rigNode,ex=True):
			print('Rig Control Attribute Override: Rig control attribute "'+rigAttr+'" not found! Unable to apply rig control attribute override...')
			continue
		
		# Paste Keys to Control
		mc.cutKey(rigAttr)
		mc.copyKey(agent_all+'.'+attr)
		mc.pasteKey(rigAttr)
		
		# Append Overridden Rig Attribute to Output
		overrideAttr.append(rigAttr)
	
	# =================
	# - Return Result -
	# =================
	
	return overrideAttr

# ================
# - CROWD Layout -
# ================

def loadLayoutRig(assetName,assetNS='',subtask='layout'):
	'''
	Load crowd layout rig.
	@param assetName: Asset to load rig from.
	@type assetName: str
	@param assetNS: Namespace to load asset into.
	@type assetNS: str
	@param subtask: Asset rig subtask to load.
	@type subtask: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Asset NS
	if not assetNS: assetNS = assetName
	
	# Increment Asset NS to Avoid Namespace Clash
	NSinc = 1
	while mc.namespace(ex=assetNS+'_'+str(NSinc)): NSinc += 1
	assetNS = assetNS+'_'+str(NSinc)
	
	# ============
	# - Load Rig -
	# ============
	
	ika.maya.sgxml.loadAsset(	'char',
								assetName,
								task='rig',
								subtask=subtask,
								name=None,
								version='latest',
								status='pub',
								xform=None,
								namespace=assetNS,
								sgxmlType=None	)
	
	# Select AllTrans Node
	if mc.objExists(assetNS+':allTransA'): mc.select(assetNS+':allTransA')
	
	# =================
	# - Return Result -
	# =================
	
	return assetNS

def unloadLayoutRig(assetNS):
	'''
	Unload crowd layout rig.
	@param assetNS: Namespace to unload.
	@type assetNS: str
	'''
	# Check AllTrans
	allTrans = assetNS+':allTransA'
	if not mc.objExists(allTrans):
		raise Exception('"'+assetNS+'" namespace is not contain a valid crowd layout rig!')
	
	# Get Reference Node
	refNode = glTools.utils.reference.getReferenceFromNamespace(assetNS)
	glTools.utils.reference.removeReference(refNode)
	
	# Delete Namespace
	if mc.namespace(ex=assetNS): glTools.utils.namespace.deleteNS(assetNS)
	
	# Return Result
	return assetNS

def duplicateLayoutRig(assetNS):
	'''
	Duplicate crowd layout rig.
	@param assetNS: Namespace to duplicate.
	@type assetNS: str
	'''
	# Check AllTrans
	allTrans = assetNS+':allTransA'
	if not mc.objExists(allTrans):
		raise Exception('"'+assetNS+'" namespace is not contain a valid crowd layout rig!')
	
	# Get AllTrans Matrix
	allTransMatrix = mc.xform(allTrans,q=True,ws=True,matrix=True)
	
	# Get Asset Context
	assetCtx = glTools.utils.reference.contextFromNsReferencePath(assetNS)
	assetName = assetCtx['asset']
	
	# Load New Layout Rig
	dupNS = loadLayoutRig(assetName,assetNS='',subtask='layout')
	
	# Apply AllTrans Matrix
	allTrans = dupNS+':allTransA'
	mc.xform(allTrans,ws=True,matrix=allTransMatrix)
	mc.select(allTrans)
	
	# Return Result
	return dupNS

def swapLayoutRigOld(assetNS,asset):
	'''
	Swap crowd layout rig.
	@param assetNS: Namespace to unload.
	@type assetNS: str
	@param asset: Asset to swap to.
	@type asset: str
	'''
	# Check AllTrans
	allTrans = assetNS+':allTransA'
	if not mc.objExists(allTrans):
		raise Exception('"'+assetNS+'" namespace is not contain a valid crowd layout rig!')
	
	# Get AllTrans Matrix
	allTransMatrix = mc.xform(allTrans,q=True,ws=True,matrix=True)
	
	# Unload Current Rig
	unloadLayoutRig(assetNS)
	
	# Load New Layout Rig
	assetNS = loadLayoutRig(asset,assetNS=asset,subtask='layout')
	
	# Apply AllTrans Matrix
	allTrans = assetNS+':allTransA'
	mc.xform(allTrans,ws=True,matrix=allTransMatrix)
	mc.select(allTrans)
	
	# Return Result
	return assetNS

def swapLayoutRig(assetNS,asset):
	'''
	Swap crowd layout rig.
	@param assetNS: Namespace to unload.
	@type assetNS: str
	@param asset: Asset to swap to.
	@type asset: str
	'''
	# Get Active Selection
	sel = mc.ls(sl=True,transforms=True)
	
	# Check AllTrans
	allTrans = assetNS+':allTransA'
	if not mc.objExists(allTrans):
		raise Exception('"'+assetNS+'" namespace is not contain a valid crowd layout rig!')
	
	# Swap Asset
	refNode = glTools.utils.reference.getReferenceNode(allTrans)
	refPath = glTools.utils.reference.getReferenceFile(refNode,withoutCopyNumber=True)
	oldAsset = dict(glTools.utils.reference.contextFromNsReferencePath(assetNS))['asset']
	swapAssetPath = refPath.replace(oldAsset,asset)
	glTools.utils.reference.replaceReference(refNode,swapAssetPath,verbose=True)
	refPath = glTools.utils.reference.getReferenceFile(refNode,withoutCopyNumber=False)
	
	# Rename Namespace
	NSinc = 1
	swapAssetNS = asset
	while mc.namespace(ex=swapAssetNS+'_'+str(NSinc)): NSinc += 1
	swapAssetNS = swapAssetNS+'_'+str(NSinc)
	print('Renaming asset namespace "'+assetNS+'" >> "'+swapAssetNS+'"...')
	mc.file(refPath,e=True,referenceNode=refNode,namespace=swapAssetNS)
	
	# Fix Top Node NS
	top = assetNS+':top'
	if mc.objExists(top):
		try: mc.rename(top,swapAssetNS+':top')
		except Exception, e: print('Unable to rename asset top node NS "'+assetNS+'" >> "'+assetNS+'"! Exception Msg: '+str(e))
	
	# Delete Old NS
	oldNSnodes = mc.ls(assetNS+':*')
	if not oldNSnodes:
		try: glTools.utils.namespace.deleteNS(assetNS)
		except Exception, e: print('Error deleteing namespace "'+assetNS+'"! Exception Msg: '+str(e))
	else:
		print('Removed asset namespace "'+assetNS+'" still contains nodes! Skipping namespace delete...')
		print(oldNSnodes)
	
	# Restore Selection
	newSel = []
	for item in sel:
		if item.startswith(assetNS): item = item.replace(assetNS,swapAssetNS)
		if mc.objExists(item): newSel.append(item)
	if newSel: mc.select(newSel)
	
	# Return Result
	return swapAssetNS

def unloadSelectedLayoutRig():
	'''
	Unload selected crowd layout rig.
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Unload Selected
	for assetNS in NSlist: unloadLayoutRig(assetNS)
	
	# Return Result
	return NSlist

def duplicateSelectedLayoutRig():
	'''
	Duplicate selected crowd layout rig.
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Unload Selected
	for assetNS in NSlist: duplicateLayoutRig(assetNS)
	
	# Return Result
	return NSlist

def swapSelectedLayoutRig(asset):
	'''
	Swap selected crowd layout rig.
	@param asset: Asset to swap to.
	@type asset: str
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Unload Selected
	for assetNS in NSlist: swapLayoutRig(assetNS,asset)
	
	# Return Result
	return NSlist

# =========================
# - Procedural Crowd Anim -
# =========================

def loadAgentLayoutRig(agentList=None,deleteOrig=False):
	'''
	'''
	# Check Agent List
	if agentList: mc.select(agentList)
	if not agentList:
		print('Load Agent Layout Rig: Getting agent list from current selection')
		agentList = mc.ls(sl=True,transforms=True)
	if not agentList:
		print('Load Agent Layout Rig: Invalid or empty agent list')
		return
	
	# Load Layout Rig(s)
	print('Load Agent Layout Rig: Loading...')
	glTools.anim.rig_utils.replaceSelectionWithRigs(	asset=None,
													assetType='char',
													subtask='layout',
													version='latest',
													status='pub',
													applyAnim=False,
													deleteOrig=deleteOrig	)
	
	# Set Costume Values
	print('Load Agent Layout Rig: Costume Match...')
	setLayoutCostumeFromOrig([agent+':all'for agent in agentList])

def setLayoutCostumeFromOrig(agentList):
	'''
	'''
	# Get Selected Namespaces
	agentNSlist = glTools.utils.namespace.getNSList(agentList,topOnly=True)
	if not agentNSlist: return
	
	costumeMap = {	'arsA':'aristocrat',
					'shpA':'shopkeeper',
					'shpB':'shopkeeper',
					'twnA':'townsfolk',
					'twnB':'townsfolk',
					'wrkA':'workman'	}
	
	for agent in agentNSlist:
		
		# Get Agent All Node
		agentAll = agent+':all'
		if not mc.objExists(agentAll):
			raise Exception('Agent rig all node object "'+agentAll+'" not found!')
		# Get Agent Orig
		agentOrig = agent+'_orig'
		if not mc.objExists(agentOrig):
			raise Exception('Unable to determine original agent object from agent namespace "'+agent+'"!')
		
		# Get Visible Costume
		costumeList = mc.listRelatives(agentOrig+'|costume',c=True)
		costumeVis = [agentOrig+'|costume|'+n for n in costumeList if mc.getAttr(agentOrig+'|costume|'+n+'.v')]
		costumeGrp = costumeVis[0].split('|')[-1]
		
		# Check Costume Key
		if not costumeMap.has_key(costumeGrp): raise Exception('Unknown costume key "'+costumeGrp+'"!')
		
		# ===========================
		# - Set Agent Costume/Groom -
		# ===========================
		
		# Set Costume
		costumeEnum = [i.lower() for i in mc.attributeQuery('var_costume',n=agentAll,listEnum=True)[0].split(':')]
		for i in range(len(costumeEnum)):
			if costumeEnum[i].startswith(costumeMap[costumeGrp]):
				mc.setAttr(agentAll+'.var_costume',i)
				break
		
		# Set Groom (Males)
		if mc.attributeQuery('var_hairGroom',n=agentAll,ex=True):
			groomEnum = [i.lower() for i in mc.attributeQuery('var_hairGroom',n=agentAll,listEnum=True)[0].split(':')]
			for i in range(len(groomEnum)):
				if groomEnum[i].startswith(costumeMap[costumeGrp]):
					mc.setAttr(agentAll+'.var_hairGroom',i)
					break
		
		# Set Hair (Females)
		if mc.attributeQuery('var_hair',n=agentAll,ex=True):
			hairEnum = [i.lower() for i in mc.attributeQuery('var_hair',n=agentAll,listEnum=True)[0].split(':')]
			for i in range(len(hairEnum)):
				if hairEnum[i].startswith(costumeMap[costumeGrp]):
					mc.setAttr(agentAll+'.var_hair',i)
					break
	
	# =================
	# - Return Result -
	# =================
	
	return agentNSlist

def addAgentAnimAttrs(rigNS):
	'''
	Add procedural crowd animation attributes to the specified rig namespace.
	The rig namespace must be a referenced "layout" subtask rig.
	@param rigNS: Rig namespace to add procedural crowd animation attributes to.
	@type rigNS: str
	'''
	# =============
	# - Check Rig -
	# =============
	
	# Check Rig All Node
	all = rigNS+':all'
	if not mc.objExists(all):
		raise Exception('Rig all node "'+all+'" not found! Unable to add attributes.')
	
	# Check Subtask
	ctx = glTools.utils.reference.contextFromNsReferencePath(rigNS)
	subtask = dict(ctx)['subtask']
	if subtask != 'layout':
		raise Exception('Rig "'+rigNS+'" is not a valid layout rig! Switch rig subtask and retry.')
	
	# =============================
	# - Add Crowd Anim Attributes -
	# =============================
	
	# Body
	if not mc.attributeQuery('crowd_body_anim',n=all,ex=True):
		mc.addAttr(all,ln='crowd_body_anim',dt='string')
	if not mc.attributeQuery('crowd_body_scale',n=all,ex=True):
		mc.addAttr(all,ln='crowd_body_scale',at='float',min=0.0,max=5.0,dv=1.0)
	if not mc.attributeQuery('crowd_body_offset',n=all,ex=True):
		mc.addAttr(all,ln='crowd_body_offset',at='float')
	if not mc.attributeQuery('crowd_body_infinity',n=all,ex=True):
		mc.addAttr(all,ln='crowd_body_infinity',at='enum',en='default:constant:linear:cycle:cycleRelative:oscillate')
	
	# Face
	if not mc.attributeQuery('crowd_face_anim',n=all,ex=True):
		mc.addAttr(all,ln='crowd_face_anim',dt='string')
	if not mc.attributeQuery('crowd_face_offset',n=all,ex=True):
		mc.addAttr(all,ln='crowd_face_offset',at='float')
	if not mc.attributeQuery('crowd_face_infinity',n=all,ex=True):
		mc.addAttr(all,ln='crowd_face_infinity',at='enum',en='default:constant:linear:cycle:cycleRelative:oscillate')
	
	# Hands
	if not mc.attributeQuery('crowd_lfHand_anim',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lfHand_anim',dt='string')
	if not mc.attributeQuery('crowd_lfHand_offset',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lfHand_offset',at='float')
	if not mc.attributeQuery('crowd_lfHand_infinity',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lfHand_infinity',at='enum',en='default:constant:linear:cycle:cycleRelative:oscillate')
		
	if not mc.attributeQuery('crowd_rtHand_anim',n=all,ex=True):
		mc.addAttr(all,ln='crowd_rtHand_anim',dt='string')
	if not mc.attributeQuery('crowd_rtHand_offset',n=all,ex=True):
		mc.addAttr(all,ln='crowd_rtHand_offset',at='float')
	if not mc.attributeQuery('crowd_rtHand_infinity',n=all,ex=True):
		mc.addAttr(all,ln='crowd_rtHand_infinity',at='enum',en='default:constant:linear:cycle:cycleRelative:oscillate')
	
	# LookAt
	if not mc.attributeQuery('crowd_lookAt',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lookAt',dt='string')
	if not mc.attributeQuery('crowd_lookAt_head',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lookAt_head',at='float',min=0,max=100,dv=50)
	if not mc.attributeQuery('crowd_lookAt_eyes',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lookAt_eyes',at='float',min=0,max=100,dv=100)
	if not mc.attributeQuery('crowd_lookAt_offset',n=all,ex=True):
		mc.addAttr(all,ln='crowd_lookAt_offset',at='float')
	
	# =================
	# - Return Result -
	# =================
	
	return all

def addAgentAnimAttrsToSel():
	'''
	Add procedural crowd animation attributes to the selected rig namespaces.
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Add Procedural Crowd Anim Attrs
	for rigNS in NSlist: addAgentAnimAttrs(rigNS)
	
	# Return Result
	return NSlist

def applyAgentLookAt(rigNS,lookAt,headWt=0.5,eyesWt=1.0,bake=False,offset=0):
	'''
	Add procedural crowd animation "lookAt" attribute values to the specified rig namespace.
	@param rigNS: Rig namespace to add procedural crowd animation "lookAt" attribute values to.
	@type rigNS: str
	@param lookAt: Procedural crowd animation "lookAt" transform target.
	@type lookAt: str
	@param headWt: LookAt head weight.
	@type headWt: float or int
	@param eyesWt: LookAt eyes weight.
	@type eyesWt: float or int
	@param bake: Bake lookAt animation to rig controls.
	@type bake: bool
	@param offset: LookAt bake animation offset. Only applied when "bake" is True.
	@type offset: float or int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Rig All Node
	all = rigNS+':all'
	if not mc.objExists(all):
		raise Exception('Rig all node "'+all+'" not found! Unable to add attributes.')
	
	# Check LookAt Attribute
	lookAtAttr = all+'.crowd_lookAt'
	if not mc.objExists(lookAtAttr):
		raise Exception('Rig lookAt attribute "'+lookAtAttr+'" not found! Run addAgentAnimAttrs() to add procedural crowd animation attributes.')
	
	# Check LookAt
	if not mc.objExists(lookAt):
		raise Exception('Specified lookAt object "'+lookAt+'" not found!')
	if not glTools.utils.transform.isTransform(lookAt):
		raise Exception('Specified lookAt object "'+lookAt+'" is not a valid transform!')
	
	# ================
	# - Apply LookAt -
	# ================
	
	mc.setAttr(lookAtAttr,lookAt,type='string')
	mc.setAttr(all+'.crowd_lookAt_head',headWt)
	mc.setAttr(all+'.crowd_lookAt_eyes',eyesWt)
	mc.setAttr(all+'.crowd_lookAt_bake',bake)
	mc.setAttr(all+'.crowd_lookAt_offset',offset)
	
	# =================
	# - Return Result -
	# =================
	
	return all

def applyAgentLookAtToSel(lookAt,headWt=(0.5,0.65),eyesWt=(0.85,1.0),bake=False,offset=(-10,10)):
	'''
	Add procedural crowd animation "lookAt" attribute values to the selected rig namespaces.
	Head and eyes lookAt weight and bake offset values will be randomly generated between the min and max values specified.
	@param lookAt: Procedural crowd animation "lookAt" transform target.
	@type lookAt: str
	@param headWt: LookAt head weight range min and max. (min,max)
	@type headWt: list or tuple
	@param eyesWt: LookAt eyes weight range min and max. (min,max)
	@type eyesWt: list or tuple
	@param bake: Bake lookAt animation to rig controls.
	@type bake: bool
	@param offset: LookAt bake animation offset range min and max. (min,max)
	@type offset: list or tuple
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# Add Procedural Crowd Anim Attrs
	for rigNS in NSlist:
		applyAgentLookAt(	rigNS=rigNS,
						lookAt=lookAt,
						headWt=headWt[0] + ( (headWt[1]-headWt[0]) * random.random() ),
						eyesWt=eyesWt[0] + ( (eyesWt[1]-eyesWt[0]) * random.random() ),
						bake=bake,
						offset=offset[0] + ( (offset[1]-offset[0]) * random.random() )	)
	
	# Return Result
	return NSlist

def applyAgentAnim(rigNS,animFile,animType='body',animOffset=0):
	'''
	Apply procedural crowd anim attribute values
	@param rigNS: Rig namespace to add procedural crowd animation "lookAt" attribute values to.
	@type rigNS: str
	@param animFile: Procedural crowd anim (or pose) file path.
	@type animFile: str
	@param animType: Anim type. "body", "face", "lfHand" or "rtHand".
	@type animType: str
	@param animOffset: Animation frame offset to apply to loaded animation.
	@type animOffset: float or int
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Rig All Node
	all = rigNS+':all'
	if not mc.objExists(all):
		raise Exception('Rig all node "'+all+'" not found! Unable to add attributes.')
	
	# Check Anim Attributes
	animAttr = all+'.crowd_'+animType+'_anim'
	if not mc.objExists(animAttr):
		raise Exception('Rig crowd anim attribute "'+animAttr+'" not found! Run addAgentAnimAttrs() to add procedural crowd animation attributes.')
	offsetAttr = all+'.crowd_'+animType+'_offset'
	if not mc.objExists(offsetAttr):
		raise Exception('Rig crowd anim offset attribute "'+offsetAttr+'" not found! Run addAgentAnimAttrs() to add procedural crowd animation attributes.')
	
	# Check Animation File Path
	if not os.path.isfile(animFile):
		raise Exception('Anim file path "'+animFile+'" does not exist!')
	
	# ===================
	# - Apply Animation -
	# ===================
	
	mc.setAttr(animAttr,animFile,type='string')
	mc.setAttr(offsetAttr,animOffset)
	
	# =================
	# - Return Result -
	# =================
	
	return all

def applyAgentAnimToSel(animFileList,animType='body',animOffset=[-10,0]):
	'''
	Apply procedural crowd anim attribute values to selected rigs.
	@param animFile: Procedural crowd anim (or pose) file path.
	@type animFile: str
	@param animType: Anim type. "body", "face", "lfHand" or "rtHand".
	@type animType: str
	@param animOffset: Animation frame offset to apply to loaded animation.
	@type animOffset: float or int
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	animFileChoice = range(len(animFileList))
	
	# Add Procedural Crowd Anim Attrs
	for rigNS in NSlist:
		applyAgentAnim(	rigNS=rigNS,
						animFile=animFileList[choice(animFileChoice)],
						animType=animType,
						animOffset=animOffset[0] + ( (animOffset[1]-animOffset[0]) * random.random() )	)
		
	# Return Result
	return NSlist

# ==============================
# - Apply Crowd Agent Settings -
# ==============================

def applyCrowdAgentSettingsUI():
	'''
	'''
	# Window
	window = 'mayaAgentSettingsUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Apply Crowd Agent Settings',resizeToFitChildren=True)
	
	# ===============
	# - UI Elements -
	# ===============
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# Body Anim
	agentBodyAnimFRL = mc.frameLayout(label='Agent Body Anim',collapsable=True,cl=False,p=FL)
	agentBodyAnimFL = mc.formLayout(numberOfDivisions=100)
	agentBodyAnimTSL = mc.textScrollList('agentSettings_bodyAnimTSL',allowMultiSelection=False)
	agentBodyScaleFFG = mc.floatFieldGrp('agentSettings_bodyScaleFFG',numberOfFields=2,label='Scale Min/Max',value1=0.75,value2=1.25,precision=2)
	agentBodyOffsetIFG = mc.intFieldGrp('agentSettings_bodyOffsetIFG',numberOfFields=2,label='Offset Min/Max',value1=-10,value2=10)
	agentBodyInfinityOMG = mc.optionMenuGrp('agentSettings_bodyInfinityOMG',label='Pre/Post Infinity')
	
	mc.menuItem(l='default')
	mc.menuItem(l='constant')
	mc.menuItem(l='linear')
	mc.menuItem(l='cycle')
	mc.menuItem(l='cycleRelative')
	mc.menuItem(l='oscillate')
	
	# Face Anim
	agentFaceAnimFRL = mc.frameLayout(label='Agent Face Anim',collapsable=True,cl=False,p=FL)
	agentFaceAnimFL = mc.formLayout(numberOfDivisions=100)
	agentFaceAnimTSL = mc.textScrollList('agentSettings_faceAnimTSL',allowMultiSelection=False)
	agentFaceOffsetIFG = mc.intFieldGrp('agentSettings_faceOffsetIFG',numberOfFields=2,label='Offset Min/Max',value1=-10,value2=10)
	agentFaceInfinityOMG = mc.optionMenuGrp('agentSettings_faceInfinityOMG',label='Pre/Post Infinity')
	
	mc.menuItem(l='default')
	mc.menuItem(l='constant')
	mc.menuItem(l='linear')
	mc.menuItem(l='cycle')
	mc.menuItem(l='cycleRelative')
	mc.menuItem(l='oscillate')
	
	# Left Hand Anim
	agentLfHandAnimFRL = mc.frameLayout(label='Agent Left Hand Anim',collapsable=True,cl=False,p=FL)
	agentLfHandAnimFL = mc.formLayout(numberOfDivisions=100)
	agentLfHandAnimTSL = mc.textScrollList('agentSettings_lfHandAnimTSL',allowMultiSelection=False)
	agentLfHandOffsetIFG = mc.intFieldGrp('agentSettings_lfHandOffsetIFG',numberOfFields=2,label='Offset Min/Max',value1=-10,value2=10)
	agentLfHandInfinityOMG = mc.optionMenuGrp('agentSettings_lfHandInfinityOMG',label='Pre/Post Infinity')
	
	mc.menuItem(l='default')
	mc.menuItem(l='constant')
	mc.menuItem(l='linear')
	mc.menuItem(l='cycle')
	mc.menuItem(l='cycleRelative')
	mc.menuItem(l='oscillate')
	
	# Right Hand Anim
	agentRtHandAnimFRL = mc.frameLayout(label='Agent Right Hand Anim',collapsable=True,cl=False,p=FL)
	agentRtHandAnimFL = mc.formLayout(numberOfDivisions=100)
	agentRtHandAnimTSL = mc.textScrollList('agentSettings_rtHandAnimTSL',allowMultiSelection=False)
	agentRtHandOffsetIFG = mc.intFieldGrp('agentSettings_rtHandOffsetIFG',numberOfFields=2,label='Offset Min/Max',value1=-10,value2=10)
	agentRtHandInfinityOMG = mc.optionMenuGrp('agentSettings_rtHandInfinityOMG',label='Pre/Post Infinity')
	
	mc.menuItem(l='default')
	mc.menuItem(l='constant')
	mc.menuItem(l='linear')
	mc.menuItem(l='cycle')
	mc.menuItem(l='cycleRelative')
	mc.menuItem(l='oscillate')
	
	# LookAt
	agentLookAtFRL = mc.frameLayout(label='Agent LookAt',collapsable=True,cl=False,p=FL)
	agentLookAtFL = mc.formLayout(numberOfDivisions=100)
	agentLookAtTargetTFB = mc.textFieldButtonGrp('agentSettings_lookAtTargetTFB',label='LookAt Target',text='',buttonLabel='<<<')
	agentLookAtHeadWtIFG = mc.intFieldGrp('agentSettings_lookAtHeadWtIFG',numberOfFields=2,label='Head Min/Max',value1=50,value2=75)
	agentLookAtEyesWtIFG = mc.intFieldGrp('agentSettings_lookAtEyesWtIFG',numberOfFields=2,label='Eyes Min/Max',value1=85,value2=100)
	agentLookAtOffsetIFG = mc.intFieldGrp('agentSettings_lookAtOffsetIFG',numberOfFields=2,label='Offset Min/Max',value1=-10,value2=10)
	
	# Apply Button
	applyB = mc.button(l='Apply Agent Settings',p=FL,c='glTools.tools.crowd.applyCrowdAgentSettingsFromUI()')
	
	# ===============
	# - Popup Menus -
	# ===============
	
	# For Each TextScrollList
	for TSL in [agentBodyAnimTSL,agentFaceAnimTSL,agentLfHandAnimTSL,agentRtHandAnimTSL]:
		
		# Create Popup Menu
		mc.popupMenu(p=TSL)
		
		# Add Menu Items
		mc.menuItem(l='Load Pose/Anim',c='glTools.tools.crowd.loadCrowdAgentAnimToUI("'+TSL+'")')
		mc.menuItem(l='Remove Selected',c='glTools.ui.utils.removeFromTSL("'+TSL+'")')
		mc.menuItem(l='Clear All',c='mc.textScrollList("'+TSL+'",e=True,ra=True)')
	
	# ================
	# - UI Callbacks -
	# ================
	
	mc.textFieldButtonGrp(agentLookAtTargetTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+agentLookAtTargetTFB+'")')
	
	# ================
	# - Form Layouts -
	# ================
	
	mc.formLayout(agentBodyAnimFL,e=True,af=[(agentBodyAnimTSL,'top',5),(agentBodyAnimTSL,'left',5),(agentBodyAnimTSL,'right',5)],ac=[(agentBodyAnimTSL,'bottom',5,agentBodyScaleFFG)])
	mc.formLayout(agentBodyAnimFL,e=True,af=[(agentBodyInfinityOMG,'bottom',5),(agentBodyInfinityOMG,'left',5),(agentBodyInfinityOMG,'right',5)])
	mc.formLayout(agentBodyAnimFL,e=True,af=[(agentBodyOffsetIFG,'left',5),(agentBodyOffsetIFG,'right',5)],ac=[(agentBodyOffsetIFG,'bottom',5,agentBodyInfinityOMG)])
	mc.formLayout(agentBodyAnimFL,e=True,af=[(agentBodyScaleFFG,'left',5),(agentBodyScaleFFG,'right',5)],ac=[(agentBodyScaleFFG,'bottom',5,agentBodyOffsetIFG)])
	
	mc.formLayout(agentFaceAnimFL,e=True,af=[(agentFaceAnimTSL,'top',5),(agentFaceAnimTSL,'left',5),(agentFaceAnimTSL,'right',5)],ac=[(agentFaceAnimTSL,'bottom',5,agentFaceOffsetIFG)])
	mc.formLayout(agentFaceAnimFL,e=True,af=[(agentFaceInfinityOMG,'bottom',5),(agentFaceInfinityOMG,'left',5),(agentFaceInfinityOMG,'right',5)])
	mc.formLayout(agentFaceAnimFL,e=True,af=[(agentFaceOffsetIFG,'left',5),(agentFaceOffsetIFG,'right',5)],ac=[(agentFaceOffsetIFG,'bottom',5,agentFaceInfinityOMG)])
	
	mc.formLayout(agentLfHandAnimFL,e=True,af=[(agentLfHandAnimTSL,'top',5),(agentLfHandAnimTSL,'left',5),(agentLfHandAnimTSL,'right',5)],ac=[(agentLfHandAnimTSL,'bottom',5,agentLfHandOffsetIFG)])
	mc.formLayout(agentLfHandAnimFL,e=True,af=[(agentLfHandInfinityOMG,'bottom',5),(agentLfHandInfinityOMG,'left',5),(agentLfHandInfinityOMG,'right',5)])
	mc.formLayout(agentLfHandAnimFL,e=True,af=[(agentLfHandOffsetIFG,'left',5),(agentLfHandOffsetIFG,'right',5)],ac=[(agentLfHandOffsetIFG,'bottom',5,agentLfHandInfinityOMG)])
	
	mc.formLayout(agentRtHandAnimFL,e=True,af=[(agentRtHandAnimTSL,'top',5),(agentRtHandAnimTSL,'left',5),(agentRtHandAnimTSL,'right',5)],ac=[(agentRtHandAnimTSL,'bottom',5,agentRtHandOffsetIFG)])
	mc.formLayout(agentRtHandAnimFL,e=True,af=[(agentRtHandInfinityOMG,'bottom',5),(agentRtHandInfinityOMG,'left',5),(agentRtHandInfinityOMG,'right',5)])
	mc.formLayout(agentRtHandAnimFL,e=True,af=[(agentRtHandOffsetIFG,'left',5),(agentRtHandOffsetIFG,'right',5)],ac=[(agentRtHandOffsetIFG,'bottom',5,agentRtHandInfinityOMG)])
	
	mc.formLayout(agentLookAtFL,e=True,af=[(agentLookAtTargetTFB,'top',5),(agentLookAtTargetTFB,'left',5),(agentLookAtTargetTFB,'right',5)])
	mc.formLayout(agentLookAtFL,e=True,af=[(agentLookAtHeadWtIFG,'left',5),(agentLookAtHeadWtIFG,'right',5)],ac=[(agentLookAtHeadWtIFG,'top',5,agentLookAtTargetTFB)])
	mc.formLayout(agentLookAtFL,e=True,af=[(agentLookAtEyesWtIFG,'left',5),(agentLookAtEyesWtIFG,'right',5)],ac=[(agentLookAtEyesWtIFG,'top',5,agentLookAtHeadWtIFG)])
	mc.formLayout(agentLookAtFL,e=True,af=[(agentLookAtOffsetIFG,'left',5),(agentLookAtOffsetIFG,'right',5)],ac=[(agentLookAtOffsetIFG,'top',5,agentLookAtEyesWtIFG)])
	
	mc.formLayout(FL,e=True,af=[(agentBodyAnimFRL,'top',5),(agentBodyAnimFRL,'left',5),(agentBodyAnimFRL,'right',5)])
	mc.formLayout(FL,e=True,af=[(agentFaceAnimFRL,'left',5),(agentFaceAnimFRL,'right',5)],ac=[(agentFaceAnimFRL,'top',5,agentBodyAnimFRL)])
	mc.formLayout(FL,e=True,af=[(agentLfHandAnimFRL,'left',5),(agentLfHandAnimFRL,'right',5)],ac=[(agentLfHandAnimFRL,'top',5,agentFaceAnimFRL)])
	mc.formLayout(FL,e=True,af=[(agentRtHandAnimFRL,'left',5),(agentRtHandAnimFRL,'right',5)],ac=[(agentRtHandAnimFRL,'top',5,agentLfHandAnimFRL)])
	mc.formLayout(FL,e=True,af=[(agentLookAtFRL,'left',5),(agentLookAtFRL,'right',5)],ac=[(agentLookAtFRL,'top',5,agentRtHandAnimFRL)])
	mc.formLayout(FL,e=True,af=[(applyB,'bottom',5),(applyB,'left',5),(applyB,'right',5)])
	
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)

def loadCrowdAgentAnimToUI(TSL):
	'''
	'''
	# Get Selected File List
	startDir = glTools.tools.animLib.animLibRoot()
	fileList = mc.fileDialog2(dir=startDir,fileFilter='Pose/Anim Files (*.anim *.pose)',dialogStyle=2,fileMode=4,okCaption='Load',caption='Load Agent Pose/Anim') or []
	
	for i in range(len(fileList)):
		
		fileItem = fileList[i]
		
		# Generalize Paths
		fileItem = fileItem.replace('gen_male_a','gen_*')
		fileItem = fileItem.replace('gen_male_b','gen_*')
		fileItem = fileItem.replace('gen_male_c','gen_*')
		fileItem = fileItem.replace('gen_male_d','gen_*')
		fileItem = fileItem.replace('gen_female_a','gen_*')
		fileItem = fileItem.replace('gen_female_b','gen_*')
		fileItem = fileItem.replace('gen_female_c','gen_*')
		fileItem = fileItem.replace('gen_boy_a','gen_*')
		fileItem = fileItem.replace('gen_girl_b','gen_*')
		
		# Add to List
		if not fileItem in (mc.textScrollList(TSL,q=True,ai=True) or []):
			mc.textScrollList(TSL,e=True,a=fileItem)
			

def applyCrowdAgentSettingsFromUI():
	'''
	'''
	# Get Selected Namespaces
	sel = mc.ls(sl=True,o=True)
	agentList = glTools.utils.namespace.getNSList(sel,topOnly=True)
	
	# For Each Agent
	for agent in agentList:
		
		# Define Agent All Node
		agent_all = agent+':all'
		agent_ctx = glTools.utils.reference.contextFromNsReferencePath(agent)
		agent_char = agent_ctx['asset']
		
		# Add Attributes
		addAgentAnimAttrs(agent)
		
		# ======================
		# - Body Anim Settings -
		# ======================
		
		bodyAnimList = mc.textScrollList('agentSettings_bodyAnimTSL',q=True,ai=True)
		if bodyAnimList:
			
			# Body Anim File
			bodyAnimFiles = []
			for bodyAnimFile in bodyAnimList:
				f = bodyAnimFile.replace('gen_*',agent_char)
				if os.path.isfile(f): bodyAnimFiles.append(f)
			if bodyAnimFiles:
				bodyAnimFile = bodyAnimFiles[choice(range(len(bodyAnimFiles)))]
				try: mc.setAttr(agent_all+'.crowd_body_anim',bodyAnimFile,type='string')
				except Exception, e: print('Apply Agent Settings: Error setting body anim path value! Exception Msg: '+str(e))
			else:
				print('Apply Crowd Agent Settings: No BODY clips/poses found for agent "'+agent+'" ('+agent_char+')!')
			
			# Body Anim Scale
			bodyScaleMin = mc.floatFieldGrp('agentSettings_bodyScaleFFG',q=True,value1=True)
			bodyScaleMax = mc.floatFieldGrp('agentSettings_bodyScaleFFG',q=True,value2=True)
			bodyScale = bodyScaleMin + ((bodyScaleMax - bodyScaleMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_body_scale',bodyScale)
			except Exception, e: print('Apply Agent Settings: Error setting body anim scale! Exception Msg: '+str(e))
			
			# Body Anim Offset
			bodyOffsetMin = mc.intFieldGrp('agentSettings_bodyOffsetIFG',q=True,value1=True)
			bodyOffsetMax = mc.intFieldGrp('agentSettings_bodyOffsetIFG',q=True,value2=True)
			bodyOffset = bodyOffsetMin + ((bodyOffsetMax - bodyOffsetMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_body_offset',bodyOffset)
			except Exception, e: print('Apply Agent Settings: Error setting body anim offset! Exception Msg: '+str(e))
			
			# Body Anim Infinity
			bodyAnimInf = mc.optionMenuGrp('agentSettings_bodyInfinityOMG',q=True,sl=True)-1
			try: mc.setAttr(agent_all+'.crowd_body_infinity',bodyAnimInf)
			except Exception, e: print('Apply Agent Settings: Error setting body anim infinity! Exception Msg: '+str(e))
		
		# ======================
		# - Face Anim Settings -
		# ======================
		
		faceAnimList = mc.textScrollList('agentSettings_faceAnimTSL',q=True,ai=True)
		if faceAnimList:
			
			# Face Anim File
			faceAnimFiles = []
			for faceAnimFile in faceAnimList:
				f = faceAnimFile.replace('gen_*',agent_char)
				if os.path.isfile(f): faceAnimFiles.append(f)
			if faceAnimFiles:
				faceAnimFile = faceAnimFiles[choice(range(len(faceAnimFiles)))]
				try: mc.setAttr(agent_all+'.crowd_face_anim',faceAnimFile,type='string')
				except Exception, e: print('Apply Agent Settings: Error setting face anim path value! Exception Msg: '+str(e))
			else:
				print('Apply Crowd Agent Settings: No FACE clips/poses found for agent "'+agent+'" ('+agent_char+')!')
			
			# Face Anim Offset
			faceOffsetMin = mc.intFieldGrp('agentSettings_faceOffsetIFG',q=True,value1=True)
			faceOffsetMax = mc.intFieldGrp('agentSettings_faceOffsetIFG',q=True,value2=True)
			faceOffset = faceOffsetMin + ((faceOffsetMax - faceOffsetMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_face_offset',faceOffset)
			except Exception, e: print('Apply Agent Settings: Error setting face anim offset! Exception Msg: '+str(e))
			
			# Face Anim Infinity
			faceAnimInf = mc.optionMenuGrp('agentSettings_faceInfinityOMG',q=True,sl=True)-1
			try: mc.setAttr(agent_all+'.crowd_face_infinity',faceAnimInf)
			except Exception, e: print('Apply Agent Settings: Error setting face anim infinity! Exception Msg: '+str(e))
		
		# ===========================
		# - Left Hand Anim Settings -
		# ===========================
		
		lfHandAnimList = mc.textScrollList('agentSettings_lfHandAnimTSL',q=True,ai=True)
		if lfHandAnimList:
			
			# Left Hand Anim File
			lfHandAnimFiles = []
			for lfHandAnimFile in lfHandAnimList:
				f = lfHandAnimFile.replace('gen_*',agent_char)
				if os.path.isfile(f): lfHandAnimFiles.append(f)
			if lfHandAnimFiles:
				lfHandAnimFile = lfHandAnimFiles[choice(range(len(lfHandAnimFiles)))]
				try: mc.setAttr(agent_all+'.crowd_lfHand_anim',lfHandAnimFile,type='string')
				except Exception, e: print('Apply Agent Settings: Error setting left hand anim path value! Exception Msg: '+str(e))
			else:
				print('Apply Crowd Agent Settings: No LEFT HAND clips/poses found for agent "'+agent+'" ('+agent_char+')!')
			
			# Left Hand Anim Offset
			lfHandOffsetMin = mc.intFieldGrp('agentSettings_lfHandOffsetIFG',q=True,value1=True)
			lfHandOffsetMax = mc.intFieldGrp('agentSettings_lfHandOffsetIFG',q=True,value2=True)
			lfHandOffset = lfHandOffsetMin + ((lfHandOffsetMax - lfHandOffsetMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_lfHand_offset',lfHandOffset)
			except Exception, e: print('Apply Agent Settings: Error setting lfHand anim offset! Exception Msg: '+str(e))
			
			# Left Hand Anim Infinity
			lfHandAnimInf = mc.optionMenuGrp('agentSettings_lfHandInfinityOMG',q=True,sl=True)-1
			try: mc.setAttr(agent_all+'.crowd_lfHand_infinity',lfHandAnimInf)
			except Exception, e: print('Apply Agent Settings: Error setting lfHand anim infinity! Exception Msg: '+str(e))
		
		# ============================
		# - Right Hand Anim Settings -
		# ============================
		
		rtHandAnimList = mc.textScrollList('agentSettings_rtHandAnimTSL',q=True,ai=True)
		if rtHandAnimList:
			
			# Right Hand Anim File
			rtHandAnimFiles = []
			for rtHandAnimFile in rtHandAnimList:
				f = rtHandAnimFile.replace('gen_*',agent_char)
				if os.path.isfile(f): rtHandAnimFiles.append(f)
			if rtHandAnimFiles:
				rtHandAnimFile = rtHandAnimFiles[choice(range(len(rtHandAnimFiles)))]
				try: mc.setAttr(agent_all+'.crowd_rtHand_anim',rtHandAnimFile,type='string')
				except Exception, e: print('Apply Agent Settings: Error setting right hand anim path value! Exception Msg: '+str(e))
			else:
				print('Apply Crowd Agent Settings: No RIGHT HAND clips/poses found for agent "'+agent+'" ('+agent_char+')!')
			
			# Right Hand Anim Offset
			rtHandOffsetMin = mc.intFieldGrp('agentSettings_rtHandOffsetIFG',q=True,value1=True)
			rtHandOffsetMax = mc.intFieldGrp('agentSettings_rtHandOffsetIFG',q=True,value2=True)
			rtHandOffset = rtHandOffsetMin + ((rtHandOffsetMax - rtHandOffsetMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_rtHand_offset',rtHandOffset)
			except Exception, e: print('Apply Agent Settings: Error setting rtHand anim offset! Exception Msg: '+str(e))
			
			# Right Hand Anim Infinity
			rtHandAnimInf = mc.optionMenuGrp('agentSettings_rtHandInfinityOMG',q=True,sl=True)-1
			try: mc.setAttr(agent_all+'.crowd_rtHand_infinity',rtHandAnimInf)
			except Exception, e: print('Apply Agent Settings: Error setting rtHand anim infinity! Exception Msg: '+str(e))
		
		# ===================
		# - LookAt Settings -
		# ===================
		
		lookAtTarget = mc.textFieldButtonGrp('agentSettings_lookAtTargetTFB',q=True,text=True)
		if lookAtTarget:
			
			# LookAt Target
			try: mc.setAttr(agent_all+'.crowd_lookAt',lookAtTarget,type='string')
			except Exception, e: print('Apply Agent Settings: Error setting LookAt target object! Exception Msg: '+str(e))
			
			# LookAt Head Weight
			lookAtHeadMin = mc.intFieldGrp('agentSettings_lookAtHeadWtIFG',q=True,value1=True)
			lookAtHeadMax = mc.intFieldGrp('agentSettings_lookAtHeadWtIFG',q=True,value2=True)
			lookAtHead = lookAtHeadMin + ((lookAtHeadMax - lookAtHeadMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_lookAt_head',lookAtHead)
			except Exception, e: print('Apply Agent Settings: Error setting lookAt head weight value! Exception Msg: '+str(e))
			
			# LookAt Eyes Weight
			lookAtEyesMin = mc.intFieldGrp('agentSettings_lookAtEyesWtIFG',q=True,value1=True)
			lookAtEyesMax = mc.intFieldGrp('agentSettings_lookAtEyesWtIFG',q=True,value2=True)
			lookAtEyes = lookAtEyesMin + ((lookAtEyesMax - lookAtEyesMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_lookAt_eyes',lookAtEyes)
			except Exception, e: print('Apply Agent Settings: Error setting lookAt eyes weight value! Exception Msg: '+str(e))
			
			# LookAt Offset
			lookAtOffsetMin = mc.intFieldGrp('agentSettings_lookAtOffsetIFG',q=True,value1=True)
			lookAtOffsetMax = mc.intFieldGrp('agentSettings_lookAtOffsetIFG',q=True,value2=True)
			lookAtOffset = lookAtOffsetMin + ((lookAtOffsetMax - lookAtOffsetMin) * random.random())
			try: mc.setAttr(agent_all+'.crowd_lookAt_offset',lookAtOffset)
			except Exception, e: print('Apply Agent Settings: Error setting lookAt anim offset! Exception Msg: '+str(e))

def randomColourVariation(agents=None):
	'''
	Randomize crowd agent costume and hair/groom colour variation.
	@param agents: List of crowd agents to randomize colours for. If None, use current selection.
	@type agents: list
	'''
	# Check Agent List
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to randomize colour variations...')
	
	# For Each Agent
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Agent Colour Randomize: Agent all node "'+agent_all+'" not found! Unable to randomize colour...')
			continue
		
		# Randomize Colour Variation
		for attr in ['var_costumeColour','var_hairColour','var_groomColour']:
			if mc.attributeQuery(attr,n=agent_all,ex=True):
				enum = str(mc.attributeQuery(attr,n=agent_all,listEnum=True)[0]).split(':')
				try: mc.setAttr(agent_all+'.'+attr,choice(range(len(enum))))
				except Exception, e:
					print('Agent Colour Randomize: Error setting agent attribute "'+agent_all+'.'+attr+'"! Exception Msg: '+str(e))
	
	# Return Result
	return agents

def randomCostumeVariation(agents=None):
	'''
	Randomize crowd agent costume and hair/groom type variation.
	@param agents: List of crowd agents to randomize costume/groom types for. If None, use current selection.
	@type agents: list
	'''
	# Check Agent List
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to randomize colour variations...')
	
	# For Each Agent
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Agent Costume/Groom Randomize: Agent all node "'+agent_all+'" not found! Unable to randomize colour...')
			continue
		
		# Randomize Costume/Groom Variation
		for attr in ['var_costume','var_hairGroom','var_hair']:
			if mc.attributeQuery(attr,n=agent_all,ex=True):
				enum = str(mc.attributeQuery(attr,n=agent_all,listEnum=True)[0]).split(':')
				try: mc.setAttr(agent_all+'.'+attr,choice(range(1,len(enum))))
				except Exception, e:
					print('Agent Costume/Groom Randomize: Error setting agent attribute "'+agent_all+'.'+attr+'"! Exception Msg: '+str(e))
	
	# Return Result
	return agents

def randomizeAccessoryVariation(agents=None):
	'''
	Randomize crowd agent accessory variation.
	@param agents: List of crowd agents to randomize accessories for. If None, use current selection.
	@type agents: list
	'''
	# Check Agent List
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to randomize colour variations...')
	
	# For Each Agent
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Agent Accessory Randomize: Agent all node "'+agent_all+'" not found! Unable to randomize colour...')
			continue
		
		# =================================
		# - Randomize Accessory Variation -
		# =================================
		
		# Male Workman (waistcoat/suspenders)
		if '_male_' in agent:
			wrkA_waistcoat = 1
			wrkA_suspenders = 0
			if choice(range(2)):
				wrkA_waistcoat = 0
				wrkA_suspenders = 1
			try:
				mc.setAttr(agent_all+'.var_wrkA_suspenders',wrkA_suspenders)
				mc.setAttr(agent_all+'.var_wrkA_waistcoat',wrkA_waistcoat)
			except Exception, e:
				print('Agent Accessory Randomize: Error setting workman suspenders/waistcoat variation for agent "'+agent+'"! Exception Msg: '+str(e))
		
		# Male Hat ====
		
		if '_male_' in agent:
			
			# Set Male Hat Tolerance
			male_hat_tol = 0.65
			
			# Aristocrat
			if int(random.random() > male_hat_tol):
				try: mc.setAttr(agent_all+'.var_arsA_hat',1)
				except Exception, e:
					print('Agent Accessory Randomize: Error enabling male aristocrat hat for agent "'+agent+'"! Exception Msg: '+str(e))
			
			# Townsfolk
			if int(random.random() > male_hat_tol):
				try: mc.setAttr(agent_all+'.var_twnA_derbyHat',1)
				except Exception, e:
					print('Agent Accessory Randomize: Error enabling male aristocrat hat for agent "'+agent+'"! Exception Msg: '+str(e))
			
		# Female Hat ====
		
		if '_female_' in agent:
			
			# Set Female Hat Tolerance
			fem_hat_tol = 0.65
			
			# Aristocrat - (Only works with AristoHairA)
			if int(random.random() > fem_hat_tol):
				try: mc.setAttr(agent_all+'.var_arsA_hat',1)
				except Exception, e:
					print('Agent Accessory Randomize: Error enabling female aristocrat hat for agent "'+agent+'"! Exception Msg: '+str(e))
			
			# Shopkeeper
			if int(random.random() > fem_hat_tol):
				try: mc.setAttr(agent_all+'.var_shpA_hat',1)
				except Exception, e:
					print('Agent Accessory Randomize: Error enabling female shopkeeper hat for agent "'+agent+'"! Exception Msg: '+str(e))
			
			# Townsfolk (Only works with TownHairC)
			if int(random.random() > fem_hat_tol):
				try: mc.setAttr(agent_all+'.var_twnA_hat',1)
				except Exception, e:
					print('Agent Accessory Randomize: Error enabling female townsfolk hat for agent "'+agent+'"! Exception Msg: '+str(e))
		
		# Boy Hat ====
		
		if '_boy_' in agent:
			
			# Set Boy Hat Tolerance
			boy_hat_tol = 2.0 # OFF
			
			# Townsfolk
			hatA = 0
			hatB = 0
			if int(random.random() > boy_hat_tol):
				hatA = choice(range(2))
				hatB = 1-hatA
			try:
				mc.setAttr(agent_all+'.var_twnA_hatA',hatA)
				mc.setAttr(agent_all+'.var_twnA_hatB',hatB)
			except Exception, e:
				print('Agent Accessory Randomize: Error enabling boy townsfolk hat for agent "'+agent+'"! Exception Msg: '+str(e))
		
		# Male Scarf
		if '_male_' in agent:
			
			# Set Male Scarf Tolerance
			male_scarf_tol = 0.9
			scarfA = 0
			scarfB = 0
			scarfC = 0
			if int(random.random() > male_scarf_tol):
				scarf = choice(range(3))
				if scarf == 0:
					scarfA = 1
					scarfB = 0
					scarfC = 0
				if scarf == 1:
					scarfA = 0
					scarfB = 1
					scarfC = 0
				if scarf == 2:
					scarfA = 0
					scarfB = 0
					scarfC = 1
			try:
				mc.setAttr(agent_all+'.var_twnA_scarfA',scarfA)
				mc.setAttr(agent_all+'.var_twnA_scarfB',scarfB)
				mc.setAttr(agent_all+'.var_twnA_scarfC',scarfC)
			except Exception, e:
				print('Agent Accessory Randomize: Error setting male townsfolk scarf variation for agent "'+agent+'"! Exception Msg: '+str(e))
		
		# Female Scarf
		if '_female_' in agent:
			
			# Set Female Scarf Tolerance
			fem_scarf_tol = 0.9
			scarfA = 0
			scarfB = 0
			if int(random.random() > fem_scarf_tol):
				scarf = choice(range(2))
				if scarf == 0:
					scarfA = 1
					scarfB = 0
				if scarf == 1:
					scarfA = 0
					scarfB = 1
			try:
				mc.setAttr(agent_all+'.var_twnA_scarfA',scarfA)
				mc.setAttr(agent_all+'.var_twnA_scarfB',scarfB)
			except Exception, e:
				print('Agent Accessory Randomize: Error setting female townsfolk scarf variation for agent "'+agent+'"! Exception Msg: '+str(e))
		
	# Return Result
	return agents

def matchHairToCostume(agents=None):
	'''
	Match agent hair/groom variation to the current costume variation.
	This may be required after running randomCostumeVariation(), where it is possible to have mis-matched hair costume variations.
	@param agents: List of crowd agents to match costume/groom types for. If None, use current selection.
	@type agents: list
	'''
	# Check Agent List
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to randomize colour variations...')
	
	# For Each Agent
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Agent Accessory Randomize: Agent all node "'+agent_all+'" not found! Unable to randomize colour...')
			continue
		
		# =========================
		# - Get Costume Variation -
		# =========================
		
		costumeAttr = 'var_costume'
		costumeList = mc.attributeQuery(costumeAttr,n=agent_all,listEnum=True)[0].split(':')
		costumeVal = mc.getAttr(agent_all+'.'+costumeAttr)
		costumeStr = str(costumeList[costumeVal]).lower()
		
		# ======================
		# - Set Hair Variation -
		# ======================
		
		hairEnum = []
		hairAttr = 'var_hair'
		if mc.attributeQuery(hairAttr,n=agent_all,ex=True):
			hairEnum = mc.attributeQuery(hairAttr,n=agent_all,listEnum=True)[0].split(':')
		
		groomEnum = []
		groomAttr = 'var_hairGroom'
		if mc.attributeQuery(groomAttr,n=agent_all,ex=True):
			groomEnum = mc.attributeQuery(groomAttr,n=agent_all,listEnum=True)[0].split(':')
		
		# Check Costume Prefix
		costumePre = ['aristo','shop','town','work']
		for prefix in costumePre:
			
			if costumeStr.startswith(prefix):
				
				if hairEnum:
					hairList = [i for i in range(len(hairEnum)) if hairEnum[i].lower().startswith(prefix)]
					try: mc.setAttr(agent_all+'.'+hairAttr,choice(hairList))
					except Exception, e: print('Match Agent Costume/Hair: Error setting agent hair variation attribute "'+agent_all+'.'+hairAttr+'"! Exception Msg: '+str(e))
				
				if groomEnum:
					groomList = [i for i in range(len(groomEnum)) if groomEnum[i].lower().startswith(prefix)]
					try: mc.setAttr(agent_all+'.'+groomAttr,choice(groomList))
					except Exception, e: print('Match Agent Costume/Hair: Error setting agent hair variation attribute "'+agent_all+'.'+hairAttr+'"! Exception Msg: '+str(e))
		
def animOffsetFalloff(agents,falloffCenter,falloffMin,falloffMax,falloffMinVal=0.0,falloffMaxVal=100.0,falloffRandVal=10.0):
	'''
	Set agent body anim offset value based on the distance to a specified object.
	@param agents: List of crowd agents to apply distance based body offset values to.
	@type agents: list
	@param falloffCenter: The falloff center object.
	@type falloffCenter: str
	@param falloffMin: The falloff min distance object.
	@type falloffMin: str
	@param falloffMax: The falloff max distance object.
	@type falloffMax: str
	@param falloffMinVal: The falloff min offset value.
	@type falloffMinVal: float or int
	@param falloffMaxVal: The falloff max offset value.
	@type falloffMaxVal: float or int
	@param falloffRandVal: Amount to randomize each agent offset value (+/-).
	@type falloffRandVal: float or int
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not agents: raise Exception('Invalid or empty agents list!')
	
	if not mc.objExists(falloffCenter):
		raise Exception('Falloff center object "'+falloffCenter+'" doesnt exist!')
	if not mc.objExists(falloffMin):
		raise Exception('Falloff min object "'+falloffMin+'" doesnt exist!')
	if not mc.objExists(falloffMax):
		raise Exception('Falloff max object "'+falloffMax+'" doesnt exist!')
	
	# =======================
	# - Anim Offset Falloff -
	# =======================
	
	#  Get Center and Min/Max Distance Values
	cnt = mc.xform(falloffCenter,q=True,ws=True,rp=True)
	minDist = glTools.utils.mathUtils.distanceBetween(cnt,mc.xform(falloffMin,q=True,ws=True,rp=True))
	maxDist = glTools.utils.mathUtils.distanceBetween(cnt,mc.xform(falloffMax,q=True,ws=True,rp=True))
	
	for agent in agents:
		
		# Agent All
		agent_all = agent+':all'
		agent_allTrans = agent+':allTransA'
		if not mc.objExists(agent_all):
			print('Agent all node "'+agent_all+'" not found! Skipping agent...')
			continue
		if not mc.objExists(agent_allTrans):
			print('Agent allTrans node "'+agent_allTrans+'" not found! Skipping agent...')
			continue
		
		# Agent Position
		pos = mc.xform(agent_allTrans,q=True,ws=True,rp=True)
		dist = glTools.utils.mathUtils.distanceBetween(cnt,pos)
		
		# Set Offset
		offset = 0.0
		if dist < minDist: offset = falloffMinVal
		elif dist > maxDist: offset = falloffMaxVal
		else: offset = falloffMinVal + ((falloffMaxVal-falloffMinVal) * ((dist-minDist) / (maxDist-minDist)))
		
		# Randomize
		if falloffRandVal > 0.001:
			rVal = (random.random() - 0.5) * 0.2
			offset += falloffRandVal * rVal
		
		# Set Offset Attribute Value
		try: mc.setAttr(agent_all+'.crowd_body_offset',offset)
		except Exception, e: print('Anim Offset Falloff: Error setting body anim offset! Exception Msg: '+str(e))
		else: print(agent_all+'.crowd_body_offset = '+str(offset))
	
def animOffsetFalloffUI():
	'''
	Crowd body anim offset falloff UI
	'''
	# Window
	window = 'animOffsetFalloffUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Agent Anim Offset Falloff',resizeToFitChildren=True)
	
	# ===============
	# - UI Elements -
	# ===============
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	animOffsetFalloff_cntTFB = mc.textFieldButtonGrp('animOffsetFalloff_cntTFB',label='Falloff Center',text='',buttonLabel='<<<')
	animOffsetFalloff_minTFB = mc.textFieldButtonGrp('animOffsetFalloff_minTFB',label='Falloff Minimum',text='',buttonLabel='<<<')
	animOffsetFalloff_maxTFB = mc.textFieldButtonGrp('animOffsetFalloff_maxTFB',label='Falloff Maximum',text='',buttonLabel='<<<')
	animOffsetFalloff_minMaxFFG = mc.floatFieldGrp('animOffsetFalloff_minMaxFFG',numberOfFields=2,label='Offset Min/Max',value1=0.0,value2=100.0,precision=1)
	animOffsetFalloff_randFFG = mc.floatFieldGrp('animOffsetFalloff_randFFG',numberOfFields=1,label='Offset Random',value1=0.0,precision=1)
	
	# Apply Button
	applyB = mc.button(l='Apply Offset Falloff',c='import glTools.tools.crowd;reload(glTools.tools.crowd);glTools.tools.crowd.animOffsetFalloffFromUI()')
	
	# ================
	# - UI Callbacks -
	# ================
	
	mc.textFieldButtonGrp(animOffsetFalloff_cntTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+animOffsetFalloff_cntTFB+'")')
	mc.textFieldButtonGrp(animOffsetFalloff_minTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+animOffsetFalloff_minTFB+'")')
	mc.textFieldButtonGrp(animOffsetFalloff_maxTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+animOffsetFalloff_maxTFB+'")')
	
	# ================
	# - Form Layouts -
	# ================
	
	mc.formLayout(FL,e=True,af=[(animOffsetFalloff_cntTFB,'top',5),(animOffsetFalloff_cntTFB,'left',5),(animOffsetFalloff_cntTFB,'right',5)])
	mc.formLayout(FL,e=True,af=[(animOffsetFalloff_minTFB,'left',5),(animOffsetFalloff_minTFB,'right',5)],ac=[(animOffsetFalloff_minTFB,'top',5,animOffsetFalloff_cntTFB)])
	mc.formLayout(FL,e=True,af=[(animOffsetFalloff_maxTFB,'left',5),(animOffsetFalloff_maxTFB,'right',5)],ac=[(animOffsetFalloff_maxTFB,'top',5,animOffsetFalloff_minTFB)])
	mc.formLayout(FL,e=True,af=[(animOffsetFalloff_minMaxFFG,'left',5),(animOffsetFalloff_minMaxFFG,'right',5)],ac=[(animOffsetFalloff_minMaxFFG,'top',5,animOffsetFalloff_maxTFB)])
	mc.formLayout(FL,e=True,af=[(animOffsetFalloff_randFFG,'left',5),(animOffsetFalloff_randFFG,'right',5)],ac=[(animOffsetFalloff_randFFG,'top',5,animOffsetFalloff_minMaxFFG)])
	mc.formLayout(FL,e=True,af=[(applyB,'bottom',5),(applyB,'left',5),(applyB,'right',5)])
	
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)

def animOffsetFalloffFromUI():
	'''
	'''
	# Get Agents
	sel = mc.ls(sl=1)
	if not sel: raise Exception('Invalid or empty agents selection!')
	NSlist = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not sel: raise Exception('Invalid or empty agents list!')
	
	# Get UI Data
	cntLoc = mc.textFieldButtonGrp('animOffsetFalloff_cntTFB',q=True,text=True)
	minLoc = mc.textFieldButtonGrp('animOffsetFalloff_minTFB',q=True,text=True)
	maxLoc = mc.textFieldButtonGrp('animOffsetFalloff_maxTFB',q=True,text=True)
	minVal = mc.floatFieldGrp('animOffsetFalloff_minMaxFFG',q=True,value1=True)
	maxVal = mc.floatFieldGrp('animOffsetFalloff_minMaxFFG',q=True,value2=True)
	randVal = mc.floatFieldGrp('animOffsetFalloff_randFFG',q=True,value1=True)
	
	# Check UI Data
	if not mc.objExists(cntLoc): raise Exception('Falloff center object "'+cntLoc+'" doesnt exist!')
	if not mc.objExists(minLoc): raise Exception('Falloff minimum object "'+minLoc+'" doesnt exist!')
	if not mc.objExists(maxLoc): raise Exception('Falloff maximum object "'+maxLoc+'" doesnt exist!')
	
	# Apply Anim Offset Falloff
	animOffsetFalloff(	agents=NSlist,
						falloffCenter=cntLoc,
						falloffMin=minLoc,
						falloffMax=maxLoc,
						falloffMinVal=minVal,
						falloffMaxVal=maxVal,
						falloffRandVal=randVal	)

def mirrorBodyAnim(agents=None):
	'''
	Add mirror body animation attribute to specified agents.
	@param agents: List of crowd agents to mirror body animation for. If None, use current selection.
	@type agents: list
	'''
	# ====================
	# - Check Agent List -
	# ====================
	
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to randomize colour variations...')
	
	# ==================
	# - For Each Agent -
	# ==================
	
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Agent Mirror Body Anim: Agent all node "'+agent_all+'" not found! Unable to mirror body animation...')
			continue
		
		# ==============================
		# - Add Body Mirror Attributes -
		# ==============================
		
		# Define Attribute Name
		mirrorAttr = 'crowd_body_mirror'
		
		# Add Attribute
		if not mc.attributeQuery(mirrorAttr,n=agent_all,ex=True):
			mc.addAttr(agent_all,ln=mirrorAttr,at='bool')
		
		# Set Attribute
		mc.setAttr(agent_all+'.'+mirrorAttr,1)
	
	# =================
	# - Return Result -
	# =================
	
	return agents

def eyeLookAtAngleOffset(agents=None,offset=None):
	'''
	Add eye lookAt angle offset attribute to specified agents.
	@param agents: List of crowd agents to add eye lookAt angle offset attribute to. If None, use current selection.
	@type agents: list
	'''
	# ====================
	# - Check Agent List -
	# ====================
	
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to add LookAt angle offset...')
		return agents
	
	# ==================
	# - For Each Agent -
	# ==================
	
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('LookAt Angle Offset: Agent all node "'+agent_all+'" not found! Unable to add LookAt angle offset...')
			continue
		
		# ==============================
		# - Add Body Mirror Attributes -
		# ==============================
		
		# Define Attribute Name
		offsetAttr = 'crowd_lookAt_eyeOffset'
		
		# Add Attribute
		if not mc.attributeQuery(offsetAttr,n=agent_all,ex=True):
			mc.addAttr(agent_all,ln=offsetAttr)
		
		# Set Attribute
		if offset != None:
			mc.setAttr(agent_all+'.'+offsetAttr,offset)
	
	# =================
	# - Return Result -
	# =================
	
	return agents

def addAgentAttribute(agents=None,attrName=None,attrVal=0.0):
	'''
	Add numeric crowd agent attribute to specified agents "all" node.
	@param agents: List of crowd agents to add eye lookAt angle offset attribute to. If None, use current selection.
	@type agents: list or None
	@param attrName: Crowd agent attribute name
	@type attrName: str
	@param attrVal: Default (initial) crowd agent attribute value
	@type attrVal: str
	'''
	# ====================
	# - Check Agent List -
	# ====================
	
	if not attrName:
		print('Invalid or empty agent attribute name! Unable to add agent attribute...')
		return None
	
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to add LookAt angle offset...')
		return agents
	
	# ==================
	# - For Each Agent -
	# ==================
	
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('LookAt Angle Offset: Agent all node "'+agent_all+'" not found! Unable to add LookAt angle offset...')
			continue
		
		# Add Attribute
		if not mc.attributeQuery(attrName,n=agent_all,ex=True):
			mc.addAttr(agent_all,ln=attrName,dv=attrVal)
	
	# =================
	# - Return Result -
	# =================
	
	return agents

def rigControlAttributeOverride(agents=None,rigAttrs=None):
	'''
	Add rig control override attributes to specified agents.
	@param agents: List of crowd agents to add rig control override attributes to. If None, use current selection.
	@type agents: list
	@param rigAttrs: List of rig control attributes to add overrides for. Control attribute names should NOT include namespaces.
	@type rigAttrs: list
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Agent List
	if not agents:
		sel = mc.ls(sl=True,transforms=True) or []
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
	if not agents:
		print('Invalid or empty agent list! Unable to add rig control attribute overrides...')
		return agents
	
	# Check Rig Control Attrs
	if not rigAttrs:
		result = mc.promptDialog(	title='Crowd Attribute Override',
									message='Attribute:',
									button=['OK', 'Cancel'],
									defaultButton='OK',
									cancelButton='Cancel',
									dismissString='Cancel')
		if result == 'OK':
			rigAttrs = [mc.promptDialog(q=True,text=True)]
	
	if not rigAttrs:
		print('Invalid or empty rig control attribute list! Unable to add rig control attribute overrides...')
		return None
	
	# ==================
	# - For Each Agent -
	# ==================
	
	for agent in agents:
		
		# Check Agent All Node
		agent_all = agent+':all'
		if not mc.objExists(agent_all):
			print('Rig Control Attribute Override: Agent all node "'+agent_all+'" not found! Unable to add rig control attribute overrides...')
			continue
		
		# =======================================
		# - Add Rig Control Attribute Overrides -
		# =======================================
		
		for rigAttr in rigAttrs:
			
			# Check Rig Attribute
			if not '.' in rigAttr:
				print('Rig Control Attribute Override: Invalid rig control attribute "'+agent_all+'"! Skipping...')
				continue
		
			# Define Attribute Name
			overrideAttr = 'crowd_override__'+rigAttr.replace('.','__')
			
			# Add Attribute
			if not mc.attributeQuery(overrideAttr,n=agent_all,ex=True):
				mc.addAttr(agent_all,ln=overrideAttr,k=True)		
	
	# =================
	# - Return Result -
	# =================
	
	return agents

# ====================
# - Crowd Agent Data -
# ====================

class CrowdAgentData(data.Data):
	'''
	Crowd Agent Data Class
	'''
	def __init__(self,agents=None):
		'''
		'''
		# Execute Super Class Init
		super(CrowdAgentData, self).__init__()
		
		# Build Agent Data
		if agents: self.buildData(agents)
		
		# Char Variation Attrs
		self.var_attrs = [	'var_costume',
							'var_costumeColour',
							'var_hair',
							'var_hairGroom',
							'var_hairColour',
							'var_groomColour',
							'var_hairTarget',
							
							'var_arsA_hat',
							'var_shpA_hat',
							'var_twnA_hat',
							'var_twnA_hatA',
							'var_twnA_hatB',
							'var_twnA_derbyHat',
							
							'var_wrkA_suspenders',
							'var_wrkA_waistcoat',
							
							'var_twnA_scarfA',
							'var_twnA_scarfB',
							'var_twnA_scarfC',
							
							'uniformScale'	]
		
		# Crowd Agent Attrs
		self.crd_attrs = [	'crowd_body_anim',
							'crowd_body_scale',
							'crowd_body_offset',
							'crowd_body_infinity',
							
							'crowd_face_anim',
							'crowd_face_offset',
							'crowd_face_infinity',
							
							'crowd_lfHand_anim',
							'crowd_lfHand_offset',
							'crowd_lfHand_infinity',
							
							'crowd_rtHand_anim',
							'crowd_rtHand_offset',
							'crowd_rtHand_infinity',
							
							'crowd_lookAt',
							'crowd_lookAt_head',
							'crowd_lookAt_eyes',
							'crowd_lookAt_offset'	]
	
	def buildData(self,agents):
		'''
		Build agent data for the specified list of agents
		@param agents: List of agents to build data for.
		@type agents: list
		'''
		# For Each Agent
		for agent in agents:
			
			# Check Agent All
			agent_all = agent+':all'
			if not mc.objExists(agent_all):
				print('Agent all "'+agent_all+'" node not found! Unable to build agent data...')
				continue
			
			# Initialize Agent Data
			self._data[agent] = {}
			print('Building Agent Data: '+agent)
			
			# Char Variation Attrs
			for attr in self.var_attrs:
				if mc.attributeQuery(attr,n=agent_all,ex=True):
					self._data[agent][attr] = mc.getAttr(agent_all+'.'+attr)
			
			# Crowd Agent Attrs
			for attr in self.crd_attrs:
				if mc.attributeQuery(attr,n=agent_all,ex=True):
					self._data[agent][attr] = mc.getAttr(agent_all+'.'+attr)
	
	def applyData(self,agents,var_attrs=True,crd_attrs=True):
		'''
		Apply agent data to the specified list of agents
		@param agents: List of agents to apply data to.
		@type agents: list
		'''
		# For Each Agent
		for agent in agents:
			
			# Check Agent All
			agent_all = agent+':all'
			if not mc.objExists(agent_all):
				print('Agent all "'+agent_all+'" node not found! Unable to apply agent data...')
				continue
			
			# Check Agent Data
			if not self._data.has_key(agent):
				print('No agent data found for "'+agent+'"! Unable to apply agent data...')
				continue
			
			# Print Agent Progress
			print('Apply Agent Data: '+agent)
			
			# ========================
			# - Char Variation Attrs -
			# ========================
			
			if var_attrs:
				for attr in self.var_attrs:
					# Check Stored Data
					if not self._data[agent].has_key(attr): continue
					# Check Target Attr
					if mc.attributeQuery(attr,n=agent_all,ex=True):
						if mc.getAttr(agent_all+'.'+attr,type=True) == 'string':
							try: mc.setAttr(agent_all+'.'+attr,self._data[agent][attr],type='string')
							except Exception, e:
								print('Apply Agent Data: Error applying agent data to attribute "'+agent_all+'.'+attr+'"!')
								print('Apply Agent Data: '+str(e))
						else:
							try: mc.setAttr(agent_all+'.'+attr,self._data[agent][attr])
							except Exception, e:
								print('Apply Agent Data: Error applying agent data to attribute "'+agent_all+'.'+attr+'"!')
								print('Apply Agent Data: '+str(e))
			
			# =====================
			# - Crowd Agent Attrs -
			# =====================
			
			if crd_attrs:
				for attr in self.crd_attrs:
					# Check Stored Data
					if not self._data[agent].has_key(attr): continue
					# Check Target Attr
					if mc.attributeQuery(attr,n=agent_all,ex=True):
						if mc.getAttr(agent_all+'.'+attr,type=True) == 'string':
							try: mc.setAttr(agent_all+'.'+attr,self._data[agent][attr],type='string')
							except Exception, e:
								print('Apply Agent Data: Error applying agent data to attribute "'+agent_all+'.'+attr+'"!')
								print('Apply Agent Data: '+str(e))
						else:
							try: mc.setAttr(agent_all+'.'+attr,self._data[agent][attr])
							except Exception, e:
								print('Apply Agent Data: Error applying agent data to attribute "'+agent_all+'.'+attr+'"!')
								print('Apply Agent Data: '+str(e))
	
	def buildDataFromSel(self):
		'''
		Build agent data for the current selected agents
		'''
		sel = mc.ls(sl=True,transforms=True)
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
		if agents: self.buildData(agents)
	
	def applyDataToSel(self,var_attrs=True,crd_attrs=True):
		'''
		Apply agent data to the current selected agents
		'''
		sel = mc.ls(sl=True,transforms=True)
		agents = glTools.utils.namespace.getNSList(sel,topOnly=True)
		if agents: self.applyData(agents,var_attrs=var_attrs,crd_attrs=crd_attrs)

