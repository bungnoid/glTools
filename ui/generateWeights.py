import maya.cmds as mc

import glTools.utils.deformer

import glTools.tools.generateWeights

def generateWeightsUI():
	'''
	'''
	win = 'generateWeightsUI'
	if mc.window(win,ex=True): mc.deleteUI(win)
	win = mc.window(win,t='Generate Weights',wh=[560,285],s=True)
	
	# FormLayout
	fl = mc.formLayout(numberOfDivisions=100)
	
	# UI Elements 
	genWt_targetAttrTFG = mc.textFieldGrp('genWt_targetAttrTFG',label='Target Attribute')
	
	genWt_targetGeoTFG = mc.textFieldButtonGrp('genWt_targetGeoTFG',l='Target Geometry',bl='Select')
	mc.textFieldButtonGrp(genWt_targetGeoTFG,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_targetGeoTFG+'")')
	
	genWt_smoothISG = mc.intSliderGrp('genWt_smoothWeightTFG',label='Smooth',f=True,minValue=0,maxValue=5,fieldMinValue=0,fieldMaxValue=100,value=0)
	
	genWt_generateB = mc.button(label='Generate Weights', c='glTools.ui.generateWeights.generateWeightsFromUI()' )
	genWt_cancelB = mc.button(label='Cancel', c='mc.deleteUI("'+win+'")' )
	
	# TabLayout
	genWt_tabLayout = mc.tabLayout('genWt_tabLayout', innerMarginWidth=5, innerMarginHeight=5 )
	
	# Layout
	mc.formLayout(fl,e=True,af=[(genWt_targetAttrTFG,'left',5),(genWt_targetAttrTFG,'top',5),(genWt_targetAttrTFG,'right',5)])
	mc.formLayout(fl,e=True,af=[(genWt_targetGeoTFG,'left',5),(genWt_targetGeoTFG,'right',5)],ac=[(genWt_targetGeoTFG,'top',5,genWt_targetAttrTFG)])
	mc.formLayout(fl,e=True,af=[(genWt_smoothISG,'left',5),(genWt_smoothISG,'right',5)],ac=[(genWt_smoothISG,'top',5,genWt_targetGeoTFG)])
	mc.formLayout(fl,e=True,af=[(genWt_tabLayout,'left',5),(genWt_tabLayout,'right',5)],ac=[(genWt_tabLayout,'top',5,genWt_smoothISG),(genWt_tabLayout,'bottom',5,genWt_generateB)])
	mc.formLayout(fl,e=True,af=[(genWt_generateB,'left',5),(genWt_generateB,'bottom',5)],ap=[(genWt_generateB,'right',5,50)])
	mc.formLayout(fl,e=True,af=[(genWt_cancelB,'right',5),(genWt_cancelB,'bottom',5)],ap=[(genWt_cancelB,'left',5,50)])
	
	# ---------------------------
	# - Gradient Weights Layout -
	# ---------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	gradWt_columnLayout = mc.columnLayout(dtg='gradient')
	
	# UI Elements
	gradWt_pt1TFB = mc.textFieldButtonGrp('genWt_gradWtPt1_TFB',l='Point 1', text='', bl='Select')
	mc.textFieldButtonGrp(gradWt_pt1TFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+gradWt_pt1TFB+'")')
	
	gradWt_pt2TFB = mc.textFieldButtonGrp('genWt_gradWtPt2_TFB',l='Point 2', text='', bl='Select')
	mc.textFieldButtonGrp(gradWt_pt2TFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+gradWt_pt2TFB+'")')
	
	mc.setParent('..')
	
	# -------------------------
	# - Radial Weights Layout -
	# -------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	radWt_columnLayout = mc.columnLayout(dtg='radial')
	
	# UI Elements
	mc.floatSliderGrp('genWt_radWtRadiusFSG',label='Radius',f=True,minValue=0.001,maxValue=10.0,fieldMinValue=0.001,fieldMaxValue=1000000,value=1.0)
	mc.floatSliderGrp('genWt_radWtInRadiusFSG',label='Inner Radius',f=True,minValue=0.0,maxValue=10.0,fieldMinValue=0.0,fieldMaxValue=1000000,value=0.0)
	
	mc.separator(style='single',w=1000,h=20)
	
	radWt_centFFG = mc.floatFieldGrp('genWt_radWtCent_TFB', numberOfFields=3, label='Center', value1=0.0, value2=0.0, value3=0.0 )
	radWt_centB = mc.button( label='Get Point', c='glTools.ui.utils.setPointValue("'+radWt_centFFG+'")' )
	
	mc.setParent('..')
	
	# -------------------------
	# - Volume Weights Layout -
	# -------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	volWt_columnLayout = mc.columnLayout(dtg='volume')
	
	# UI Elements
	genWt_volBoundaryTFB = mc.textFieldButtonGrp('genWt_volBoundaryTFB',l='Volume Boundary',bl='Select')
	mc.textFieldButtonGrp(genWt_volBoundaryTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_volBoundaryTFB+'")')
	
	genWt_volInteriorTFB = mc.textFieldButtonGrp('genWt_volInteriorTFB',l='Volume Interior',bl='Select')
	mc.textFieldButtonGrp(genWt_volInteriorTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_volInteriorTFB+'")')
	
	mc.separator(style='single',w=1000,h=20)
	
	volWt_centFFG = mc.floatFieldGrp('genWt_volWtCent_TFB', numberOfFields=3, label='Volume Center', value1=0.0, value2=0.0, value3=0.0 )
	volWt_centB = mc.button( label='Get Point', c='glTools.ui.utils.setPointValue("'+volWt_centFFG+'")' )
	
	mc.setParent('..')
	
	# ----------------------------------
	# - Geometry Volume Weights Layout -
	# ----------------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	geoVolWt_columnLayout = mc.columnLayout(dtg='geometryVolume')
	
	# UI Elements
	genWt_geoBoundaryTFB = mc.textFieldButtonGrp('genWt_geoBoundaryTFB',l='Volume Boundary',bl='Select')
	mc.textFieldButtonGrp(genWt_geoBoundaryTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_geoBoundaryTFB+'")')
	
	genWt_geoInteriorTFB = mc.textFieldButtonGrp('genWt_geoInteriorTFB',l='Volume Interior',bl='Select')
	mc.textFieldButtonGrp(genWt_geoInteriorTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_geoInteriorTFB+'")')
	
	mc.separator(style='single',w=1000,h=20)
	
	geoVolWt_centFFG = mc.floatFieldGrp('genWt_geoVolWtCent_TFB', numberOfFields=3, label='Volume Center', value1=0.0, value2=0.0, value3=0.0 )
	geoVolWt_centB = mc.button( label='Get Point', c='glTools.ui.utils.setPointValue("'+volWt_centFFG+'")' )
	
	mc.setParent('..')
	
	# ----------------------------------
	# - Curve Proximity Weights Layout -
	# ----------------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	curveWt_columnLayout = mc.columnLayout(dtg='curveProximity')
	
	# UI Elements
	genWt_curveWtCurveTFB = mc.textFieldButtonGrp('genWt_curveWtCurveTFB',l='Curve',bl='Select')
	mc.textFieldButtonGrp(genWt_curveWtCurveTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_curveWtCurveTFB+'")')
	
	mc.floatSliderGrp('genWt_curveWtMinDistFSG',label='Min Distance',f=True,minValue=0.0,maxValue=10.0,fieldMinValue=0.0,fieldMaxValue=1000000,value=0.0)
	mc.floatSliderGrp('genWt_curveWtMaxDistFSG',label='Max Distance',f=True,minValue=0.001,maxValue=10.0,fieldMinValue=0.001,fieldMaxValue=1000000,value=1.0)
	
	mc.setParent('..')
	
	# ------------------------------
	# - Mesh Offset Weights Layout -
	# ------------------------------
	
	mc.setParent(genWt_tabLayout)
	
	# Layout
	meshOffsetWt_columnLayout = mc.columnLayout(dtg='meshOffset')
	
	# UI Elements
	genWt_meshOffsetBaseTFB = mc.textFieldButtonGrp('genWt_meshOffsetBaseTFB',l='Base Mesh',bl='Select')
	mc.textFieldButtonGrp(genWt_meshOffsetBaseTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_meshOffsetBaseTFB+'")')
	
	genWt_meshOffsetTargetTFB = mc.textFieldButtonGrp('genWt_meshOffsetTargetTFB',l='Target Mesh',bl='Select')
	mc.textFieldButtonGrp(genWt_meshOffsetTargetTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+genWt_meshOffsetTargetTFB+'")')
	
	genWt_meshOffsetNormalizeCBG = mc.checkBoxGrp('genWt_meshOffsetNormalizeCBG',numberOfCheckBoxes=1,label='Normalize')
	genWt_meshOffsetNormalRayCBG = mc.checkBoxGrp('genWt_meshOffsetNormalRayCBG',numberOfCheckBoxes=1,label='Normal Ray Intersect')
	
	mc.setParent('..')
	
	# --------------
	# - End Layout -
	# --------------
	
	# Set TabLayout Labels
	mc.tabLayout(genWt_tabLayout,e=True,tabLabel=((gradWt_columnLayout,'Gradient'),(radWt_columnLayout,'Radial'),(volWt_columnLayout,'Volume'),(geoVolWt_columnLayout,'Geometry Volume'),(curveWt_columnLayout,'Curve Proximity'),(meshOffsetWt_columnLayout,'Mesh Offset')) )
	
	# Display UI 
	mc.showWindow(win)
	mc.window(win,e=True,wh=[560,285])

	
def generateWeightsFromUI():
	'''
	'''
	# Get source geometry
	geometry = mc.textFieldGrp('genWt_targetGeoTFG',q=True,tx=True)
	
	# Get smooth value
	smoothVal = mc.intSliderGrp('genWt_smoothWeightTFG',q=True,v=True)
	
	# ------------------------
	# - Get Target Attribute -
	# ------------------------
	
	targetAttr = mc.textFieldGrp('genWt_targetAttrTFG',q=True,tx=True)
	
	# Check target attr
	if not targetAttr: raise Exception('No target attribute specified!')
	if not mc.objExists(targetAttr): raise Exception('Attribute "'+targetAttr+'" does not exist!')
	
	# Determine target attribute type
	targetNode = targetAttr.split('.')[0]
	targetType = mc.objectType(targetNode)
	#attrIsMulti = mc.attributeQuery('') 
	
	# --------------------
	# - Generate Weights -
	# --------------------
	
	wt = []
	
	# Determine weight generation type
	selLayout = mc.tabLayout('genWt_tabLayout',q=True,st=True)
	layoutTag = mc.columnLayout(selLayout,q=True,dtg=True)
	
	if layoutTag == 'gradient':
		
		# Gradient
		pnt1 = mc.textFieldButtonGrp('genWt_gradWtPt1_TFB',q=True,tx=True)
		pnt2 = mc.textFieldButtonGrp('genWt_gradWtPt2_TFB',q=True,tx=True)
		wt = glTools.tools.generateWeights.gradientWeights(geometry,pnt1,pnt2,smoothVal)
		
	elif layoutTag == 'radial':
		
		# Radial
		radius = mc.floatSliderGrp('genWt_radWtRadiusFSG',q=True,v=True)
		inRadius = mc.floatSliderGrp('genWt_radWtInRadiusFSG',q=True,v=True)
		center = (	mc.floatFieldGrp('genWt_radWtCent_TFB',q=True,v1=True),
					mc.floatFieldGrp('genWt_radWtCent_TFB',q=True,v2=True),
					mc.floatFieldGrp('genWt_radWtCent_TFB',q=True,v3=True)	)
		wt = glTools.tools.generateWeights.radialWeights(geometry,center,radius,inRadius,smoothVal)
		
	elif layoutTag == 'volume':
		
		# Volume
		volBoundary = mc.textFieldButtonGrp('genWt_volBoundaryTFB',q=True,tx=True)
		volInterior = mc.textFieldButtonGrp('genWt_volInteriorTFB',q=True,tx=True)
		volCenter = (	mc.floatFieldGrp('genWt_volWtCent_TFB',q=True,v1=True),
						mc.floatFieldGrp('genWt_volWtCent_TFB',q=True,v2=True),
						mc.floatFieldGrp('genWt_volWtCent_TFB',q=True,v3=True)	)
		wt = glTools.tools.generateWeights.volumeWeights(geometry,volCenter,volBoundary,volInterior,smoothVal)
		
	elif layoutTag == 'geometryVolume':
		
		# Geometry Volume
		geoBoundary = mc.textFieldButtonGrp('genWt_geoBoundaryTFB',q=True,tx=True)
		geoInterior = mc.textFieldButtonGrp('genWt_geoInteriorTFB',q=True,tx=True)
		geoCenter = (	mc.floatFieldGrp('genWt_geoVolWtCent_TFB',q=True,v1=True),
						mc.floatFieldGrp('genWt_geoVolWtCent_TFB',q=True,v2=True),
						mc.floatFieldGrp('genWt_geoVolWtCent_TFB',q=True,v3=True)	)
		wt = glTools.tools.generateWeights.geometryVolumeWeights(geometry,geoCenter,geoBoundary,geoInterior,smoothVal)
		
	elif layoutTag == 'curveProximity':
		
		# Curve Proximity
		proximityCurve = mc.textFieldButtonGrp('genWt_curveWtCurveTFB',q=Tru,tx=True)
		minDist = mc.floatSliderGrp('genWt_curveWtMinDistFSG',q=True,v=True)
		maxDist = mc.floatSliderGrp('genWt_curveWtMaxDistFSG',q=True,v=True)
		wt = glTools.tools.generateWeights.curveProximityWeights(geometry,proximityCurve,minDist,maxDist,smoothVal)
	
	elif layoutTag == 'meshOffset':
		
		# Mesh Offset
		meshBase = mc.textFieldButtonGrp('genWt_meshOffsetBaseTFB',q=True,tx=True)
		meshTarget = mc.textFieldButtonGrp('genWt_meshOffsetTargetTFB',q=True,tx=True)
		normalize = mc.checkBoxGrp('genWt_meshOffsetNormalizeCBG',q=True,v1=True)
		useNormal = mc.checkBoxGrp('genWt_meshOffsetNormalRayCBG',q=True,v1=True)
		wt = glTools.tools.generateWeights.meshOffsetWeights(meshBase,meshTarget,normalize,useNormal,smoothVal)
		
	# -----------------------
	# - Set Attribute Value -
	# -----------------------
	
	
