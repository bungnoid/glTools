import maya.cmds as mc
import maya.mel as mm

import glTools.utils.channelState
import glTools.utils.curve

_overrideId = {'lf':14,'rt':13,'cn':17}
_controlType = ['anchor','arch','arcArrow','arrow','box','circle','crescent','diamond','eye','face','locator','pyramid','spiral','sphere','sphereAnchor','square','teardrop','text']
	
def create(controlType,controlName,translate=(0,0,0),rotate=(0,0,0),scale=1,colour=0,text=''):
	'''
	This script builds curve control objects based on the arguments input by the user
	@param controlType: Type of control to build
	@type controlType: str
	@param controlName: Name of the resultant curve control
	@type controlName: str
	'''
	# Check Control Type
	if not _controlType.count(controlType):
		raise Exception('Unsupported control shape type("'+controlType+'")!!')
		
	# Create Control
	control = ''
	if controlType == 'anchor': control = self.anchor()
	elif controlType == 'arch': control = self.arch()
	elif controlType == 'arcArrow': control = self.arcArrow()
	elif controlType == 'arrow': control = self.arrow()
	elif controlType == 'box': control = self.box()
	elif controlType == 'circle': control = self.circle()
	elif controlType == 'crescent': control = self.crescent()
	elif controlType == 'diamond': control = self.diamond()
	elif controlType == 'eye': control = self.eye()
	elif controlType == 'face': control = self.face()
	elif controlType == 'locator': control = self.locator()
	elif controlType == 'pyramid': control = self.pyramid()
	elif controlType == 'spiral': control = self.spiral()
	elif controlType == 'sphere': control = self.sphere()
	elif controlType == 'sphereAnchor': control = self.sphereAnchor()
	elif controlType == 'square': control = self.square()
	elif controlType == 'teardrop': control = self.teardrop()
	elif controlType == 'text': control = self.text(text=text)
	else: raise Exception('Unsupported control shape type("'+controlType+'")!!')
	
	# Check Control
	if not control: raise Exception('Error creating controls')
	
	# Rename Control
	control = mc.rename(control,controlName+'#')
	controlShape = mc.listRelatives(control,s=1,ni=1,pa=True)
	if len(controlShape) == 1:
		controlShape = mc.rename(controlShape[0],control+'Shape')
	else:
		for c in range(len(controlShape)):
			mc.rename(controlShape[c],control+'Shape'+str(c))
	
	# Color it
	prefix = controlName.split('_')[0]
	if _overrideId.has_key(prefix):
		mc.setAttr(controlShape+'.overrideEnabled',1)
		mc.setAttr(controlShape+'.overrideColor',_overrideId[prefix])
	
	# Position Control
	mc.move(translate[0],translate[1],translate[2],control,r=True)
	mc.rotate(rotate[0],rotate[1],rotate[2],control)
	mc.scale(scale,scale,scale,control)
	mc.makeIdentity(control,apply=True,translate=True,rotate=True,scale=True,normal=False)
	
	# Set channel states
	glTools.utils.channelState.ChannelState().setFlags([0,0,0,0,0,0,0,0,0,1],[control])
	
	# Return result
	return str(control)
	
def anchor(self):
	'''
	Create anchor control object
	'''
	# Create control object
	pts = [(0.000,0.000,0.000),(0.000,0.826,0.000),(0.087,0.826,0.000),(0.087,1.000,0.000),(-0.087,1.000,0.000),(-0.087,0.826,0.000),(0.000,0.826,0.000)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def arch(self):
	'''
	'''
	# Create control object
	pts = [(0.100,0.000,-0.500),(-0.100,0.000,-0.500),(-0.100,0.250,-0.433),(-0.100,0.433,-0.250),(-0.100,0.500,0.000),(-0.100,0.433,0.250),(-0.100,0.250,0.433),(-0.100,0.000,0.500),(0.100,0.000,0.500),(0.100,0.250,0.433),(0.100,0.433,0.250),(0.100,0.500,0.000),(0.100,0.433,-0.250),(0.100,0.250,-0.433),(0.100,0.000,-0.500)]
	knots = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0]
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def arcArrow(self):
	'''
	'''
	# Create control object
	pts = [(0.0,0.414,-0.854),(0.0,0.487,-0.942),(0.0,0.148,-0.941),(0.0,0.226,-0.627),(0.0,0.293,-0.708),(0.0,0.542,-0.542),(0.0,0.708,-0.293),(0.0,0.767,0.0),(0.0,0.708,0.293),(0.0,0.542,0.542),(0.0,0.293,0.708),(0.0,0.235,0.607),(0.0,0.126,0.914),(0.0,0.445,0.967),(0.0,0.389,0.871),(0.0,0.678,0.678),(0.0,0.885,0.367),(0.0,0.958,0.0),(0.0,0.885,-0.367),(0.0,0.678,-0.678),(0.0,0.414,-0.854)]
	knots = [0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0]
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control
	
def arrow(self):
	'''
	Create arrow control object
	'''
	# Create control object
	pts = [	(-0.333,0.0,-1.0), (0.333,0.0,-1.0), (0.333,0.0,0.333), (0.666,0.0,0.333),
		(0.0,0.0,1.0), (-0.666,0.0,0.333), (-0.333,0.0,0.333), (-0.333,0.0,-1.0) ]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def box(self):
	'''
	Create box control object
	'''
	# Create control object
	pts = [	(-0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,-0.5,0.5),
			(-0.5,-0.5,0.5), (-0.5,0.5,0.5), (-0.5,0.5,-0.5),
			(-0.5,-0.5,-0.5), (-0.5,-0.5,0.5), (-0.5,0.5,0.5),
			(0.5,0.5,0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
			(-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5),
			(0.5,0.5,0.5), (0.5,-0.5,0.5), (0.5,-0.5,-0.5)	]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def circle(self):
	'''
	Create circle control object
	'''
	return mc.circle(c=(0,0,0),nr=(0,0,1),sw=360,r=0.5,d=3,ut=0,tol=0.01,s=8,ch=0)[0]

def crescent(self):
	'''
	Create Crescent control object
	'''
	# Create control object
	control = mc.curve(d=3,p=[(0.392,0.392,-0.000),(-0.000,0.554,-0.000),(-0.392,0.392,-0.000),(-0.554,0.000,-0.000),(-0.392,0.228,-0.000),(-0.000,0.323,-0.000),(0.392,0.228,-0.000),(0.554,-0.000,0.000),(0.392,0.392,-0.000),(-0.000,0.554,-0.000),(-0.392,0.392,-0.000)],k=[-0.25,-0.125,0.0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1.0,1.125,1.25])
	
	# Return control
	return control

def diamond(self):
	'''
	Create diamond control object
	'''
	# Create control object
	pts = [(0.0,0.5,0.0),(-0.25,0.0,0.0),(0.0,-0.5,0.0),(0.25,0.0,0.0),(0.0,0.5,0.0)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def eye(self):
	'''
	Create eye control object
	'''
	# Create control object
	pts = [(1.000,0.064,0.000),(-0.000,0.747,0.000),(-1.000,0.064,0.000),(-1.000,0.000,0.000),(-1.000,-0.064,0.000),(-0.000,-0.747,0.000),(1.000,-0.064,0.000),(1.000,-0.000,0.000),(1.000,0.064,0.000),(-0.000,0.747,0.000),(-1.000,0.064,0.000)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def face(self):
	'''
	Create face control object
	'''
	# Create control object
	pts = [(0.573,0.863,0.000),(-0.000,1.047,0.000),(-0.573,0.863,0.000),(-0.770,0.266,0.000),(-0.750,0.000,0.000),(-0.409,-0.656,0.000),(-0.322,-0.953,0.000),(-0.000,-1.020,0.000),(0.322,-0.953,0.000),(0.409,-0.656,0.000),(0.750,-0.000,0.000),(0.770,0.266,0.000),(0.573,0.863,0.000),(-0.000,1.047,0.000),(-0.573,0.863,0.000)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def locator(self):
	'''
	Create locator control object
	'''
	# Create control object
	pts = [	(-0.5, 0.0, 0.0), (0.5, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.5, 0.0), (0.0, -0.5, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, -0.5), (0.0, 0.0, 0.5)	]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def pyramid(self):
	'''
	Create pyramid control object
	'''
	# Create control object
	pts = [	(-0.5,-0.5,0.5), (0.5,-0.5,0.5), (0.5,-0.5,-0.5), (-0.5,-0.5,-0.5), (-0.5,-0.5,0.5),
		(0.0,0.5,0.0), (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.0,0.5,0.0), (0.5,-0.5,0.5)	]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def sphere(self):
	'''
	Create sphere control object
	'''
	# Create control object
	pts = [	(0.5, 0.0, 0.0), (0.462, 0.0, 0.19), (0.35, 0.0, 0.35),
		(0.19, 0.0, 0.46), (0.0, 0.0, 0.5), (-0.19, 0.0, 0.46),
		(-0.35, 0.0, 0.35), (-0.46, 0.0, 0.19), (-0.5, 0.0, 0.0),
		(-0.46, 0.0, -0.19), (-0.35, 0.0, -0.35), (-0.19, 0.0, -0.46),
		(0.0, 0.0, -0.5), (0.19, 0.0, -0.46), (0.35, 0.0, -0.35),
		(0.46, 0.0, -0.19), (0.5, 0.0, 0.0), (0.46, -0.19, 0.0),
		(0.35, -0.35, 0.0), (0.19, -0.46, 0.0), (0.0, -0.5, 0.0), 
		(-0.19, -0.46, 0.0), (-0.35, -0.35, 0.0), (-0.46, -0.19, 0.0), 
		(-0.5, 0.0, 0.0), (-0.46, 0.19, 0.0), (-0.35, 0.35, 0.0), 
		(-0.19, 0.46, 0.0), (0.0, 0.5, 0.0), (0.19, 0.46, 0.0), 
		(0.35, 0.35, 0.0), (0.46, 0.19, 0.0), (0.5, 0.0, 0.0), 
		(0.46, 0.0, 0.19), (0.35, 0.0, 0.35), (0.19, 0.0, 0.46), 
		(0.0, 0.0, 0.5), (0.0, 0.24, 0.44), (0.0, 0.44, 0.24), 
		(0.0, 0.5, 0.0), (0.0, 0.44, -0.24), (0.0, 0.24, -0.44), 
		(0.0, 0.0, -0.5), (0.0, -0.24, -0.44), (0.0, -0.44, -0.24), 
		(0.0, -0.5, 0.0), (0.0, -0.44, 0.24), (0.0, -0.24, 0.44), 
		(0.0, 0.0, 0.5)	]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def sphereAnchor(self):
	'''
	Create sphereAnchor control object
	'''
	# Create control object
	pts = [	(0.0, 1.0, -0.05), (0.0, 0.981, -0.0462), (0.0, 0.965, -0.035),
		(0.0, 0.954, -0.019), (0.0, 0.95, 0.0), (0.0, 0.954, 0.019),
		(0.0, 0.965, 0.035), (0.0, 0.981, 0.046), (0.0, 1.0, 0.05),
		(0.0, 1.019, 0.046), (0.0, 1.035, 0.035), (0.0, 1.046, 0.019),
		(0.0, 1.05, 0.0), (0.0, 1.046, -0.019), (0.0, 1.035, -0.035),
		(0.0, 1.019, -0.046), (0.0, 1.0, -0.05), (-0.019, 1.0, -0.046),
		(-0.035, 1.0, -0.035), (-0.046, 1.0, -0.019), (-0.05, 1.0, 0.0),
		(-0.046, 1.0, 0.019), (-0.035, 1.0, 0.035), (-0.019, 1.0, 0.046),
		(0.0, 1.0, 0.05), (0.019, 1.0, 0.046), (0.035, 1.0, 0.035),
		(0.046, 1.0, 0.019), (0.05, 1.0, 0.0), (0.046, 1.0, -0.019),
		(0.035, 1.0, -0.035), (0.019, 1.0, -0.046), (0.0, 1.0, -0.05),
		(0.0, 0.981, -0.046), (0.0, 0.965, -0.035), (0.0, 0.954, -0.019),
		(0.0, 0.95, 0.0), (0.024, 0.956, 0.0), (0.044, 0.976, 0.0),
		(0.05, 1.0, 0.0), (0.044, 1.024, 0.0), (0.024, 1.044, 0.0),
		(0.0, 1.05, 0.0), (-0.024, 1.044, 0.0), (-0.044, 1.024, 0.0),
		(-0.05, 1.0, 0.0), (-0.044, 0.976, 0.0), (-0.024, 0.956, 0.0),
		(0.0, 0.95, 0.0), (0.0, 0.0, 0.0) ]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control

def spiral(self):
	'''
	Create spiral control object
	'''
	# Build Point Array
	pts = [	(0.0, 0.0, 0.0), (0.0, 0.1, 0.0), (0.0, 0.2, 0.0),
		(0.0, 0.28, 0.0), (0.0, 0.288, 0.0), (0.0, 0.325, 0.0),
		(0.0, 0.346, -0.05), (0.01, 0.35, -0.12), (0.13, 0.38, -0.11),
		(0.21, 0.4, -0.02), (0.16, 0.44, 0.14), (0.0, 0.46, 0.2),
		(-0.14, 0.5, 0.12), (-0.21, 0.5, -0.06), (-0.18, 0.525, -0.28),
		(0.0, 0.55, -0.39), (0.28, 0.576, -0.312), (0.4, 0.615, -0.09),
		(0.3, 0.67, 0.186), (0.0, 0.7, 0.28), (-0.28, 0.728, 0.187),
		(-0.4, 0.768, -0.09), (-0.336, 0.823, -0.428), (0.0, 0.847, -0.595),
		(0.425, 0.867, -0.486), (0.589, 0.9, -0.09), (0.435, 0.97, 0.311),
		(0.158, 0.997, 0.415), (0.0, 1.0, 0.407) ]
			
	# Build Knot Array
	knots = [0,0]
	knots.extend(range(len(pts)-2))
	knots.extend([len(pts)-3,len(pts)-3])
	degree = 3
	
	# Create control object
	control = mc.curve(d=degree,p=pts,k=knots)
	
	# Return control name
	return control

def square(self):
	'''
	Create square control object
	'''
	# Create control object
	pts = [(-0.5,0.5,0.0),(-0.5,-0.5,0.0),(0.5,-0.5,0.0),(0.5,0.5,0.0),(-0.5,0.5,0.0)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	
	# Return control name
	return control
	
def teardrop(self):
	'''
	'''
	# Create control object
	pts = [(-0.000,0.554,0.000),(-0.015,0.548,0.000),(-0.554,0.109,0.000),(-0.392,-0.392,0.000),(-0.000,-0.554,0.000),(0.392,-0.392,0.000),(0.554,0.109,0.000),(0.015,0.548,0.000),(-0.000,0.554,0.000)]
	knots = range(len(pts))
	control = mc.curve(d=1,p=pts,k=knots)
	#control = mc.rebuildCurve(control,ch=False,rt=0,rpo=True,end=True,kr=True,d=3,kcp=True)[0]
	
	# Return control name
	return control
	
def text(self,text='text'):
	'''
	Create text control object
	@param text: Text string
	@type: str
	'''
	# Check text string
	if not text: raise Exception('Empty string error!')
	
	# Create Text
	textCurve = mc.textCurves(ch=False,f='Arial',t=text)
	
	# Parent shapes to single treansform
	textShapes = mc.ls(mc.listRelatives(textCurve,ad=True),type='nurbsCurve')
	for textShape in textShapes:
		textXform = mc.listRelatives(textShape,p=True)[0]
		textXform = mc.parent(textXform,w=True)
		mc.makeIdentity(textXform,apply=True,t=True,r=True,s=True,n=False)
		mc.parent(textShape,textCurve,r=True,s=True)
		mc.delete(textXform)
	
	# Delete unused transforms
	textChildren = mc.listRelatives(textCurve,c=True,type='transform')
	if textChildren: mc.delete(textChildren)
	
	# Position text
	mc.select(textCurve)
	mm.eval('CenterPivot')
	piv = mc.xform(textCurve,q=True,ws=True,rp=True)
	mc.move(-piv[0],-piv[1],-piv[2],textCurve,ws=True,r=True)
	
	# Scale text
	width = (mc.getAttr(textCurve[0]+'.boundingBoxMaxX') - mc.getAttr(textCurve[0]+'.boundingBoxMinX'))
	height = (mc.getAttr(textCurve[0]+'.boundingBoxMaxY') - mc.getAttr(textCurve[0]+'.boundingBoxMinY'))
	if width > height: sc = 1.0/ width
	else: sc = 1.0/ height
	mc.scale(sc,sc,sc,textCurve)
	
	# Freeze Transforms
	mc.makeIdentity(textCurve,apply=True,t=True,r=True,s=True,n=False)
	
	# Return result
	return textCurve

def controlShape(transform,controlType,translate=(0,0,0),rotate=(0,0,0),scale=1,text='',orient=True):
	'''
	'''
	# Control Builder
	controlBuilder = ControlBuilder()
	
	# Create Control
	if controlType == 'text':
		control = controlBuilder.create(controlType,'temp_control_transform',text=text)
	else:
		control = controlBuilder.create(controlType,'temp_control_transform')
	controlShapeList = mc.listRelatives(control,s=True)
	
	# Match Control
	if not orient: mc.setAttr(control+'.rotate',rotate[0],rotate[1],rotate[2])
	mc.delete(mc.pointConstraint(transform,control))
	mc.parent(control,transform)
	mc.setAttr(control+'.translate',translate[0],translate[1],translate[2])
	if orient: mc.setAttr(control+'.rotate',rotate[0],rotate[1],rotate[2])
	mc.setAttr(control+'.scale',scale,scale,scale)
	mc.makeIdentity(control,apply=True,t=1,r=1,s=1,n=0)
	
	# For each shape
	for i in range(len(controlShapeList)):
		
		# Parent Control Shape
		controlShapeList[i] = mc.parent(controlShapeList[i],transform,r=True,s=True)[0]
		controlShapeList[i] = mc.rename(controlShapeList[i],transform+'Shape'+str(i+1))
	
	# Delete temp transform 
	mc.delete(control)
	
	# Colour Control
	colourControl(transform)
	
	# Return result
	return controlShapeList

def colourControl(control):
	'''
	'''
	# Get control transform
	if not glTools.utils.transform.isTransform(control):
		controlParent = mc.listRelatives(control,p=True)
		if not controlParent:
			raise Exception('Unable to determine controls transform!')
		control = controlParent[0]
	
	# Determine Colour
	if control.startswith('cn'): colour = _overrideId['cn']
	elif control.startswith('lf') or control.startswith('L'): colour = _overrideId['lf']
	elif control.startswith('rt') or control.startswith('R'): colour = _overrideId['rt']
	else: colour = 17
	
	# Set colour
	controlShapes = mc.listRelatives(control,s=True)
	for controlShape in controlShapes:
		mc.setAttr(controlShape+'.overrideEnabled',1)
		mc.setAttr(controlShape+'.overrideColor',colour)
	
	# Return result
	return colour

def anchorCurve(control,anchor,template=True):
	'''
	'''
	# Check control
	if not mc.objExists(control):
		raise Exception('Control "'+control+'" does not exist!')
	if not mc.objExists(anchor):
		raise Exception('Anchor transform "'+anchor+'" does not exist!')
	
	# Create curve shape
	crv = mc.curve(p=[(0,0,0),(0,1,0)],k=[0,1],d=1,n=control+'Anchor')
	crvShape = mc.listRelatives(crv,s=True,pa=True)
	if not crvShape:
		raise Exception('Unable to determine shape for curve "'+crv+'"!')
	
	# Create curve locators
	crvLoc = glTools.utils.curve.locatorCurve(crv,locatorScale=0.0,local=True,prefix=control)
	mc.parent(crvLoc,control)
	mc.setAttr(crvLoc[0]+'.t',0,0,0)
	mc.setAttr(crvLoc[1]+'.t',0,0,0)
	mc.setAttr(crvLoc[0]+'.v',0)
	mc.setAttr(crvLoc[1]+'.v',0)
	
	# Rename and Parent curve shape
	crvShape = mc.parent(crvShape[0],control,r=True,s=True)[0]
	crvShape = mc.rename(crvShape,control+'Shape0')
	
	# Delete original curve transform
	mc.delete(crv)
	
	# Connect to anchor
	mc.pointConstraint(anchor,crvLoc[1])
	
	# Template
	if template: mc.setAttr(crvShape+'.template',1)
	
	# Set channel states
	glTools.utils.channelState.ChannelState().setFlags([2,2,2,2,2,2,2,2,2,1],crvLoc)
	
	# Return result
	return crvShape

def freezeCtrlScale(ctrl):
	'''
	'''
	grp = mc.listRelatives(ctrl,p=True)[0]
	mdn = ctrl.replace('ctrl','multiplyDivide')
	mdn = mc.createNode('multiplyDivide',n=mdn)
	mc.connectAttr(grp+'.s',mdn+'.input2',f=True)
	mc.setAttr(mdn+'.input1',1.0,1.0,1.0)
	mc.setAttr(mdn+'.operation',2)
	mc.connectAttr(mdn+'.output',ctrl+'.s',f=True)
	
def unfreezeCtrlScale(ctrl):
	'''
	'''
	mdn = mc.listConnections(ctrl+'.s',s=True,d=False)
	if mdn: mc.delete(mdn)
	
def setTranslateLimits(ctrl,tx=[],ty=[],tz=[]):
	'''
	'''
	if(tx): mc.transformLimits(ctrl,tx=(tx[0],tx[1]),etx=(1,1))
	if(ty): mc.transformLimits(ctrl,ty=(ty[0],ty[1]),ety=(1,1))
	if(tz): mc.transformLimits(ctrl,tz=(tz[0],tz[1]),etz=(1,1))
