import maya.cmds as mc

def jointDrivenRmanAttr(geo,joint,axis='z',min=0,max=180,prefix=''):
	'''
	Create a renderman output variable attribute on a specified geometry and drive with a given joint rotation.
	@param geo: Geometry to add renderman output variable attribute to.
	@type geo: str
	@param joint: Joint that will drive the value of the output variable attribute.
	@type joint: str
	@param axis: The rotation axis of the joint that will drive the output variable value.
	@type axis: str
	@param min: Minimum joint rotation value. This value, and any value below, will correspont to a 0.0 output value.
	@type min: float
	@param min: Maximum joint rotation value. This value, and any value above, will correspont to a 1.0 output value.
	@type min: float
	@param prefix: Node and attribute naming prefix.
	@type prefix: str
	'''
	# Check prefix
	if not prefix: prefix = joint
	
	# Check joint
	if not mc.objExists(joint): raise Exception('Joint "'+joint+'" does not exist!!')
	
	# Check axis
	axis = axis.lower()
	if not ['x','y','z'].count(axis):
		raise Exception('Invalid rotation axis specified! Acceptable values are "x", "y" or "z"!')
	
	# Check mesh
	if not mc.objExists(geo): raise Exception('Object "'+geo+'" does not exist!!')
	
	# Add renderman variable attr
	meshShape = mc.listRelatives(mesh,s=True,ni=True,pa=True)[0]
	mc.addAttr(meshShape,ln='rmanF'+prefix,min=0,max=1,dv=0,k=True)
	
	# Add joint min/max value attrs
	mc.addAttr(joint,ln='outputMin',dv=min,k=True)
	mc.addAttr(joint,ln='outputMax',dv=max,k=True)
	
	# Remap to 0-1 range
	remapNode = mc.createNode('remapValue',n=prefix+'_remapValue')
	mc.connectAttr(joint+'.r'+axis,remapNode+'.inputValue',f=True)
	mc.connectAttr(joint+'.outputMin',remapNode+'.inputMin',f=True)
	mc.connectAttr(joint+'.outputMax',remapNode+'.inputMax',f=True)
	mc.setAttr(remapNode+'.outputMin',0.0)
	mc.setAttr(remapNode+'.outputMax',1.0)
	
	# Connect to shape attr
	mc.connectAttr(remapNode+'.outValue',meshShape+'.rmanF'+prefix,f=True)
	
	# Return result
	return meshShape+'.rmanF'+prefix
