import maya.cmds as mc
import maya.mel as mm

def add(	srfPtList=[],
			surface="",
			anchorType="transform",
			rotate=1,
			normalAttr=0,
			tanAttr=0,
			surfPtsNode='',
			maintainOffset=1,
			scaleAttr='',
			namePrefix=''	):
	'''
	'''
	return_list = mm.eval( 'surfPts_add( '+ str(srfPtList).replace("['",'{"').replace("']",'"}').replace("'",'"') +', "'+ surface +'", "'+ str(anchorType) +'", '+ str(rotate) +', '+ str(normalAttr) +', '+ str(tanAttr) +', "'+ surfPtsNode +'", '+ str(maintainOffset) +', "'+ scaleAttr +'", "'+ namePrefix +'")' )
	return return_list

def gen(	surface,
			targets=[]	):
	'''
	'''
	return_list = mm.eval( 'surfPts_gen( "'+ surface +'", '+ str(targets).replace("[u","{").replace("[","{").replace("]","}").replace("'",'"') +')' )
	return return_list


