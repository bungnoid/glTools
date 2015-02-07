import re

class NamingConvention( object ):
	
	def __init__(self):
		
		# Base Hierarchy
		self.base = {}
		self.base['all'] = 'all'
		self.base['constrain'] = 'constrain'
		self.base['gimbal'] = 'gimbal'
		self.base['misc'] = 'misc'
		self.base['model'] = 'model'
		self.base['orient'] = 'orient'
		self.base['orientOffset'] = 'orientOffset'
		self.base['supermover'] = 'supermover'
		self.base['xform'] = 'xform'
		
		# Valid name elements
		self.namePattern = ['[a-z]{2}','[a-z]{3}\d{2}','[a-z]{2}\d{2}','[a-z]{3}']
		self.elemCount = (3,5)
		
		# Delineator
		self.delineator = '_'
		
		# Side
		self.side = {}
		self.side['center'] = 'cn'
		self.side['left'] = 'lf'
		self.side['right'] = 'rt'
		self.side['front'] = 'ft'
		self.side['back'] = 'bk'
		self.side['top'] = 'tp'
		self.side['bottom'] = 'bt'
		self.side['upper'] = 'up'
		self.side['lower'] = 'lw'
		self.side['high'] = 'hi'
		self.side['low'] = 'lo'
		self.side['middle'] = 'md'
		
		# Part
		self.part = {}
		self.part['ankle'] = 'ank'
		self.part['antenna'] = 'ant'
		self.part['arm'] = 'arm'
		self.part['back'] = 'bck'
		self.part['ball'] = 'bal'
		self.part['beak'] = 'bek'
		self.part['body'] = 'bdy'
		self.part['brow'] = 'brw'
		self.part['cheek'] = 'chk'
		self.part['chest'] = 'cht'
		self.part['chin'] = 'chn'
		self.part['clavicle'] = 'clv'
		self.part['claw'] = 'clw'
		self.part['ear'] = 'ear'
		self.part['elbow'] = 'elb'
		self.part['eye'] = 'eye'
		self.part['eyelid'] = 'lid'
		self.part['face'] = 'fac'
		self.part['fang'] = 'fng'
		self.part['feather'] = 'fth'
		self.part['finger'] = 'fng'
		self.part['foot'] = 'fot'
		self.part['hair'] = 'har'
		self.part['hand'] = 'hnd'
		self.part['head'] = 'hed'
		self.part['hip'] = 'hip'
		self.part['hips'] = 'hip'
		self.part['knee'] = 'kne'
		self.part['leg'] = 'leg'
		self.part['lip'] = 'lip'
		self.part['mouth'] = 'mth'
		self.part['neck'] = 'nck'
		self.part['pelvis'] = 'plv'
		self.part['shin'] = 'shn'
		self.part['spine'] = 'spn'
		self.part['sternum'] = 'str'
		self.part['stomache'] = 'stm'
		self.part['tail'] = 'tal'
		self.part['tendon'] = 'tnd'
		self.part['tooth'] = 'tth'
		self.part['teeth'] = 'tth'
		self.part['thigh'] = 'thg'
		self.part['toe'] = 'toe'
		self.part['tounge'] = 'tng'
		self.part['whisker'] = 'wsk'
		self.part['wing'] = 'wng'
		self.part['wrist'] = 'wst'
		
		# Sub Part
		self.subPart = {}
		self.subPart['ankle'] = 'an'
		self.subPart['ball'] = 'bl'
		self.subPart['base'] = 'bs'
		self.subPart['bend'] = 'bd'
		self.subPart['bendPosition'] = 'bp'
		self.subPart['blend'] = 'bn'
		self.subPart['claw'] = 'cw'		# "cl" reserved for "cluster" sub-part
		self.subPart['cluster'] = 'cl'
		self.subPart['combine'] = 'cm'
		self.subPart['controlPoint'] = 'cv'
		self.subPart['curve'] = 'cr'
		self.subPart['default'] = 'xx'
		self.subPart['distance'] = 'dt'
		self.subPart['edge'] = 'eg'
		self.subPart['editPoint'] = 'ep'
		self.subPart['elbow'] = 'el'
		self.subPart['finger'] = 'fn'
		self.subPart['fixed'] = 'fx'
		self.subPart['FK'] = 'fk'
		self.subPart['feather'] = 'fh'
		self.subPart['free'] = 'fr'
		self.subPart['gimbal'] = 'gb'
		self.subPart['IK'] = 'ik'
		self.subPart['joint'] = 'jt'
		self.subPart['knee'] = 'kn'
		self.subPart['lattice'] = 'lt'
		self.subPart['latticeBase'] = 'lb'
		self.subPart['length'] = 'ln'
		self.subPart['negate'] = 'ng'
		self.subPart['point'] = 'pt'
		self.subPart['poleVector'] = 'pv'
		self.subPart['rotate'] = 'rt'
		self.subPart['round'] = 'rd'
		self.subPart['rebuild'] = 'rb'
		self.subPart['scale'] = 'sc'
		self.subPart['shin'] = 'sh'		# ----
		self.subPart['shoulder'] = 'sh'		# Duplicate value !!
		self.subPart['stretch'] = 'st'
		self.subPart['surfacePoint'] = 'sp'
		self.subPart['target'] = 'tr'
		self.subPart['tendon'] = 'tn'
		self.subPart['thigh'] = 'th'
		self.subPart['toe'] = 'to'
		self.subPart['toggle'] = 'tg'
		self.subPart['translate'] = 'tr'
		self.subPart['twist'] = 'tw'
		self.subPart['vertex'] = 'vx'
		self.subPart['wire'] = 'wi'
		self.subPart['wireBase'] = 'wb'
		self.subPart['wrist'] = 'wr'
		
		# Node Type
		self.node = {}
		self.node['addDoubleLinear'] = 'adl'
		self.node['angleBetween'] = 'abn'
		self.node['attachCurve'] = 'acn'
		self.node['attachSurface'] = 'asn'
		self.node['aimConstraint'] = 'amc'
		self.node['avgCurves'] = 'avc'
		self.node['bindPreMatrix'] = 'bpm'
		self.node['blendColors'] = 'blc'
		self.node['blendShape'] = 'bld'
		self.node['blendTwoAttr'] = 'bta'
		self.node['blendWeighted'] = 'bwt'
		self.node['buffer'] = 'buf'
		self.node['bufferJoint'] = 'bfj'
		self.node['choice'] = 'chc'
		self.node['chooser'] = 'chs'
		self.node['clamp'] = 'cpl'
		self.node['closestPointOnMesh'] = 'cpm'
		self.node['closestPointOnSurface'] = 'cps'
		self.node['condition'] = 'cnd'
		self.node['contrast'] = 'cnt'
		self.node['control'] = 'ccc'
		self.node['curveInfo'] = 'cin'
		self.node['curve'] = 'crv'
		self.node['curveFromMeshEdge'] = 'cme'
		self.node['curveFromSurface'] = 'cfs'
		self.node['decomposeMatrix'] = 'dcm'
		self.node['deformerHandle'] = 'ddd'
		self.node['deformer'] = 'dfm'
		self.node['detachCurve'] = 'dcn'
		self.node['detachSurface'] = 'dsn'
		self.node['distanceBetween'] = 'dst'
		self.node['endEffector'] = 'fff'
		self.node['expression'] = 'exp'
		self.node['geometryConstraint'] = 'gmc'
		self.node['gimbal'] = 'gbl'
		self.node['gluster'] = 'gls'
		self.node['group'] = 'grp'
		self.node['ikHandle'] = 'hhh'
		self.node['ikEffector'] = 'fff'
		self.node['joint'] = 'jjj'
		self.node['lidSurface'] = 'lsn'
		self.node['locator'] = 'loc'
		self.node['loft'] = 'lft'
		self.node['mesh'] = 'msh'
		self.node['multDoubleLinear'] = 'mdl'
		self.node['multiplyDivide'] = 'mdn'
		self.node['multMatrix'] = 'mmx'
		self.node['normalConstraint'] = 'nrc'
		self.node['nurbsCurve'] = 'crv'
		self.node['nurbsSurface'] = 'srf'
		self.node['orient'] = 'ori'
		self.node['orientConstraint'] = 'orc'
		self.node['parentConstraint'] = 'prc'
		self.node['plusMinusAverage'] = 'pma'
		self.node['pointConstraint'] = 'ptc'
		self.node['pointMatrixMult'] = 'pmm'
		self.node['pointOnCurveInfo'] = 'poc'
		self.node['pointOnSurfaceInfo'] = 'pos'
		self.node['poleVectorConstraint'] = 'pvc'
		self.node['poseTarget'] = 'ptg'
		self.node['poseTransform'] = 'ptf'
		self.node['rebuildCurve'] = 'rbc'
		self.node['rebuildSurface'] = 'rbs'
		self.node['remapValue'] = 'rvn'
		self.node['reverse'] = 'rvs'
		self.node['revolve'] = 'rvl'
		self.node['sampler'] = 'spl'
		self.node['samplerInfo'] = 'smp'
		self.node['sculpt'] = 'scp'
		self.node['scaleConstraint'] = 'scc'
		self.node['setRange'] = 'srn'
		self.node['skinCluster'] = 'scl'
		self.node['smoothCurve'] = 'scv'
		self.node['smoothProxy'] = 'prx'
		self.node['softMod'] = 'smd'
		self.node['subCurve'] = 'sbc'
		self.node['subSurface'] = 'sbs'
		self.node['surface'] = 'srf'
		self.node['surfPts'] = 'srp'
		self.node['surfacePoints'] = 'srp'
		self.node['surfaceSkin'] = 'skn'
		self.node['tangentConstraint'] = 'tgc'
		self.node['transform'] = 'xfm'
		self.node['uniformRebuild'] = 'urb'
		self.node['unitConversion'] = 'ucv'
		self.node['vectorProduct'] = 'vpn'
		self.node['wire'] = 'wir'
		self.node['wrap'] = 'wrp'
		
	def getName(self,side='',part='',optSide='',subPart='',node='',optSideIndex=1,partIndex=1,subPartIndex=1):
		'''
		Return a valid control name based on the provided input argument values
		@param side: Side component of the name
		@type side: str
		@param part: Part component of the name
		@type part: str
		@param optSide: Optional side component of the name
		@type optSide: str
		@param subPart: Optional sub-part component of the name
		@type subPart: str
		@param node: Node type component of the name
		@type node: str
		@param optSideIndex: Optional side index of the name
		@type optSideIndex: int
		@param partIndex: Part index of the name
		@type partIndex: int
		@param subPartIndex: Optional sub-part index of the name
		@type subPartIndex: int
		'''
		# Check input arguments
		if not self.side.has_key(side): raise UserInputError('Invalid side ("'+side+'") provided!')
		if not self.part.has_key(part): raise UserInputError('Invalid part name ("'+part+'") provided!')
		if not self.node.has_key(node): raise UserInputError('Invalid node type ("'+node+'") provided!')
		if optSide:
			if not self.side.has_key(optSide): raise UserInputError('Invalid otional side ("'+optSide+'") provided!')
		if subPart:
			if not self.subPart.has_key(subPart): raise UserInputError('Invalid sub-part name ("'+subPart+'") provided!')
		
		#---------------------
		# Get index variables
		optSideInd = str(optSideIndex)
		if optSideIndex < 10: optSideInd = '0'+optSideInd
		partInd = str(partIndex)
		if partIndex < 10: partInd = '0'+partInd
		subPartInd = str(subPartIndex)
		if subPartIndex < 10: subPartInd = '0'+subPartInd
		
		# Build name string1.00
		#-------------------
		# Side
		if side:
			nameStr = self.side[side]
			nameStr += self.delineator # -
		# Part name
		if part:
			nameStr += self.part[part]
			nameStr += partInd
			nameStr += self.delineator # -
		# Optional Side
		if optSide:
			nameStr += self.side[optSide]
			nameStr += optSideInd
			nameStr += self.delineator # -
		# Sub part name
		if subPart:
			nameStr += self.subPart[subPart]
			nameStr += subPartInd
			nameStr += self.delineator # -
		# Node type
		if node: nameStr += self.node[node]
		
		return nameStr
	
	def isValid(self,name):
		'''
		Compare a name string against the naming convention string patterns
		@param name: Name string to compare against naming convention
		@type name: str
		'''
		# Check name
		nameElem = name.split(self.delineator)
		nameStrCount = len(nameElem)
		if nameStrCount < self.elemCount[0]:
			print 'Name element count ('+str(nameStrCount)+') is lower than the minimum ('+str(self.elemCount[0])+') expected by the naming conventions!'
			return False
		if nameStrCount > self.elemCount[1]:
			print 'Name element count ('+str(nameStrCount)+') is higher than the maximum ('+str(self.elemCount[1])+') expected by the naming conventions (3-5)!'
			return False
		
		# Check prefix
		if nameElem[0] != re.search(self.namePattern[0],nameElem[0]).group(0):
			print 'Prefix string ("'+nameElem[0]+'") does not match naming convention pattern (xx)!'
			return False
		# Check part
		if nameElem[1] != re.search(self.namePattern[1],nameElem[1]).group(0):
			print 'Part string ("'+nameElem[1]+'") does not match naming convention pattern (xxx00)!'
			return False
		# Check optional side / sub part
		if nameStrCount > 3:
			if nameElem[2] != re.search(self.namePattern[2],nameElem[2]).group(0):
				print 'OptinalSide/SubPart string ("'+nameElem[2]+'") does not match naming convention pattern (xx00)!'
				return False
		if nameStrCount > 4:
			if nameElem[3] != re.search(self.namePattern[2],nameElem[3]).group(0):
				print 'OptinalSide/SubPart string ("'+nameElem[3]+'") does not match naming convention pattern (xx00)!'
				return False
		# Check suffix
		if nameElem[-1] != re.search(self.namePattern[3],nameElem[-1]).group(0):
			print 'Suffix string ("'+nameElem[-1]+'") does not match naming convention pattern (xxx)!'
			return False
		
		# Build regular expression match string
		regExpStr = self.namePattern[0]+self.delineator			# Prefix: Side
		regExpStr += self.namePattern[1]+self.delineator		# Part
		if nameStrCount > 3:
			regExpStr += self.namePattern[2]+self.delineator	# OptionalSide / SubPart
		if nameStrCount > 4:
			regExpStr += self.namePattern[2]+self.delineator	# OptionalSide / SubPart
		regExpStr += self.namePattern[-1]				# Suffix: NodeType
		
		# Match name to expression string
		match = re.search(regExpStr,name)
		if not name == match.group(0):
			print 'Name string pattern does not match naming convention!'
			return False
		
		# Return result
		return True
	
	def appendName(self,name='',appendString='',stripNameSuffix=False,trimName=False):
		'''
		Return a string name based on an original name and an append string. There are options to 
		maintain string element count to satisfy the naming convention rules.
		@param name: Original name string to append to
		@type name: str
		@param appendString: String to append to the original name string
		@type appendString: str
		@param stripNameSuffix: Automatically strip the suffix from the original name string
		@type stripNameSuffix: bool
		@param trimName: Maintain string element length to fit within naming convention bounds. This will remove string elements from the original name if necessary.
		@type trimName: bool
		'''
		# Check name string
		nameElem = name.split(self.delineator)
		nameStrCount = len(nameElem)
		if stripNameSuffix and (nameStrCount > 1): nameStrCount -= 1
		# Check append string
		appendElem = appendString.split(self.delineator)
		appendStrCount = len(appendElem)
		
		# Determine string intersection point
		if trimName and (nameStrCount + appendStrCount) > self.elemCount[1]:
			maxNameIndex = self.elemCount[1] - appendStrCount
		else:	maxNameIndex = nameStrCount
		
		# Build new name string
		newName = ''
		for i in range(maxNameIndex):
			newName += nameElem[i]+self.delineator
		for i in range(appendStrCount-1):
			newName += appendElem[i]+self.delineator
		newName += appendElem[-1]
		
		# Return new name
		return newName
	
	def stripSuffix(self,name,delineator=''):
		'''
		Return the portion of name minus the last element separated by the name delineator.
		Useful for determining a name prefix from an existing object name.
		@param name: String name to strip the suffix from
		@type name: str
		@param delineator: String delineator to split the string name with. If default will inherit the class delineator string.
		@type delineator: str
		'''
		# Determine string delineator
		if not delineator: delineator = self.delineator
		# Check for delineator in name
		if not name.count(delineator): return name
		# Determine name suffix
		suffix = name.split(self.delineator)[-1]
		# Remove suffix
		newName = name.replace(self.delineator+suffix,'')
		# Return result
		return newName
	
	def stringIndex(self,index,padding=2):
		'''
		Return the string equivalent for the specified iteger index.
		@param index: The index to get the string equivalent for
		@type index: int
		@param padding: The number of characters for the index string
		@type padding: int
		'''
		# Convert to string
		strInd = str(index)
		# Prepend padding
		for i in range(padding-len(strInd)): strInd = '0'+strInd
		# Return string result
		return strInd
