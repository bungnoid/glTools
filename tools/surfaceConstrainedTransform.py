import maya.cmds as mc

def surfaceConstraint(obj,surface,point=True,orient=True,normalAxis='x',upAxis='y',upMode='',upVector=(0,1,0),upObject='',pointMode=0,prefix=''):
	'''
	@param obj: Target object that the surface constrained transform will goal to.
	@type obj: str
	@param surface: Surface to constrain to
	@type surface: str
	@param point: Constrain point (translate)
	@type point: bool
	@param orient: Constrain orient (rotate)
	@type orient: bool
	@param normalAxis: Constrained transform axis to align with surface normal 
	@type normalAxis: str
	@param upAxis: Constrained transform axis to align with defined upVector
	@type upAxis: str
	@param upMode: Constraint upVector mode. Valid values are 'scene', 'object', 'objectrotation', 'vector' or 'none'. 
	@type upMode: str
	@param upVector: Constraint upVector. 
	@type upVector: list or tuple
	@param upObject: Constraint upVector object. Only needed for 'object' or 'objectrotation' upVector modes.
	@type upObject: str
	@param pointMode: Point (translate) constraint mode. 0 = geometryConstraint, 1 = boundaryConstraint.
	@type pointMode: int
	@param prefix: Name prefix for newly created nodes
	@type prefix: str
	'''
	# Build axis dictionary
	axisDict = {'x':(1,0,0),'y':(0,1,0),'z':(0,0,1),'-x':(-1,0,0),'-y':(0,-1,0),'-z':(0,0,-1)}
		
	# ==========
	# - Checks -
	# ==========
	
	if not mc.objExists(obj):
		raise Exception('Object "'+obj+'" does not exist!')
	
	if not mc.objExists(surface):
		raise Exception('Surface "'+surface+'" does not exist!')
	
	if not axisDict.keys().count(normalAxis):
		raise Exception('Invalid normal axis specified "'+normalAxis+'"!')
	
	if not axisDict.keys().count(upAxis):
		raise Exception('Invalid up axis specified "'+upAxis+'"!')
	
	if ((upMode == 'object') or (upMode == 'objectrotation')) and not mc.objExists(upObject):
		raise Exception('Invalid up object specified "'+upObject+'"!')
	
	# ===============================
	# - Create Constraint Transform -
	# ===============================
	
	surfConnNode = mc.createNode('transform',n=prefix+'_surfConn_grp')
	
	# ================================
	# - Constraint point (translate) -
	# ================================
	
	if point:
		
		if pointMode == 0:
			
			# Geometry Constraint
			pntConn = mc.pointConstraint(obj,surfConnNode,n=prefix+'_pointConstraint')
			geoConn = mc.geometryConstraint(surface,surfConnNode,n=prefix+'_geometryConstraint')
			
		else:
			
			# =======================
			# - Boundary Constraint -
			# =======================
			
			# World Position (vectorProduct)
			vecProduct = mc.createNode('vectorProduct',n=prefix+'_worldPos_vectorProduct')
			mc.setAttr(vecProduct+'.operation',4) # Point Matrix Product
			mc.connectAttr(obj+'.worldMatrix',vecProduct+'.matrix',f=True)
			
			# Closest Point On Surface
			cposNode = mc.createNode('closestPointOnSurface',n=prefix+'_surfacePos_closestPointOnSurface')
			mc.connectAttr(surface+'.worldSpace[0]',cposNode+'.inputSurface',f=True)
			mc.connectAttr(vecProduct+'.output',cposNode+'.inPoint',f=True)
			
			# Point On Surface Info
			posiNode = mc.createNode('pointOnSurfaceInfo',n=prefix+'_surfacePt_pointOnSurfaceInfo')
			mc.connectAttr(surface+'.worldSpace[0]',cposNode+'.inputSurface',f=True)
			mc.connectAttr(cposNode+'.parameterU',posiNode+'.parameterU',f=True)
			mc.connectAttr(cposNode+'.parameterV',posiNode+'.parameterV',f=True)
			
			# Calculate Offset
			offsetNode = mc.createNode('plusMinusAverage',n=prefix+'_surfaceOffset_plusMinusAverage')
			mc.setAttr(offsetNode+'.operation',2) # Subtract
			mc.connectAttr(vecProduct+'.output',offsetNode+'.input3D[0]',f=True)
			mc.connectAttr(cposNode+'.position',offsetNode+'.input3D[1]',f=True)
			
			# Offset * Normal (dotProduct)
			dotProduct = mc.createNode('vectorProduct',n=prefix+'_dotProduct_vectorProduct')
			mc.setAttr(dotProduct+'.operation',1) # Dot Product
			mc.connectAttr(offsetNode+'.ouput3D',dotProduct+'.input1',f=True)
			mc.connectAttr(posiNode+'.normal',dotProduct+'.input2',f=True)
			
			# Boundary Condition
			condition = mc.createNode('condition',n=prefix+'_condition')
			mc.setAttr(condition+'.operation',2) # Greater Than
			mc.connectAttr(dotProduct+'.outputX',condition+'.firstTerm',f=True)
			mc.connectAttr(vecProduct+'.output',condition+'.colorIfTrue',f=True)
			mc.connectAttr(cposNode+'.position',condition+'.colorIfFalse',f=True)
			
			# Connect to transform
			mc.connectAttr(condition+'.outColor',surfConnNode+'.t',f=True)
	
	else:
		
		# Point Constraint
		pntConn = mc.pointConstraint(obj,surfConnNode,n=prefix+'_pointConstraint')
	
	# =============================
	# - Constrain Orient (rotate) -
	# =============================
	
	if orient:
		
		# Normal Constraint
		normConn = mc.normalConstraint(surface,surfConnNode,aim=axisDict[normalAxis],u=axisDict[upAxis],wut=upMode,wu=upVector,wuo=upObject,n=prefix+'_normalConstraint')
	
	else:
		
		# Orient Constraint
		oriConn = mc.normalConstraint(obj,surfConnNode,n=prefix+'_orientConstraint')
	
	# =================
	# - Return Result -
	# =================
	
	return surfConnNode

def blendTarget(slaveTransform,driverAttr,attrMin=0.0,attrMax=1.0,translate=True,rotate=False,scale=False,prefix=''):
	'''
	'''
	# Checks
	if not mc.objExists(slaveTransform):
		raise Exception('Slave transform "'+slaveTransform+'" does not exist!')
	if not mc.objExists(driverAttr):
		raise Exception('Driver attribute "'+driverAttr+'" does not exist!')
	
	# Check blendTarget node
	if mc.objExists(slaveTransform):
		pass
	
	# Create target locator
	targetLoc = mc.spaceLocator(n=prefix+'_loc')[0]
	
	# Parent target locator
	slaveParent = mc.listRelatives(slaveTransform,p=True,pa=True)
	if not slaveParent: raise Exception('Slave transform has no transform parent!')
	mc.parent(targetLoc,slaveParent[0])
	
	# Check blendCombine nodes
	slaveTransConn = mc.listConnections(slaveTransform+'.t',s=True,d=False)
	slaveRotateConn = mc.listConnections(slaveTransform+'.r',s=True,d=False)
	slaveScaleConn = mc.listConnections(slaveTransform+'.s',s=True,d=False)
	
	#
	
