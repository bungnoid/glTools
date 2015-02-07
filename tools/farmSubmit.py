import ika.run
from ika.run.steps.maya_step import MayaCmdJob

import os.path

import types

def submit(workfile,name,cmd,args={}):
	'''
	Submit a farm job to run a command on the specified workfile.
	@param workfile: Workfile to operate on
	@type workfile: str
	@param name: Farm job name
	@type name: str
	@param cmd: Command to run on workfile
	@type cmd: funtion
	@param args: kwargs dictionary to pass to cmd
	@type args: dict
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Workfile
	if not os.path.isfile(workfile):
		raise Exception('Workfile "'+workfile+'" does not exist!')
	
	# Check Command Function
	if not isinstance(cmd,types.FunctionType):
		raise Exception('Invalid function "'+cmd.__module__+'.'+cmd.__name__+'"!')
	
	# ===================
	# - Build Job Graph -
	# ===================
	
	# Initialize Graph
	graph = ika.run.Graph('maya_cmd')
	
	# Build Step
	step = MayaCmdJob(frames=[1],sceneFile=workfile,jobName=name,cmd=cmd,kwargs=args)
	graph.add_node(step)
	
	# Run Graph on Farm
	graph.run(farm=True)

def submitBatch(workfileList,name,cmd,args):
	'''
	Submit a farm job to run a command on the specified list of workfiles.
	@param workfileList: Workfiles to operate on
	@type workfileList: str
	@param name: Farm job name
	@type name: str
	@param cmd: Command to run on workfile
	@type cmd: funtion
	@param args: kwargs dictionary to pass to cmd
	@type args: dict
	'''
	# ==========
	# - Checks -
	# ==========
	
	# Check Workfile
	for workfile in workfileList:
		if not os.path.isfile(workfile):
			raise Exception('Workfile "'+workfile+'" does not exist!')
	
	# Check Command Function
	if not isinstance(cmd,types.FunctionType):
		raise Exception('Invalid function "'+cmd.__module__+'.'+cmd.__name__+'"!')
	
	# ===================
	# - Build Job Graph -
	# ===================
	
	# Initialize Graph
	graph = ika.run.Graph('maya_cmd')
	
	# Build Step
	for workfile in workfileList:
		step = MayaCmdJob(frames=[1],sceneFile=workfile,jobName=name,cmd=cmd,kwargs=args)
		graph.add_node(step)
	
	# Run Graph on Farm
	graph.run(farm=True)
