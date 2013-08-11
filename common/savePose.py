import maya.cmds as mc
import maya.mel as mm
from xml_utilities import *

def save_selectedPose():
	pose_dict, namespace = record_selectedPose()
	exportXml(pose_dict, namespace)
	
#######################################
def save_pose(controls=[], filePath=""):
	pose_dict, namespace =record_pose(controls)
	writePoseXmlDoc( pose_dict, namespace, filePath="" )

#######################################
def record_selectedPose():
	sel = mc.ls(sl=1)
	pose_dict, namespace = record_pose(sel)
	
	return pose_dict, namespace
#######################################	
def record_pose(controls=[]):
	namespace=""
	name_elems=[]
	if controls[0].count(':'): name_elems.extend( controls[0].split(":"))
	if len(name_elems): namespace=name_elems[0]
	pose_dict={}
	for i in controls:
		attrs = mc.listAttr( i, k=1 )
		for a in attrs:
			if len(namespace): pose_dict[ i.replace(namespace+":", "")+"."+a ] = mc.getAttr(i +"."+ a )
			else: pose_dict[ i +"."+a ] = mc.getAttr(i +"."+ a )
	return pose_dict, namespace
#######################################
def set_Pose(filePath=""):
	pose_dict, namespace = readPoseXmlDoc( filePath )
	if len(namespace): namespace+=":"
	for i in pose_dict:
		try:
			mc.setAttr(namespace+i, pose_dict.get(i))
		except:
			print "Warning : couldn't set "+namespace+i
		
#######################################
def readPoseXmlDoc( filePath=""):
	doc, root = xml_openDocument( filePath )
	elem = xml_getChildElements(root)
	info = xml_getChildElements(elem[0])
	pose = xml_getChildElements(elem[1])
	
	#read info
	info_dict = xml_getAttributeDictionary(info[0])
	namespace = info_dict.get("namespace")
	
	#read pose
	pose_dict = {}
	for i in pose:
		elem_dict = xml_getAttributeDictionary(i)
		pose_dict[ elem_dict.get("object") ] = float(elem_dict.get("value"))
	return pose_dict, namespace
#######################################
def writePoseXmlDoc( pose_dict={}, namespace="", filePath="" ):
	if filePath == "" :
		print "must provide a valid file path!"
		return
	# create doc
	doc, root = xml_newDocument("pose")
	
	poseInfo = xml_addElement(doc, root, "poseInfo")
	info = xml_addElement(doc, poseInfo, "info")
	xml_addAttr(info, "namespace", namespace )
	
	# add pose objects
	objects = xml_addElement(doc, root, "objects")
	for i in pose_dict:
		obj = pose_dict.get( i )
		pose = xml_addElement(doc, objects, "pose")
		xml_addAttr(pose, "object", i )
		xml_addAttr(pose, "value", obj )
	xml_write(doc, filePath)
	
#######################################0.45
def exportXml(pose_dict={}, namespace=""):
	
	result = mc.promptDialog(
			title='File Path to Save Pose',
			message='Enter Path:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel')
	
	if result == 'OK':
		path = mc.promptDialog(query=True, text=True)
		writePoseXmlDoc( pose_dict, namespace, path )
		
#######################################
def importXml():
	
	result = mc.promptDialog(
			title='File Path to Import Pose',
			message='Enter Path:',
			button=['OK', 'Cancel'],
			defaultButton='OK',
			cancelButton='Cancel',
			dismissString='Cancel')
	
	if result == 'OK':
		path = mc.promptDialog(query=True, text=True)
		pose_dict = readPoseXmlDoc( path )
	return pose_dict

