import maya.cmds as mc

import channelData

class ChannelStateData( channelData.ChannelData ):
	'''
	ChannelStateData class object.
	Contains functions to save, load and rebuild channel values and connections.
	This class can be sub-classed to create more specialized data objects.
	'''
	def __init__(self,verbosity=0):
		'''
		ChannelStateData class initializer.
		@param verbosity: Level of detailed output messages.
		@type verbosity: int
		'''
		# Define Channel List
		chanList=['channelState','defaultAttrState']
		
		# Define Node List
		nodeList = []
		chanStateList = mc.ls('*.channelState',r=True,o=True)
		if chanStateList: nodeList.extend(chanStateList)
		attrStateList = mc.ls('*.defaultAttrState',r=True,o=True)
		if attrStateList: nodeList.extend(attrStateList)
		
		# Execute Super Class Initilizer
		super(ChannelStateData, self).__init__(	nodeList=nodeList,
												chanList=chanList,
												verbosity=verbosity	)
		
	def buildData(self,nodeList=None,chanList=None):
		'''
		Build ChannelData class.
		@param nodeList: List of nodes to store channel values and connections for.
		@type nodeList: list
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Node List
		if not nodeList:
			print('ChannelData: Empty node list! Unable to build channelData!')
			return
		
		# Channel List
		if not chanList: chanList = self.userChannelList
		if not chanList: chanList = []
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Reset Data --- ?
		self.reset()
		
		# Build Node Channel Data
		self._data['channelDataNodes'] = []
		for node in nodeList:
			
			# Initialize Node Data
			self._channelData[node] = {}
			self._data['channelDataNodes'].append(node)
			
			# Build Node.Channel List
			nodeChanList = [node+'.'+i for i in chanList if mc.objExists(node+'.'+i)]
			
			# Get Value Channel List
			valChanList = []
			if chanList: valChanList = chanList
			else: valChanList = mc.listAttr(node,se=True,r=True,w=True,m=True,v=True)
			
			# Get Source Connection Channel List
			srcChanList = []
			if nodeChanList: srcChanList = mc.listConnections(nodeChanList,s=True,d=False,p=True,c=True,sh=True) or []
			else: srcChanList = mc.listConnections(node,s=True,d=False,p=True,c=True,sh=True) or []
			
			# Get Destination Connection Channel List
			dstChanList = []
			if nodeChanList: dstChanList = mc.listConnections(nodeChanList,s=False,d=True,p=True,c=True,sh=True) or []
			else: dstChanList = mc.listConnections(node,s=False,d=True,p=True,c=True,sh=True) or []
			
			# Add Channel Value Data
			for chan in valChanList:
				
				# Check Attribute
				#if not mc.attributeQuery(chan,n=node,ex=True):
				if not mc.objExists(node+'.'+chan):
					if self.verbosity > 0: print('ChannelData: Node "'+node+'" has no attribute "'+chan+'"! Skipping...')
					continue
				
				# Check Settable
				if not mc.getAttr(node+'.'+chan,se=True):
					if not mc.listConnections(node+'.'+chan,s=True,d=False):
						if self.verbosity > 0: print('ChannelData: Attribute "'+node+'.'+chan+'" is not settable! Skipping...')
						continue
				
				# Get Channel Value
				chanVal = None
				try: chanVal = mc.getAttr(node+'.'+chan)
				except Exception, e:
					if self.verbosity > 0: print('ChannelData: Error getting channel value "'+node+'.'+chan+'"! Skipping...')
					if self.verbosity > 1: print('ChannelData: Exception message: '+str(e))
				else:
					# Create Channel Entry
					if not self._channelData[node].has_key(chan): self._channelData[node][chan] = {}
					
					# Store Channel Value
					if not chanVal == None:
						if type(chanVal) == list:
							if type(chanVal[0]) == tuple:
								chanVal = list(chanVal[0])
						self._channelData[node][chan]['value'] = chanVal
			
			# Add Channel Source Data
			for i in range(0,len(srcChanList),2):
				
				# Get Channel Name
				chan = str(srcChanList[i].replace(node+'.',''))
				
				# Create Channel Entry
				if not self._channelData[node].has_key(chan): self._channelData[node][chan] = {}
				
				# Store Channel Source Data
				self._channelData[node][chan]['source'] = srcChanList[i+1]
				
				# Store Channel Value Data
				try: chanVal = mc.getAttr(srcChanList[i])
				except Exception, e:
					if self.verbosity > 0: print('ChannelData: Error getting channel value "'+node+'.'+chan+'"! Skipping...')
					if self.verbosity > 1: print('ChannelData: Exception message: '+str(e))
				else:
					self._channelData[node][chan]['value'] = chanVal
			
			# Add Channel Desitination Data
			for i in range(0,len(dstChanList),2):
				
				# Get Channel Name
				chan = dstChanList[i].replace(node+'.','')
				
				# Create Channel Entry
				if not self._channelData[node].has_key(chan): self._channelData[node][chan] = {}
				
				# Store Channel Desitination Data
				self._channelData[node][chan]['destination'] = dstChanList[i+1]
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('ChannelData: Data build time for nodes "'+str(nodeList)+'": '+str(buildTime))
		
		# =================
		# - Return Result -
		# =================
		
		return self._data.keys()
	
	def rebuild(self,nodeList=[],chanList=[],connectSource=False,connectDestination=False):
		'''
		Rebuild the channel values and connections from the stored ChannelData.
		@param nodeList: List of nodes to restore channel values and connections for. If empty, rebuild all stored channel data.
		@type nodeList: List
		@param chanList: List of nodes channels to restore values and connections for. If empty, rebuild all stored channel data.
		@type chanList: List
		@param connectSource: Attempt to restore all source connections.
		@type connectSource: bool
		@param connectDestination: Attempt to restore all destination connections. 
		@type connectDestination: bool
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Node List
		if not self._data['channelDataNodes']:
			raise Exception('ChannelData has not been initialized!')
		
		# ========================
		# - Rebuild Channel Data -
		# ========================
		
		# Start Timer
		timer = mc.timerX()
		
		# Get Node List
		if not nodeList: nodeList = self._data['channelDataNodes']
		if not nodeList:
			print('ChannelData: No channel data nodes to rebuild!')
			return
		
		# Rebuild Node Channel Data
		for node in nodeList:
			
			# Check Node Key
			if not self._channelData.has_key(node):
				if self.verbosity > 0: print('ChannelData: No channel data stored for "'+node+'"!! Skipping...')
			
			# Get Node Channel List
			channelList = self._channelData[node].keys()
			
			# Rebuild Node Channel Data
			for chan in sorted(channelList):
				
				# Check Channel Exists
				if not mc.objExists(node+'.'+chan):
					if self.verbosity > 0: print('ChannelData: Channel "" does not exist! Unable to rebuild channel data! Skipping...')
					continue
				
				# Restore Channel Value
				if self._channelData[node][chan].has_key('value'):
					chanVal = self._channelData[node][chan]['value']
					
					# Set Channel Value
					if mc.getAttr(node+'.'+chan,se=True):
						
						# Get Channel Type
						chanType = str(mc.getAttr(node+'.'+chan,type=True))
						#print chanType
						if chanType == 'matrix':
							try: mc.setAttr(node+'.'+chan,chanVal,type=chanType)
							except Exception, e:
								if self.verbosity > 0: print('ChannelData: Error setting matrix channel value for "'+node+'.'+chan+'"!')
								if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
						elif chanType == 'string':
							try: mc.setAttr(node+'.'+chan,chanVal,type=chanType)
							except Exception, e:
								if self.verbosity > 0: print('ChannelData: Error setting string channel value for "'+node+'.'+chan+'"!')
								if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
						else:
							if type(chanVal) == list:
								try: mc.setAttr(node+'.'+chan,*chanVal)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Error setting list channel value on "'+node+'.'+chan+'"!')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
							else:
								try: mc.setAttr(node+'.'+chan,chanVal)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Error setting scalar channel value on "'+node+'.'+chan+'"!')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
					else:
						if self.verbosity > 0:
							print('ChannelData: Node channel "'+node+'.'+chan+'" is not settable!! Unable to restore channel value...')
				
				# Restore Channel Destination Connection
				if connectDestination:
					if self._channelData[node][chan].has_key('destination'):
						src = node+'.'+chan
						dst = self._channelData[node][chan]['destination']
						
						# Check existing connections
						connect = True
						dstConn = mc.listConnections(dst,s=True,d=False,p=True,sh=True)
						if dstConn:
							if dstConn[0] == src:
								if self.verbosity > 0: print('ChannelData: "'+src+'" already connected to "'+dst+'"! Skipping...')
								connect = False
						
						# Check Locked Destination
						if connect:
							dstLocked = mc.getAttr(dst,l=True)
							if dstLocked:
								try: mc.setAttr(dst,l=False)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Unable to unlock destination channel "'+dst+'"! Skipping...')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
									connect = False
								else:
									if self.verbosity > 0: print('ChannelData: Unlocked channel "'+dst+'"')
						
						# Rebuild Connection
						if connect:
							try: mc.connectAttr(src,dst,f=True)
							except Exception, e:
								if self.verbosity > 0: print('ChannelData: Unable to connect "'+src+'" --> "'+dst+'"! Skipping...')
								if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
							else:
								if self.verbosity > 0: print('ChannelData: Connected "'+src+'" --> "'+dst+'"')
							if dstLocked:
								try: mc.setAttr(dst,l=False)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Unable to relock channel "'+dst+'"')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
								else:
									if self.verbosity > 0: print('ChannelData: Relocked channel "'+dst+'"')
				
				# Rebuild Channel Source Connection
				if connectSource:
					
					if self._channelData[node][chan].has_key('source'):
						src = self._channelData[node][chan]['source']
						dst = node+'.'+chan
						
						# Check existing connections
						connect = True
						dstConn = mc.listConnections(dst,s=True,d=False,p=True,sh=True)
						if dstConn:
							if dstConn[0] == src:
								if self.verbosity > 0: print('ChannelData: "'+src+'" already connected to "'+dst+'"! Skipping...')
								connect = False
						
						# Check Locked Destination
						if connect:
							dstLocked = mc.getAttr(dst,l=True)
							if dstLocked:
								try: mc.setAttr(dst,l=False)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Unable to unlock destination channel "'+dst+'"! Skipping...')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
									connect = False
								else:
									if self.verbosity > 0: print('ChannelData: Unlocked channel "'+dst+'"')
						
						# Rebuild Connection
						if connect:
							try: mc.connectAttr(src,dst,f=True)
							except Exception, e:
								if self.verbosity > 0: print('ChannelData: Unable to connect "'+src+'" --> "'+dst+'"! Skipping...')
								if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
							else:
								if self.verbosity > 0: print('ChannelData: Connected "'+src+'" --> "'+dst+'"')
							if dstLocked:
								try: mc.setAttr(dst,l=False)
								except Exception, e:
									if self.verbosity > 0: print('ChannelData: Unable to relock channel "'+dst+'"')
									if self.verbosity > 1: print('ChannelData: Exception message '+str(e))
								else:
									if self.verbosity > 0: print('ChannelData: Relocked channel "'+dst+'"')
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('ChannelData: Rebuild time "'+str(nodeList)+'": '+str(buildTime))
			
		# =================
		# - Return Result -
		# =================
		
		return nodeList
	
	def nodeChannels(self,node):
		'''
		Return a list of stored channel data for the specified node.
		'''
		if not self._channelData.has_key(node):
			if self.verbosity > 0: print('ChannelData: No channel data stored for "'+node+'"!! Skipping...')
		channelList = sorted(self._channelData[node].keys())
		return channelList
	
 
