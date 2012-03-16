import maya.cmds as mc

import glTools.utils.joint
import glTools.utils.mathUtils
import glTools.utils.stringUtils

class UserInputError(Exception): pass
class UIError(Exception): pass

def jointOrientUI():
	'''
	UI for jointOrient()
	'''
	# Window
	window = 'jointOrientUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Joint Orient Tool')
	
	# UI Elements
	#---
	width = 272
	height = 459
	cw1 = 90
	cw2 = 60
	cw3 = 60
	cw4 = 50
	
	# Layout
	CL = mc.columnLayout(w=width,adj=True)
	
	# Aim Method
	aimRBG = mc.radioButtonGrp('jointOrientAimRBG',nrb=3,l='Aim Method',la3=['Axis','Object','Cross'],sl=1,cc='glTools.ui.joint.jointOrientRefreshUI_aimMethod()',cw=[(1,cw1),(2,cw2),(3,cw3)])
	
	# Aim Axis Direction Layout
	axisFL = mc.frameLayout('jointOrientAxisFL',l='Orientation Axis',w=(width-8),h=70,cll=0)
	axisCL = mc.columnLayout(adj=True)
	
	primAxisRBG = mc.radioButtonGrp('jointOrientPrimAxisRBG',nrb=3,l='Primary Axis',la3=['X','Y','Z'],sl=1,cc='glTools.ui.joint.jointOrientRefreshUI_aimAxis()',cw=[(1,cw1),(2,cw2),(3,cw3),(4,cw4)])
	aimAxisRBG = mc.radioButtonGrp('jointOrientAimAxisRBG',nrb=2,l='Aim Axis',la2=['Y','Z'],sl=1,cw=[(1,cw1),(2,cw2)])
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Aim Axis Direction Layout
	aimAxisFL = mc.frameLayout('jointOrientAimAxisFL',l='Orientation Aim Axis',w=(width-8),h=70,cll=0)
	aimAxisCL = mc.columnLayout(adj=True)
	
	oriAxisPosRBG = mc.radioButtonGrp('jointOrientOriAxisPosRBG',nrb=3,l='Aim Direction',la3=['+X','+Y','+Z'],sl=1,cw=[(1,cw1),(2,cw2),(3,cw3),(4,cw4)])
	oriAxisNegRBG = mc.radioButtonGrp('jointOrientOriAxisNegRBG',nrb=3,scl=oriAxisPosRBG,l='',la3=['-X','-Y','-Z'],cw=[(1,cw1),(2,cw2),(3,cw3),(4,cw4)])
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Aim Object Layout
	aimObjFL = mc.frameLayout('jointOrientAimObjFL',l='Aim Object',w=(width-8),h=55,cll=0)
	aimObjCL = mc.columnLayout(adj=True)
	aimObjCreateB = mc.button(l='Create Aim Object',w=(width-12),c='glTools.ui.joint.jointOrientCreateControl()')
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Cross Product Layout
	crossProdFL = mc.frameLayout('jointOrientCrossProdFL',l='Cross Product',w=(width-8),h=70,cll=0)
	crossProdCL = mc.columnLayout(adj=True)
	crossProdCBG = mc.checkBoxGrp('jointOrientCrossProdCBG',l='Invert Result',ncb=1,cw=[(1,cw1),(2,cw2)])
	crossProdRBG = mc.radioButtonGrp('jointOrientCrossProdRBG',l='Joint As',nrb=3,la3=['Base','Apex','Tip'],sl=2,cw=[(1,cw1),(2,cw2),(3,cw3),(4,cw4)])
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Rotate Joint Orientation
	#rotJointOriFL = mc.frameLayout('jointOrientRotOriFL',l='Rotate Joint Orientation',w=(width-8),h=55,cll=0)
	rotJointOriFL = mc.frameLayout('jointOrientRotOriFL',l='Rotate Joint Orientation',cll=0)
	rotJointOriRCL = mc.rowColumnLayout(nr=3)
	mc.text(l=' X - ')
	mc.text(l=' Y - ')
	mc.text(l=' Z - ')
	mc.button(w=80,l='-90',c='glTools.ui.joint.jointOrientRotateOrient(-90,0,0)')
	mc.button(w=80,l='-90',c='glTools.ui.joint.jointOrientRotateOrient(0,-90,0)')
	mc.button(w=80,l='-90',c='glTools.ui.joint.jointOrientRotateOrient(0,0,-90)')
	mc.button(w=80,l='180',c='glTools.ui.joint.jointOrientRotateOrient(180,0,0)')
	mc.button(w=80,l='180',c='glTools.ui.joint.jointOrientRotateOrient(0,180,0)')
	mc.button(w=80,l='180',c='glTools.ui.joint.jointOrientRotateOrient(0,0,180)')
	mc.button(w=80,l='+90',c='glTools.ui.joint.jointOrientRotateOrient(90,0,0)')
	mc.button(w=80,l='+90',c='glTools.ui.joint.jointOrientRotateOrient(0,90,0)')
	mc.button(w=80,l='+90',c='glTools.ui.joint.jointOrientRotateOrient(0,0,90)')
	
	mc.setParent('..')
	mc.setParent('..')
	
	# Toggle Axis View
	mc.button(l='Toggle Local Axis Display',w=(width-8),c='mc.toggle(localAxis=True)')
	# Orient Joint
	mc.button(l='Orient Joint',w=(width-8),c='glTools.ui.joint.jointOrientFromUI()')
	# Close UI
	mc.button(l='Close',c='mc.deleteUI("'+window+'")')
	
	# Prepare Window
	mc.window(window,e=True,w=width,h=height)
 	mc.frameLayout(aimObjFL,e=True,en=False)
	mc.frameLayout(crossProdFL,e=True,en=False)
 	
 	# Show Window
	mc.showWindow(window)

def jointOrientFromUI(close=False):
	'''
	Execute jointOrient() from UI
	'''
	# Window
	window = 'jointOrientUI'
	if not mc.window(window,q=True,ex=1): raise UIError('JointOrient UI does not exist!!')
	
	# Build Axis List
	axisList = ['x','y','z','-x','-y','-z']
	#axisList = [(1,0,0),(0,1,0),(0,0,1),(-1,0,0),(0,-1,0),(0,0,-1)]
	
	# Build UpAxis List
	upAxisList = [('y','z'),('x','z'),('x','y')]
	#upAxisList = [((0,1,0),(0,0,1)),((1,0,0),(0,0,1)),((1,0,0),(0,1,0))]
	
	# Build Axis Dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
	
	# Get joint selection
	jntList = mc.ls(sl=True,type='joint')
	if not jntList: return
	
	# Aim Method
	aimMethod = mc.radioButtonGrp('jointOrientAimRBG',q=True,sl=True)
	
	# Get Axis Selection
	aimAx = mc.radioButtonGrp('jointOrientPrimAxisRBG',q=True,sl=True)
	upAx = mc.radioButtonGrp('jointOrientAimAxisRBG',q=True,sl=True)
	# Build Axis Values
	aimAxis = axisList[aimAx-1]
	upAxis = upAxisList[aimAx-1][upAx-1]
	
	# Axis
	upVector = (0,1,0)
	if aimMethod == 1:
		
		# Check joint selection
		if not jntList: raise UserInputError('Invalid joint selection!!')
		# Get UpVector Selection
		upVec = mc.radioButtonGrp('jointOrientOriAxisPosRBG',q=True,sl=True)
		if not upVec: upVec = mc.radioButtonGrp('jointOrientOriAxisNegRBG',q=True,sl=True) + 3
		# Build UpAxis Value
		upVector = axisDict[axisList[upVec-1]]
		
		# Execute Command
		for jnt in jntList:
			glTools.utils.joint.orient(jnt,aimAxis=aimAxis,upAxis=upAxis,upVec=upVector)
		
	# Object
	elif aimMethod == 2:
		
		# Check for orient control selection
		cccList = mc.ls('*_ori01_orientControl',sl=True)
		for ccc in cccList:
			if mc.objExists(ccc+'.joint'):
				cJnt = mc.listConnections(ccc+'.joint',s=True,d=False,type='joint')
				if not cJnt: continue
				if not jntList.count(cJnt[0]): jntList.append(cJnt[0])
		
		# Determine orient control
		for jnt in jntList:
			prefix = glTools.utils.stringUtils.stripSuffix(jnt)
			ctrlGrp = prefix+'_ori01_orientGrp'
			oriCtrl = prefix+'_ori01_orientControl'
			upLoc = prefix+'_up01_orientLoc'
			if (not mc.objExists(ctrlGrp)) or (not mc.objExists(oriCtrl)) or (not mc.objExists(upLoc)):
				print('Joint "'+jnt+'" has no orient control!! Unable to orient joint!!')
				continue
			# Extract upVector from orient control
			jPos = mc.xform(jnt,q=True,ws=True,rp=True)
			upPos = mc.xform(upLoc,q=True,ws=True,rp=True)
			upVector = glTools.utils.mathUtils.offsetVector(upPos,jPos)
			
			# Execute Command
			glTools.utils.joint.orient(jnt,aimAxis=aimAxis,upAxis=upAxis,upVec=upVector)
			
			# Delete orient control
			mc.delete(ctrlGrp)
	
	# Cross
	elif aimMethod == 3:
		
		# Invert
		invert = mc.checkBoxGrp('jointOrientCrossProdCBG',q=True,v1=True)
		# Joint As
		jointAs = mc.radioButtonGrp('jointOrientCrossProdRBG',q=True,sl=True)
		
		# Get Cross vector
		for jnt in jntList:
			
			# Check for child joint
			if not mc.listRelatives(jnt,c=True):
				glTools.utils.joint.orient(jnt)
				continue
			if jointAs == 1: # BASE
				bJnt = jnt
				aJnt = mc.listRelatives(jnt,c=True,pa=True,type='joint')
				if not aJnt: raise UserInputError('Insufficient joint connectivity to determine apex from base "'+jnt+'"!!')
				aJnt = aJnt[0]
				tJnt = mc.listRelatives(aJnt,c=True,pa=True,type='joint')
				if not tJnt: raise UserInputError('Insufficient joint connectivity to determine tip from apex "'+aJnt+'"!!')
				tJnt = tJnt[0]
			elif jointAs == 2: # APEX
				bJnt = mc.listRelatives(jnt,c=True,pa=True,type='joint')
				if not bJnt: raise UserInputError('Insufficient joint connectivity to determine base from base "'+jnt+'"!!')
				bJnt = bJnt[0]
				aJnt = jnt
				tJnt = mc.listRelatives(jnt,p=True,pa=True,type='joint')
				if not tJnt: raise UserInputError('Insufficient joint connectivity to determine tip from apex "'+jnt+'"!!')
				tJnt = tJnt[0]
			elif jointAs == 3: # TIP
				tJnt = jnt
				aJnt = mc.listRelatives(jnt,p=True,pa=True,type='joint')
				if not tJnt: raise UserInputError('Insufficient joint connectivity to determine apex from tip "'+jnt+'"!!')
				aJnt = aJnt[0]
				bJnt = mc.listRelatives(aJnt,p=True,pa=True,type='joint')
				if not bJnt: raise UserInputError('Insufficient joint connectivity to determine base from apex "'+aJnt+'"!!')
				bJnt = bJnt[0]
			
			# Get joint positions
			bPos = mc.xform(bJnt,q=True,ws=True,rp=True)
			aPos = mc.xform(aJnt,q=True,ws=True,rp=True)
			tPos = mc.xform(tJnt,q=True,ws=True,rp=True)
			# Calculate cross product
			vec1 = glTools.utils.mathUtils.offsetVector(aPos,bPos)
			vec2 = glTools.utils.mathUtils.offsetVector(tPos,aPos)
			cross = glTools.utils.mathUtils.crossProduct(vec1,vec2)
			# Invert
			if invert: cross = (-cross[0],-cross[1],-cross[2])
			
			# Execute Command
			glTools.utils.joint.orient(jnt,aimAxis=aimAxis,upAxis=upAxis,upVec=cross)
	
	# Select Joint Children
	mc.select(mc.listRelatives(jntList,c=True,type='joint'))
	
	# Cleanup
	if close: mc.deleteUI(window)

def jointOrientRefreshUI_aimMethod():
	'''
	Refresh Aim Axis list based on Primary Axis selection.
	'''
	aimMethod = mc.radioButtonGrp('jointOrientAimRBG',q=True,sl=True)
	mc.frameLayout('jointOrientAimAxisFL',e=True,en=(aimMethod==1))
	mc.frameLayout('jointOrientAimObjFL',e=True,en=(aimMethod==2))
	mc.frameLayout('jointOrientCrossProdFL',e=True,en=(aimMethod==3))

def jointOrientRefreshUI_aimAxis():
	'''
	Refresh Aim Axis list based on Primary Axis selection.
	'''
	labelIndex = mc.radioButtonGrp('jointOrientPrimAxisRBG',q=True,sl=True)
	labelArray = [('Y','Z'),('X','Z'),('X','Y')]
	mc.radioButtonGrp('jointOrientAimAxisRBG',e=True,la2=labelArray[labelIndex-1])

def jointOrientRotateOrient(rx,ry,rz):
	'''
	Incremental joint orient rotation for selected joints
	@param rx: Joint orient rotation around the X axis
	@type rx: float
	@param ry: Joint orient rotation around the Y axis
	@type ry: float
	@param rz: Joint orient rotation around the Z axis
	@type rz: float
	'''
	jntList = mc.ls(sl=True,type='joint')
	for jnt in jntList:
		childList = mc.parent(mc.listRelatives(jnt,c=True,pa=True),w=True)
		jOri = mc.getAttr(jnt+'.jo')[0]
		mc.setAttr(jnt+'.jo',jOri[0]+rx,jOri[1]+ry,jOri[2]+rz)
		mc.parent(childList,jnt)
	mc.select(jntList)

def jointOrientCreateControl():
	'''
	Create joint orient control for each selected joint
	'''
	# Check Window
	window = 'jointOrientUI'
	upAxis = (0,1,0)
	if mc.window(window,q=True,ex=1):
		
		# Build UpAxis List
		upAxisList = [((0,1,0),(0,0,1)),((1,0,0),(0,0,1)),((1,0,0),(0,1,0))]
		# Get Axis Selection
		aimAx = mc.radioButtonGrp('jointOrientPrimAxisRBG',q=True,sl=True)
		upAx = mc.radioButtonGrp('jointOrientAimAxisRBG',q=True,sl=True)
		# Build Axis Values
		upAxis = upAxisList[aimAx-1][upAx-1]
	
	# Create control
	jntList = mc.ls(sl=True,type='joint')
	ctrlList = [] 
	for jnt in jntList:
		
		# Get child joint
		cJnt = mc.listRelatives(jnt,c=True,pa=True)
		if not cJnt: continue
		
		# Generate control prefix
		prefix = glTools.utils.stringUtils.stripSuffix(jnt)
		
		# Check for existing orien control
		if mc.objExists(prefix+'_ori01_orientGrp'):
			print('Orient control already exists for joint "'+jnt+'"!!')
			continue
		
		# Create orient control
		circle = mc.circle(c=(0,0,0),nr=(0,1,0),sw=360,r=1,d=3,ut=0,tol=0.01,s=8,ch=1,n=prefix+'_ori01_orientControl')
		for ch in ['tx','ty','tz','rx','rz','sx','sy','sz']: mc.setAttr(circle[0]+'.'+ch,l=True,k=False)
		
		# Create orient UP locator
		upLoc = mc.spaceLocator(n=prefix+'_up01_orientLoc')
		mc.parent(upLoc[0],circle[0])
		mc.setAttr(upLoc[0]+'.tz',1.0)
		mc.connectAttr(upLoc[0]+'.tz',circle[1]+'.radius',f=True)
		for ch in ['tx','ty','rx','ry','rz','sx','sy','sz']: mc.setAttr(upLoc[0]+'.'+ch,l=True,k=False)
		
		# Create orient control group
		ctrlGrp = mc.group(em=True,n=prefix+'_ori01_orientGrp')
		mc.parent(circle[0],ctrlGrp)
		
		# Position control group
		mc.delete(mc.pointConstraint(jnt,ctrlGrp))
		mc.delete(mc.aimConstraint(cJnt[0],ctrlGrp,aimVector=(0,1,0),upVector=(0,0,1),wu=upAxis,wuo=jnt,wut='objectrotation'))
		
		# Scale control elements
		dist = glTools.utils.mathUtils.distanceBetween(mc.xform(jnt,q=True,ws=True,rp=True),mc.xform(cJnt[0],q=True,ws=True,rp=True))
		mc.setAttr(upLoc[0]+'.tz',dist*0.5)
		
		# Lock orient control group
		mc.parent(ctrlGrp,jnt)
		for ch in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']: mc.setAttr(ctrlGrp+'.'+ch,l=True,k=False)
		
		# Add message connection form joint to orient control
		mc.addAttr(circle[0],ln='joint',at='message')
		mc.connectAttr(jnt+'.message',circle[0]+'.joint',f=True)
		
		# Append control list
		ctrlList.append(circle[0])
		
	# Select controls
	mc.select(ctrlList)

