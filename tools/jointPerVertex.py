import maya.cmds as mc

import glTools.utils.base
import glTools.utils.stringUtils

class UIError(Exception): pass

def jointPerVertex(ptList,orientSurface='',prefix='',suffix='jnt'):
	'''
	'''
	# Generate position list from input point
	posList = []
	for pt in ptList: posList.append(glTools.utils.base.getPosition(pt))
	
	# Create joints
	jntList = []
	for i in range(len(posList)):
		
		# Clear selection
		mc.select(cl=1)
		
		# Get string index
		strInd = glTools.utils.stringUtils.stringIndex(i+1,2)
		
		# Create joint
		jnt = mc.joint(n=prefix+'_'+strInd+'_'+suffix)
		# Position joint
		mc.move(posList[i][0],posList[i][1],posList[i][2],jnt,ws=True,a=True)
		
		# Orient joint
		if mc.objExists(orientSurface): mc.delete(mc.normalConstraint(orientSurface,jnt))
		
		# Append return list
		jntList.append(jnt)
	
	# Return Result
	return  jntList

def jointPerVertexUI():
	'''
	UI for jointPerVertex()
	'''
	# Window
	win = 'jntPerVtxUI'
	if mc.window(win,q=True,ex=1): mc.deleteUI(win)
	win = mc.window(win,t='Create Joint Per Vertex')
	
	# Layout
	cl = mc.columnLayout()
	
	# UI Elements
	prefixTFG = mc.textFieldGrp('jntPerVtx_prefixTFG',label='Prefix', text='')
	suffixTFG = mc.textFieldGrp('jntPerVtx_suffixTFG',label='Suffix', text='jnt')
	oriSurfaceTFB = mc.textFieldButtonGrp('jntPerVtx_oriSurfaceTFB',label='Orient Surface',text='',buttonLabel='Load Selected')
	
	# Buttons
	createB = mc.button('jntPerVtx_createB',l='Create',c='glTools.tools.jointPerVertex.jointPerVertexFromUI(False)')
	cancelB = mc.button('jntPerVtx_cancelB',l='Cancel',c='mc.deleteUI("'+win+'")')
	
	# UI callbacks
	mc.textFieldButtonGrp(oriSurfaceTFB,e=True,bc='glTools.ui.utils.loadObjectSel("'+oriSurfaceTFB+'","")')
	
	# Show Window
	mc.showWindow(win)
	
def jointPerVertexFromUI(close=False):
	'''
	Execute jointPerVertex() from UI
	'''
	# Window
	win = 'jntPerVtxUI'
	if not mc.window(win,q=True,ex=1): raise UIError('jointPerVertex UI does not exist!!')
	
	# Get UI data
	pre = mc.textFieldGrp('jntPerVtx_prefixTFG',q=True,text=True)
	suf = mc.textFieldGrp('jntPerVtx_suffixTFG',q=True,text=True)
	oriSurface = mc.textFieldButtonGrp('jntPerVtx_oriSurfaceTFB',q=True,text=True)
	
	# Execute command
	ptList = mc.ls(sl=1,fl=True)
	jointPerVertex(ptList,orientSurface=oriSurface,prefix=pre,suffix=suf)
	
	# Cleanup
	if close: mc.deleteUI(win)
