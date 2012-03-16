import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import random

def list_removeDuplicates(dupList):
	'''
	list_removeDuplicates(dupList): return a copy of list with all trailing duplicates removed.
	@param dupList: The list to strip duplicates from
	@type dupList: list
	'''
	returnList = []
	[returnList.append(i) for i in dupList if not returnList.count(i)]
	return returnList
	
def dict_orderedKeyListFromValues(sortDict):
	'''
	dict_orderedKeyListFromValues(dict): return a list of keys from dict, ordered based on their values
	@param sortDict: The dictionary to construct list from
	@type sortDict: dict
	'''
	sortList = []
	[sortList.append((item[1],item[0])) for item in sortDict.items()]
	sortList.sort()
	returnList = []
	[returnList.append(val[1]) for val in sortList]
	return returnList
	
def dict_orderedValueListFromKeys(sortDict):
	'''
	dict_orderedValueListFromKeys(dict): return a list of values from dict, ordered based on their keys
	@param sortDict: The dictionary to construct list from
	@type sortDict: dict
	'''
	# Get ordered key list
	sortKeys = sortDict.keys()
	sortKeys.sort()
	# Get value list from key list
	returnList = []
	[returnList.append(sortDict[key]) for key in sortKeys]
	return returnList

def shuffleList(origList):
	'''
	Return a shuffled version of the input list.
	shuffledList = shuffleList(origList)
	@param origList: The list to shuffle
	@type origList: list
	'''
	shuffledList = []
	if not origList: return shuffledList
	#generate a random list
	for i in range(0, len(origList), 1):
		#pick a random number
		rand = random.randint(0, len(origList)-1)
		#put that value into shuffle
		shuffledList.append(origList[rand])
		#remove that item from the list
		origList.remove(origList[rand])
	return shuffledList

def flattenList(listToFlatten):
	'''
	Return a flattened version of the input list. flatList = flattenList(listToFlatten)
	@param listToFlatten: The list to flatten
	@type listToFlatten: list
	'''
	elems = []
	order = []
	for i in listToFlatten :
		if type(i) == list or type(i) == tuple: listToFlatten.extend(i)
		else: elems.append(i)
	return elems

def swapKeyValuePairs(dictionary):
	'''
	Swap the key/value pairs of the input dictionary.
	Usefull if you need to get a dictionary key by value.
	@param dictionary: Dictionary to swap key/value pairs for
	@type dictionary: dict
	'''
	if type(dictionary) != dict: raise UserInputError('Input variable is not a valid dictionary!')
	returnDict = {}
	for value in dictionary.iterkeys(): returnDict[dictionary[value]] = value
	return returnDict

