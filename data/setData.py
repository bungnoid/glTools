import maya.cmds as mc

import data

class SetData( data.Data ):
	'''
	SetData class object.
	Contains functions to save, load and rebuild maya sets.
	'''
	def __init__(self,setNode=None):
		'''
		SetData class initializer.
		
		'''
		# Execute Super Class Initilizer
		super(SetData, self).__init__()
		
		# Initialize Default Class Data Members
		self._data['name'] = ''
		self._data['membership'] = []
		self.mode = ['add','replace']
		
		# Build Data
		if setNode: self.buildData(setNode)
		
	def verifySet(self,setNode):
		'''
		Run standard checks on the specified set
		@param setNode: Set to verify
		@type setNode: str
		'''
		# Check Set Exists
		if not mc.objExists(setNode):
			raise Exception('Set "'+setNode+'" does not exists!')
		
		# Check Set Node Type
		if mc.objectType(setNode) != 'objectSet':
			raise Exception('Object "'+setNode+'" is not a vaild "set" node!')
	
	def buildData(self,setNode):
		'''
		Build setData class.
		@param setNode: Set to initialize data for
		@type setNode: str
		'''
		# ==========
		# - Checks -
		# ==========
		
		if not setNode:
			raise Exception('Invalid set node! Unable to build setData...')
			return
		
		self.verifySet(setNode)
		
		# ==============
		# - Build Data -
		# ==============
		
		# Start timer
		timer = mc.timerX()
		
		# Reset Data
		self.reset()
		
		# Get basic set info
		self._data['name'] = setNode
		self._data['membership'] = mc.sets(setNode,q=True)
		
		# Print timer result
		buildTime = mc.timerX(st=timer)
		print('SetData: Data build time for set "'+setNode+'": '+str(buildTime))
		
		# =================
		# - Return Result -
		# =================
		
		return self._data['name']
	
	def rebuild(self,mode='add',forceMembership=True):
		'''
		Rebuild the set from the stored setData.
		@param mode: Membership mode if the specified set already exists. Accepted values are "add" and "replace".
		@type mode: str
		@param forceMembership: Forces addition of items to the set. If items are in another set which is in the same partition as the given set, the items will be removed from the other set in order to keep the sets in the partition mutually exclusive with respect to membership. 
		@type forceMembership: bool
		'''
		# ==========
		# - Checks -
		# ==========
		
		# Set Name
		if not self._data['name']:
			raise Exception('SetData has not been initialized!')
		
		# Member Items
		memberList = self._data['membership'] or []
		for obj in memberList:
			if not mc.objExists(obj):
				print('Set member item "'+obj+'" does not exist! Unable to add to set...')
				memberList.remove(obj)
		
		# Flatten Membership List
		memberList = mc.ls(memberList,fl=True) or []
			
		# Mode
		if not mode in self.mode:
			raise Exception('Invalid set membership mode "'+mode+'"! Use "add" or "replace"!')
		
		# ===============
		# - Rebuild Set -
		# ===============
		
		# Start timer
		timer = mc.timerX()
		
		# Create Set
		setName = self._data['name']
		
		# Delete Set (REPLACE only)
		if mc.objExists(setName) and mode == 'replace': mc.delete(setName)
		
		# Create Set
		if not mc.objExists(setName): setName = mc.sets(n=setName)
		
		# Add Members
		if memberList:
			if forceMembership:
				for obj in memberList:
					try: mc.sets(obj,e=True,fe=setName)
					except Exception, e:
						print('Error adding item "'+obj+'" to set "'+setName+'"! Skipping')
						print(str(e))
			else:
				for obj in memberList:
					try: mc.sets(obj,e=True,add=setName)
					except Exception, e:
						print('Error adding item "'+obj+'" to set "'+setName+'"! Skipping')
						print(str(e))
		
		# Print Timer Result
		buildTime = mc.timerX(st=timer)
		print('SetData: Rebuild time for set "'+setName+'": '+str(buildTime))
			
		# =================
		# - Return Result -
		# =================
		
		self.setName = setName
		
		result = {}
		result['set'] = setName
		result['membership'] = memberList
		return result
	

