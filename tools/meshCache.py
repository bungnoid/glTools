import maya.cmds as mc
import maya.OpenMaya as OpenMaya

import glTools.utils.mesh
import glTools.utils.stringUtils

import os
import os.path

import gzip

def writeGeoCache(path,name,mesh,startFrame,endFrame,pad=4,uvSet='',worldSpace=True,gz=False):
	'''
	Write a .geo cache per frame for the specified mesh geometry.
	@param path: Destination directory path for the cache files.
	@type path: str
	@param name: Cache file output name.
	@type name: str
	@param mesh: Mesh geometry to write cache for.
	@type mesh: str
	@param startFrame: Cache start frame
	@type startFrame: float
	@param endFrame: Cache end frame
	@type endFrame: float
	@param pad: Frame number padding for file name.
	@type pad: str
	@param uvSet: UVSet to export with cache
	@type uvSet: str
	@param worldSpace: Export mesh in world space instead of local or object space.
	@type worldSpace: bool
	@param gz: Gzip the cache files
	@type gz: bool
	'''
	# Check path
	if not os.path.isdir(path): os.makedirs(path)
	
	# Check mesh
	if not mc.objExists(mesh): raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check UVs
	uv = False
	if uvSet:
		if mc.polyUVSet(mesh,q=True,auv=True).count(uvSet): uv = True
		else: print('UVSet "'+uvSet+'" does not exist for mesh "'+mesh+'"!')
	else:
		uvSet = str(mc.polyUVSet(mesh,q=True,cuv=True)[0])
	
	# Determine Sample Space
	if worldSpace: sampleSpace = OpenMaya.MSpace.kWorld
	else: sampleSpace = OpenMaya.MSpace.kObject
	
	# Write mesh cache
	for f in range(startFrame,endFrame+1):
		
		# Update frame
		mc.currentTime(f)
		
		# -------------------------
		# - Open file for writing -
		# -------------------------
		
		fPad = glTools.utils.stringUtils.stringIndex(f,pad)
		
		if gz:
			filename = path+'/'+name+'.'+fPad+'.geo.gz'
			print 'Writing '+filename
			FILE = gzip.open(filename,"wb")
		else:
			filename = path+'/'+name+'.'+fPad+'.geo'
			print 'Writing '+filename
			FILE = open(filename,"w")
		
		# Write cache file header
		FILE.write('PGEOMETRY V5\n')
		
		# Determine the total number of vertices
		numVerts = mc.polyEvaluate(mesh,v=True)
		numFaces = mc.polyEvaluate(mesh,f=True)
		
		# Write total number pf points/primitives
		FILE.write('NPoints '+str(numVerts)+' NPrims '+str(numFaces)+'\n')
		
		# Write Point/Prim Group info
		FILE.write('NPointGroups 0 NPrimGroups 0\n')
		
		# Write Point/Vert/Prim/Detail Attribute info
		if uv: numVtxAttr = 1
		else: numVtxAttr = 0
		FILE.write('NPointAttrib 1 NVertexAttrib '+str(numVtxAttr)+' NPrimAttrib 0 NAttrib 0\n')
		
		# -------------------------
		# - Write Point Attr Info -
		# -------------------------
		
		FILE.write('PointAttrib\n')
		FILE.write('N 3 vector 0 0 0\n')
		
		vtxArray = OpenMaya.MPointArray()
		normArray = OpenMaya.MFloatVectorArray()
		meshFn = glTools.utils.mesh.getMeshFn(mesh)
		meshFn.getPoints(vtxArray,sampleSpace)
		meshFn.getVertexNormals(False,normArray,sampleSpace)
		
		# Write vertex array
		for i in range(vtxArray.length()):
			FILE.write(str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+' '+str(vtxArray[i].w)+' ('+str(normArray[i].x)+' '+str(normArray[i].y)+' '+str(normArray[i].z)+')\n')
		
		# -------------------
		# - Write Face Data -
		# -------------------
		
		if uv:
			FILE.write('VertexAttrib\n')
			FILE.write('uv 3 float 0 0 0\n')
		
		FILE.write('Run '+str(numFaces)+' Poly\n')
		
		# Face vertex id array
		faceVtxArray = OpenMaya.MIntArray()
		faceUArray = OpenMaya.MFloatArray()
		faceVArray = OpenMaya.MFloatArray()
		
		# Get mesh face iterator
		faceIter = glTools.utils.mesh.getMeshFaceIter(mesh)
		
		# Iterate over mesh faces
		faceIter.reset()
		while not faceIter.isDone():
			
			# Get face vertices
			faceIter.getVertices(faceVtxArray)
			vtxArray = list(faceVtxArray)
			vtxArray.reverse()
			
			# Get face UVs
			if uv:
				faceIter.getUVs(faceUArray,faceVArray,uvSet)
				uArray = list(faceUArray)
				vArray = list(faceVArray)
				uArray.reverse()
				vArray.reverse()
			
			# Build face data string
			faceData = ' '+str(len(vtxArray))+' <'
			for i in range(len(vtxArray)):
				faceData += ' '+str(vtxArray[i])
				if uv: faceData += ' ( '+str(uArray[i])+' '+str(vArray[i])+' 0.0 )'
			faceData += '\n'
			
			# Write face data
			FILE.write(faceData)
			
			# Iterate to next face
			faceIter.next()
		
		# -----------------------
		# - Finalize cache file -
		# -----------------------
		
		FILE.write('beginExtra\n')
		FILE.write('endExtra\n')
		
		# Close File
		FILE.close()
	
	# Print result
	print 'Write cache completed!'
	
def writeGeoCombineCache(path,name,meshList,startFrame,endFrame,pad=4,uvSet='',worldSpace=True,gz=False):
	'''
	Write a .geo cache per frame for the specified list of mesh objects.
	All meshes in the list will be combined to a single cache, and an 'id' vertex attribute will be added to identify the individual objects. 
	@param path: Destination directory path for the cache files.
	@type path: str
	@param name: Cache file output name.
	@type name: str
	@param meshList: List of mesh objects to write cache for.
	@type meshList: list
	@param startFrame: Cache start frame
	@type startFrame: float
	@param endFrame: Cache end frame
	@type endFrame: float
	@param pad: Frame number padding for file name.
	@type pad: str
	@param uvSet: UVSet to export with cache
	@type uvSet: str
	@param worldSpace: Export mesh in world space instead of local or object space.
	@type worldSpace: bool
	@param gz: Gzip the cache files
	@type gz: bool
	'''
	# Check path
	if not os.path.isdir(path): os.makedirs(path)
	
	# Check mesh list
	fullMeshList = meshList
	for mesh in meshList:
		if not mc.objExists(mesh): raise Exception('Mesh "'+mesh+'" does not exist!')
		if not glTools.utils.mesh.isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check UVs
	uv = False
	if uvSet:
		for mesh in meshList:
			if mc.polyUVSet(mesh,q=True,auv=True).count(uvSet): uv = True
			else: print('UVSet "'+uvSet+'" does not exist for mesh "'+mesh+'"!')
	
	# Determine Sample Space
	if worldSpace: sampleSpace = OpenMaya.MSpace.kWorld
	else: sampleSpace = OpenMaya.MSpace.kObject
		
	# Write mesh cache
	for f in range(startFrame,endFrame+1):
		
		# Update frame
		mc.currentTime(f)
		
		# Check mesh visibility
		meshList = [mesh for mesh in fullMeshList if mc.getAttr(mesh+'.v')]
		if not meshList: continue
		
		# -------------------------
		# - Open file for writing -
		# -------------------------
		
		fPad = glTools.utils.stringUtils.stringIndex(f,pad)
		
		if gz:
			filename = path+'/'+name+'.'+fPad+'.geo.gz'
			print 'Writing '+filename
			FILE = gzip.open(filename,"wb")
		else:
			filename = path+'/'+name+'.'+fPad+'.geo'
			print 'Writing '+filename
			FILE = open(filename,"w")
		
		# Write cache file header
		FILE.write('PGEOMETRY V5\n')
		
		# Determine the total number of vertices
		numVertList = []
		numFaceList = []
		totalNumVerts = 0
		totalNumFaces = 0
		
		# For each mesh
		for mesh in meshList:
			
			# Get mesh data
			numVerts = mc.polyEvaluate(mesh,v=True)
			numFaces = mc.polyEvaluate(mesh,f=True)
			totalNumVerts += numVerts
			totalNumFaces += numFaces
			numVertList.append(numVerts)
			numFaceList.append(numFaces)
		
		# Write total number pf points/primitives
		FILE.write('NPoints '+str(totalNumVerts)+' NPrims '+str(totalNumFaces)+'\n')
		
		# Write Point/Prim Group info
		FILE.write('NPointGroups 0 NPrimGroups 0\n')
		
		# Write Point/Vert/Prim/Detail Attribute info
		if uv: numVtxAttr = 1
		else: numVtxAttr = 0
		FILE.write('NPointAttrib 2 NVertexAttrib '+str(numVtxAttr)+' NPrimAttrib 0 NAttrib 0\n')
		
		# -------------------------
		# - Write Point Attr Info -
		# -------------------------
		
		FILE.write('PointAttrib\n')
		FILE.write('N 3 vector 0 0 0\n')
		FILE.write('id 1 int 0\n')
		
		# Write raw point data
		for m in range(len(meshList)):
			
			# Get vertex and normal arrays
			vtxArray = OpenMaya.MPointArray()
			normArray = OpenMaya.MFloatVectorArray()
			meshFn = glTools.utils.mesh.getMeshFn(meshList[m])
			meshFn.getPoints(vtxArray,sampleSpace)
			meshFn.getVertexNormals(False,normArray,sampleSpace)
			
			# Write vertex array
			for i in range(vtxArray.length()):
				FILE.write(str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+' '+str(vtxArray[i].w)+' ('+str(normArray[i].x)+' '+str(normArray[i].y)+' '+str(normArray[i].z)+' '+str(m)+')\n')
			
		# -------------------
		# - Write Face Data -
		# -------------------
		
		if uv:
			FILE.write('VertexAttrib\n')
			FILE.write('uv 3 float 0 0 0\n')
		
		FILE.write('Run '+str(totalNumFaces)+' Poly\n')
		
		# Track per mesh vertex id offsets 
		vertexOffset = 0
		
		# Face vertex id array
		faceVtxArray = OpenMaya.MIntArray()
		faceUArray = OpenMaya.MFloatArray()
		faceVArray = OpenMaya.MFloatArray()
		
		# Iterate over meshes
		for m in range(len(meshList)):
			
			# Get mesh face iterator
			faceIter = glTools.utils.mesh.getMeshFaceIter(meshList[m])
			
			# Iterate over mesh faces
			faceIter.reset()
			while not faceIter.isDone():
				
				# Get face vertices
				faceIter.getVertices(faceVtxArray)
				vtxArray = list(faceVtxArray)
				#vtxArray.reverse()
				
				# Get face UVs
				if uv:
					faceIter.getUVs(faceUArray,faceVArray,uvSet)
					uArray = list(faceUArray)
					vArray = list(faceVArray)
					uArray.reverse()
					vArray.reverse()
				
				# Build face data string
				faceData = ' '+str(len(vtxArray))+' <'
				for i in range(len(vtxArray)):
					faceData += ' '+str(vtxArray[i]+vertexOffset)
					if uv: faceData += ' ( '+str(faceUArray[i])+' '+str(faceVArray[i])+' 0.0 )'
				faceData += '\n'
				
				# Write face data
				FILE.write(faceData)
				
				# Iterate to next face
				faceIter.next()
			
			# Update vertex offset
			vertexOffset += numVertList[m]
		
		# -----------------------
		# - Finalize cache file -
		# -----------------------
		
		FILE.write('beginExtra\n')
		FILE.write('endExtra\n')
		
		# Close File
		FILE.close()
	
	# Print result
	print 'Write cache completed!'

def writeObjCache(path,name,mesh,startFrame,endFrame,pad=4,uvSet='',worldSpace=True,gz=False):
	'''
	Write a .obj cache per frame for the specified mesh geometry.
	@param path: Destination directory path for the cache files.
	@type path: str
	@param name: Cache file output name.
	@type name: str
	@param mesh: Mesh geometry to write cache for.
	@type mesh: str
	@param startFrame: Cache start frame
	@type startFrame: float
	@param endFrame: Cache end frame
	@type endFrame: float
	@param pad: Frame number padding for file name.
	@type pad: str
	@param uvSet: UVSet to export with cache
	@type uvSet: str
	@param worldSpace: Export mesh in world space instead of local or object space.
	@type worldSpace: bool
	@param gz: Gzip the cache files
	@type gz: bool
	'''
	# Check path
	if not os.path.isdir(path): os.makedirs(path)
	
	# Check mesh
	if not mc.objExists(mesh): raise Exception('Mesh "'+mesh+'" does not exist!')
	if not glTools.utils.mesh.isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check UVs
	uv = False
	if uvSet:
		if mc.polyUVSet(mesh,q=True,auv=True).count(uvSet): uv = True
		else: print('UVSet "'+uvSet+'" does not exist for mesh "'+mesh+'"!')
	else:
		uvSet = str(mc.polyUVSet(mesh,q=True,cuv=True)[0])
	
	# Determine Sample Space
	if worldSpace: sampleSpace = OpenMaya.MSpace.kWorld
	else: sampleSpace = OpenMaya.MSpace.kObject
	
	# Write mesh cache
	for f in range(startFrame,endFrame+1):
		
		# Update frame
		mc.currentTime(f)
		
		# -------------------------
		# - Open file for writing -
		# -------------------------
		
		fPad = glTools.utils.stringUtils.stringIndex(f,pad)
		
		if gz:
			filename = path+'/'+name+'.'+fPad+'.obj.gz'
			print 'Writing '+filename
			FILE = gzip.open(filename,"wb")
		else:
			filename = path+'/'+name+'.'+fPad+'.obj'
			print 'Writing '+filename
			FILE = open(filename,"w")
		
		# Write cache file header
		FILE.write('g\n')
		
		# ---------------------
		# - Write Vertex Data -
		# ---------------------
		
		meshFn = glTools.utils.mesh.getMeshFn(mesh)
		
		# Vertex Positions
		vtxArray = OpenMaya.MPointArray()
		meshFn.getPoints(vtxArray,sampleSpace)
		for i in range(vtxArray.length()):
			FILE.write('v '+str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+'\n')
		
		# Vertex UVs
		uArray = OpenMaya.MFloatArray()
		vArray = OpenMaya.MFloatArray()
		meshFn.getUVs(uArray,vArray,uvSet)
		for i in range(uArray.length()):
			FILE.write('vt '+str(uArray[i])+' '+str(vArray[i])+'\n')
		
		# Vertex Normals
		normArray = OpenMaya.MFloatVectorArray()
		meshFn.getVertexNormals(False,normArray,sampleSpace)
		for i in range(vtxArray.length()):
			FILE.write('vn '+str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+'\n')
		
		FILE.write('g\n')
		
		# -------------------
		# - Write Face Data -
		# -------------------
		
		# Initialize face vertex array
		faceVtxArray = OpenMaya.MIntArray()
		
		# Build UV Id pointer object
		uvIdUtil = OpenMaya.MScriptUtil()
		uvIdUtil.createFromInt(0)
		uvIdPtr = uvIdUtil.asIntPtr()
		
		# Get mesh face iterator
		faceIter = glTools.utils.mesh.getMeshFaceIter(mesh)
		
		# Iterate over mesh faces
		faceIter.reset()
		while not faceIter.isDone():
			
			# Get face vertices
			faceIter.getVertices(faceVtxArray)
			vtxArray = list(faceVtxArray)
			vtxCount = len(vtxArray)
			
			# Build face data string
			faceData = 'f '
			for i in range(vtxCount):
				
				# Vertex Id
				faceData += str(vtxArray[i]+1)
				faceData += '/'
				
				# UV Id
				try: faceIter.getUVIndex(i,uvIdPtr,uvSet)
				except: pass
				else: faceData += str(OpenMaya.MScriptUtil(uvIdPtr).asInt()+1)
				faceData += '/'
				
				# Vertex Normal Id
				faceData += str(vtxArray[i]+1)
				faceData += ' '
			
			faceData += '\n'
				
			# Write face data
			FILE.write(faceData)
			
			# Iterate to next face
			faceIter.next()
		
		# -----------------------
		# - Finalize cache file -
		# -----------------------
		
		# Close File
		FILE.close()
	
	# Print result
	print 'Write OBJ cache completed!'

def writeObjCombineCache(path,name,meshList,startFrame,endFrame,pad=4,uvSet='',worldSpace=True,gz=False):
	'''
	Write a .obj cache per frame for the specified list of mesh objects.
	All meshes in the list will be combined to a single cache. 
	@param path: Destination directory path for the cache files.
	@type path: str
	@param name: Cache file output name.
	@type name: str
	@param meshList: List of mesh objects to write cache for.
	@type meshList: list
	@param startFrame: Cache start frame
	@type startFrame: float
	@param endFrame: Cache end frame
	@type endFrame: float
	@param pad: Frame number padding for file name.
	@type pad: str
	@param uvSet: UVSet to export with cache
	@type uvSet: str
	@param worldSpace: Export mesh in world space instead of local or object space.
	@type worldSpace: bool
	@param gz: Gzip the cache files
	@type gz: bool
	'''
	# Check path
	if not os.path.isdir(path): os.makedirs(path)
	
	# Check mesh list
	fullMeshList = meshList
	for mesh in meshList:
		if not mc.objExists(mesh): raise Exception('Mesh "'+mesh+'" does not exist!')
		if not glTools.utils.mesh.isMesh(mesh): raise Exception('Object "'+mesh+'" is not a valid mesh!')
	
	# Check UVs
	uv = False
	if uvSet:
		for mesh in meshList:
			if mc.polyUVSet(mesh,q=True,auv=True).count(uvSet): uv = True
			else: print('UVSet "'+uvSet+'" does not exist for mesh "'+mesh+'"!')
	
	# Determine Sample Space
	if worldSpace: sampleSpace = OpenMaya.MSpace.kWorld
	else: sampleSpace = OpenMaya.MSpace.kObject
		
	# Write mesh cache
	for f in range(startFrame,endFrame+1):
		
		# Update frame
		mc.currentTime(f)
		mc.dgdirty(a=True)
		
		# Check mesh visibility
		meshList = [mesh for mesh in fullMeshList if mc.getAttr(mesh+'.v')]
		if not meshList: continue
		
		# -------------------------
		# - Open file for writing -
		# -------------------------
		
		fPad = glTools.utils.stringUtils.stringIndex(f,pad)
		
		if gz:
			filename = path+'/'+name+'.'+fPad+'.obj.gz'
			print 'Writing '+filename
			FILE = gzip.open(filename,"wb")
		else:
			filename = path+'/'+name+'.'+fPad+'.obj'
			print 'Writing '+filename
			FILE = open(filename,"w")
			
		# Write cache file header
		FILE.write('g\n')
		
		# ---------------------
		# - Write Vertex Data -
		# ---------------------
		
		# Write raw point data
		for m in range(len(meshList)):
			
			meshFn = glTools.utils.mesh.getMeshFn(meshList[m])
			
			# Vertex Positions
			vtxArray = OpenMaya.MPointArray()
			meshFn.getPoints(vtxArray,sampleSpace)
			for i in range(vtxArray.length()):
				FILE.write('v '+str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+'\n')
			
			# Vertex UVs
			if uvSet: uvSetName = uvSet
			else: uvSetName = str(mc.polyUVSet(meshList[m],q=True,cuv=True)[0])
			uArray = OpenMaya.MFloatArray()
			vArray = OpenMaya.MFloatArray()
			meshFn.getUVs(uArray,vArray,uvSetName)
			for i in range(uArray.length()):
				FILE.write('vt '+str(uArray[i])+' '+str(vArray[i])+'\n')
			
			# Vertex Normals
			normArray = OpenMaya.MFloatVectorArray()
			meshFn.getVertexNormals(False,normArray,sampleSpace)
			for i in range(vtxArray.length()):
				FILE.write('vn '+str(vtxArray[i].x)+' '+str(vtxArray[i].y)+' '+str(vtxArray[i].z)+'\n')
			
		# -------------------
		# - Write Face Data -
		# -------------------
		
		# Track per mesh vertex id offsets 
		vertexOffset = 0
		uvOffset = 0
		
		# Initialize face vertex array
		faceVtxArray = OpenMaya.MIntArray()
		
		# Build UV Id pointer object
		uvIdUtil = OpenMaya.MScriptUtil()
		uvIdUtil.createFromInt(0)
		uvIdPtr = uvIdUtil.asIntPtr()
		
		# Iterate over meshes
		for m in range(len(meshList)):
			
			# Write cache file header
			grp = meshList[m].replace(':','_').lower()
			FILE.write('g '+grp+'\n')
			
			# Get mesh face iterator
			faceIter = glTools.utils.mesh.getMeshFaceIter(meshList[m])
			
			# Iterate over mesh faces
			faceIter.reset()
			while not faceIter.isDone():
				
				# Get face vertices
				faceIter.getVertices(faceVtxArray)
				vtxArray = list(faceVtxArray)
				vtxCount = len(vtxArray)
				
				# Build face data string
				faceData = 'f '
				for i in range(vtxCount):
					
					# Vertex Id
					faceData += str(vtxArray[i]+1+vertexOffset)
					faceData += '/'
					
					# UV Id
					try: faceIter.getUVIndex(i,uvIdPtr)
					except: pass
					else: faceData += str(OpenMaya.MScriptUtil(uvIdPtr).asInt()+1+uvOffset)
					faceData += '/'
					
					# Vertex Normal Id
					faceData += str(vtxArray[i]+1+vertexOffset)
					faceData += ' '
				
				faceData += '\n'
				
				# Write face data
				FILE.write(faceData)
				
				# Iterate to next face
				faceIter.next()
			
			# Update vertex offset
			vertexOffset += mc.polyEvaluate(meshList[m],v=True)
			uvOffset += mc.polyEvaluate(meshList[m],uv=True,uvs=uvSetName)
		
		# -----------------------
		# - Finalize cache file -
		# -----------------------
		
		# Close File
		FILE.close()
	
	# Print result
	print 'Write OBJ cache completed!'

def gzipCache(path,name,deleteOriginal=False):
	'''
	'''
	# Check path
	if not os.path.isdir(path): raise Exception('Path "'+path+'" does not exist!')
	
	# Get directory file list
	dirList = os.listdir(path)
	dirList.sort()
	
	# Iterate over file list
	gziplist = []
	for fname in dirList:
		
		# Check name
		if not fname.startswith(name): continue
		
		# Gzip file
		filepath = path+'/'+fname
		gzippath = filepath+'.gz'
		print('GZIPcache - Creating "'+gzippath+'"...')
		FILE_IN = open(filepath, 'rb')
		FILE_OUT = gzip.open(gzippath, 'wb')
		FILE_OUT.writelines(FILE_IN)
		FILE_OUT.close()
		FILE_IN.close()
		
		# Check gzip
		if not os.path.isfile(gzippath): raise Exception('Gzip of file "'+gzippath+'" failed!')
		
		# Append to return list
		gziplist.append(gzippath)
		
		# Delete original
		if deleteOriginal: os.remove(filepath)
	
	# Return result
	return gziplist
