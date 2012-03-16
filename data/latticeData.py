import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import deformerData

# Create exception class
class UserInputError(Exception): pass

###############################################################
#<OPEN>
#<CLASS NAME>
#		LatticeData
#</CLASS NAME>
#
#<DESCRIPTION>
#		Data Class for lattice (FFD) deformer data.
#</DESCRIPTION>
#
#<USAGE>
#		lattice1Data = DeformerData('lattice1')
#		lattice1Data.save('/home/$USER/lattice1.pkl')
#		newLatticeData = DeformerData.load('/home/$USER/lattice1.pkl')
#</USAGE>
#
#<CLOSE>
#############################################################

class LatticeData( deformerData.DeformerData ):
	'''
	LatticeData class object.
	'''
	# INIT
	def __init__(self,lattice=''):
		
		# Escape
		if not lattice: return
		
		# Verify node
		if not mc.objExists(lattice):
			raise UserInputError('Lattice deformer '+lattice+' does not exists! No influence data recorded!!')
		objType = mc.objectType(lattice)
		if objType == 'transform':
			lattice = mc.listRelatives(lattice,s=True,ni=True)[0]
			objType = mc.objectType(lattice)
		if objType == 'lattice':
			lattice = mc.listConnections(lattice+'.latticeOutput',s=False,d=True,type='ffd')[0]
			objType = mc.objectType(lattice)
		if objType != 'ffd':
			raise UserInputError('Object '+lattice+' is not a vaild lattice deformer! Incorrect class for node type '+objType+'!!')
		
		# Execute super class initilizer
		super(LatticeData, self).__init__(lattice)
		
		#===================
		# Get Deformer Data
		self.local = mc.getAttr(lattice+'.local')
		self.outside = mc.getAttr(lattice+'.outsideLattice')
		self.falloff = mc.getAttr(lattice+'.outsideFalloffDist')
		self.resolution = mc.getAttr(lattice+'.usePartialResolution')
		self.partialResolution = mc.getAttr(lattice+'.partialResolution')
		self.freeze = mc.getAttr(lattice+'.freezeGeometry')
		self.localInfluenceS = mc.getAttr(lattice+'.localInfluenceS')
		self.localInfluenceT = mc.getAttr(lattice+'.localInfluenceT')
		self.localInfluenceU = mc.getAttr(lattice+'.localInfluenceU')
		
		# Get Input Lattice and Base
		self.latticeShape = mc.listConnections(lattice+'.deformedLatticePoints')[0]
		self.lattice = mc.listRelatives(self.latticeShape,p=True)[0]
		self.latticeBaseShape = mc.listConnections(lattice+'.baseLatticeMatrix')[0]
		self.latticeBase = mc.listRelatives(latticeBase,p=True)[0]
		
		# Get Lattice Data
		self.sDivisions = mc.getAttr(self.latticeShape+'.sDivisions')
		self.tDivisions = mc.getAttr(self.latticeShape+'.tDivisions')
		self.uDivisions = mc.getAttr(self.latticeShape+'.uDivisions')
		self.latticeXform = mc.xform(self.lattice,q=True,ws=True,m=True)
		
		# Get Lattice Base Data
		self.baseXform = mc.xform(self.latticeBase,q=True,ws=True,m=True)
		
	def rebuild(self):
		'''
		Rebuild the lattice deformer from the recorded deformerData
		'''
		# Rebuild deformer
		ffd = mc.lattice(self.getMemberList(),n=self.deformerName)
		lattice = ffd[0]
		latticeShape = ffd[1]
		latticeBase = ffd[2]
		
		# Set Deformer Attributes
		mc.setAttr(lattice+'.local',self.local)
		mc.setAttr(lattice+'.outsideLattice',self.outside)
		mc.setAttr(lattice+'.outsideFalloffDist',self.falloff)
		mc.setAttr(lattice+'.usePartialResolution',self.resolution)
		mc.setAttr(lattice+'.partialResolution',self.partialResolution)
		mc.setAttr(lattice+'.freezeGeometry',self.freeze)
		mc.setAttr(lattice+'.localInfluenceS',self.localInfluenceS)
		mc.setAttr(lattice+'.localInfluenceT',self.localInfluenceT)
		mc.setAttr(lattice+'.localInfluenceU',self.localInfluenceU)
		
		# Set Lattice Shape Attributes
		mc.setAttr(latticeShape+'.sDivisions',self.sDivisions)
		mc.setAttr(latticeShape+'.tDivisions',self.tDivisions)
		mc.setAttr(latticeShape+'.uDivisions',self.uDivisions)
		
		# Restore World Transform Data
		mc.xform(lattice,ws=True,m=self.latticeXform)
		mc.xform(latticeBase,ws=True,m=self.baseXform)
		
		# Return result
		return lattice
