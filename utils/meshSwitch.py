import maya.cmds as mc

def create(sourceList,targetList):
	'''
	Create meshSwitch nodes for all meshes specified by the targetList argument.
	Each mesh in the sourceList will be connected to each meshSwitch nodes inMesh attributes.
	@param sourceList: The list of source meshes that can be switched between
	@type sourceList: list
	@param targetList: The list of target meshes that will be driven by the meshSwitch nodes
	@type targetList: list
	'''
	# For Each Target
	meshSwitchList = []
	for target in targetList:
		
		# Determine Prefix
		pre = target.replace(target.split('_')[-1],'')
		
		# Create meshSwitch Node
		meshSwitch = mc.createNode('meshSwitch',n=pre+'meshSwitch')
		meshSwitchList.append(meshSwitch)
		
		# Connect Source Meshes
		for i in range(len(sourceList)):
			mc.connectAttr(sourceList[i]+'.outMesh',meshSwitch+'.inMesh['+str(i)+']',f=True)
		
		# Connect To Target
		mc.connectAttr(meshSwitch+'.outMesh',target+'.inMesh',f=True)
	
	# Return Result
	return meshSwitchList

def connect(switchList,sourceList):
	'''
	Connect the list of meshes specified by the sourceList argument to the list of meshSwitch nodes.
	@param switchList: The list of meshSwitch nodes to connect to.
	@type switchList: list
	@param sourceList: The list of source meshes to connect to the meshSwitch nodes.
	@type sourceList: list
	'''
	# Check switchList
	if type(switchList) == str or type(switchList) == unicode:
		switchList = [str(switchList)]
	
	# For each switch
	for meshSwitch in switchList:
		
		# For item in source list
		for i in range(len(sourceList)):
			
			# Connect source item to meshSwitch input
			try: mc.connectAttr(sourceList[i]+'.outMesh',meshSwitch+'.inMesh['+str(i)+']',f=True)
			except: pass

def clearInput(switchList):
	'''
	Disconnect all incoming mesh connections to the list of specified meshSwitch nodes
	@param switchList: The list of meshSwitch nodes to disconnect incoming connections from.
	@type switchList: list
	'''
	# Check switchList
	if type(switchList) == str or type(switchList) == unicode:
		switchList = [str(switchList)]
	
	# For each switch
	for meshSwitch in switchList:
		
		# Get list of incoming mesh connections
		connectionList = mc.listConnections(meshSwitch+'.inMesh',s=True,d=False,p=True,c=True)
		if not connectionList: continue
		
		# Iterate over connections
		for i in range(len(connectionList)):
			
			# Skip odd numbered iteration
			if i%2: continue
			
			# Disconnect attribute
			mc.disconnectAttr(connectionList[i+1],connectionList[i])
