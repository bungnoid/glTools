import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

import utilities
import glTools.utils.component
import glTools.utils.selection

#import OpenGL.GL
#import OpenGL.GLU

###########################################################
#<OPEN>
#<Class NAME>
#			surfaceSkinEditInfMembershipCTX
#</Class NAME>
#
#<USAGE>
#			surfaceSkinEditInfMembershipCTX()
#</USAGE>
#<CLOSE>
###########################################################

class SurfaceSkinEditInfMembershipCTX( object ):
	
	#------
	# INIT
	#------------------------------
	
	def __init__(self,name):
		
		self.userSelection = []
		self.cursor = 'crossHair'
		self.dragStart = [0,0]
		self.dragEnd = [0,0]
		self.dragComponentSelection = []
		self.dragObjectSelection = []
		self.modifier = 'none'
		self.context = name+'_CTX'
		
		if mc.draggerContext(self.context,q=1,ex=1):
			mc.deleteUI(self.context)
		self.context = mc.draggerContext(self.context, pressCommand=name+'.onPress()', dragCommand=name+'.onDrag()', releaseCommand=name+'.onRelease()', cursor=self.cursor )
	
	#----------------
	# Enable Context
	#------------------------------------
	
	def enable(self):
		
		# Get user selection
		self.userSelection = mc.ls(sl=1)
		mc.select(cl=1)
		
		# Invoke edit membership context
		mc.setToolTo(self.context)
		
		# Hilite members for current influence
		self.hiliteMembers()
		
		print('Edit Membership context enabled!')
		
	#-----------------
	# Disable Context
	#------------------------------------
	
	def disable(self):
		
		# Set default context
		if mc.currentCtx() == self.context:
			mc.setToolTo('moveSuperContext')
		
			# Restore user selection
			if len(self.userSelection):
				mc.select(self.userSelection)
			else:
				mc.select(cl=1)
			
			# Clear user selection
			self.userSelection = []
			
			print('Edit Membership context disabled!')
	
	#---------------
	# Context Press
	#------------------------------------
	
	def onPress(self):
		
		pressPosition = mc.draggerContext(self.context,q=1,anchorPoint=1)
		dragPosition = pressPosition
		self.dragStart = [pressPosition[0],pressPosition[1]]
	
	#--------------
	# Context Drag
	#------------------------------------
	
	def onDrag(self):
		
		dragPosition = mc.draggerContext(self.context,q=1,dragPoint=1)
		self.dragEnd = [dragPosition[0],dragPosition[1]]
		
		'''
		# Draw drag region on viewport overlay
		view = OpenMayaUI.M3dView.active3dView()
		view.refresh(1,1)
		view.beginOverlayDrawing()
		view.clearOverlayPlane()
		
		# Setup orthographic projection matrix
		OpenGL.GL.glMatrixMode(OpenGL.GL.GL_PROJECTION)
		OpenGL.GL.glLoadIdentity()
		OpenGL.GLU.gluOrtho2D(0.0,view.portWidth(),0.0,view.portHeight())
		OpenGL.GL.glMatrixMode(OpenGL.GL.GL_MODELVIEW)
		OpenGL.GL.glLoadIdentity()
		
		# Line draw setting
		OpenGL.GL.glLineWidth(1.0)
		OpenGL.GL.glColor3f(0.4,0.4,0.4) # Set line colour
		OpenGL.GL.glEnable(OpenGL.GL.GL_LINE_STIPPLE)
		
		# Draw triangle
		OpenGL.GL.glBegin(OpenGL.GL.GL_LINE_LOOP)
		OpenGL.GL.glVertex2i(int(self.dragStart[0]),int(self.dragStart[1]))
		OpenGL.GL.glVertex2i(int(dragPosition[0]),int(self.dragStart[1]))
		OpenGL.GL.glVertex2i(int(dragPosition[0]),int(dragPosition[1]))
		OpenGL.GL.glVertex2i(int(self.dragStart[0]),int(dragPosition[1]))
		
		# Finished drawing
		OpenGL.GL.glEnd()
		view.endOverlayDrawing()
		'''
	
	#-----------------
	# Context Release
	#------------------------------------
	
	def onRelease(self):
		
		# Get component selection from drag region
		dragStartX = OpenMaya.MScriptUtil()
		dragStartX.createFromInt(int(self.dragStart[0]))
		dragStartY = OpenMaya.MScriptUtil()
		dragStartY.createFromInt(int(self.dragStart[1]))
		dragEndX = OpenMaya.MScriptUtil()
		dragEndX.createFromInt(int(self.dragEnd[0]))
		dragEndY = OpenMaya.MScriptUtil()
		dragEndY.createFromInt(int(self.dragEnd[1]))
		OpenMaya.MGlobal.selectFromScreen(dragStartX.asShortPtr(),dragStartY.asShortPtr(),dragEndX.asShortPtr(),dragEndY.asShortPtr(),OpenMaya.MGlobal.kReplaceList)
		
		# Get component selection
		self.dragComponentSelection = mc.filterExpand(ex=1,sm=(28,31))
		# Get object selection
		self.dragObjectSelection = mc.ls(sl=1,type='transform')
		# Deselect objects
		if len(self.dragObjectSelection): mc.select(self.dragObjectSelection,d=1)
		
		# Get context modifier
		self.modifier = mc.draggerContext(self.context,q=1,modifier=1)
		
		# Adjust influence membership
		if type(self.dragComponentSelection) == list:
			# Add components to membership
			if self.modifier == 'shift': self.addInfluenceMembership()
			# Remove components from membership
			elif self.modifier == 'ctrl': self.removeInfluenceMembership()
		
		# Enable component selection for objects
		affectedGeo = []
		if mc.window('surfaceSkin_editMembershipToolUI',q=1,ex=1):
			surfaceSkinNode = mc.optionMenuGrp('ssEditInfMemberToolSurfaceSkin_OMG',q=1,v=1)
			affectedGeo = surfaceSkin_utilities().getAffectedGeometry(surfaceSkinNode).keys()
		if type(self.dragObjectSelection):
			for obj in self.dragObjectSelection:
				objType = mc.objectType(glTools.utils.selection.getShapes(obj)[0])
				if (objType == 'mesh') or (objType == 'nurbsSurface') or (objType == 'nurbsCurve'):
					if affectedGeo.count(obj):
						glTools.utils.selection.enableObjectVertexSelection(obj)
		
		# Hilite members
		self.hiliteMembers()
	
	#-------------------------
	# Add Influence Membership
	#------------------------------------
	
	def addInfluenceMembership(self):
		
		# Check Context Status
		if mc.currentCtx() != self.context: return
		# Check UI Status
		if not mc.window('surfaceSkin_editMembershipToolUI',q=1,ex=1): return
		
		# Get surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp('ssEditInfMemberToolSurfaceSkin_OMG',q=1,v=1)
		# Get influence from list
		influence = mc.textScrollList('ssEditInfMemberToolInfluence_TSL',q=1,si=1)[0] # Get first selected item in list
		# Get prebind option
		calcPreBind = mc.checkBoxGrp('ssEditInfMemberToolPrebind_CBG',q=1,v1=1)
		
		# Add influence membership
		if type(self.dragComponentSelection) == list:
			componentList = glTools.utils.component.getComponentIndex(self.dragComponentSelection)
			for obj in componentList.keys():
				surfaceSkin_utilities().setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,0,calcPreBind,mode=1)
	
	#-------------------------
	# Remove Influence Membership
	#------------------------------------
	
	def removeInfluenceMembership(self):
		
		# Check Context Status
		if mc.currentCtx() != self.context: return
		# Check UI Status
		if not mc.window('surfaceSkin_editMembershipToolUI',q=1,ex=1): return
		
		# Get surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp('ssEditInfMemberToolSurfaceSkin_OMG',q=1,v=1)
		# Get influence from list
		influence = mc.textScrollList('ssEditInfMemberToolInfluence_TSL',q=1,si=1)[0] # Get first selected item in list
		
		# Remove influence membership
		if type(self.dragComponentSelection) == list:
			componentList = glTools.utils.component.getComponentIndex(self.dragComponentSelection)
			for obj in componentList.keys():
				surfaceSkin_utilities().setSurfaceCoordArray(obj,componentList[obj],influence,surfaceSkinNode,mode=3)
	
	#-----------------
	# Hilite Members
	#------------------------------------
	
	def hiliteMembers(self):
		
		# Check Context Status
		if mc.currentCtx() != self.context: return
		# Check UI Status
		if not mc.window('surfaceSkin_editMembershipToolUI',q=1,ex=1): return
		
		# Get surfaceSkin node
		surfaceSkinNode = mc.optionMenuGrp('ssEditInfMemberToolSurfaceSkin_OMG',q=1,v=1)
		# Get influence from list
		influence = mc.textScrollList('ssEditInfMemberToolInfluence_TSL',q=1,si=1)[0] # Get first selected item in list
		
		# Get affected geometry and components
		affectedGeo = surfaceSkin_utilities().getAffectedGeometry(surfaceSkinNode).keys()
		influenceMembers = surfaceSkin_utilities().getInfluenceMembership(influence,surfaceSkinNode,[],0)
		
		# Hilite component members
		if len(influenceMembers):
			for geo in affectedGeo: glTools.utils.selection.enableObjectVertexSelection(geo)
			mc.select(influenceMembers)

# Create Context Object (Global)
#ssEditInfluenceMembershipCTX = SurfaceSkinEditInfMembershipCTX('ssEditInfluenceMembershipCTX')