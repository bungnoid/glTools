import maya.cmds as mc
import maya.mel as mm

def create():
	'''
	This generates the menu for all rigTools.
	'''
	# This is a temporary hack to get maya to evaluate $gMainWindow
	gMainWindow = mm.eval('string $temp = $gMainWindow')
	if mc.menu('rigToolsMenu',q=True,ex=True): mc.deleteUI('rigToolsMenu')
	
	if (len(gMainWindow)):
		mc.setParent(gMainWindow)
		mc.menu('rigToolsMenu', label='Rig Tools', tearOff=True, allowOptionBoxes=True)
		
		#----------------------------------------#
		
		mc.menuItem(label='Checks', subMenu=True, tearOff=True)
		mc.menuItem(label='Namespaces', command='mm.eval("mCleanerNamespaces(0)")')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(label='Fixes', subMenu=True, tearOff=True)
		mc.menuItem(label='Namespaces', command='mm.eval("mCleanerNamespaces(1)")')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider=True)
		
		mc.menuItem(allowOptionBoxes=True, label= 'Rig Propagation', subMenu=True, tearOff=True)
		
		mc.menuItem(label= 'Blengine', command='mm.eval("blengine")')
		mc.menuItem(label= 'Blend Installer', command='mm.eval("blendInstaller(0)")')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		mc.menuItem(divider=True)
		
		mc.menuItem(allowOptionBoxes=True, label= 'Rig', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create Base Rig', command='glTools.builder.BaseRig().build()')
		mc.menuItem(label='Control Builder', command='glTools.ui.controlBuilder.controlBuilderUI()')
		mc.menuItem(label='Group', command='for i in mc.ls(sl=True,type="transform"): glTools.utils.base.group(i,0,True,True)',ann='Create a centered and oriented transform group for the selected object/s')
		mc.menuItem(label='Buffer', command='for i in mc.ls(sl=True,type="transform"): glTools.utils.base.group(i,1,True,True)',ann='Create a centered and oriented transform buffer for the selected object/s')
		mc.menuItem(label='Channel State', command='glTools.utils.ChannelState().ui()')
		mc.menuItem(label='Toggle Override', command='glTools.utils.toggleOverride.ui()')
		mc.menuItem(label='Colorize', command='mm.eval("colorize")')
		mc.menuItem(label='Replace Geometry', command='glTools.ui.replaceGeometry.replaceGeometryFromUI()', ann='First select the replacement geometry and then the geometry to be replaced.')
		mc.menuItem(label='Create Surface Skin Menu', command='glTools.surfaceSkin.SurfaceSkinUI().menu()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='General', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Namespacer', command='mm.eval("namespacer")')
		mc.menuItem(label='Renamer', command='mm.eval("renamer")')
		mc.menuItem(label='Dag Sort', command='mm.eval("quicksort")')
		mc.menuItem(label='Dk Anim', command='mm.eval("dkAnim")')
		mc.menuItem(label='Parent List', command='glTools.ui.base.parentListUI()')
		mc.menuItem(label='Reorder Attributes', command='glTools.tools.reorderAttr.reorderAttrUI()')
		mc.menuItem(label='Rename History Nodes', command='glTools.ui.base.renameHistoryNodesUI()')
		mc.menuItem(label='Create Intermediate Shape', command='glTools.utils.shape.createIntermediate(mc.listRelatives(mc.ls(sl=1)[0],s=True,pa=True)[0])')
		mc.menuItem(label='Attribute Presets', command='glTools.ui.attrPreset.ui()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Animation', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Graph Editor Filter', command='glTools.tools.graphFilter.ui()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Joint', subMenu=True, tearOff=True)
		mc.menuItem(label='Joint Orient Tool', command='glTools.ui.joint.jointOrientUI()')
		mc.menuItem(label='Joint Match Orient', command='glTools.utils.joint.orientTo(mc.ls(sl=1)[1],mc.ls(sl=1)[0])')
		mc.menuItem(label='Freeze Joint Transform', command='mc.makeIdentity(mc.ls(sl=True,type="joint"),apply=True,t=True,r=True,s=True,n=False)')
		
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='IK', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create IK Handle', command='glTools.ui.ik.ikHandleUI()')
		mc.menuItem(label='Stretchy IK Chain', command='glTools.ui.ik.stretchyIkChainUI()')
		mc.menuItem(label='Stretchy IK Limb', command='glTools.ui.ik.stretchyIkLimbUI()')
		mc.menuItem(label='Stretchy IK Spline', command='glTools.ui.ik.stretchyIkSplineUI()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Curve', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Locator Curve', command='glTools.ui.curve.locatorCurveUI()')
		mc.menuItem(label='Attach To Curve', command='glTools.ui.curve.attachToCurveUI()')
		mc.menuItem(label='Curve To Locators', command='glTools.ui.curve.curveToLocatorsUI()')
		mc.menuItem(label='Create Along Curve', command='glTools.ui.curve.createAlongCurveUI()')
		mc.menuItem(label='Curve From Edge Loop', command='glTools.ui.curve.edgeLoopCurveUI()')
		mc.menuItem(label='Uniform Rebuild', command='glTools.ui.curve.uniformRebuildCurveUI()')
		
		mc.menuItem(allowOptionBoxes=True, label='LidRails', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create LidSurface', command='glTools.ui.lidRails.lidSurfaceCreateUI()')
		mc.menuItem(label='3 Control Setup', command='glTools.ui.lidRails.threeCtrlSetupUI()')
		mc.menuItem(label='4 Control Setup', command='glTools.ui.lidRails.fourCtrlSetupUI()')
		
		mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Surface', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Locator Surface', command='glTools.ui.surface.locatorSurfaceUI()')
		mc.menuItem(label='Snap To Surface', command='glTools.ui.surface.snapToSurfaceUI()')
		mc.menuItem(label='Attach To Surface', command='glTools.ui.surface.attachToSurfaceUI()')
		mc.menuItem(label='Surface Points', command='glTools.ui.surface.surfacePointsUI()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Mesh', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Snap To Mesh', command='glTools.ui.mesh.snapToMeshUI()')
		mc.menuItem(label='Interactive Snap Tool', command='glTools.ui.mesh.interactiveSnapToMeshUI()')
		mc.menuItem(label='Attach To Mesh', command='glTools.ui.mesh.attachToMeshUI()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='SkinCluster', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Make Relative', command='glTools.ui.skinCluster.makeRelativeUI()')
		mc.menuItem(label='Reset', command='glTools.ui.skinCluster.resetFromUI()')
		mc.menuItem(label='Clear Weights', command='glTools.utils.skinCluster.clearWeights()')
		mc.menuItem(label='Delete BindPose Nodes', command='mc.delete(mc.ls(type="dagPose"))')
		mc.menuItem(label='Rename SkinCluster', command='for i in mc.ls(sl=1): glTools.utils.skinCluster.rename(i)')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='nDynamics', subMenu=True, tearOff=True)
		
		mc.menuItem(label='UI', command='glTools.ui.nDynamics.create()')
		mc.menuItem(divider=True)
		mc.menuItem(label='Create nucleus', command='glTools.utils.nDynamics.createNucleus()')
		mc.menuItem(label='Create nCloth', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.createNCloth(i)')
		mc.menuItem(label='Create nRigid', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.createNRigid(i)')
		mc.menuItem(divider=True)
		mc.menuItem(label='Delete nCloth', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.deleteNCloth(i)')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Spaces', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create/Add', command='glTools.ui.spaces.createAddUI()')
		mc.menuItem(label='Spaces UI', command='glTools.tools.spaces.Spaces().ui()')
		
		mc.menuItem(ob=True, command='glTools.ui.spaces.charUI()')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Pose Match Setup', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Evaluation Order', command='glTools.ui.poseMatch.evaluationOrderUI()')
		mc.menuItem(label='Match Rules', command='glTools.ui.poseMatch.matchRulesUI()')
		
		mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider=True)
		
		mc.menuItem(allowOptionBoxes=True, label= 'Aci Utilities', subMenu=True, tearOff=False)
		
		mc.menuItem(label='Load Default Page', command='stage.editAciFile("/home/r/rgomez/Desktop/ACI/prop.aci",actorName="")')
		mc.menuItem(label='Build Prop Aci', command='import glTools.utils.propAci;glTools.utils.propAci.PropAci().addControls(mc.ls(sl=1))')
				
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider=True)
		
		mc.menuItem(allowOptionBoxes=True, label= 'Resolution Utilities', subMenu=True, tearOff=False)
		
		mc.menuItem(label='Add Char Res', command='glTools.ui.resolution.addResAttr(isProp=False);glTools.common.SmoothMeshUtilities().smoothWrapper()')
		mc.menuItem(label='Add Prop Res', command='glTools.ui.resolution.addResAttr(isProp=True);glTools.common.SmoothMeshUtilities().smoothWrapper()')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
				
		mc.menuItem(divider=True)
		
		mc.menuItem(allowOptionBoxes=True, label= 'Display Utilities', subMenu=True, tearOff=False)
		
		mc.menuItem(label='Connect Control Vis', command='glTools.common.VisibilityUtilities().connectControls()')
				
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider =True)
		
		mc.menuItem(label='Refresh Menu', command='reload(glTools.ui.menu);glTools.ui.menu.create()')
		
		mc.setParent('..')
