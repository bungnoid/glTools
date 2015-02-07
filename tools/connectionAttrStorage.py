import maya.cmds as mc
import glTools.utils.transform

class ConnectionAttrStorage(object):

	def __init__(self):
		self.nodes = []
		self.connectionStorage={}
		self.storageAttr = 'connectionStorage'
		
	def storeData(self, nodes=None):
		
		if nodes: self.addNodes(nodes)
		
		if not self.nodes:
			raise Exception('No nodes to store data for.')
			
		self.getParent()
		self.getIncomingConnections()
		self.getOutgoingConnections()
		self.createAttrs()
		self.setAttrs()
		
	def rebuild(self):
		pass
		
	def addNodes(self, nodes):
		for node in nodes: self.nodes.append(node)
		
	def getParent(self):
		
		if not self.nodes:
			raise Exception('No nodes added to get parents of.')
			
		for node in self.nodes:
			if not glTools.utils.transform.isTransform(node): continue
			
			parent = mc.listRelatives(node, allParents=True)[0]
			
			if not self.connectionStorage.has_key(node): self.connectionStorage[node] = []
			
			self.connectionStorage[node].append(['parent', parent]) 
			
				
	def getIncomingConnections(self):
		
		if not self.nodes:
			raise Exception('No nodes added to get incoming connections on.')
		
		for node in self.nodes:
			connections = mc.listConnections(node, plugs=True, source=True, destination=False, connections=True, skipConversionNodes=True)
			
			if not connections: continue
			
			if not self.connectionStorage.has_key(node): self.connectionStorage[node] = []
			
			count = len(self.connectionStorage[node])
			
			# set connection source
			for i in range(1, len(connections), 2): self.connectionStorage[node].append([connections[i], None]) 
				
			# set connection destination
			for i in range(0, len(connections), 2):
				self.connectionStorage[node][count][1] = connections[i] 
				count+=1

	def getOutgoingConnections(self):
		
		if not self.nodes:
			raise Exception('No nodes added to get outgoing connections on.')
		
		for node in self.nodes:
			connections = mc.listConnections(node, plugs=True, source=False, destination=True, connections=True, skipConversionNodes=True)
			
			if not connections: continue
			
			if not self.connectionStorage.has_key(node): self.connectionStorage[node] = []
			
			count = len(self.connectionStorage[node])
			
			# set connection source
			for i in range(0, len(connections), 2): self.connectionStorage[node].append([connections[i], None]) 
				
			# set connection destination
			for i in range(1, len(connections), 2):
				self.connectionStorage[node][count][1] = connections[i] 
				count+=1
				
	def createAttrs(self):
		
		if not self.connectionStorage:
			raise Exception('No nodes added to create attributes on.')
			
		for node in self.connectionStorage.keys():
			if not mc.objExists('%s.%s' % (node, self.storageAttr)):
				mc.addAttr(node,ln=self.storageAttr,dataType='string',en=':Keyable:NonKeyable:Locked:',m=1)
		
	def setAttrs(self):
		if not self.connectionStorage:
			raise Exception('No connection data stored to set attributes with.')
			
		for node in self.connectionStorage.keys():
			for i, connection in enumerate(self.connectionStorage[node]):
				mc.setAttr('%s.%s[%s]' % (node, self.storageAttr, i), str(connection), type='string')
				print 'Set :: %s.%s[%s], To :: %s' % (node, self.storageAttr, i, connection)
	
	def getAttrs(self):
		if not self.nodes:
			raise Exception('No nodes added to get attribute data from.')
		
		for node in self.nodes:
			
			if not self.connectionStorage.has_key(node): self.connectionStorage[node] = []
			
			if not mc.objExists('%s.%s' % (node, self.storageAttr)): 
				print "Skipping %s because it does not have a %s attribute." % (node, self.storageAttr)
				continue
			
			for index in mc.getAttr('%s.%s' % (node, self.storageAttr), multiIndices=True):
				self.connectionStorage[node].append( eval(mc.getAttr('%s.%s[%s]' % (node, self.storageAttr, index))) )

	def rebuildConnections(self):
		if not self.connectionStorage:
			raise Exception('No connection data stored to connect attributes with.')				
			
		for node in self.connectionStorage:
			print "Node :: %s" % node
			for connectionPair in self.connectionStorage[node]:
				
				if connectionPair[0] == 'parent':
					try: mc.parent(node, connectionPair[1])
					except: print "Could not connect :: %s To :: %s" % (node, connectionPair[1])
				
				if not mc.objExists(connectionPair[0]) or not mc.objExists(connectionPair[1]):
					print '%s or %s are not valid objects, skipping to the next connection' % (connectionPair[0], connectionPair[1])
					continue
				
				print "Connecting :: %s To :: %s" % (connectionPair[0], connectionPair[1])
	
				if not mc.isConnected(connectionPair[0], connectionPair[1]):
					try: mc.connectAttr(connectionPair[0], connectionPair[1], f=True)
					except: print "Could not connect :: %s To :: %s" % (connectionPair[0], connectionPair[1])
				 
		
