import maya.cmds as mc

import glTools.utils.stringUtils

def multChainRotation(sourceChain,targetChain,multValue=0.5,addMultAttr=True,multAttr='multRotation'):
	'''
	Multiply a source joint chain rotation and apply to a target joint chain.
	@param sourceChain: Source joint chain list
	@type sourceChain: list
	@param targetChain: Target joint chain list
	@type targetChain: list
	@param multValue: Amount to multiply roation value by
	@type multValue: float
	@param addMultAttr: Add a float attribute to control the multiply amount. Attribute will be added to the root of the target chain
	@type addMultAttr: bool
	@param multAttr: String name for the multiply attribute
	@type multAttr: str
	'''
	# Check source/target chain
	sourceChainLen = len(sourceChain)
	targetChainNum = len(targetChain)
	
	if sourceChainLen != targetChainNum:
		raise Exception('Source and Target chain length mis-match! Source and Target chains must have the same number of joints!')
		
	# For each joint in the chain
	multNodeList = []
	for i in range(sourceChainLen):
		
		# Generate prefix
		pre = glTools.utils.stringUtils.stripSuffix(sourceChain[i])
		
		# Create taper node - multiplyDivide
		multNode = mc.createNode('multiplyDivide',n=pre+'_multiplyDivide')
		multNodeList.append(multNode)
		
		# Make rotation connections
		mc.setAttr(multNode+'.input1',multValue,multValue,multValue)
		mc.connectAttr(sourceChain[i]+'.r',multNode+'.input2',f=True)
		mc.connectAttr(multNode+'.output',targetChain[i]+'.r',f=True)
	
	# Check taper attribute
	if addMultAttr:
		
		# Add attribute
		mc.addAttr(targetChain[0],ln=multAttr,min=0,max=1,dv=multValue,k=True)
		
		# Connect taper attribute to taper nodes
		for multNode in multNodeList:
			mc.connectAttr(targetChain[0]+'.'+multAttr,multNode+'.input1X',f=True)
			mc.connectAttr(targetChain[0]+'.'+multAttr,multNode+'.input1Y',f=True)
			mc.connectAttr(targetChain[0]+'.'+multAttr,multNode+'.input1Z',f=True)

def blendChainRotation(inputChain1,inputChain2,targetChain,blendValue=0.5,addBlendAttr=True,blendAttr='blendRotation'):
	'''
	Blend the joint chain rotation between 2 input chains and apply to a target joint chain.
	@param inputChain1: Source joint chain list 1
	@type inputChain1: list
	@param inputChain1: Source joint chain list 2
	@type inputChain1: list
	@param targetChain: Target joint chain list
	@type targetChain: list
	@param blendValue: Amount to blend roation value by
	@type blendValue: float
	@param addBlendAttr: Add a float attribute to control the blend amount. Attribute will be added to the root of the target chain.
	@type addBlendAttr: bool
	@param blendAttr: String name for the blend attribute
	@type blendAttr: str
	'''
	# Check input/target chain
	input1ChainLen = len(input1Chain)
	input2ChainLen = len(input2Chain)
	targetChainNum = len(targetChain)
	
	if input1ChainLen != input2ChainLen:
		raise Exception('Input chain length mis-match! Input joint chains must have the same number of joints!')
	if input1ChainLen != targetChainLen:
		raise Exception('Input and Target chain length mis-match! Input and Target joint chains must have the same number of joints!')
	
	# For each joint in the chain
	blendNodeList = []
	for i in range(input1ChainLen):
		
		# Generate prefix
		pre = glTools.utils.stringUtils.stripSuffix(input1Chain[i])
		
		# Create blend node - blendColors
		blendNode = mc.createNode('blendColors',n=pre+'_blendColors')
		blendNodeList.append(blendNode)
		
		# Make connections
		mc.setAttr(blendNode+'.blender',blendValue)
		mc.connectAttr(input1Chain[i]+'.r',blendNode+'.color1',f=True)
		mc.connectAttr(input2Chain[i]+'.r',blendNode+'.color2',f=True)
		mc.connectAttr(blendNode+'.output',targetChain[i]+'.r',f=True)
		
	# Check blend attribute
	if addBlendAttr:
		
		# Add blend attribute
		mc.addAttr(targetChains[0],ln=blendAttr,min=0,max=1,dv=blendValue,k=True)
		
		# Connect blend attribute to taper nodes
		for blendNode in blendNodeList:
			mc.connectAttr(targetChains[0]+'.'+blendAttr,blendNode+'.blender',f=True)

def taperChainRotationMulti(sourceChain,targetChains,useMaxValue=False,addTaperAttr=True,taperAttr='taperRotation'):
	'''
	Taper joint chain rotation across a list of target joint chains.
	@param sourceChain: Source joint chain list
	@type sourceChain: list
	@param targetChains: Target joint chain list
	@type targetChains: list[]
	@param useMaxValue: Start the taper at 100%
	@type useMaxValue: bool
	@param addTaperAttr: Add a float attribute to control the taper amount. Attribute will be added to the root of each target chain
	@type addTaperAttr: bool
	@param taperAttr: String name for the taper attribute
	@type taperAttr: str
	'''
	# Check max value
	notMax = int(not useMaxValue)
	
	# Check source chain
	sourceChainLen = len(sourceChain)
	
	# Check target chains
	targetChainNum = len(targetChains)
	for i in range(targetChainNum):
		targetChainLen = len(targetChainNum[i])
		if targetChainLen != sourceChainLen:
			raise Exception('Chain length mis-match! Source and target chains must have the same number of joints!')
		
	# Calculate blend increments
	blendInc = 1.0 / (targetChainNum + notMax)
	
	# Blend chains
	for i in range(targetChainNum):
	
		# Get chain index (alpha) 
		chainInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		
		# Calculate taper weight
		taperWt = 1.0 - (blendInc * (i + notMax))
	
		# For each joint in the chain
		taperNodeList = []
		for n in range(sourceChainLen):
			
			# Generate prefix
			pre = glTools.utils.stringUtils.stripSuffix(sourceChain[i]) + chainInd
			
			# Create taper node - multiplyDivide
			taperNode = mc.createNode('multiplyDivide',n=pre+'_multiplyDivide')
			taperNodeList.append(taperNode)
			
			# Make connections
			mc.setAttr(taperNode+'.input1',taperWt,taperWt,taperWt)
			mc.connectAttr(sourceChain[n]+'.r',taperNode+'.input2',f=True)
			mc.connectAttr(taperNode+'.output',targetChains[i][n]+'.r',f=True)
		
		# Check taper attribute
		if addTaperAttr:
			
			# Add attribute
			mc.addAttr(targetChains[i][0],ln=taperAttr,min=0,max=1,dv=taperWt,k=True)
			
			# Connect taper attribute to taper nodes
			for taperNode in taperNodeList:
				mc.connectAttr(targetChains[i][0]+'.'+taperAttr,taperNode+'.input1X',f=True)
				mc.connectAttr(targetChains[i][0]+'.'+taperAttr,taperNode+'.input1Y',f=True)
				mc.connectAttr(targetChains[i][0]+'.'+taperAttr,taperNode+'.input1Z',f=True)
		

def blendChainRotationMulti(startChain,endChain,targetChains,useMinValue=False,useMaxValue=False,addBlendAttr=False,blendAttr='blendRotation'):
	'''
	@param startChain: Start joint chain list
	@type startChain: list
	@param endChain: End joint chain list
	@type endChain: list
	@param targetChains: Target joint chain list
	@type targetChains: list[]
	@param useMinValue: End the blend at 0%
	@type useMinValue: bool
	@param useMaxValue: Start the blend at 100%
	@type useMaxValue: bool
	@param addBlendAttr: Add a float attribute to control the blend amount. Attribute will be added to the root of each target chain
	@type addBlendAttr: bool
	@param blendAttr: String name for the blend attribute
	@type blendAttr: str
	'''
	# Check min/max values
	notMin = int(not useMinValue)
	notMax = int(not useMaxValue)
	
	# Check start/end chain
	startChainLen = len(sourceChain)
	endChainLen = len(sourceChain)
	if startChainLen != endChainLen:
			raise Exception('Start and End chain length mis-match! Start and End chains must have the same number of joints!')
	
	# Check target chains
	targetChainNum = len(targetChains)
	for i in range(targetChainNum):
		targetChainLen = len(targetChainNum[i])
		if targetChainLen != startChainLen:
			raise Exception('Chain length mis-match! Source and target chains must have the same number of joints!')
		
	# Calculate blend increments
	blendInc = 1.0 / (targetChainNum + notMin + notMax)
	
	# Blend chains
	for i in range(targetChainNum):
	
		# Get chain index (alpha) 
		chainInd = glTools.utils.stringUtils.alphaIndex(i,upper=True)
		
		# Calculate blend weight
		blendWt = 1.0 - (blendInc * (i + notMax))
	
		# For each joint in the chain
		blendNodeList = []
		for n in range(startChainLen):
			
			# Generate prefix
			pre = glTools.utils.stringUtils.stripSuffix(sourceChain[i]) + chainInd
			
			# Create blend node
			blendNode = mc.createNode('blendColors',n=pre+'_blendColors')
			blendNodeList.append(blendNode)
			
			# Make connections
			mc.setAttr(blendNode+'.blender',blendWt)
			mc.connectAttr(startChain[n]+'.r',blendNode+'.color1',f=True)
			mc.connectAttr(endChain[n]+'.r',blendNode+'.color2',f=True)
			mc.connectAttr(blendNode+'.output',targetChains[i][n]+'.r',f=True)
		
		# Check taper attribute
		if addBlendAttr:
			
			# Add attribute
			mc.addAttr(targetChains[i][0],ln=blendAttr,min=0,max=1,dv=blendWt,k=True)
			
			# Connect taper attribute to taper nodes
			for taperNode in taperNodeList:
				mc.connectAttr(targetChains[i][0]+'.'+blendAttr,blendNode+'.blender',f=True)
		
		
