import maya.cmds as mc

import glTools.utils.colorize

def buildMasterCurveGroup(grpName):
	'''
	Build master group name
	@param grpName: Existing mocap namespace
	@type grpName: str
	'''
	grp = grpName
	if not mc.objExists(grpName): grp = mc.group(em=True,n=grpName)
	return grp

def buildCurveGroup(name,color=None):
	'''
	Build master group name
	@param name: Curve group name. Final group will be suffiex with "_grp"
	@type name: str
	@param color: Color to apply to the edge curve (group).
	@type color: int or str or None
	'''
	grp = name+'_edgeCurves_grp'
	if not mc.objExists(grp): grp = mc.group(em=True,n=grp)
	if color: glTools.utils.colorize.colorize(grp,color)
	#mc.setAttr(grp+'.overrideEnabled',1)
	#mc.setAttr(grp+'.overrideDisplayType',2) # Reference
	return grp

def buildEdgeCurves(edges,name,color=None):
	'''
	Build poly edge curves.
	Group, name and color resulting curves.
	@param edges: List of poly edges to extract as curves.
	@type edges: str
	@param name: Curve and group name prefix.
	@type name: str
	@param color: Color to apply to the edge curve (group).
	@type color: int or str or None
	'''
	# Get Edges
	edges = mc.filterExpand(ex=True,sm=32) # Poly Edges
	if not edges: raise Exception('Invalid or empty edge list!')
	
	# Get Master Group
	masterGrp = buildMasterCurveGroup('edgeCurveGroup')
	
	# Get Curve Group
	curveGrp = buildCurveGroup(name,color)
	try: mc.parent(curveGrp,masterGrp)
	except: pass
	
	# Build Edge Curves
	crvList = []
	for edge in edges:
		crv = mc.polyToCurve(edge,form=2,degree=1)[0]
		for at in 'trs': mc.setAttr(crv+'.'+at,l=True,cb=False)
		mc.parent(crv,curveGrp)
	
	# Return Result
	return curveGrp

def buildEdgeCurvesUI():
	'''
	Build Edge Curves UI
	'''
	# Window
	window = 'buildEdgeCurvesUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Build PolyEdge Curves',s=True)
	
	# Layout
	CL = mc.columnLayout()
	
	# UI Elements
	mc.textFieldGrp('buildEdgeCurves_nameTFG',label='Curve Group Name',text='',editable=True)
	mc.colorIndexSliderGrp('buildEdgeCurves_colorCISG',label="Curve Color",min=1,max=32,value=16)
	mc.button('buildEdgeCurvesB',l='Create',w=390,c='glTools.tools.polyEdgeCurve.buildEdgeCurvesFromUI()')
	
	# Show Window
	mc.window(window,e=True,wh=[392,64])
	mc.showWindow(window)

def buildEdgeCurvesFromUI():
	'''
	Build Edge Curves From UI
	'''
	# Get Selected Edges
	sel = mc.ls(sl=True,fl=True)
	edges = mc.filterExpand(sel,ex=True,sm=32)
	if not edges:
		print('Invalid Selection! Select polygon edges and run again...')
		return
	
	# Get UI Parameters
	name = mc.textFieldGrp('buildEdgeCurves_nameTFG',q=True,text=True)
	color = mc.colorIndexSliderGrp('buildEdgeCurves_colorCISG',q=True,v=True) - 1
	
	# Build Edge Curves
	crvGrp = buildEdgeCurves(edges,name,color)
	mc.select(crvGrp)
