import maya.mel as mm
import maya.cmds as mc

import glTools.ui.utils

import os.path

def import2dTrackUI():
	'''
	'''
	# Build UI Window
	window = 'import2dTrackUI'
	if mc.window(window,q=True,ex=True): mc.deleteUI(window)
	window = mc.window(window,title='Import 2D Track',wh=[500,350])
	
	# Build UI Elements
	mc.columnLayout(adjustableColumn=True)
	perspCamListTSL = mc.textScrollList('importTrack_camListTSL',numberOfRows=8,ams=False)
	fileTFB = mc.textFieldButtonGrp('importTrack_fileTFB',label='2D Track File',buttonLabel='Browse')
	mc.textFieldButtonGrp(fileTFB,e=True,bc='glTools.ui.utils.loadFilePath("'+fileTFB+'",fileFilter="*.*")')
	mc.textFieldGrp('importTrack_nameTFG',label="Point Name",text='trackPoint1')
	mc.floatFieldGrp('importTrack_widthFFG',numberOfFields=1,label='Source Pixel Width',value1=2348)
	mc.floatFieldGrp('importTrack_heightFFG',numberOfFields=1,label='Source Pixel Height',value1=1566)
	mc.button(label='Import Track',c='import glTools.tools.import2dTrack;reload(glTools.tools.import2dTrack);glTools.tools.import2dTrack.import2dTrack()')
	mc.button(label='Close',c='mc.deleteUI("'+window+'")')
	
	# Build Camera List
	camList = mc.listCameras(p=True)
	for cam in camList: mc.textScrollList(perspCamListTSL,e=True,a=cam)
	
	# Show Window
	mc.showWindow(window)

def import2dTrack():
	'''
	'''
	# Get UI Elements
	perspCamListUI = 'importTrack_camListTSL'
	fileUI = 'importTrack_fileTFB'
	pixelWidthUI = 'importTrack_widthFFG'
	pixelHeightUI = 'importTrack_heightFFG'
	pointNameUI = 'importTrack_nameTFG'
	
	# Get UI Values
	w = mc.floatFieldGrp(pixelWidthUI,q=True,v1=True)
	h = mc.floatFieldGrp(pixelHeightUI,q=True,v1=True)
	cam = mc.textScrollList(perspCamListUI,q=True,si=True)[0]
	filePath = mc.textFieldButtonGrp(fileUI,q=True,text=True)
	pointName = mc.textFieldGrp(pointNameUI,q=True,text=True)
	
	# Ensure Camera Transform is Selected
	if mc.objectType(cam) == 'camera':
		cam = mc.listRelatives(cam,p=True)[0]
	
	# Check Track File Path
	if not os.path.isfile(filePath):
		raise Exception('Invalid file path "'+filePath+'"!')
	
	# Build Track Point Scene Elements
	point = mc.spaceLocator(n=pointName)[0]
	plane = mc.nurbsPlane(ax=(0,0,1),w=1,lr=1,d=1,u=1,v=1,ch=1,n=pointName+'Plane')[0]
	print plane
	
	# Position Track Plane
	plane = mc.parent(plane,cam)[0]
	mc.setAttr(plane+'.translate',0,0,-5)
	mc.setAttr(plane+'.rotate',0,0,0)
	for attr in ['.tx','.ty','.rx','.ry','.rz']:
		mc.setAttr(plane+attr,l=True)
	
	# Add FOV Attributes
	if not mc.objExists(cam+'.horizontalFOV'):
		mc.addAttr(cam,ln='horizontalFOV',at='double')
	if not mc.objExists(cam+'.verticalFOV'):
		mc.addAttr(cam,ln='verticalFOV',at='double')
	
	# Create FOV Expression
	expStr = '// Get Horizontal and Vertical FOV\r\n\r\n'
	expStr += 'float $focal ='+cam+'.focalLength;\r\n'
	expStr += 'float $aperture = '+cam+'.horizontalFilmAperture;\r\n\r\n'
	expStr += 'float $fov = (0.5 * $aperture) / ($focal * 0.03937);\r\n'
	expStr += '$fov = 2.0 * atan ($fov);\r\n'
	expStr += cam+'.horizontalFOV = 57.29578 * $fov;\r\n\r\n'
	expStr += 'float $aperture = '+cam+'.verticalFilmAperture;\r\n\r\n'
	expStr += 'float $fov = (0.5 * $aperture) / ($focal * 0.03937);\r\n'
	expStr += '$fov = 2.0 * atan ($fov);\r\n'
	expStr += cam+'.verticalFOV = 57.29578 * $fov;\r\n\r\n'
	expStr += '// Scale plane based on FOV\r\n\r\n'
	expStr += 'float $dist = '+plane+'.translateZ;\r\n'
	expStr += 'float $hfov = '+cam+'.horizontalFOV / 2;\r\n'
	expStr += 'float $vfov = '+cam+'.verticalFOV / 2;\r\n\r\n'
	expStr += 'float $hyp = $dist / cos(deg_to_rad($hfov));\r\n'
	expStr += 'float $scale = ($hyp * $hyp) - ($dist * $dist);\r\n'
	expStr += plane+'.scaleX = (sqrt($scale)) * 2;\r\n\r\n'
	expStr += 'float $hyp = $dist / cos(deg_to_rad($vfov));\r\n'
	expStr += 'float $scale = ($hyp * $hyp) - ($dist * $dist);\r\n'
	expStr += plane+'.scaleY = (sqrt($scale)) * 2;'
	mc.expression(s=expStr,o=plane,n='planeFOV_exp',ae=1,uc='all')
	
	# Open Track Data File
	count = 0
	f = open(filePath,'r')
	
	# Build Track Path Curve
	crvCmd = 'curveOnSurface -d 1 '
	for line in f:
		u,v = line.split()
		crvCmd += '-uv '+str(float(u)*(1.0/w))+' '+str(float(v)*(1.0/h))+' '
		count+=1
	crvCmd += plane
	print crvCmd
	path = mm.eval(crvCmd)
	
	# Close Track Data File
	f.close()
	
	# Rebuild Curve
	mc.rebuildCurve(path,fitRebuild=False,keepEndPoints=True,keepRange=True,spans=0,degree=3)
	
	# Attach Track Point to Path
	motionPath = mc.pathAnimation(point,path,fractionMode=False,follow=False,startTimeU=1,endTimeU=count)
	exp = mc.listConnections(motionPath+'.uValue')
	if exp: mc.delete(exp)
	mc.setKeyframe(motionPath,at='uValue',t=1,v=0)
	mc.setKeyframe(motionPath,at='uValue',t=count,v=count-1)

