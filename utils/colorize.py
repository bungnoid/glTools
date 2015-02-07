import maya.cmds as mc

def colorize(obj,color=None):
	'''
	Set override color for a specified object
	@param obj: The dag node to set the color for
	@type obj: str
	@param color: Dsiplay override colour. If None, colour is selected based on name prefix.
	@type color: str or int
	'''
	# Check object
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!!')
	
	# Create color lookup dictionary
	colorDict = {	'grey':0,
					'black':1,
					'dark grey':2,
					'light grey':3,
					'maroon':4,
					'dark blue':5,
					'blue':6,
					'dark green':7,
					'dark purple':8,
					'purple':9,
					'brown':10,
					'dark brown':11,
					'dull red':12,
					'red':13,
					'green':14,
					'dull blue':15,
					'white':16,
					'yellow':17,
					'light blue':18,
					'aqua':19,
					'pink':20,
					'pale orange':21,
					'pale yellow':22,
					'pale green':23,
					'pale brown':24,
					'dull yellow':25,
					'dull green':26,
					'dull aqua':27	}
	
	# Enable Overrides
	mc.setAttr(obj+'.overrideEnabled',1)
	
	# Set Color
	if type(color) == str:
		if colorDict.has_key(color): mc.setAttr(obj+'.overrideColor',colorDict[color])
		else: raise Exception('Color "'+color+'" is not recognised!!')
	elif type(color) == int:
		mc.setAttr(obj+'.overrideColor',color)
	else:
		raise Exception('No valid color value supplied!!')

def setColour(obj):
	'''
	Set object colour by name prefix
	@param obj: The dag node to set the color for
	@type obj: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	# ====================
	# - Colorize By Name -
	# ====================
	
	if obj.startswith('cn_') or obj.startswith('C_'):
		
		# Center
		if mc.objectType(obj) == 'joint':
			colorize(obj,'dull yellow')
		else:
			colorize(obj,'yellow')
		
	elif obj.startswith('lf_') or obj.startswith('L_'):
		
		# LEFT
		if mc.objectType(obj) == 'joint':
			colorize(obj,'pale green')
		else:
			colorize(obj,'green')
	
	elif obj.startswith('rt_') or obj.startswith('R_'):
		
		# LEFT
		if mc.objectType(obj) == 'joint':
			colorize(obj,'maroon')
		else:
			colorize(obj,'red')

def colourHierarchy(root):
	'''
	Set colour by name prefix for a hierarchy of DAG nodes.
	@param root: The root node of the hierarchy to colour.
	@type root: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(root):
		raise Exception('Object "'+root+'" does not exist!')
	
	if not mc.ls(root,dag=True):
		raise Exception('Object "'+root+'" is not a valid DAG node!')
	
	# ====================
	# - Colorize By Name -
	# ====================
	
	hier = mc.ls(mc.listRelatives(root,ad=True),dag=True)
	if not hier: hier = []
	hier.append(root)
	for node in hier: setColour(node)

def colorizeUI(	colorIndex,
				applyTo,
				setState,
				visibility,
				template,
				layerOverride ):
	'''
	'''
	
	# =================
	# - Create Window -
	# =================
	
	window = 'colorizeUI'
	if mc.window(window,q=True,ex=1): mc.deleteUI(window)
	window = mc.window(window,t='Colorize',s=True)
	
	mc.columnLayout()
	mc.columnLayout(cw=550,adjustableColumn=True)
	mc.text(fn='boldLabelFont',align='center',label='Select all objects that you wish to adjust the override color of and then click OK or Apply.')
	mc.setParent('..')
	
	mc.separator(w=550,h=25)
	
	mc.columnLayout(cw=550,adjustableColumn=True)
	mc.colorIndexSliderGrp('buildEdgeCurves_colorCISG',label="Select Color",min=1,max=32,value=colorIndex)						
	mc.setParent('..')
	
	mc.separator(w=550,h=25)
		
	mc.columnLayout(cw=550,adjustableColumn=True)
	mc.radioButtonGrp(	'colorize_applyToRBG',
						numberOfRadioButtons	= 3,
						label					= 'Apply To:',
						labelArray3				= ['Shape(s)','Transform','Both'],
						sl						= applyTo,
						ann						= 'Select whether to apply your colorize choices to the selected shape node(s), the transformation node, or both.')
	mc.setParent('..')
	
	mc.separator(w=550,h=25)	
	
	"""
	rowColumnLayout -nc 2 -cw 1 362 -cw 2 188 ;
	checkBoxGrp -ncb 2 
	-label "Advanced Overrides:"
	-labelArray2 "Visible" "Template"
	-v1 $visibility
	-v2 $template
	-ann "This will toggle the template or visibility state of the Shape(s) or Transformation nodes."
	advancedOptField;
	checkBox -label "Override Display Layers" 
	-v $layerOverride 
	-cc "colorizeWinUpdate"
	layerOverrideField;
	setParent..;
	
	text -vis `checkBox -q -v layerOverrideField` 
	-label "WARNING: If your objects are in display layers, they will be removed by selecting this checkbox!" -align "center";                           
	
	
	separator -w 550 -h 25;	
	
	rowColumnLayout -nc 1 -cw 1 550 ;
	radioButtonGrp -numberOfRadioButtons 2
	-label "Set Override State:" 
	-labelArray2 "Enable Override" "Disable Override"  
	-sl $setState 
	-ann "This will enable or disable the overrides that you are changing in this window."
	setStateField;
	setParent..;
	
	separator -w 550 -h 25;												
	
	rowColumnLayout -nc 6 -cw 1 80 -cw 2 140 -cw 3 8 -cw 4 140 -cw 5 8 -cw 6 140;
	text -label "";						
	button -align "center" -label "OK" -c ("colorizeProc; deleteUI colorizeWin");
	text -label "";	
	button -align "center" -label "Apply" -c ("colorizeProc");	
	text -label "";					
	button -align "center" -label "Close" -c ("deleteUI colorizeWin");
	"""
	
	mc.setParent('..')
	
	# ===============
	# - Show Window -
	# ===============
	
	mc.showWindow(window)	

