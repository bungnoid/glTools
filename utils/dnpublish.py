import maya.mel as mm
import maya.cmds as mc

import dnpypub
import dnPubFuncs

def faceRigPubInfo(char,vidx=-1):
	'''
	Return publish information for a character face rig
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	fRig_info = dnPubFuncs.getLatestVersion( {'item':'CHARACTER:'+char.upper()+':FACE','job':'JCOM','objkind':'RIG','type':'anim','lod':1} )
	return fRig_info

def faceModelPubInfo(char,vidx=-1):
	'''
	Return publish information for a character face model
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	model_info = dnpypub.getLatestVersions( {'item':'CHARACTER:'+char.upper()+':FACE$','job':'JCOM','objkind':'MOD','type':'main','lod':'high'} )[0]
	return model_info

def expressionSculptPubInfo(char,vidx=-1):
	'''
	Return publish information for a character expression sculpt
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	sculpt_info = dnPubFuncs.getLatestVersion( {'item':'CHARACTER:'+char.upper()+':FACE:sculpt','job':'JCOM','objkind':'MOD','type':'main','lod':'high'} )
	return sculpt_info
	
def conceptSculptPubInfo(char,vidx=-1):
	'''
	Import a published character expression concept models
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	concept_info = dnPubFuncs.getLatestVersion( {'item':'CHARACTER:'+char.upper()+':FACE:concept','job':'JCOM','objkind':'MOD','type':'main','lod':'high'} )
	return concept_info
	
def importFaceRig(char,vidx=-1):
	'''
	Import a published character face rig
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	print('IMPORTING: '+char.upper()+' Face Rig')
	
	# Get face rig publish info
	fRig_info = faceRigPubInfo(char)
	fRig_idx = fRig_info['idx']
	
	# Import latest version
	dnPubFuncs.importMOD({'idx':fRig_idx,'vidx':vidx},{})
	
	# Return result
	return fRig_info['vname']
	
def importFaceModel(char,vidx=-1):
	'''
	Import a published character face model
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	print('IMPORTING: '+char.upper()+' Face Model')
	
	# Get model publish info
	model_info = faceModelPubInfo(char)
	model_idx = model_info['idx']
	
	# Import latest version
	dnPubFuncs.importMOD({'idx':model_idx,'vidx':vidx},{})
	
	# Return result
	return model_info['vname']
	
def importExpressionSculpts(char,vidx=-1):
	'''
	Import a published character face expression models
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	print('IMPORTING: '+char.upper()+' Expression Sculpts')
	
	# Get expression sculpt publish info
	sculpt_info = expressionSculptPubInfo(char)
	sculpt_idx = sculpt_info['idx']
	
	# Import latest version
	dnPubFuncs.importMOD({'idx':sculpt_idx,'vidx':vidx},{})
	
	# Return result
	return sculpt_info['vname']
	
def importConceptSculpts(char,vidx=-1):
	'''
	Import a published character expression concept models
	@param char: Character to import
	@type char: str
	@param vidx: Version Id to import. Defualt value (-1) will import the latest published version
	@type char: int
	'''
	print('IMPORTING: '+char.upper()+' Concept Sculpts')
	
	# Get concept sculpt publish info
	concept_info = conceptSculptPubInfo(char)
	concept_idx = concept_info['idx']
	
	# Import latest version
	dnPubFuncs.importMOD({'idx':concept_idx,'vidx':vidx},{})
	
	# Return result
	return concept_info['vname']
