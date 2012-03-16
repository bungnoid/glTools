import maya.cmds as mc

def create(prefix=''):
	'''
	'''
	# Check prefix
	if not prefix: prefix = 'rivet'
	
	# Get selected polygon edges
	edges = mc.filterExpand(sm=32)
	
	# Check edge selection
	if edges:
		
		# Check selection length
		if len(edges) != 2:
			raise Exception('Select 2 poly edges or a nurbs surface point and run again!')
	
		# Determine object and edge indices
		obj = mc.ls(edges[0],o=True)
		edgeIndex1 = int(edges[0].split('.')[-1].strip('e[]'))
		edgeIndex2 = int(edges[1].split('.')[-1].strip('e[]'))
	
		# Create curves from poly edges 
		curveEdge1 = mc.createNode('curveFromMeshEdge',n=prefix+'_edge1_curveFromMeshEdge')
		mc.setAttr(curveEdge1+'.ihi',1)
		mc.setAttr(curveEdge1+'.ei[0]',edgeIndex1)
		curveEdge2 = mc.createNode('curveFromMeshEdge',n=prefix+'_edge2_curveFromMeshEdge')
		mc.setAttr(curveEdge2+'.ihi',1)
		mc.setAttr(curveEdge2+'.ei[0]',edgeIndex2)
		
		# Generate loft from edge curves
		loft = mc.createNode('loft',n=prefix+'_loft')
		mc.setAttr(loft+'.ic',s=2)
		mc.setAttr(loft+'.u',1)
		mc.setAttr(loft+'.rsn',1)
	
		# Create pointOnSurfaceInfo node
		pointInfo = mc.createNode('pointOnSurfaceInfo',n=prefix+'_pointOnSurfaceInfo')
		mc.setAttr(pointInfo+'.turnOnPercentage',1)
		mc.setAttr(pointInfo+'.parameterU',0.5)
		mc.setAttr(pointInfo+'.parameterV',0.5)
		
		# Connect nodes
		mc.connectAttr(loft+'.os',pointInfo+'.is',f=True)
		mc.connectAttr(curveEdge1+'.oc',loft+'.ic[0]',f=True)
		mc.connectAttr(curveEdge2+'.oc',loft+'.ic[1]',f=True)
		mc.connectAttr(obj+'.w',curveEdge1+'.im',f=True)
		mc.connectAttr(obj+'.w',curveEdge2+'.im',f=True)
		
	else:
		
		# Get surface point selection
		points = mc.filterExpand(sm=41)
		
		# Check point selection
		if not points:
			if len(points) > 1:
				raise Exception('Select 2 poly edges or a nurbs surface point and run again!')
			
			# Determine object and UV parameter
			obj = mc.ls(edges[0],o=True)
			uv = points[0].split('.')[-1].strip('uv[]').split(',')
			u = float(uv[0])
			v = float(uv[1])
			
			# Create pointOnSurfaceInfo node
			pointInfo = mc.createNode('pointOnSurfaceInfo',n=prefix+'_pointOnSurfaceInfo')
			mc.setAttr(pointInfo+'.turnOnPercentage',1)
			mc.setAttr(pointInfo+'.parameterU',0.5)
			mc.setAttr(pointInfo+'.parameterV',0.5)
			
			# Connect nodes
			mc.connectAttr(obj+'.ws',pointInfo+'.is',f=True)

	# Create rivet locator
	loc = mc.createNode('transform',n=prefix+'_locator')
	
	# Create aim constraint
	aim = mc.createNode('aimConstraint',p=loc,n=prefix+'_aimConstraint')
	mc.setAttr(aim+'.tg[0].tw',1)
	mc.setAttr(aim+'.a',0,1,0)
	mc.setAttr(aim+'.u',0,0,1)
	for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz','v']: mc.setAttr(aim+'.'+attr,k=0)
	
	mc.connectAttr(pointInfo+'.position',loc+'.translate',f=True)
	mc.connectAttr(pointInfo+'.normal',aim+'.tg[0].tt',f=True)
	mc.connectAttr(pointInfo+'.tv',aim+'.wu',f=True)
	
	mc.connectAttr(aim+'.crx',loc+'.rx',f=True)
	mc.connectAttr(aim+'.cry',loc+'.ry',f=True)
	mc.connectAttr(aim+'.crz',loc+'.rz',f=True)
	
	# Return result
	return loc
