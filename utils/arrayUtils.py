import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import random
import types

def removeDuplicates(seq):
	'''
	Remove list duplicates and maintain original order
	@param seq: The list to remove duplicates for
	@type seq: list
	'''
	seen = set()
	seen_add = seen.add
	return [ x for x in seq if not (x in seen or seen_add(x))]

def dict_orderedKeyListFromValues(d):
	'''
	Return a list of keys from dict, ordered based on their values
	@param d: The dictionary to construct list from
	@type d: dict
	'''
	return [ i[0] for i in sorted(d.items(), key=lambda (k, v): v) ]
	
def dict_orderedValueListFromKeys(d):
	'''
	Return a list of dictionary values, ordered based on their keys
	@param d: The dictionary to construct list from
	@type d: dict
	'''
	return [ d[key] for key in sorted(d.keys()) ]

def flattenList(listToFlatten):
	'''
	Return a flattened version of the input list.
	@param listToFlatten: The list to flatten
	@type listToFlatten: list
	'''
	elems = []
	for i in listToFlatten:
		if isinstance(i,types.ListType): elems.extend(i)
		else: elems.append(i)
	return elems

