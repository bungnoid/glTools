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
		
		# > CHECKS
		mc.menuItem(label='Checks', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Run Checks', command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_RIG_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=False)')
		mc.menuItem(label='Run Checks On Selected', command='import glTools.spotcheck.runChecks;reload(glTools.spotcheck.runChecks);glTools.spotcheck.runChecks.run(envKey="IKA_RIG_SPOTCHECKS",checkTitle="Rig Checks",selectedNodes=True)')
		mc.menuItem(divider=True)
		mc.menuItem(label='Check NonReference Geo Inputs', command='import glTools.tools.fixNonReferenceInputShape;reload(glTools.tools.fixNonReferenceInputShape);glTools.tools.fixNonReferenceInputShape.checkNonReferenceInputShapes(mc.ls(sl=1)[0],verbose=True)')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		# > FIXES
		mc.menuItem(label='Fixes', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Fix NonReference Geo Inputs', command='import glTools.tools.fixNonReferenceInputShape;reload(glTools.tools.fixNonReferenceInputShape);glTools.tools.fixNonReferenceInputShape.fixNonReferenceInputShapes(mc.ls(sl=1)[0],verbose=True)')
		
		mc.setParent('..', menu=True)
		
		# > MENU
		
		mc.menuItem(label='Menu', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create Surface Skin Menu', command='import glTools.surfaceSkin; glTools.surfaceSkin.SurfaceSkinUI().menu()')
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		
		mc.menuItem(divider=True)
		
		# > GENERAL
		mc.menuItem(allowOptionBoxes=True, label='General', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Renamer', command='mm.eval("renamer")',ann='Open Renamer UI')
		mc.menuItem(label='Colorize UI', command='mm.eval("colorize")',ann='Open Colorizer UI')
		mc.menuItem(label='Set Colour', command='import glTools.utils.colorize;reload(glTools.utils.colorize);[glTools.utils.colorize.setColour(i) for i in mc.ls(sl=1)]',ann='Set colours based on object naming')
		mc.menuItem(label='Colour Hierarchy', command='import glTools.utils.colorize;reload(glTools.utils.colorize);[glTools.utils.colorize.colourHierarchy(i) for i in mc.ls(sl=1)]',ann='Set colours for all nodes in hierarchy based on object naming')
		mc.menuItem(label='Namespacer', command='mm.eval("namespacer")',ann='Open Namespacer UI')
		mc.menuItem(label='Dag Sort', command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.dagSort()',ann='Sort DAG objects by name')
		mc.menuItem(label='Rename Duplicates', command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.renameDuplicates()',ann='Rename duplicate objects')
		mc.menuItem(label='Select By Attribute',command='import glTools.utils.selection;reload(glTools.utils.selection);mc.select(glTools.utils.selection.selectByAttr())',ann='Select objects by attribute name')
		mc.menuItem(label='Parent List', command='glTools.ui.base.parentListUI()',ann='Open Parent List UI')
		mc.menuItem(label='Parent Shapes', command='import glTools.utils.shape;reload(glTools.utils.shape);glTools.utils.shape.parent(mc.ls(sl=True)[0],mc.ls(sl=True)[1])',ann='Parent shape(s) to a different transform. Select shape node or transform, follwed by the target transform')
		mc.menuItem(label='Unparent Shapes', command='import glTools.utils.shape;reload(glTools.utils.shape);[glTools.utils.shape.unparent(i) for i in mc.ls(sl=True)]',ann='Unparent shapes from the selected tarnsform')
		mc.menuItem(label='Rename Shapes', command='import glTools.utils.shape;reload(glTools.utils.shape);[glTools.utils.shape.rename(i) for i in mc.ls(sl=1)]',ann='Rename shape nodes based on the parent transform')
		mc.menuItem(label='Reorder Attributes', command='glTools.tools.reorderAttr.reorderAttrUI()',ann='Open Reorder Attributes UI')
		mc.menuItem(label='Rename History Nodes', command='glTools.ui.base.renameHistoryNodesUI()',ann='Open Rename History Nodes UI')
		mc.menuItem(label='Create Intermediate Shape', command='glTools.utils.shape.createIntermediate(mc.ls(sl=1)[0])',ann='Create Intermediate Shape for the selected geometry.')
		mc.menuItem(label='Attribute Presets', command='glTools.ui.attrPreset.ui()',ann='Open attribute presets UI')
		mc.menuItem(label='Swap Nodes', command='import glTools.utils.connection;reload(glTools.utils.connection);glTools.utils.connection.swap(mc.ls(sl=1)[0],mc.ls(sl=1)[1])',ann='Swap Node Connections')
		mc.menuItem(label='Delete Unknown Nodes',command='import glTools.utils.cleanup;reload(glTools.utils.cleanup);glTools.utils.cleanup.deleteUnknownNodes()',ann='Delete all "unknown" nodes')
		
		mc.menuItem(label='Match Transform', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=mc.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected transform to second selected transform')
		mc.menuItem(label='Match Bounding Box', command='import glTools.utils.boundingBox;reload(glTools.utils.boundingBox);sel=mc.ls(sl=1);glTools.utils.boundingBox.match(sel[0],sel[1])',ann='Match first selected transform to second selected transform based on bounding box comparison')
		#mc.menuItem(label='Match Position', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=mc.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object position to second selected object')
		#mc.menuItem(label='Match Orientation', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=mc.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object orientation/rotation to second selected object')
		#mc.menuItem(label='Match Scale', command='import glTools.utils.transform;reload(glTools.utils.transform);sel=mc.ls(sl=1);glTools.utils.transform.match(sel[0],sel[1])',ann='Match first selected object scale to second selected object')
		
		# >> MATCH ATTRIBUTES
		mc.menuItem(allowOptionBoxes=True, label='Match Attrs', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Match All', command='import glTools.tools.match;reload(glTools.tools.match);sel=mc.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["tx","ty","tz","rx","ry","rz","sx","sy","sz"])',ann='Match all local transform values')
		mc.menuItem(label='Match Translate', command='import glTools.tools.match;reload(glTools.tools.match);sel=mc.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["tx","ty","tz"])',ann='Match local translate values')
		mc.menuItem(label='Match Rotate', command='import glTools.tools.match;reload(glTools.tools.match);sel=mc.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["rx","ry","rz"])',ann='Match local rotate values')
		mc.menuItem(label='Match Scale', command='import glTools.tools.match;reload(glTools.tools.match);sel=mc.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],["sx","sy","sz"])',ann='Match local scale values')
		mc.menuItem(label='Match From CB', command='import glTools.tools.match;reload(glTools.tools.match);sel=mc.ls(sl=1);glTools.tools.match.matchAttrs(sel[0],sel[1],"fromChannelBox")',ann='Match all values based on channel selection (channelBox)')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(label='Graph Profiler', command='import glTools.ui.qt.graphProfiler;reload(glTools.ui.qt.graphProfiler);glTools.ui.qt.graphProfiler.GraphProfiler().show()',ann='Tools to Collect and Display Dependency Graph Data')
		
		mc.setParent('..', menu=True)
		
		# > TOOLS
		mc.menuItem(allowOptionBoxes=True, label='Tools', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Center Pt Locator', command='import glTools.tools.center;reload(glTools.tools.center);glTools.tools.center.centerPointLocator(mc.ls(sl=True,fl=True))',ann='Create locator at center of point selection.')
		mc.menuItem(label='Center to Geometry', command='import glTools.tools.center;reload(glTools.tools.center);sel = mc.ls(sl=True,fl=True);glTools.tools.center.centerToGeometry(sel[0],sel[1])',ann='Select the geometry and the object to position.')
		mc.menuItem(label='Center to Points', command='import glTools.tools.center;reload(glTools.tools.center);sel = mc.ls(sl=True,fl=True);glTools.tools.center.centerToPoints(sel[:-1],sel[-1])',ann='Select the points and the object to position.')
		mc.menuItem(label='Point Face Mesh', command='import glTools.tools.pointFaceMesh;reload(glTools.tools.pointFaceMesh);glTools.tools.pointFaceMesh.pointFaceMesh(mc.ls(sl=True,fl=True),combine=False)',ann='Create single mesh face at each point in selection.')
		
		mc.menuItem(label='Slide Deformer', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.slideDeformer(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Strain Relaxer', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.strainRelaxer(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Directional Smooth', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.directionalSmooth(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Delta Mush', command='import glTools.model.utils;reload(glTools.model.utils);[glTools.model.utils.deltaMush(i) for i in mc.ls(sl=1)]')
		
		mc.setParent('..', menu=True)
		
		# > SELECTION
		mc.menuItem(allowOptionBoxes=True, label='Select', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Select Hierarchy', command='mm.eval("SelectHierarchy")')
		
		mc.menuItem(allowOptionBoxes=True, label='Select All Below (by type)', subMenu=True, tearOff=True)
		mc.menuItem(label='constraint', command='mc.select(mc.ls(mc.listRelatives(ad=True,pa=True) or [],type="constraint"))')
		mc.menuItem(label='ikHandle', command='mc.select(mc.ls(mc.listRelatives(ad=True,pa=True) or [],type="ikHandle"))')
		mc.menuItem(label='joint', command='mc.select(mc.ls(mc.listRelatives(ad=True,pa=True) or [],type="joint"))')
		
		mc.setParent('..', menu=True)
		
		mc.menuItem(allowOptionBoxes=True, label='Select Directly Below (by type)', subMenu=True, tearOff=True)
		mc.menuItem(label='constraint', command='mc.select(mc.ls(mc.listRelatives(c=True,pa=True) or [],type="constraint"))')
		mc.menuItem(label='ikHandle', command='mc.select(mc.ls(mc.listRelatives(c=True,pa=True) or [],type="ikHandle"))')
		mc.menuItem(label='joint', command='mc.select(mc.ls(mc.listRelatives(c=True,pa=True) or [],type="joint"))')
		
		mc.setParent('..', menu=True)
		mc.menuItem(label='Mirror Polygon Selection', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorSelection()')
		
		mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		# > REFERENCE
		mc.menuItem(allowOptionBoxes=True, label='Reference', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Reload Reference', command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.reloadSelected()')
		mc.menuItem(label='Unload Reference', command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.unloadSelected()')
		mc.menuItem(label='Remove Reference', command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.removeSelected(removeNS=False)')
		mc.menuItem(label='Remove Reference and NS', command='import glTools.anim.reference_utils;reload(glTools.anim.reference_utils);glTools.anim.reference_utils.removeSelected(removeNS=True)')
		mc.menuItem(label='Remove Unloaded References', command='import glTools.utils.reference;reload(glTools.utils.reference);glTools.utils.reference.removeUnloadedReferences()')
		mc.menuItem(label='Remove Reference Edits', command='import glTools.tools.removeReferenceEdits;reload(glTools.tools.removeReferenceEdits);glTools.tools.removeReferenceEdits.removeReferenceEditsUI()')
		
		mc.setParent('..', menu=True)
		
		# > SHADER
		mc.menuItem(allowOptionBoxes=True, label='Shader', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Apply Reference Shader', command='import glTools.utils.shader;reload(glTools.utils.shader);[glTools.utils.shader.applyReferencedShader(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Reconnect Shader', command='import glTools.utils.shader;reload(glTools.utils.shader);[glTools.utils.shader.reconnectShader(i) for i in mc.ls(sl=1)]')
		
		mc.setParent('..', menu=True)
		
		# > RIG
		mc.menuItem(allowOptionBoxes=True, label= 'Rig', subMenu=True, tearOff=True)
		
		#mc.menuItem(label='Create Base Rig', command='glTools.builder.BaseRig().build()')
		mc.menuItem(label='Rename Chain', command='import glTools.utils.base;reload(glTools.utils.base);glTools.utils.base.renameChain(mc.ls(sl=1,l=False)[0])',ann='Rename the selected joint hierarchy')
		mc.menuItem(label='Control Builder', command='glTools.ui.controlBuilder.controlBuilderUI()',ann='Open ControlBuilder UI')
		mc.menuItem(label='Group', command='for i in mc.ls(sl=True,type=["transform","joint","ikHandle"]): glTools.utils.base.group(i,True,True)',ann='Create a centered and oriented transform group for the selected object/s')
		mc.menuItem(label='Toggle Override', command='glTools.utils.toggleOverride.ui()',ann='Open Toggle Override UI')
		mc.menuItem(label='Replace Geometry', command='glTools.ui.replaceGeometry.replaceGeometryFromUI()', ann='First select the replacement geometry and then the geometry to be replaced.')
		mc.menuItem(label='Create Bind Joint Set', command='mc.sets(mc.ls("*.bindJoint",o=True),n="bindJoints")', ann='Create a bindJoints set for all tagged bind joints. ("*.bindJoint")')
		mc.menuItem(label='Clean Rig', command='import glTools.rig.cleanup;reload(glTools.rig.cleanup);glTools.rig.cleanup.clean()',ann='Clean Rig Workfile')
		
		# > > Flatten Scene
		mc.menuItem(allowOptionBoxes=True, label= 'Flatten Scene', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Flatten Scene', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.flatten()',ann='Flatten Scene - Import all references and delete all namespaces etc.')
		#----------------------------------------#
		mc.menuItem(divider =True)
		#----------------------------------------#
		mc.menuItem(label='NodesToDelete Set', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.createNodesToDeleteSet(mc.ls(sl=True))',ann='Create "nodesToDelete" set')
		mc.menuItem(label='Add Rename Attr', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addRenameAttr(i) for i in mc.ls(sl=True)]',ann='Add "renameOnFlatten" attribute.')
		mc.menuItem(label='Add Reparent Attr', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);glTools.tools.flattenScene.addReparentAttrFromSel()',ann='Add "reparentOnFlatten" attribute based on current selection.')
		mc.menuItem(label='Add Delete History Attr', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addDeleteHistoryAttr(i) for i in mc.ls(sl=True,dag=True)]',ann='Add "deleteHistoryOnFlatten" attribute based on current selection.')
		mc.menuItem(label='Add Reference Path Attr', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addReferencePathAttr(i) for i in mc.ls(sl=True)]',ann='Add "fixNonReferenceInputsRoot" attribute based on current selection.')
		mc.menuItem(label='Add Fix NonReference Inputs Attr', command='import glTools.tools.flattenScene;reload(glTools.tools.flattenScene);[glTools.tools.flattenScene.addFixNonReferenceInputAttr(i) for i in mc.ls(sl=True)]',ann='Add "encodeReferenceFilePath" attribute based on current selection.')
		
		mc.setParent('..', menu=True)
		
		# > > Channel State
		mc.menuItem(allowOptionBoxes=True, label= 'Channel State', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Channel State', command='import glTools.utils.channelState; reload(glTools.utils.channelState); glTools.utils.channelState.ChannelState().ui()',ann='Open ChannelState UI')
		mc.menuItem(divider=True)
		mc.menuItem(label='Record Visibility State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.recordVisibility(mc.listRelatives("all",ad=True))',ann='Record default visibility state for all nodes under rig root node ("all").')
		mc.menuItem(label='Record Display Override State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.recordDisplayOverrides(mc.listRelatives("all",ad=True))',ann='Record default display override state for all nodes under rig root node ("all").')
		mc.menuItem(divider=True)
		mc.menuItem(label='Disable Visibility State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setVisibilityState(visibilityState=0)',ann='Disable visibility state for all nodes with recorded default visibility state.')
		mc.menuItem(label='Disable Display Override State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setDisplayOverridesState(displayOverrideState=0)',ann='Disable display override state for all nodes with recorded default display override state.')
		mc.menuItem(divider=True)
		mc.menuItem(label='Restore Visibility State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setVisibilityState(visibilityState=1)',ann='Restore visibility state for all nodes with recorded default visibility state.')
		mc.menuItem(label='Restore Display Override State', command='import glTools.utils.defaultAttrState;reload(glTools.utils.defaultAttrState);glTools.utils.defaultAttrState.setDisplayOverridesState(displayOverrideState=1)',ann='Restore display override state for all nodes with recorded default display override state.')
		
		mc.setParent('..', menu=True)
		
		# > > Export Attrs
		mc.menuItem(allowOptionBoxes=True, label= 'Export Attrs', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Rest Cache Name',command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);[glTools.snapshot.utils.restCacheName(i) for i in mc.ls(sl=1)]',ann='Add "restCacheName" attribute to the selected components')
		mc.menuItem(label='Include in Snapshot',command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);[glTools.snapshot.utils.includeInSnapshot(i) for i in mc.ls(sl=1)]',ann='Add "includeInSnapshot" attribute to the selected objects')
		mc.menuItem(label='Distance To Camera',command='import glTools.snapshot.utils;reload(glTools.snapshot.utils);sel = mc.ls(sl=1);glTools.snapshot.utils.distToCamObjAttr(sel[0],sel[1])',ann='Add "distToCamObj" attribute to the first selected object, and connect to the second selected object')
		mc.menuItem(divider=True)
		mc.menuItem(label='Set NonRenderable Faces',command='import glTools.rig.utils;reload(glTools.rig.utils);glTools.rig.utils.nonRenderableFaceSet(facelist=mc.ls(sl=1))',ann='Add a non-renderable faceset attribute to a mesh(es) based on the selected polygon faces.')
		mc.menuItem(label='Select NonRenderable Faces',command='import glTools.rig.utils;reload(glTools.rig.utils);sel = mc.ls(sl=1);glTools.rig.utils.selectNonRenderableFaces(sel[0])',ann='Select non-renderable faces on the first selected mesh.')
		
		mc.setParent('..', menu=True)
		
		# > > Proxy Mesh
		mc.menuItem(allowOptionBoxes=True, label= 'Proxy Mesh', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Joint Proxy Bounds', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.skeletonProxyCage(mc.ls(sl=1,type="joint"))')
		mc.menuItem(label='Joint Proxy Mirror', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.mirrorProxy(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Make Proxy Bounds', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.makeProxyBounds(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Reset Proxy Bounds', command='import glTools.utils.mesh;reload(glTools.utils.mesh);[glTools.utils.mesh.resetVertices(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Fit To Mesh', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxyFitMeshSel(-1.0)')
		mc.menuItem(label='Fit To Joint', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.proxyFitJoint(i) for i in mc.ls(sl=1)]')
		mc.menuItem(label='Snap to Joint', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.proxyConstraint(prx,deleteConstraint=True) for prx in mc.ls(sl=True,type="transform")]')
		mc.menuItem(label='Freeze to Joint', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);[glTools.tools.proxyMesh.freezeToJoint(prx) for prx in mc.ls(sl=True,type="transform")]')
		mc.menuItem(label='Set Proxy Cut Geometry', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setCutGeoFromSel()')
		mc.menuItem(label='Set Proxy Add Geometry', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setAddGeoFromSel()')
		mc.menuItem(label='Set Apply Initial SG', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.setApplyInitialSGFromSel()')
		mc.menuItem(label='Apply Proxies', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.applyProxies(mc.ls(sl=True,type="transform"))')
		mc.menuItem(label='Create SkinClusters', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxySkinClusters()')
		
		mc.setParent('..', menu=True)
		
		# > > AUTO MODULE
		mc.menuItem(allowOptionBoxes=True, label= 'Auto Module', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Base Template', command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.baseModuleTemplate)')
		mc.menuItem(label='FK Chain Template', command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.fkChainModuleTemplate)')
		mc.menuItem(label='IK Chain Template', command='import glTools.rig.autoModuleTemplate;reload(glTools.rig.autoModuleTemplate);glTools.rig.autoModuleTemplate.moduleTemplateDialog(glTools.rig.autoModuleTemplate.ikChainModuleTemplate)')
		mc.menuItem(divider=True)
		mc.menuItem(label='Build Selected Module(s)', command='import glTools.rig.autoModuleBuild;reload(glTools.rig.autoModuleBuild);[glTools.rig.autoModuleBuild.moduleBuild(i) for i in mc.ls(sl=True,type="transform")]')
		mc.menuItem(label='Build All Modules', command='import glTools.rig.autoModuleBuild;reload(glTools.rig.autoModuleBuild);glTools.rig.autoModuleBuild.moduleBuildAll()')
		
		mc.setParent('..', menu=True)
		
		# > BIPED
		mc.menuItem(allowOptionBoxes=True, label= 'Biped', subMenu=True, tearOff=True)
		
		biped_template = '/laika/library/VFX/rigging/biped_template.mb'
		mc.menuItem(label='Import Template', command='mc.file("'+biped_template+'",i=True,type="mayaBinary")')
		mc.menuItem(label='Mirror Template (Left To Right)', command='import glTools.nrig.rig.biped;reload(glTools.nrig.rig.biped);glTools.nrig.rig.biped.BipedRig().mirrorTemplate(leftToRight=True)')
		mc.menuItem(label='Mirror Template (Right To Left)', command='import glTools.nrig.rig.biped;reload(glTools.nrig.rig.biped);glTools.nrig.rig.biped.BipedRig().mirrorTemplate(leftToRight=False)')
		
		mc.setParent('..', menu=True)
		
		# > FACE
		mc.menuItem(allowOptionBoxes=True, label= 'Face', subMenu=True, tearOff=True)
		
		# Brow Template
		template_file = '/laika/library/VFX/rigging/face/brow/brow_template.mb'
		mc.menuItem(label='Import Brow Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Cheek Template
		template_file = '/laika/library/VFX/rigging/face/cheek/cheek_template.mb'
		mc.menuItem(label='Import Cheek Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Eye Template
		template_file = '/laika/library/VFX/rigging/face/eye/vfx_eye_rig.mb'
		mc.menuItem(label='Import Eye Template', command='mc.file("'+template_file+'",reference=True,namespace="eye",type="mayaBinary")')
		
		# Eyelid Template
		template_file = '/laika/library/VFX/rigging/face/eyelid/eyelid_template.mb'
		mc.menuItem(label='Import Eyelids Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Jaw Template
		template_file = '/laika/library/VFX/rigging/face/jaw/jaw_template.mb'
		mc.menuItem(label='Import Jaw Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Mouth Template
		template_file = '/laika/library/VFX/rigging/face/mouth/mouth_template.mb'
		mc.menuItem(label='Import Mouth Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Nose Template
		template_file = '/laika/library/VFX/rigging/face/nose/nose_template.mb'
		mc.menuItem(label='Import Nose Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Teeth Template
		template_file = '/laika/library/VFX/rigging/face/teeth/teeth_template.mb'
		mc.menuItem(label='Import Teeth Template', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		# Tongue Template
		template_file = '/laika/library/VFX/rigging/face/tongue/tongue_rig.mb'
		mc.menuItem(label='Import Tongue Template', command='mc.file("'+template_file+'",reference=True,namespace="tongue",type="mayaBinary")')
		
		# Secondary Control Locators
		template_file = '/laika/library/VFX/rigging/face/secondary/secondary_locs.mb'
		mc.menuItem(label='Import Secondary Ctrl Locators', command='mc.file("'+template_file+'",i=True,type="mayaBinary")')
		
		#mc.menuItem(label='Import Template', command='mc.file("/laika/jobs/hbm/vfx/asset/char/template/rig/scene_graph/pub/face_template.latest/template.rig.face_template.base.mb",i=True,type="mayaBinary")')
		#mc.menuItem(divider =True)
		#mc.menuItem(label='Create Sculpt Mask', command='import glTools.rig.faceRig;reload(glTools.rig.faceRig);glTools.rig.faceRig.FaceRig().createSculptMesh()')
		#mc.menuItem(label='Secondary Ctrl Input Mesh', command='import glTools.rig.faceRig;reload(glTools.rig.faceRig);glTools.rig.faceRig.FaceRig().connectSecondaryCtrlInputMesh()')
		#mc.menuItem(label='Create Secondary Ctrls', command='import glTools.rig.faceRig;reload(glTools.rig.faceRig);glTools.rig.faceRig.FaceRig().buildLocalCtrl()')
		#mc.menuItem(label='Set Secondary Ctrls Attach', command='import glTools.rig.faceRig;reload(glTools.rig.faceRig);glTools.rig.faceRig.FaceRig().buildLocalCtrl()')
		
		mc.setParent('..', menu=True)
		
		# > PROP
		mc.menuItem(allowOptionBoxes=True, label= 'Prop', subMenu=True, tearOff=True)
		mc.menuItem(label='Build Basic Prop', command='import glTools.nrig.rig.prop;reload(glTools.nrig.rig.prop);glTools.nrig.rig.prop.PropRig().build(clean=True)')
		
		mc.setParent('..', menu=True)
		
		# > Rig Constraints
		#mc.menuItem(allowOptionBoxes=True, label= 'Rig Constraints', subMenu=True, tearOff=True)
		#mc.menuItem(label='Create Constraint Target Locator', command='import glTools.rig.constraintTargetControl;reload(glTools.rig.constraintTargetControl);glTools.rig.constraintTargetControl.createTargetLocatorFromSel()')
		#mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		# Animation
		mc.menuItem(allowOptionBoxes=True, label='Animation', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Set To Default', command='import glTools.rig.utils;reload(glTools.rig.utils);[glTools.rig.utils.setToDefault(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Mirror Selected', command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().twinSelection()')
		mc.menuItem(label='Swap Selected', command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().swapSelection()')
		mc.menuItem(label='Select Mirror', command='import glTools.tools.match;reload(glTools.tools.match);glTools.tools.match.Match().selectTwin()')
		mc.menuItem(label='IK/FK Match', command='import glTools.rig.ikFkMatch;reload(glTools.rig.ikFkMatch);[glTools.rig.ikFkMatch.match(i) for i in mc.ls(sl=True)]')
		mc.menuItem(label='Dk Anim', command='mm.eval("dkAnim")')
		mc.menuItem(label='Graph Editor Filter', command='glTools.tools.graphFilter.ui()')
		
		mc.setParent('..', menu=True)
		
		# > JOINT
		mc.menuItem(allowOptionBoxes=True, label='Joint', subMenu=True, tearOff=True)
		mc.menuItem(label='Joint Group', command='import glTools.utils.joint;reload(glTools.utils.joint);[glTools.utils.joint.group(joint=i,indexStr="") for i in mc.ls(sl=1,type="joint")]')
		mc.menuItem(label='Connect Inverse Scale', command='import glTools.utils.joint;reload(glTools.utils.joint);[glTools.utils.joint.connectInverseScale(jnt) for jnt in mc.ls(sl=True,type="joint")]')
		mc.menuItem(label='Joint Orient Tool', command='import glTools.ui.joint;reload(glTools.ui.joint);glTools.ui.joint.jointOrientUI()')
		mc.menuItem(label='Joint Match Orient', command='glTools.utils.joint.orientTo(mc.ls(sl=1)[1],mc.ls(sl=1)[0])')
		mc.menuItem(label='Zero Joint Orient', command='[mc.setAttr(jnt+".jo",0,0,0) for jnt in mc.ls(sl=1,type="joint")]')
		mc.menuItem(label='Freeze Joint Transform', command='mc.makeIdentity(mc.ls(sl=True,type="joint"),apply=True,t=True,r=True,s=True,n=False)')
		mc.menuItem(label='Draw Style (Bone)', command='import glTools.utils.joint;reload(glTools.utils.joint);jnts = mc.ls(sl=1);glTools.utils.joint.setDrawStyle(jnts,drawStyle="bone")')
				
		mc.setParent('..', menu=True)
		
		# > IK
		mc.menuItem(allowOptionBoxes=True, label='IK', subMenu=True, tearOff=True)
		mc.menuItem(label='Create IK Handle', command='glTools.ui.ik.ikHandleUI()')
		mc.menuItem(label='Stretchy IK Chain', command='glTools.ui.ik.stretchyIkChainUI()')
		mc.menuItem(label='Stretchy IK Limb', command='glTools.ui.ik.stretchyIkLimbUI()')
		mc.menuItem(label='Stretchy IK Spline', command='glTools.ui.ik.stretchyIkSplineUI()')
		
		mc.setParent('..', menu=True)
		
		# > CURVE
		mc.menuItem(allowOptionBoxes=True, label='Curve', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Mirror Curve', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.mirrorCurveFromSel()')
		mc.menuItem(label='Locator Curve', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.locatorCurveUI()')
		mc.menuItem(label='Attach To Curve', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.attachToCurveUI()')
		mc.menuItem(label='Curve To Locators', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.curveToLocatorsUI()')
		mc.menuItem(label='Create Along Curve', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.createAlongCurveUI()')
		mc.menuItem(label='Curve From Edge Loop', command='import glTools.ui.curve;reload(glTools.ui.curve);glTools.ui.curve.edgeLoopCurveUI()')
		mc.menuItem(label='Build Curve Command', command='import glTools.utils.curve;reload(glTools.utils.curve);print glTools.utils.curve.buildCmd(mc.ls(sl=1)[0],True)')
		mc.menuItem(label='Uniform Rebuild', command='import glTools.utils.curve;reload(glTools.utils.curve);glTools.ui.curve.uniformRebuildCurveUI()')
		
		#mc.menuItem(allowOptionBoxes=True, label='LidRails', subMenu=True, tearOff=True)
		#
		#mc.menuItem(label='Create LidSurface', command='glTools.ui.lidRails.lidSurfaceCreateUI()')
		#mc.menuItem(label='3 Control Setup', command='glTools.ui.lidRails.threeCtrlSetupUI()')
		#mc.menuItem(label='4 Control Setup', command='glTools.ui.lidRails.fourCtrlSetupUI()')
		#
		#mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		# > SURFACE
		mc.menuItem(allowOptionBoxes=True, label='Surface', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Locator Surface', command='glTools.ui.surface.locatorSurfaceUI()')
		mc.menuItem(label='Snap To Surface', command='glTools.ui.surface.snapToSurfaceUI()')
		mc.menuItem(label='Attach To Surface', command='glTools.ui.surface.attachToSurfaceUI()')
		mc.menuItem(label='Surface Points', command='glTools.ui.surface.surfacePointsUI()')
		
		mc.setParent('..', menu=True)
		
		# > MESH
		mc.menuItem(allowOptionBoxes=True, label='Mesh', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Snap To Mesh', command='glTools.ui.mesh.snapToMeshUI()')
		mc.menuItem(label='Interactive Snap Tool', command='glTools.ui.mesh.interactiveSnapToMeshUI()')
		mc.menuItem(label='Attach To Mesh', command='glTools.ui.mesh.attachToMeshUI()')
		mc.menuItem(label='Mirror (select middle edge)', command='import glTools.utils.edgeFlowMirror;reload(glTools.utils.edgeFlowMirror);glTools.utils.edgeFlowMirror.mirrorGeo(mc.ls(sl=True,fl=True)[0])')
		mc.menuItem(label='Reconstruct Mesh', command='import glTools.tools.mesh;reload(glTools.tools.mesh);sel = mc.ls(sl=1);[glTools.tools.mesh.reconstructMesh(i,False) for i in sel]')
		mc.menuItem(label='Reconstruct and Replace', command='import glTools.tools.mesh;reload(glTools.tools.mesh);sel = mc.ls(sl=1);[glTools.tools.mesh.reconstructMesh(i,True) for i in sel]')
		
		mc.setParent('..', menu=True)
		
		# > SKINCLUSTER
		mc.menuItem(allowOptionBoxes=True, label='SkinCluster', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Reset', command='glTools.ui.skinCluster.resetFromUI()')
		mc.menuItem(label='Clean', command='glTools.ui.skinCluster.cleanFromUI()')
		mc.menuItem(label='Rename', command='for i in mc.ls(sl=1): glTools.utils.skinCluster.rename(i)')
		mc.menuItem(label='Skin As', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);sel = mc.ls(sl=1);glTools.utils.skinCluster.skinAs(sel[0],sel[1])')
		mc.menuItem(label='Skin Objects', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.utils.skinCluster.skinObjectListFromUI()')
		mc.menuItem(label='Copy To Many', command='import glTools.tools.skinCluster;reload(glTools.tools.skinCluster);sel = mc.ls(sl=1);glTools.tools.skinCluster.copyToMany(sel[0],sel[1:])')
		mc.menuItem(label='Clear Weights', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.utils.skinCluster.clearWeights(mc.ls(sl=True)[0])')
		mc.menuItem(label='Delete BindPose Nodes', command='mc.delete(mc.ls(type="dagPose"))')
		mc.menuItem(label='Lores Weights', command='import glTools.tools.proxyMesh;reload(glTools.tools.proxyMesh);glTools.tools.proxyMesh.proxySkinWeights(mc.ls(sl=1)[0])')
		mc.menuItem(label='Make Relative', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);glTools.ui.skinCluster.makeRelativeUI()')
		mc.menuItem(label='Lock SkinCluster Weights', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);[glTools.utils.skinCluster.lockSkinClusterWeightsFromGeo(geo,True,True) for geo in mc.ls(sl=1)]')
		mc.menuItem(label='Unlock SkinCluster Weights', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);[glTools.utils.skinCluster.lockSkinClusterWeightsFromGeo(geo,False,False) for geo in mc.ls(sl=1)]')
		mc.menuItem(label='Remove Multiple Base Infs', command='import glTools.utils.skinCluster;reload(glTools.utils.skinCluster);sel = mc.ls(sl=1);glTools.utils.skinCluster.removeMultipleInfluenceBases(sel[0],sel[1:])')
		mc.menuItem(label='SkinCluster Data UI', command='import glTools.ui.skinClusterData;reload(glTools.ui.skinClusterData);glTools.ui.skinClusterData.skinClusterDataUI()')
		mc.menuItem(label='Weights Manager', command='import glTools.ui.qt.weightsManager;reload(glTools.ui.qt.weightsManager);glTools.ui.qt.weightsManager.WeightsManager().show()')
		
		mc.setParent('..', menu=True)
		
		# > BLENDSHAPE
		mc.menuItem(allowOptionBoxes=True, label='BlendShape', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Create BlendShape',command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);glTools.tools.blendShape.createFromSelection()',ann='Create basic blendShape from selection')
		mc.menuItem(label='BlendShape Manager',command='import glTools.ui.blendShape;reload(glTools.ui.blendShape);glTools.ui.blendShape.blendShapeManagerUI()',ann='Open BlendShape Manager UI')
		mc.menuItem(label='Update Targets',command='import glTools.ui.blendShape;reload(glTools.ui.blendShape);glTools.ui.blendShape.updateTargetsUI()',ann='Open Update BlendShape Targets UI')
		mc.menuItem(divider=True)
		mc.menuItem(label='Override BlendShape',command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);[glTools.tools.blendShape.endOfChainBlendShape(i) for i in mc.ls(sl=1)]',ann='Create override (end of chain) blendShape deformers on the selected geometry')
		mc.menuItem(label='Add Override Target',command='import glTools.tools.blendShape;reload(glTools.tools.blendShape);glTools.tools.blendShape.addOverrideTarget(mc.ls(sl=1)[1],mc.ls(sl=1)[0])',ann='Add override blendShape target based on the selected geometry')
		
		mc.setParent('..', menu=True)
		
		# > NDYNAMICS
		mc.menuItem(allowOptionBoxes=True, label='nDynamics', subMenu=True, tearOff=True)
		
		mc.menuItem(label='UI', command='glTools.ui.nDynamics.create()')
		mc.menuItem(divider=True)
		mc.menuItem(label='Create nucleus', command='glTools.utils.nDynamics.createNucleus()')
		mc.menuItem(label='Create nCloth', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.createNCloth(i)')
		mc.menuItem(label='Create nRigid', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.createNRigid(i)')
		mc.menuItem(divider=True)
		mc.menuItem(label='Delete nCloth', command='for i in mc.ls(sl=1): glTools.utils.nDynamics.deleteNCloth(i)')
		
		mc.setParent('..', menu=True)
		
		# > SPACES
		#mc.menuItem(allowOptionBoxes=True, label='Spaces', subMenu=True, tearOff=True)
		#mc.menuItem(label='Create/Add', command='glTools.ui.spaces.createAddUI()')
		#mc.menuItem(label='Spaces UI', command='glTools.tools.spaces.Spaces().ui()')
		#mc.menuItem(ob=True, command='glTools.ui.spaces.charUI()')
		#mc.setParent('..', menu=True)
		
		# > POSE MATCH
		mc.menuItem(allowOptionBoxes=True, label='Pose Match Setup', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Evaluation Order', command='glTools.ui.poseMatch.evaluationOrderUI()')
		mc.menuItem(label='Match Rules', command='glTools.ui.poseMatch.matchRulesUI()')
		
		mc.setParent('..', menu=True)
		
		# > KUBO
		mc.menuItem(allowOptionBoxes=True, label='KUBO', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Load Model', command='import glTools.nrig.rig.rig;reload(glTools.nrig.rig.rig);glTools.nrig.rig.rig.Rig().loadModel()')
		
		mc.menuItem(divider =True)
		
		mc.menuItem(allowOptionBoxes=True, label='Smoke Demon', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Clean Curve', command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.cleanCurve()')
		mc.menuItem(label='Build CV Rig', command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.CVrig()')
		mc.menuItem(label='Attach Path Rig', command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.attachPathRig()')
		
		mc.menuItem(divider =True)
		
		mc.menuItem(label='Add Path Bulge',en=0,command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.addPathBulge()')
		mc.menuItem(label='Add Tube Bulge',en=0,command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.addTubeBulge()')
		
		mc.menuItem(divider =True)
		
		mc.menuItem(label='Export Cache', command='import glTools.show.kbo.char.smoke_demon;reload(glTools.show.kbo.char.smoke_demon);glTools.show.kbo.char.smoke_demon.exportUI()')
		
		mc.setParent('..', menu=True)
		mc.setParent('..', menu=True)
		
		# > HBM
		mc.menuItem(allowOptionBoxes=True, label='HBM', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Load Model', command='import glTools.nrig.rig;reload(glTools.rig.rig);glTools.nrig.rig.Rig().loadModel()')
		mc.menuItem(label='Load Groom', command='import glTools.nrig.groomRig;reload(glTools.rig.groomRig);glTools.nrig.groomRig.GroomRig().loadGroom()')
		
		mc.menuItem(divider =True)
		
		
		# > > BoxTroll
		
		mc.menuItem(allowOptionBoxes=True, label= 'BoxTroll', subMenu=True, tearOff=True)
		
		mc.menuItem(label='Import Template', command='mc.file("/laika/jobs/hbm/vfx/asset/char/template/rig/scene_graph/pub/boxtroll_template.latest/template.rig.boxtroll_template.base.mb",i=True,type="mayaBinary")')
		mc.menuItem(label='Mirror Template (Left To Right)', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().mirrorTemplate(leftToRight=True)')
		mc.menuItem(label='Mirror Template (Right To Left)', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().mirrorTemplate(leftToRight=False)')
		mc.menuItem(label='Build Full Rig', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().build(assetName="")')
		
		#----------------------------------------#
		mc.menuItem(divider =True)
		#----------------------------------------#
		
		mc.menuItem(label='Build Base Rig', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().build_base(assetName="")')
		mc.menuItem(label='Build Body Rig (Box)', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().build_body()')
		mc.menuItem(label='Build Arms Rig', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);rig = glTools.show.hbm.char.boxtrollRig.BoxtrollRig();rig.build_arms();rig.limbStretch_arms();rig.limbTwist_arms()')
		mc.menuItem(label='Build Legs Rig', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);rig = glTools.show.hbm.char.boxtrollRig.BoxtrollRig();rig.build_legs();rig.limbStretch_legs();rig.limbTwist_legs()')
		mc.menuItem(label='Build Head Rig', command='import glTools.show.hbm.char.boxtrollRig;reload(glTools.show.hbm.char.boxtrollRig);glTools.show.hbm.char.boxtrollRig.BoxtrollRig().build_head()')
		
		#----------------------------------------#
		mc.menuItem(divider =True)
		#----------------------------------------#
		
		mc.menuItem(label='Build Rig from Parts', command='print("NOT IMPLEMENTED!")')
		
		mc.setParent('..', menu=True)
		
		# > > HUMAN RIG SUB-MENUS
		
		#mc.menuItem(allowOptionBoxes=True, label='Human', subMenu=True, tearOff=True)
		#
		#mc.menuItem(label='Build Body Rig', command='import glTools.show.hbm.char.human;reload(glTools.show.hbm.char.human);glTools.show.hbm.char.human.run("bodyRig_build")')
		#mc.menuItem(label='Build Face Rig',en=0) # , command='import glTools.show.hbm.char.human;reload(glTools.show.hbm.char.human);glTools.show.hbm.char.human.run("faceRig_build")')
		#mc.menuItem(label='Build Mocap Rig', command='import glTools.show.hbm.char.human;reload(glTools.show.hbm.char.human);glTools.show.hbm.char.human.run("mocapRig_build")')
		#mc.menuItem(label='Build Groom Rig', command='import glTools.show.hbm.char.human;reload(glTools.show.hbm.char.human);glTools.show.hbm.char.human.run("groomRig_build")')
		#mc.menuItem(label='Build Hair Rig',en=0) # command='import glTools.show.hbm.char.human;reload(glTools.show.hbm.char.human);glTools.show.hbm.char.human.run("hairRig_build")')
		#mc.menuItem(divider =True)
		#mc.menuItem(label='Attach Face Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().faceRig_attach()')
		#mc.menuItem(label='Attach Groom Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().groomRig_attach()')
		#mc.menuItem(label='Attach Costume Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().costumeRig_attach()')
		#mc.menuItem(label='Attach Hair Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().hairRig_attach()')
		#mc.menuItem(divider =True)
		#mc.menuItem(label='Remove Face Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().faceRig_remove()')
		#mc.menuItem(label='Remove Groom Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().groomRig_remove()')
		#mc.menuItem(label='Remove Costume Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().costumeRig_remove()')
		#mc.menuItem(label='Remove Hair Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().hairRig_remove()')
		#
		#mc.setParent('..', menu=True)
		
		# > > CHARACTER SPECIFIC SUB-MENUS
		
		charList = []
		charList.append(('gen_male_a','GenMaleA'))
		charList.append(('gen_male_b','GenMaleB'))
		charList.append(('gen_male_c','GenMaleC'))
		charList.append(('gen_male_d','GenMaleD'))
		charList.append(('gen_female_a','GenFemaleA'))
		charList.append(('gen_female_b','GenFemaleB'))
		charList.append(('gen_boy_a','GenBoyA'))
		charList.append(('gen_girl_b','GenGirlB'))
		
		for char in charList:
			
			mc.menuItem(allowOptionBoxes=True, label= char[1], subMenu=True, tearOff=True)
		
			mc.menuItem(label='Build Body Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().bodyRig_build()')
			mc.menuItem(label='Build Face Rig',en=0) # , command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().bodyRig_build()')
			mc.menuItem(label='Build Mocap Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().mocapRig_build()')
			mc.menuItem(label='Build Groom Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().groomRig_build()')
			mc.menuItem(label='Build Hair Rig',en=0) # command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().hairRig_build()')
			mc.menuItem(divider =True)
			mc.menuItem(label='Attach Face Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().faceRig_attach()')
			mc.menuItem(label='Attach Groom Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().groomRig_attach()')
			mc.menuItem(label='Attach Costume Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().costumeRig_attach()')
			mc.menuItem(label='Attach Hair Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().hairRig_attach()')
			mc.menuItem(divider =True)
			mc.menuItem(label='Remove Face Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().faceRig_remove()')
			mc.menuItem(label='Remove Groom Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().groomRig_remove()')
			mc.menuItem(label='Remove Costume Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().costumeRig_remove()')
			mc.menuItem(label='Remove Hair Rig', command='import glTools.show.hbm.char.'+char[0]+'_rig;reload(glTools.show.hbm.char.'+char[0]+'_rig);glTools.show.hbm.char.'+char[0]+'_rig.'+char[1]+'().hairRig_remove()')
			
			mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		mc.setParent('..', menu=True)
		
		#----------------------------------------#
		mc.menuItem(divider =True)
		#----------------------------------------#
		
		mc.menuItem(label='Refresh Menu', command='import glTools.ui.menu;reload(glTools.ui.menu);glTools.ui.menu.create()')
		
		mc.setParent('..')
