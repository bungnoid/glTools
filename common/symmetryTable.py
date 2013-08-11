import maya.cmds as mc
import copy

class SymmetryTable(object):
	
	def __init__(self):
		
		self.symTable = []
		self.asymTable = []
		self.positiveVertexList = []
		self.positiveIndexList = []
		self.negativeVertexList = []
		self.negativeIndexList = []
		
	def buildSymTable(self,mesh,axis=0,tol=0.001,usePivot=False):
		'''
		Build symmetry table for specified mesh
		@param mesh: Mesh to build symmetry table for
		@type mesh: str
		@param axis: Axis to check for symmetry across
		@type axis: int
		@param tol: Distance tolerance for finding symmetry pairs
		@type tol: float
		@param usePivot: Use the object pivot
		@type usePivot: bool
		'''
		# Initialize list variables
		aNegVerts=[]
		aPosVerts=[]
		aNonSymVerts=[]
		aPosVertsInt=[]
		aNegVertsInt=[]
		aNegVertTrans=[]
		aPosVertTrans=[]
		aVtxTrans=[]
		aVtx2Trans=[]
		
		# Set constants
		mAxisInd = axis
		axis2Ind = (mAxisInd + 1) % 3
		axis3Ind = (mAxisInd + 2) % 3
		midOffsetTol = -0.0000001
		
		# Reset counter
		vertCounter = 0
		
		# Check pivot
		if usePivot:
			aVtxTrans = mc.xform(mesh,q=True,ws=True,rp=True)
			mid = aVtxTrans[mAxisInd]
		else:
			meshParent = mesh
			if mc.objectType(meshParent) != 'transform':
				meshParent = mc.listRelatives(mesh,p=True)[0]
			bBox = mc.xform(meshParent,q=True,ws=True,boundingBox=True)
			mid = bBox[mAxisInd] + ((bBox[mAxisInd+3] - bBox[mAxisInd])/2)
		
		# Get total verts
		totVtx = mc.polyEvaluate(mesh,v=True)
		# Initialize abSymTable
		abSymTable = range(int(totVtx))
		
		# Determin pos and neg verts
		for i in range(totVtx):
			vtx = mesh+'.vtx['+str(i)+']'
			aVtxTrans = mc.xform(vtx,q=True,ws=True,translation=True)
			midOffset = aVtxTrans[mAxisInd] - mid
			# Check for pos/neg position
			if midOffset >= midOffsetTol:
				aPosVerts.append(vtx)
				aPosVertsInt.append(i)
				aPosVertTrans.append(aVtxTrans[mAxisInd])
			else:
				if midOffset < midOffsetTol:
					aNegVerts.append(vtx)
					aNegVertsInt.append(i)
					aNegVertTrans.append(aVtxTrans[mAxisInd])
		
		# Update class member variabels
		self.positiveVertexList = copy.deepcopy(aPosVerts)
		self.positiveIndexList = copy.deepcopy(aPosVertsInt)
		self.negativeVertexList = copy.deepcopy(aNegVerts)
		self.negativeIndexList = copy.deepcopy(aNegVertsInt)
		
		# Find Non-Symmetrical verts
		for i in range(len(aPosVerts)):
			vtx = aPosVerts[i]
			posOffset = aPosVertTrans[i] - mid
			if posOffset < tol:
				aPosVerts[i] = 'm'
				vertCounter+=1
				continue
			
			for j in range(len(aNegVerts)):
				if aNegVerts[j] == 'm': continue
				negOffset = mid - aNegVertTrans[j]
				if negOffset < tol:
					aNegVerts[j] = 'm'
					vertCounter+=1
					continue
				
				if abs(posOffset-negOffset) <= tol:
					aVtxTrans = mc.xform(vtx,q=True,ws=True,t=True)
					aVtx2Trans = mc.xform(aNegVerts[j],q=True,ws=True,t=True)
					test1 = aVtxTrans[axis2Ind] - aVtx2Trans[axis2Ind]
					test2 = aVtxTrans[axis3Ind] - aVtx2Trans[axis3Ind];
					if (abs(test1) < tol) and (abs(test2) < tol):
						# match
						abSymTable[aNegVertsInt[j]] = aPosVertsInt[i]
						abSymTable[aPosVertsInt[i]] = aNegVertsInt[j]
						vertCounter += 2
						aPosVerts[i] = aNegVerts[j] = 'm'
						break
		
		# Determine asymmetrical vertices
		aNonSymVerts = []
		[aNonSymVerts.append(i) for i in aPosVerts if i != 'm']
		[aNonSymVerts.append(i) for i in aNegVerts if i != 'm']
		
		if vertCounter != totVtx:
			print 'Warning: Mesh object "'+mesh+'" is not symmetrical!'
		
		# Update class member variabels
		self.symTable = abSymTable
		self.asymTable = aNonSymVerts
		
		# retuurn result
		return abSymTable
