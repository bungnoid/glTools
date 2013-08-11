###############################################################
#<OPEN>
#<FILE NAME>
#		arrayUtilities.py
#</FILE NAME>
#
#<VERSION HISTORY>
#		04/02/08 : Grant Laker : initial release
#</VERSION HISTORY>
#
#<DESCRIPTION>
#		A collection of utility scripts for with lists and dictionaries
#</DESCRIPTION>
#
#<DEPARTMENTS>
#		<+> rig
#</DEPARTMENTS>
#
#<KEYWORDS>
#		<+>array
#		<+>list
#		<+>dictionary
#</KEYWORDS>
#
#<APP>
#		Maya
#</APP>
#
#<APP VERSION>
#	 	8.5
#</APP VERSION>
#
#<CLOSE>
#############################################################

import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import random

# Create exception class
class UserInputError(Exception): pass

class ArrayUtilities(object):
	'''
	Class: ArrayUtilities
	A collection of utility functions for working with python lists and dictionaries
	'''
	
	def __init__(self): pass

	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		list_removeDuplicates
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Return a copy of the input list with all trailing duplicates removed.
	#</DESCRIPTION>
	#
	#<USAGE>
	#		list_removeDuplicates([1,1,1,1,2,2,2,2,3,3,3,3])
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def list_removeDuplicates(self,dupList):
		"""
		list_removeDuplicates(dupList): return a copy of list with all trailing duplicates removed.
		
		@param dupList: The list to strip duplicates from
		@type dupList: list
		"""
		returnList = []
		[returnList.append(i) for i in dupList if not returnList.count(i)]
		return returnList
		
	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		dict_orderedKeyListFromValues
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Return a list of keys from a dictionary, ordered based on their values.
	#</DESCRIPTION>
	#
	#<USAGE>
	#		orderedKeyList = dict_orderedKeyListFromValues(dict)
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def dict_orderedKeyListFromValues(self,sortDict):
		"""
		dict_orderedKeyListFromValues(dict): return a list of keys from dict, ordered based on their values
		
		@param sortDict: The dictionary to construct list from
		@type sortDict: dict
		"""
		sortList = []
		[sortList.append((item[1],item[0])) for item in sortDict.items()]
		sortList.sort()
		returnList = []
		[returnList.append(val[1]) for val in sortList]
		return returnList
			
	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		dict_orderedValueListFromKeys
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Return a list of values from a dictionary, ordered based on their keys.
	#</DESCRIPTION>
	#
	#<USAGE>
	#		orderedValueList = dict_orderedValueListFromKeys(dict)
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def dict_orderedValueListFromKeys(self,sortDict):
		"""
		dict_orderedValueListFromKeys(dict): return a list of values from dict, ordered based on their keys
		
		@param sortDict: The dictionary to construct list from
		@type sortDict: dict
		"""
		# Get ordered key list
		sortKeys = sortDict.keys()
		sortKeys.sort()
		# Get value list from key list
		returnList = []
		[returnList.append(sortDict[key]) for key in sortKeys]
		return returnList
	
	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		shuffleList
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Return a shuffled version of the input list
	#</DESCRIPTION>
	#
	#<USAGE>
	#		shuffledList = shuffleList(origList)
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def shuffleList(self,origList):
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
	
	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		flattenList
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Return a flattened version of the input list
	#</DESCRIPTION>
	#
	#<USAGE>
	#		flatList = flattenList( listToFlatten )
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def flattenList(self,listToFlatten):
		'''
		Return a flattened version of the input list
		flatList = flattenList( listToFlatten )
		
		@param listToFlatten: The list to flatten
		@type listToFlatten: list
		'''
		elems = []
		order = []
		for i in listToFlatten :
			if type(i) == list or type(i) == tuple: listToFlatten.extend(i)
			else: elems.append(i)
		return elems
	
	###############################################################
	#<OPEN>
	#<PROC NAME>
	#		swapKeyValuePairs
	#</PROC NAME>
	#
	#<DESCRIPTION>
	#		Swap the key/value pairs of the input dictionary.
	#		Usefull if you need to get a dictionary key by value.
	#</DESCRIPTION>
	#
	#<USAGE>
	#		flatList = flattenList( listToFlatten )
	#</USAGE>
	#
	#<CLOSE>
	#############################################################
	
	def swapKeyValuePairs(self,dictionary):
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

