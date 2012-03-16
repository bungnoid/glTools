###########################################################
#<OPEN>
#<KEEP_FORMAT>
#<FILE NAME>
#		rig_surf_pts.mel
#</FILE NAME>
#
#<VERSION HISTORY>
#			01/12/06 : Grant laker : Initial release
#			01/02/07 : Greg Smith 	: added surfPts_gen
#				- changed counting to start at 01 not 00
#				- changed surfPts suffix to srp
#				- added min of .001 and max of .999 instead of zero and one
#			04/10/07 : Grant Laker 	: added support for surfPts offset 
#				- surfPts_add now accepts polygon vertices and transforms
#			04/18/07 : Grant Laker	: added rig_srfPts_reset() procedure.
#			09/05/07 : Grant Laker	: Added check for existing offsetScale connection in surfPts_add().
#			11/06/07 : Grant Laker 	: Fixed bug that was clamping parameter values to 0-1, regardless of actual range
#			05/13/07 : Ramiro Gomez : Updated with altest formating
#			07/05/07 : Grant Laker : Added rig_srfPts_resetTarget() procedure
#</VERSION HISTORY>
#
#<DESCRIPTION>
#			Collection of utilities for operating on the surfPts plugin.
#</DESCRIPTION>
#
#<NOTES>
#			lidRails plugin must be loaded to access surfPts node.
#</NOTES>
#
#<REQUIRED SCRIPTS>
#			<+> channelState.mel
#</REQUIRED SCRIPTS>
#
#<REQUIRED PLUGINS>
#			<+> lidRails
#</REQUIRED PLUGINS>
#
#<DEPARTMENTS>
#                      <+> rig
#</DEPARTMENTS>
#
#<KEYWORDS>
#			<+> surfPts
#			<+> rigging
#			<+> skinning
#</KEYWORDS>
#
#<APP>
#			Maya
#</APP>
#
#<APP VERSION>
#			7.0.1, 8.5
#</APP VERSION>
#
#<CLOSE>
###########################################################
#====================================================================================================================

import maya.cmds as mc
import maya.mel as mm

###############################################################
#<OPEN>
#<PROC NAME>
#		add
#</PROC NAME>
#
#<DESCRIPTION>
#		Create surfPts node.
#</DESCRIPTION>
#
#<USAGE>
#		list_removeDuplicates([1,1,1,1,2,2,2,2,3,3,3,3])
#</USAGE>
#
#<CLOSE>
#############################################################

def add( srfPtList=[], surface="", anchorType="transform", rotate=1, normalAttr=0, tanAttr=0, surfPtsNode="", maintainOffset=1, scaleAttr="", namePrefix=""):
	
	return_list = mm.eval( 'surfPts_add( '+ str(srfPtList).replace("['",'{"').replace("']",'"}').replace("'",'"') +', "'+ surface +'", "'+ str(anchorType) +'", '+ str(rotate) +', '+ str(normalAttr) +', '+ str(tanAttr) +', "'+ surfPtsNode +'", '+ str(maintainOffset) +', "'+ scaleAttr +'", "'+ namePrefix +'")' )
	return return_list

def gen( surface, targets=[]):
	
	return_list = mm.eval( 'surfPts_gen( "'+ surface +'", '+ str(targets).replace("[u","{").replace("[","{").replace("]","}").replace("'",'"') +')' )
	return return_list


