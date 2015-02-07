import maya.cmds as mc
import maya.mel as mm

def create():
	'''
	This generates the menu for all modelTools.
	'''
	# This is a temporary hack to get maya to evaluate $gMainWindow
	gMainWindow = mm.eval('string $temp = $gMainWindow')
	if mc.menu('modelToolsMenu',q=True,ex=True): mc.deleteUI('modelToolsMenu')
	
	if gMainWindow:
		
		mc.setParent(gMainWindow)
		mc.menu('modelToolsMenu', label='Model Tools', tearOff=True, allowOptionBoxes=True)
		
		#----------------------------------------#
		
		mc.menuItem(label='Checks', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Run Checks', command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_MODEL_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=False)')
		mc.menuItem(label='Run Checks On Selected', command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_MODEL_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=True)')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider=True)
		
		# GENERAL
		mc.menuItem(allowOptionBoxes=True, label='General', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Align to Ground Plane', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.setVerticalPlacement(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Build Poly Edge Curves', command='import glTools.tools.polyEdgeCurve;reload(glTools.tools.polyEdgeCurve);glTools.tools.polyEdgeCurve.buildEdgeCurvesUI()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(divider=True)
		
		# TOOLS
		mc.menuItem(allowOptionBoxes=True, label='Tools', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Slide Deformer', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.slideDeformer(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Strain Relaxer', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.strainRelaxer(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Directional Smooth', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.directionalSmooth(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Straighten Vertices...', command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.straightenVertsUI()')
		mc.menuItem(label='Even Edge Spacing...', command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.evenEdgeSpacingUI()')
		mc.menuItem(label='Smooth Edge Line...', command='import glTools.model.straightenVerts;reload(glTools.model.straightenVerts);glTools.model.straightenVerts.smoothEdgeLineUI()')
		
		mc.menuItem(allowOptionBoxes=True, label='Mirror Tools', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Auto Mirror', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.autoMirror()')
		mc.menuItem(label='Mirror X (+ -> -)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0])')
		mc.menuItem(label='Mirror X (- -> +)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0],posToNeg=False)')
		mc.menuItem(label='Mirror Y (+ -> -)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0]),axis="y"')
		mc.menuItem(label='Mirror Y (- -> +)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0],axis="y",posToNeg=False)')
		mc.menuItem(label='Mirror Z (+ -> -)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0]),axis="z"')
		mc.menuItem(label='Mirror Z (- -> +)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0],axis="z",posToNeg=False)')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Align Tools', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Align to Best Fit', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="bestFitPlane",localAxis=False)')
		
		mc.menuItem(label='Align (+X) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+x",localAxis=True)')
		mc.menuItem(label='Align (-X) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-x",localAxis=True)')
		mc.menuItem(label='Align (+Y) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+y",localAxis=True)')
		mc.menuItem(label='Align (-Y) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-y",localAxis=True)')
		mc.menuItem(label='Align (+Z) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+z",localAxis=True)')
		mc.menuItem(label='Align (-Z) Local', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-z",localAxis=True)')
		
		mc.menuItem(label='Align (+X) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+x",localAxis=False)')
		mc.menuItem(label='Align (-X) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-x",localAxis=False)')
		mc.menuItem(label='Align (+Y) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+y",localAxis=False)')
		mc.menuItem(label='Align (-Y) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-y",localAxis=False)')
		mc.menuItem(label='Align (+Z) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="+z",localAxis=False)')
		mc.menuItem(label='Align (-Z) World', command='import glTools.model.utils;reload(glTools.model.utils);glTools.model.utils.alignControlPoints(mc.ls(sl=True,fl=True),axis="-z",localAxis=False)')
		
		mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider =True)
		mc.menuItem(label='Refresh Menu', command='import glTools.model.menu;reload(glTools.model.menu);glTools.model.menu.create()')
		mc.setParent('..')
