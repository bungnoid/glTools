import maya.cmds as mc
import glTools.ui.utils
import glTools.utils.base
import glTools.utils.mesh

class UserInputError(Exception): pass
class UIError(Exception): pass

# Global point list
interactiveSnapSrcList = []
interactiveSnapDstList = []

def interactiveSnapToMeshUI():
	'''
	UI for snapToMesh()
	'''
	# Window
	window = 'interactiveSnapUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Snap To Mesh - Interactive')
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	#---
	
	# Target Mesh
	snapMeshTFB = mc.textFieldButtonGrp('interactiveSnapMeshTFB',label='Target Mesh',text='',buttonLabel='Load Selected')
	
	# Slider
	snapFSG = mc.floatSliderGrp('interactiveSnapFSG', label='Drag:',field=False, minValue=0.0, maxValue=1.0,value=0 )
	snapRangeFFG = mc.floatFieldGrp('interactiveSnapRangeFSG', numberOfFields=2, label='Slider Min/Max', value1=0.0, value2=1.0)
	
	# UI Callbacks
	mc.textFieldButtonGrp(snapMeshTFB,e=True,bc='glTools.ui.utils.loadMeshSel("'+snapMeshTFB+'")')
	mc.floatSliderGrp('interactiveSnapFSG',e=True,cc='glTools.ui.mesh.interactiveSnapChangeCommand()')
	mc.floatSliderGrp('interactiveSnapFSG',e=True,dc='glTools.ui.mesh.interactiveSnapDragCommand()')
	
	# Buttons
	cancelB = mc.button('interactiveSnapCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(snapMeshTFB,'top',5),(snapMeshTFB,'left',5),(snapMeshTFB,'right',5)])
	mc.formLayout(FL,e=True,af=[(snapFSG,'left',5),(snapFSG,'right',5)],ac=[(snapFSG,'top',5,snapMeshTFB)])
	mc.formLayout(FL,e=True,af=[(snapRangeFFG,'left',5),(snapRangeFFG,'right',5)],ac=[(snapRangeFFG,'top',5,snapFSG)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Show Window
	mc.showWindow(window)

def interactiveSnapUpdateCommand():
	'''
	'''
	global interactiveSnapSrcList
	global interactiveSnapDstList
	
	# Clear global lists
	interactiveSnapSrcList = []
	interactiveSnapDstList = []
	
	# Get current selection
	sel = mc.ls(sl=1,fl=1)
	if not sel: return
	
	# Get target mesh
	mesh = mc.textFieldGrp('interactiveSnapMeshTFB',q=True,text=True)
	
	# Rebuild global lists
	for i in sel:
		pnt = glTools.utils.base.getPosition(i)
		cpos = glTools.utils.mesh.closestPoint(mesh,pnt)
		interactiveSnapSrcList.append(pnt)
		interactiveSnapDstList.append(cpos)

def interactiveSnapChangeCommand():
	'''
	'''
	global interactiveSnapSrcList
	global interactiveSnapDstList
	
	# Clear global lists
	interactiveSnapSrcList = []
	interactiveSnapDstList = []

def interactiveSnapDragCommand():
	'''
	'''
	global interactiveSnapSrcList
	global interactiveSnapDstList
	
	# Get current selection
	sel = mc.ls(sl=1,fl=1)
	if not sel: return
	
	# Check global list validity
	if not interactiveSnapSrcList or not interactiveSnapDstList:
		interactiveSnapUpdateCommand()
	
	# Get Snap amount
	amount = mc.floatSliderGrp('interactiveSnapFSG',q=True,v=True)
	
	# Move points
	pos = [0,0,0]
	for i in range(len(sel)):
		
		# Calculate new position
		pos[0] = interactiveSnapSrcList[i][0] + ((interactiveSnapDstList[i][0] - interactiveSnapSrcList[i][0]) * amount)
		pos[1] = interactiveSnapSrcList[i][1] + ((interactiveSnapDstList[i][1] - interactiveSnapSrcList[i][1]) * amount)
		pos[2] = interactiveSnapSrcList[i][2] + ((interactiveSnapDstList[i][2] - interactiveSnapSrcList[i][2]) * amount)
		
		# Set position
		mc.move(pos[0],pos[1],pos[2],sel[i],ws=True,a=True)

def snapToMeshUI():
	'''
	UI for snapToMesh()
	'''
	# Window
	window = 'snapToMeshUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Snap To Mesh')
	
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements
	#---
	
	# Surface
	meshTFB = mc.textFieldButtonGrp('snapToMeshTFB',label='Target Mesh',text='',buttonLabel='Load Selected')
	
	# Orient
	orientCBG = mc.checkBoxGrp('snapToMeshOrientCBG',label='Orient To Face',ncb=1,v1=False)
	
	# ----------
	# - Orient -
	# ----------
	
	# Orient Frame
	orientFrameL = mc.frameLayout('snapToMeshOriFL',l='Orient Options',cll=0,en=0)
	orientFormL = mc.formLayout(numberOfDivisions=100)
	
	# OptionMenuGrp
	axList = ['X','Y','Z','-X','-Y','-Z']
	orientNormAxisOMG = mc.optionMenuGrp('snapToMeshNormOMG',label='Normal Axis',en=False)
	for ax in axList: mc.menuItem(label=ax)
	orientUpVecAxisOMG = mc.optionMenuGrp('snapToMeshUpVecOMG',label='UpVector Axis',en=False)
	for ax in axList: mc.menuItem(label=ax)
	# Set Default Value
	mc.optionMenuGrp('snapToMeshUpVecOMG',e=True,sl=2)
	
	# Up Vector
	upVectorFFG = mc.floatFieldGrp('snapToMeshUpVecFFG',label='UpVector',nf=3,v1=0,v2=1,v3=0,en=0)
	upVectorObjectTFB = mc.textFieldButtonGrp('snapToMeshUpVecObjTFG',label='WorldUpObject',text='',buttonLabel='Load Selected',en=0)
	
	mc.setParent('..')
	mc.setParent('..')
	
	# UI callback commands
	mc.textFieldButtonGrp(meshTFB,e=True,bc='glTools.ui.utils.loadMeshSel("'+meshTFB+'")')
	mc.checkBoxGrp(orientCBG,e=True,cc='glTools.ui.utils.checkBoxToggleLayout("'+orientCBG+'","'+orientFrameL+'")')
	mc.textFieldButtonGrp(upVectorObjectTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+upVectorObjectTFB+'")')
	
	# Buttons
	snapB = mc.button('snapToMeshSnapB',l='Snap!',c='glTools.ui.mesh.snapToMeshFromUI(False)')
	snapCloseB = mc.button('snapToMeshSnapCloseB',l='Snap and Close',c='glTools.ui.mesh.snapToMeshFromUI(True)')
	cancelB = mc.button('snapToMeshCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(meshTFB,'top',5),(meshTFB,'left',5),(meshTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(orientCBG,'top',5,meshTFB)],af=[(orientCBG,'left',5),(orientCBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(orientFrameL,'top',5,orientCBG),(orientFrameL,'bottom',5,snapB)],af=[(orientFrameL,'left',5),(orientFrameL,'right',5)])
	mc.formLayout(FL,e=True,ac=[(snapB,'bottom',5,snapCloseB)],af=[(snapB,'left',5),(snapB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(snapCloseB,'bottom',5,cancelB)],af=[(snapCloseB,'left',5),(snapCloseB,'right',5)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Form Layout - Orient
	mc.formLayout(orientFormL,e=True,af=[(orientNormAxisOMG,'top',5),(orientNormAxisOMG,'left',5),(orientNormAxisOMG,'right',5)])
	mc.formLayout(orientFormL,e=True,ac=[(orientUpVecAxisOMG,'top',5,orientNormAxisOMG)])
	mc.formLayout(orientFormL,e=True,af=[(orientUpVecAxisOMG,'left',5),(orientUpVecAxisOMG,'right',5)])
	
	mc.formLayout(orientFormL,e=True,ac=[(upVectorFFG,'top',5,orientUpVecAxisOMG)])
	mc.formLayout(orientFormL,e=True,af=[(upVectorFFG,'left',5),(upVectorFFG,'right',5)])
	
	mc.formLayout(orientFormL,e=True,ac=[(upVectorObjectTFB,'top',5,upVectorFFG)])
	mc.formLayout(orientFormL,e=True,af=[(upVectorObjectTFB,'left',5),(upVectorObjectTFB,'right',5)])
	
	# Show Window
	mc.showWindow(window)

def snapToMeshFromUI(close=False):
	'''
	Execute snapToMesh() from UI
	'''
	# Window
	window = 'snapToMeshUI'
	if not mc.window(window,q=True,ex=1): raise UIError('SnapToSurface UI does not exist!!')
	# Get UI data
	mesh = mc.textFieldGrp('snapToMeshTFB',q=True,text=True)
	# Check surface
	if not glTools.utils.mesh.isMesh(mesh):
		raise UserInputError('Object "'+mesh+'" is not a valid mesh!!')
	# Orient
	orient = mc.checkBoxGrp('snapToMeshOrientCBG',q=True,v1=True)
	# Orient Options
	normAx = str.lower(str(mc.optionMenuGrp('snapToMeshNormOMG',q=True,v=True)))
	upVecAx = str.lower(str(mc.optionMenuGrp('snapToMeshUpVecOMG',q=True,v=True)))
	# Up Vector
	upVec = (mc.floatFieldGrp('snapToMeshUpVecFFG',q=True,v1=True),mc.floatFieldGrp('snapToMeshUpVecFFG',q=True,v2=True),mc.floatFieldGrp('snapToMeshUpVecFFG',q=True,v3=True))
	upVecObj = mc.textFieldButtonGrp('snapToMeshUpVecObjTFG',q=True,text=True)
	
	# Get User Selection
	sel = mc.ls(sl=True,fl=True)
	
	# Execute Command
	glTools.utils.mesh.snapPtsToMesh(mesh,sel)
	# Orient
	if orient:
		for obj in sel:
			try:
				glTools.utils.mesh.orientToMesh(mesh=mesh,transform=obj,upVector=upVec,upVectorObject=upVecObj,normalAxis=normAx,upAxis=upVecAx)
			except:
				raise Exception('Object "'+obj+'" is not a valid transform!! Unable to orient!')
	
	# Cleanup
	if close: mc.deleteUI(window)

def attachToMeshUI():
	'''
	UI for attachToMesh()
	'''
	# Window
	window = 'attachToMeshUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Attach To Mesh')
	# Layout
	FL = mc.formLayout(numberOfDivisions=100)
	# UI Elements
	#---
	# Surface
	meshTFB = mc.textFieldButtonGrp('attachToMeshTFB',label='Target Mesh',text='',buttonLabel='Load Selected')
	# Transform
	transformTFB = mc.textFieldButtonGrp('attachToMeshTransformTFB',label='Transform',text='',buttonLabel='Load Selected')
	# Transform
	prefixTFG = mc.textFieldGrp('attachToMeshPrefixTFG',label='Prefix',text='')
	# Orient
	orientCBG = mc.checkBoxGrp('attachToMeshOrientCBG',label='Orient To Face',ncb=1,v1=False)
	
	# Orient Frame
	orientFrameL = mc.frameLayout('attachToMeshOriFL',l='Orient Options',cll=0,en=0)
	orientFormL = mc.formLayout(numberOfDivisions=100)
	# OMG
	axList = ['X','Y','Z','-X','-Y','-Z']
	orientNormAxisOMG = mc.optionMenuGrp('attachToMeshNormOMG',label='Normal Axis',en=False)
	for ax in axList: mc.menuItem(label=ax)
	orientTanAxisOMG = mc.optionMenuGrp('attachToMeshTanOMG',label='Tangent Axis',en=False)
	for ax in axList: mc.menuItem(label=ax)
	# Set Default Value
	mc.optionMenuGrp(orientTanAxisOMG,e=True,sl=2)
	
	mc.setParent('..')
	mc.setParent('..')
	
	# UI callback commands
	mc.textFieldButtonGrp(meshTFB,e=True,bc='glTools.ui.utils.loadMeshSel("'+meshTFB+'")')
	mc.textFieldButtonGrp(transformTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+transformTFB+'","'+prefixTFG+'")')
	mc.checkBoxGrp(orientCBG,e=True,cc='glTools.ui.utils.checkBoxToggleLayout("'+orientCBG+'","'+orientFrameL+'")')
	
	# Buttons
	snapB = mc.button('attachToMeshAttachB',l='Attach',c='glTools.ui.mesh.attachToMeshFromUI(False)')
	snapCloseB = mc.button('attachToMeshAttachCloseB',l='Attach and Close',c='glTools.ui.mesh.attachToMeshFromUI(True)')
	cancelB = mc.button('attachToMeshCancelB',l='Cancel',c='mc.deleteUI("'+window+'")')
	
	# Form Layout - MAIN
	mc.formLayout(FL,e=True,af=[(meshTFB,'top',5),(meshTFB,'left',5),(meshTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(transformTFB,'top',5,meshTFB)])
	mc.formLayout(FL,e=True,af=[(transformTFB,'left',5),(transformTFB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(prefixTFG,'top',5,transformTFB)])
	mc.formLayout(FL,e=True,af=[(prefixTFG,'left',5),(prefixTFG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(orientCBG,'top',5,prefixTFG)])
	mc.formLayout(FL,e=True,af=[(orientCBG,'left',5),(orientCBG,'right',5)])
	mc.formLayout(FL,e=True,ac=[(orientFrameL,'top',5,orientCBG)])
	mc.formLayout(FL,e=True,af=[(orientFrameL,'left',5),(orientFrameL,'right',5)])
	mc.formLayout(FL,e=True,ac=[(orientFrameL,'bottom',5,snapB)])
	mc.formLayout(FL,e=True,ac=[(snapB,'bottom',5,snapCloseB)])
	mc.formLayout(FL,e=True,af=[(snapB,'left',5),(snapB,'right',5)])
	mc.formLayout(FL,e=True,ac=[(snapCloseB,'bottom',5,cancelB)])
	mc.formLayout(FL,e=True,af=[(snapCloseB,'left',5),(snapCloseB,'right',5)])
	mc.formLayout(FL,e=True,af=[(cancelB,'left',5),(cancelB,'right',5),(cancelB,'bottom',5)])
	
	# Form Layout - Orient
	mc.formLayout(orientFormL,e=True,af=[(orientNormAxisOMG,'top',5),(orientNormAxisOMG,'left',5),(orientNormAxisOMG,'right',5)])
	mc.formLayout(orientFormL,e=True,ac=[(orientTanAxisOMG,'top',5,orientNormAxisOMG)])
	mc.formLayout(orientFormL,e=True,af=[(orientTanAxisOMG,'left',5),(orientTanAxisOMG,'right',5)])
	
	# Show Window
	mc.showWindow(window)

def attachToMeshFromUI(close=False):
	'''
	Execute attachToMesh() from UI
	'''
	# Window
	window = 'attachToMeshUI'
	if not mc.window(window,q=True,ex=1): raise UIError('SnapToSurface UI does not exist!!')
	# Get UI data
	mesh = mc.textFieldGrp('attachToMeshTFB',q=True,text=True)
	# Check surface
	if not glTools.utils.mesh.isMesh(mesh):
		raise UserInputError('Object "'+surface+'" is not a valid nurbs surface!!')
	# Transform
	obj = mc.textFieldGrp('attachToMeshTransformTFB',q=True,text=True)
	# Prefix
	pre = mc.textFieldGrp('attachToMeshPrefixTFG',q=True,text=True)
	# Orient
	orient = mc.checkBoxGrp('attachToMeshOrientCBG',q=True,v1=True)
	# Orient Options
	normAx = str.lower(str(mc.optionMenuGrp('attachToMeshNormOMG',q=True,v=True)))
	tanAx = str.lower(str(mc.optionMenuGrp('attachToMeshTanOMG',q=True,v=True)))
	
	# Execute command
	glTools.utils.attach.attachToMesh(mesh=mesh,transform=obj,useClosestPoint=True,orient=orient,normAxis=normAx,tangentAxis=tanAx,prefix=pre)
	
	# Cleanup
	if close: mc.deleteUI(window)
