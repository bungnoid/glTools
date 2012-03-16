import maya.mel as mm
import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import math
import os.path

import glTools.utils.base
import glTools.utils.mesh
import glTools.utils.matrix

def export2DPointData(path,pt,cam,start,end,width=2348,height=1152):
	'''
	Export raw 2D (screen space) point position data based on the specified camera to an ascii text file
	@param path: Directory to save the 2D data export file to
	@type path: str
	@param pt: The point to export 2D position data for
	@type pt: str
	@param cam: The camera used to calculate the 2D screen space from
	@type cam: str
	@param start: The first frame of the data sequence
	@type start: int
	@param end: The last frame of the data sequence
	@type end: int
	@param width: Maximum output screen space width
	@type width: int
	@param height: Maximum output screen space height
	@type height: int
	'''
	# Check path
	dirpath = path.replace(path.split('/')[-1],'')
	if not os.path.isdir(dirpath): os.makedirs(dirpath)
	
	# Open file for writing
	file = open(path,"w")
	
	# -----------------------
	# - Write Position Data -
	# -----------------------
	
	# Cycle through frame range
	for f in range(start,end+1):
	
		# Set current frame
		mc.currentTime(f)
		
		# Get point world space position
		pos = glTools.utils.base.getMPoint(pt)
		
		# Get camera details
		cam_hfv = mc.camera(cam,q=True,hfv=True)
		cam_vfv = mc.camera(cam,q=True,vfv=True)
		cam_mat = glTools.utils.matrix.getMatrix(cam).inverse()
		
		# Calculate 2D point
		ssPt = pos * cam_mat
		ptx = ( ( ( ssPt.x / -ssPt.z ) / math.tan( math.radians(cam_hfv / 2) ) ) / 2.0) + 0.5
		pty = ( ( ( ssPt.y / -ssPt.z ) / math.tan( math.radians(cam_vfv / 2) ) ) / 2.0) + 0.5
		
		# Write data to file
		file.write(str(ptx * width) + ' ' + str(pty * height) + '\n')
	
	# End file with new line
	file.write('')
	
	# Close file
	file.close()
	
	# Print result
	print('2D point data exported to '+path)

def export2DOffsetData(path,pt,cam,start,end,width=1,height=1,refFrame=1):
	'''
	Export raw 2D (screen space) point offset data based on the specified camera to an ascii text file
	@param path: Directory to save the 2D data export file to
	@type path: str
	@param pt: The point to export 2D position data for
	@type pt: str
	@param cam: The camera used to calculate the 2D screen space from
	@type cam: str
	@param start: The first frame of the data sequence
	@type start: int
	@param end: The last frame of the data sequence
	@type end: int
	@param width: Maximum output screen space width
	@type width: int
	@param height: Maximum output screen space height
	@type height: int
	@param refFrame: Offset base frame. All offset values will be relative to the point position on this frame.
	@type refFrame: int
	'''
	# Check path
	dirpath = path.replace(path.split('/')[-1],'')
	if not os.path.isdir(dirpath): os.makedirs(dirpath)
	
	# Open file for writing
	file = open(path,"w")
	
	# ---------------------
	# - Get Base Position -
	# ---------------------
	
	# Set current frame
	mc.currentTime(refFrame)
	
	# Get point world space position
	pos = glTools.utils.base.getMPoint(pt)
	
	# Get camera data
	cam_hfv = mc.camera(cam,q=True,hfv=True)
	cam_vfv = mc.camera(cam,q=True,vfv=True)
	cam_mat = glTools.utils.matrix.getMatrix(cam).inverse()
	
	# Calculate 2D point
	ssPt = pos * cam_mat
	basex = ( ( ( ssPt.x / -ssPt.z ) / math.tan( math.radians(cam_hfv / 2) ) ) / 2.0) + 0.5
	basey = ( ( ( ssPt.y / -ssPt.z ) / math.tan( math.radians(cam_vfv / 2) ) ) / 2.0) + 0.5
	
	# ---------------------
	# - Write Offset Data -
	# ---------------------
	
	# Cycle through frame range
	for f in range(start,end+1):
	
		# Set current frame
		mc.currentTime(f)
		
		# Get point world space position
		pos = glTools.utils.base.getMPoint(pt)
		
		# Get camera details
		cam_hfv = mc.camera(cam,q=True,hfv=True)
		cam_vfv = mc.camera(cam,q=True,vfv=True)
		cam_mat = glTools.utils.matrix.getMatrix(cam).inverse()
		
		# Calculate 2D point
		ssPt = pos * cam_mat
		ptx = ( ( ( ssPt.x / -ssPt.z ) / math.tan( math.radians(cam_hfv / 2) ) ) / 2.0) + 0.5
		pty = ( ( ( ssPt.y / -ssPt.z ) / math.tan( math.radians(cam_vfv / 2) ) ) / 2.0) + 0.5
		
		# Write data to file
		file.write(str((ptx - basex) * width) + ' ' + str((pty - basey) * height) + '\n')
	
	# End file with new line
	file.write('')
	
	# Close file
	file.close()
	
	# Print result
	print('2D point offset data exported to '+path)

def export3DPointData(path,pt,start,end):
	'''
	Export raw 3D point position data to an ascii text file
	@param path: Directory to save the 3D data export file to
	@type path: str
	@param pt: The point to export 3D position data for
	@type pt: str
	@param start: The first frame of the data sequence
	@type start: int
	@param end: The last frame of the data sequence
	@type end: int
	'''
	# Check path
	dirpath = path.replace(path.split('/')[-1],'')
	if not os.path.isdir(dirpath): os.makedirs(dirpath)
	
	# Open file for writing
	file = open(path,"w")
	
	# -----------------------
	# - Write Position Data -
	# -----------------------
	
	# Cycle through frame range
	for f in range(start,end+1):
		
		# Set current frame
		mc.currentTime(f)
		
		# Get point world space position
		pos = glTools.utils.base.getPosition(pt)
		
		# Write data to file
		file.write(str(pos[0]) + ' ' + str(pos[1]) + ' ' + str(pos[2]) + '\n')
	
	# End file with new line
	file.write('')
	
	# Close file
	file.close()
	
	# Print result
	print('3D point data exported to '+path)

def export3DRotationData(path,pt,start,end,upVec=(0,1,0),rotateOrder='xyz'):
	'''
	Export raw 3D point position data to an ascii text file
	@param path: Directory to save the 3D data export file to
	@type path: str
	@param pt: The point to export 3D position data for
	@type pt: str
	@param start: The first frame of the data sequence
	@type start: int
	@param end: The last frame of the data sequence
	@type end: int
	@param upVec: Up vector used to contruct rotation matrix for non-transform point. 
	@type upVec: list or tuple
	'''
	# Check path
	dirpath = path.replace(path.split('/')[-1],'')
	if not os.path.isdir(dirpath): os.makedirs(dirpath)
	
	# Open file for writing
	file = open(path,"w")
	
	# -----------------------
	# - Write Rotation Data -
	# -----------------------
	
	# Cycle through frame range
	for f in range(start,end+1):
		
		# Set current frame
		mc.currentTime(f)
		
		# Get object world space rotation
		rot = getRotation(pt,upVec,rotateOrder)
		
		# Write data to file
		file.write(str(rot[0]) + ' ' + str(rot[1]) + ' ' + str(rot[2]) + '\n')
	
	# End file with new line
	file.write('')
	
	# Close file
	file.close()
	
	# Print result
	print('3D rotation data exported to '+path)

def getRotation(obj,upVec=(0,1,0),rotateOrder='xyz'):
	'''
	Return the rotation/orientation (in degrees) of any point or transform
	@param obj: Point to return position for
	@type obj: str or list or tuple
	'''
	# Get Rotation Matrix
	if ['transform','joint'].count(mc.objectType(obj)):
		
		# Get transform matrix
		mat = glTools.utils.matrix.getMatrix(obj)
		
	else:
		
		# Check polyVert selection
		mc.select(obj)
		sel = mc.filterExpand(ex=True,sm=31)
		if not sel: raise Exception('Invalid object selection! Supply a valid transform or polygon vertex!')
		
		# Get mesh object and component id
		mesh = mc.ls(obj,o=True)[0]
		vtxId = int(obj.split('[')[-1].split(']')[0])
		
		# Up Vector
		upVecVec = OpenMaya.MVector(upVec[0],upVec[1],upVec[2]).normal()
		
		# Get component normal
		norm = glTools.utils.mesh.getNormal(mesh,vtxId,worldSpace=True)
		normVec = OpenMaya.MVector(norm[0],norm[1],norm[2]).normal()
		
		# Cross Vector
		crossVec = (normVec * upVecVec).normal()
		cross = [crossVec.x,crossVec.y,crossVec.z]
		
		# Allign Up Vector
		upVecVec = (crossVec * normVec).normal()
		upVec = [upVecVec.x,upVecVec.y,upVecVec.z]
		
		# Build rotation matrix
		mat = glTools.utils.matrix.buildMatrix(xAxis=cross,yAxis=upVec,zAxis=norm)
		
	# Get matrix rotation based on input rotateOrder
	rot = glTools.utils.matrix.getRotation(mat,rotateOrder)
	
	# Return result
	return rot
