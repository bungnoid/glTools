import maya.cmds as mc

def measureBoundingBox(geo):
	'''
	Create visual distance dimensions for the specified geometry or geometry group.
	@param geo: Geometry or geometry group to create distance dimensions for.
	@type geo: str
	'''
	# Check Geo
	if not mc.objExists(geo): raise Exception('Geometry "'+geo+'" does not exist!!')
	
	# ==============================
	# - Create Distance Dimensions -
	# ==============================
	
	del_locs = []
	
	# Height
	hDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(hDimensionShape,s=True,d=False) or []
	del_locs += locs
	hDimension = mc.listRelatives(hDimensionShape,p=True)[0]
	hDimension = mc.rename(hDimension,geo+'_height_measure')
	
	# Width
	wDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(wDimensionShape,s=True,d=False) or []
	del_locs += locs
	wDimension = mc.listRelatives(wDimensionShape,p=True)[0]
	wDimension = mc.rename(wDimension,geo+'_width_measure')
	
	# Depth
	dDimensionShape = mc.distanceDimension(sp=(0,0,0),ep=(1,1,1))
	locs = mc.listConnections(dDimensionShape,s=True,d=False) or []
	del_locs += locs
	dDimension = mc.listRelatives(dDimensionShape,p=True)[0]
	dDimension = mc.rename(dDimension,geo+'_depth_measure')
	
	# Group
	measure_grp = mc.group([hDimension,wDimension,dDimension],n=geo+'_measure_grp')
	
	# ===============================
	# - Connect Distance Dimensions -
	# ===============================
	
	# Height
	mc.connectAttr(geo+'.boundingBoxMin',hDimension+'.startPoint',f=True)
	addHeightNode = mc.createNode('plusMinusAverage',n=geo+'_height_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addHeightNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeY',addHeightNode+'.input3D[1].input3Dy',f=True)
	mc.connectAttr(addHeightNode+'.output3D',hDimension+'.endPoint',f=True)
	
	# Width
	mc.connectAttr(geo+'.boundingBoxMin',wDimension+'.startPoint',f=True)
	addWidthNode = mc.createNode('plusMinusAverage',n=geo+'_width_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addWidthNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeX',addWidthNode+'.input3D[1].input3Dx',f=True)
	mc.connectAttr(addWidthNode+'.output3D',wDimension+'.endPoint',f=True)
	
	# Depth
	mc.connectAttr(geo+'.boundingBoxMin',dDimension+'.startPoint',f=True)
	addDepthNode = mc.createNode('plusMinusAverage',n=geo+'_depth_plusMinusAverage')
	mc.connectAttr(geo+'.boundingBoxMin',addDepthNode+'.input3D[0]',f=True)
	mc.connectAttr(geo+'.boundingBoxSizeZ',addDepthNode+'.input3D[1].input3Dz',f=True)
	mc.connectAttr(addDepthNode+'.output3D',dDimension+'.endPoint',f=True)
	
	# Delete Unused Locators
	if del_locs: mc.delete(del_locs)
	
	# Return Result
	return measure_grp
