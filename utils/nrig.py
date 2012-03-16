ika.node_rigging as nrig

def messageConnection(graph,sourceNode,destinationNode):
	'''
	'''
	# Get source/destination node objects
	if type(sNode) == 'str': sNode = graph.getNode(sourceNode)
	else: sNode = sourceNode
	if type(dNode) == 'str': dNode = graph.getNode(destinationNode)
	else: dNode = destinationNode
	
	# Create message plugs
	if not sNode.hasPlug('outMessage'):
		sNode.createPlug('outMessage',str,sNode.name,asOutput=True)
	if not dNode.hasPlug('inMessage'):
		dNode.createPlug('inMessage',str,asInput=True)
	
	# Connect message plugs
	g.connect(sNode.name+'.outMessage',dNode.name+'.inMessage')
