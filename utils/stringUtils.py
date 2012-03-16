import math

def stripSuffix(name,delineator='_'):
	'''
	Return the portion of name minus the last element separated by the name delineator.
	Useful for determining a name prefix from an existing object name.
	@param name: String name to strip the suffix from
	@type name: str
	@param delineator: String delineator to split the string name with. If default will inherit the class delineator string.
	@type delineator: str
	'''
	# Check for delineator in name
	if not name.count(delineator): return name
	# Determine name suffix
	suffix = name.split(delineator)[-1]
	# Remove suffix
	result = name.replace(delineator+suffix,'')
	# Return result
	return result
		
def stringIndex(index,padding=2):
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
	
def alphaIndex(index,upper=True):
	'''
	Return the alpha string equivalent for the specified iteger index.
	@param index: The index to get the alpha string equivalent for
	@type index: int
	@param upper: Return the result in upper case form
	@type upper: bool
	'''
	# Define alpha list
	alpha = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
		
	# Build alpha index
	alphaInd = alpha[index % 26]
	depth = index / 26.0
	while int(math.floor(depth)):
		alphaInd = alpha[depth % 26] + alphaInd
		depth = depth / 26.0
	
	# Check case
	if upper: alphaInd = alphaInd.upper()
	
	# Return result
	return alphaInd
