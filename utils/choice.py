import maya.cmds as mc

import glTools.utils.attribute

def create(inputType='string',selectInput=None,inputVal=None,inputSrc=None,dst=None,prefix=None):
	'''
	Create choice node from the input arguments
	@param inputType: Input data type
	@type inputType: str
	@param selectInput: Selector source value attribute (optional)
	@type selectInput: str
	@param inputVal: List of input values to apply as setAttr's (optional)
	@type inputVal: list
	@param inputSrc: List of input source value attributes (optional)
	@type inputSrc: list
	@param dst: Output destination attribute (optional)
	@type dst: str
	@param prefix: Choice node naming prefix (optional)
	@type prefix: str
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Selector Input
	if selectInput:
		if not mc.objExists(selectInput):
			raise Exception('Selector input source "'+selectInput+'" does not exist!')
		if not glTools.utils.attribute.isAttr(selectInput):
			raise Exception('Selector input source "'+selectInput+'" is not a valid attribute!')
	
	# Input
	if inputSrc:
		for inSrc in inputSrc:
			if not mc.objExists(inSrc):
				raise Exception('Input source "'+inSrc+'" does not exist!')
			if not glTools.utils.attribute.isAttr(inSrc):
				raise Exception('Input source "'+inSrc+'" is not a valid attribute!')
	
	# Destination
	if dst:
		if not mc.objExists(selectInput):
			raise Exception('Destination plug "'+dst+'" does not exist!')
		if not glTools.utils.attribute.isAttr(dst):
			raise Exception('Destination plug "'+dst+'" is not a valid attribute!')
	
	# Prefix
	if not prefix:
		prefix = ''
		if dst: prefix = dst.split('.')[0]
	
	# ======================
	# - Create Choice Node -
	# ======================
	
	choiceNode = mc.createNode('choice',n=prefix+('_'*int(bool(prefix)))+'choice')
	
	# =======================
	# - Connect Choice Node -
	# =======================
	
	# Selector Input
	if selectInput:
		try:
			mc.connectAttr(selectInput,choiceNode+'.selector',f=True)
		except Exception, e:
			raise Exception('Error connecting selector input "'+selectInput+'" >> "'+choiceNode+'.selector"! Exception msg: '+str(e))
		else:
			print ('Connected "'+selectInput+'" >> "'+choiceNode+'.selector"')
	
	# Input
	inputLen = 0
	if inputVal:
		if len(inputVal) > inputLen:
			inputLen = len(inputVal)
	if inputSrc:
		if len(inputSrc) > inputLen:
			inputLen = len(inputSrc)
	
	if inputLen:
		
		# Create Attribute (based on input type)
		if inputType == 'string':
			mc.addAttr(choiceNode,ln='inputValue',dt=inputType,m=True)
		elif inputType == 'long' or inputType == 'float':
			mc.addAttr(choiceNode,ln='inputValue',at=inputType,m=True)
		else:
			raise Exception('Invalid input type "'+inputType+'"!')
		
		# Set Input Values
		if inputVal:
			for i in range(len(inputVal)):
				if not inputVal[i] == None:
					if inputType == 'string':
						try: mc.setAttr(choiceNode+'.inputValue['+str(i)+']',inputVal[i],type=inputType)
						except Exception, e: raise Exception('Error setting input value "'+choiceNode+'.inputValue['+str(i)+']"! Exception msg: '+str(e))
					elif inputType == 'long' or inputType == 'float':
						try: mc.setAttr(choiceNode+'.inputValue['+str(i)+']',inputVal[i])
						except Exception, e: raise Exception('Error setting input value "'+choiceNode+'.inputValue['+str(i)+']"! Exception msg: '+str(e))
					else:
						raise Exception('Invalid input type "'+inputType+'"!')
		
		# Connect Input Source
		if inputSrc:
			for i in range(len(inputSrc)):
				if not inputSrc[i] == None:
					try: mc.connectAttr(inputSrc[i],choiceNode+'.inputValue['+str(i)+']',f=True)
					except Exception, e: raise Exception('Error connecting input source "'+inputSrc[i]+'" >> "'+choiceNode+'.inputValue['+str(i)+']"! Exception msg: '+str(e))
		
		# Connect Input
		for i in range(inputLen):
			try: mc.connectAttr(choiceNode+'.inputValue['+str(i)+']',choiceNode+'.input['+str(i)+']',f=True)
			except Exception, e: raise Exception('Error connecting input value "'+choiceNode+'.inputValue['+str(i)+']" >> "'+choiceNode+'.input['+str(i)+']"! Exception msg: '+str(e))
		
		# Connect Destination
		if dst:
			try: mc.connectAttr(choiceNode+'.output',dst,f=True)
			except Exception, e: raise Exception('Error connecting to choice destination "'+dst+'"! Exception msg: '+str(e))
			else: print('Connected "'+choiceNode+'.output" >> "'+dst+'"')
	
	# =================
	# - Return Result -
	# =================
	
	return choiceNode
