import maya.cmds as mc

import glTools.utils.surface

def create(samplePt,pntList,weightCalc=[True,True,True],prefix=''):
	'''
	Generate the barycentric point weight setup based on the input arguments
	@param samplePt: The locator used to define the triangle sample point to generate weights for
	@type samplePt: str
	@param pntList: List of points to define triangle
	@type pntList: list
	@param weightCalc: List of booleans to define which point weights are calculated
	@type weightCalc: list
	@param prefix: String name prefix for all created nodes
	@type prefix: str
	'''
	
	# Check prefix
	if not prefix: prefix = 'barycentricPointWeight'
	
	# ========================
	# - Setup Full Area Calc -
	# ========================
	
	# Build pntFace surface
	pntFace = mc.nurbsPlane(p=(0,0,0),ax=(0,1,0),d=1,ch=False,n=prefix+'_sample_surface')[0]
	pntLoc = glTools.utils.surface.locatorSurface(pntFace,prefix=prefix)
	mc.delete(mc.pointConstraint(pntList[0],pntLoc[0]))
	mc.delete(mc.pointConstraint(pntList[1],pntLoc[1]))
	mc.delete(mc.pointConstraint(pntList[2],pntLoc[2]))
	mc.delete(mc.pointConstraint(pntList[2],pntLoc[3]))
	
	# Attach follow pt
	followLoc = mc.spaceLocator(n=prefix+'_follow_locator')[0]
	follow_cpos = mc.createNode('closestPointOnSurface',n=prefix+'_closestPointOnSurface')
	mc.connectAttr(samplePt+'.worldPosition[0]',follow_cpos+'.inPosition',f=True)
	mc.connectAttr(pntFace+'.worldSpace[0]',follow_cpos+'.inputSurface',f=True)
	mc.connectAttr(follow_cpos+'.position',followLoc+'.translate',f=True)
	
	# Calculate triArea
	triEdge1_pma = mc.createNode('plusMinusAverage',n=prefix+'_triEdge1Vec_plusMinusAverage')
	triEdge2_pma = mc.createNode('plusMinusAverage',n=prefix+'_triEdge2Vec_plusMinusAverage')
	mc.setAttr(triEdge1_pma+'.operation',2) # Subtract
	mc.setAttr(triEdge2_pma+'.operation',2) # Subtract
	mc.connectAttr(pntLoc[1]+'.worldPosition[0]',triEdge1_pma+'.input3D[0]',f=True)
	mc.connectAttr(pntLoc[0]+'.worldPosition[0]',triEdge1_pma+'.input3D[1]',f=True)
	mc.connectAttr(pntLoc[2]+'.worldPosition[0]',triEdge2_pma+'.input3D[0]',f=True)
	mc.connectAttr(pntLoc[0]+'.worldPosition[0]',triEdge2_pma+'.input3D[1]',f=True)
	
	triArea_vpn = mc.createNode('vectorProduct',n=prefix+'_triArea_vectorProduct')
	mc.setAttr(triArea_vpn+'.operation',2) # Cross Product
	mc.connectAttr(triEdge1_pma+'.output3D',triArea_vpn+'.input1',f=True)
	mc.connectAttr(triEdge2_pma+'.output3D',triArea_vpn+'.input2',f=True)
	
	triArea_dist = mc.createNode('distanceBetween',n=prefix+'_triArea_distanceBetween')
	mc.connectAttr(triArea_vpn+'.output',triArea_dist+'.point1',f=True)
	
	# =======================
	# - Setup Sub Area Calc -
	# =======================
	
	# Calculate triPt weights
	for i in range(3):
		
		# Check weight calculation (bool)
		if weightCalc[i]:
			
			# Calculate sub-TriArea
			pntEdge1_pma = mc.createNode('plusMinusAverage',n=prefix+'_pt'+str(i)+'Edge1Vec_plusMinusAverage')
			pntEdge2_pma = mc.createNode('plusMinusAverage',n=prefix+'_pt'+str(i)+'Edge2Vec_plusMinusAverage')
			mc.setAttr(pntEdge1_pma+'.operation',2) # Subtract
			mc.setAttr(pntEdge2_pma+'.operation',2) # Subtract
			mc.connectAttr(pntLoc[(i+1)%3]+'.worldPosition[0]',pntEdge1_pma+'.input3D[0]',f=True)
			mc.connectAttr(followLoc+'.worldPosition[0]',pntEdge1_pma+'.input3D[1]',f=True)
			mc.connectAttr(pntLoc[(i+2)%3]+'.worldPosition[0]',pntEdge2_pma+'.input3D[0]',f=True)
			mc.connectAttr(followLoc+'.worldPosition[0]',pntEdge2_pma+'.input3D[1]',f=True)
			
			pntArea_vpn = mc.createNode('vectorProduct',n=prefix+'_pt'+str(i)+'Area_vectorProduct')
			mc.setAttr(pntArea_vpn+'.operation',2) # Cross Product
			mc.connectAttr(pntEdge1_pma+'.output3D',pntArea_vpn+'.input1',f=True)
			mc.connectAttr(pntEdge2_pma+'.output3D',pntArea_vpn+'.input2',f=True)
			
			pntArea_dist = mc.createNode('distanceBetween',n=prefix+'_pt'+str(i)+'Area_distanceBetween')
			mc.connectAttr(pntArea_vpn+'.output',pntArea_dist+'.point1',f=True)
			
			# Divide ptArea by triArea to get weight
			pntWeight_mdn = mc.createNode('multiplyDivide',n=prefix+'_pt'+str(i)+'Weight_multiplyDivide')
			mc.setAttr(pntWeight_mdn+'.operation',2) # Divide
			mc.connectAttr(pntArea_dist+'.distance',pntWeight_mdn+'.input1X',f=True)
			mc.connectAttr(triArea_dist+'.distance',pntWeight_mdn+'.input2X',f=True)
			
			# Add weight attribute to pntLoc
			mc.addAttr(pntLoc[i],ln='weight',min=0.0,max=1.0,dv=0.0)
			mc.connectAttr(pntWeight_mdn+'.outputX',pntLoc[i]+'.weight',f=True)

	# ============
	# - CLEAN UP -
	# ============
	
	# Group mesh locators
	pntLoc_grp = mc.group(pntLoc,n=prefix+'_3Point_grp')
	mc.parent(pntFace,pntLoc_grp)
	
	# Turn off inheritTransforms for tri point face
	mc.setAttr(pntFace+'.inheritsTransform',0)
	
	# Scale follow locator
	mc.setAttr(followLoc+'.localScale',0.05,0.05,0.05)
	
	# Parent and hide coincident locator
	mc.parent(pntLoc[3],pntLoc[2])
	mc.setAttr(pntLoc[3]+'.v',0)
	
	# =================
	# - Return Result -
	# =================
	
	# Return result
	return [pntLoc,pntFace,pntLoc_grp]
