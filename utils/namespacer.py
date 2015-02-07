import os, sys
import collections
import types

import ika.io.logger as logger
import ika.exceptions

import maya.cmds as mc
import maya.mel as mm
import maya.utils as mu

if 'eval' not in dir(mm):
    logger.error('something failed trying to import maya modules.')
    sys.exit(1)

DEFAULT_NODES = [u'characterPartition', u'defaultHardwareRenderGlobals', u'defaultLayer', u'defaultLightList1', u'defaultLightSet', 
u'defaultObjectSet', u'defaultRenderGlobals', u'defaultRenderLayer', u'defaultRenderLayerFilter', u'defaultRenderQuality', 
u'defaultRenderUtilityList1', u'defaultResolution', u'defaultShaderList1', u'defaultTextureList1', u'dof1', u'dynController1', 
u'globalCacheControl', u'hardwareRenderGlobals', u'hyperGraphInfo', u'hyperGraphLayout', u'ikSystem', u'initialMaterialInfo', 
u'initialParticleSE', u'initialShadingGroup', u'lambert1', u'layerManager', u'layersFilter', u'lightLinker1', u'lightList1', 
u'objectNameFilter4', u'objectScriptFilter10', u'objectTypeFilter69', u'objectTypeFilter70', u'objectTypeFilter71', 
u'particleCloud1', u'postProcessList1', u'relationshipPanel1LeftAttrFilter', u'relationshipPanel1RightAttrFilter', 
u'renderGlobalsList1', u'renderLayerFilter', u'renderLayerManager', u'renderPartition', u'renderingSetsFilter', u'shaderGlow1',
u'strokeGlobals', u'test:brush1', u'time1', u'|front', u'|front|frontShape', u'|persp', u'|persp|perspShape', u'|side', 
u'|side|sideShape', u'|top', u'|top|topShape', u'front', u'frontShape', u'persp', u'perspShape', u'side', 
u'sideShape', u'top', u'topShape', u'polyMergeEdgeToolDefaults', u'polyMergeFaceToolDefaults']

HISTORY_STACK = []
 
class NamespacerError(ika.exceptions.Error):
    pass
 
    
class InvalidNamespaceError(NamespacerError):
    pass


def getSelectedNS():
    #get the selection
    sel = mc.ls(sl=True)

    if not sel:
        logger.debug("namespacer.getSelectedNS was unable to locate any selected objects!")
        return []

    #create a namespace list
    namespaces = []

    #cycle through the selection and add them to the namespace
    for node in sel:
        parts = splitNS(node)
        if parts[0]:
            #if there is a namspace on the node and it is not in the list add it
            if not namespaces.count(parts[0]):
                namespaces.append(parts[0])

    namespaces.sort()
    return namespaces
    #END

def getAllNS():

    #set the current naemspace to world
    curNS = mc.namespaceInfo(cur=True)
    mc.namespace(set=":")

    #because maya can only list the child namespaces of the current set namespace, we have to recursively go through setting
    #and checking child namespaces

    #start by getting the worlds children
    namespaces = []
    childspaces = mc.namespaceInfo(lon=True)

    while childspaces:
        #move the current add spaces into the namespaces list (what we will return)
        namespaces.extend(childspaces)
        #create a list from the childspaces so that we can check for their children
        checkspaces = childspaces
        #empty the childspaces so all new children can be added to it for the next round
        childspaces = []
        #cycle through the current checkspaces and get their child namespaces
        for check in checkspaces:
            mc.namespace(set=(":" + check))
            grandchildspaces = mc.namespaceInfo(lon=True)
            if grandchildspaces:
                childspaces.extend(grandchildspaces)
                
    #remove default namespaces
    if namespaces.count('UI'): namespaces.remove('UI')
    if namespaces.count('shared'): namespaces.remove('shared')
      
    mc.namespace(set=(":" + curNS))
    namespaces.sort()
    return namespaces
    #END

def getRelatedNS(ns, mode='children'):
    '''
    Find the namespaces that are part of a namespace provieded. You can use this function to find all the namespaces that are children
    of a given namespace, all the namespaces that are parents of a given namespace.
    
    @todo: add ability for siblings
    
    @note: this does not act like the old mel version of this function, this will not return the enire tree (cousins and all) for
    a namespace, you can return the children of a namespace (recursively), the parents (full namespaces for each parent), or both.
    
    @param ns: the namespace to find relatives for
    @type ns: str
    @param mode: the type of relatives to locate, options are "children", "parents", "both"
    @type mode: str
    
    @return: a list of namespaces
    @rtype: list(str)
    '''
    # check the mode
    mode = mode.lower()
    vaildModes = ['children', 'parents', 'both']
    if not mode in vaildModes:
        raise ika.exceptions.InvalidArgError('The mode specified "%s" is not a valid choice %s' % (mode, vaildModes))
    
    # clean the namespace
    ns = cleanNS(ns)
    
    # make sure the namespace specified exists
    if not mc.namespace(exists=":%s" % ns):
        raise InvalidNamespaceError('The namespace "%s" does not exist, unable to locate relatives' % ns)
    
    # get the current namespace
    curNS = mc.namespaceInfo(cur=True)
    
    # create the return list
    relatives = [ns]
    
    if mode == 'parents' or mode == 'both':
        # break the namespace into its parts
        nsParts = ns.split(':')
        base = []
        # cycle through the parts
        for part in nsParts:
            #construct the new item
            base.append(str(part))
            # add the new item
            relatives.append(":".join(base))
    
    
    if mode == 'children' or mode == 'both':
        # create a queue to find children recursively on
        queue = collections.deque([ns])
        
        # cycle through the namespaces to recurse on
        while queue:
            cur = queue.popleft()
            # add to the relatives
            if not relatives.count(cur):
                relatives.append(cur)
            # set the namspace
            mc.namespace(set=':%s' % cur)
            # get children and add to queue
            children = mc.namespaceInfo(listOnlyNamespaces=True)
            if children:
                queue.extend(children)
    
    # set the namespace back
    curNS = cleanNS(curNS)
    mc.namespace(set=":%s" % curNS)
            
    return relatives
    

def separateNS(name):
    logger.warning('DEPRECATED METHOD: namespacer.separateNS(): use splitNS() instead')
    return splitNS(name)
    
def splitNS(name):
    '''
    Take the namespace on the string and return a tuple with the namespace in the first field, and the short name in the second
    
    @param name: name to separate namespace from
    @type: str
    
    @return: (namespace, baseName)
    @rtype: tuple(str, str)
    '''
    if not name:
        return None, None
        
    # remove full paths
    path = [x for x in name.split('|') if x]
    name = path[-1]
        
    stack = [x for x in name.split(":") if x]
    
    if stack == []:
        return ("", "")
    if len(stack) == 1:
        return ("", stack[0])
    else:
        return (':'.join(stack[:-1]), stack[-1])
    

def getObjectsOfNS(namespace, filterOut=None, recursive=False):
    '''
    '''
    filterOut = filterOut if filterOut else []
    
    # create a set for the objects
    objects = set()
    
    # handle recursive
    namespaces = [cleanNS(namespace)]
    if recursive:
        namespaces.extend(getRelatedNS(namespace))
    
    # cycle through the objects
    for ns in namespaces:
        # get the objects in that namespace
        allObjects = set(mc.ls(':%s:*' % ns))
        # get the filter objects (objects of type that we dont want)
        filterObjects = set()
        for filterItem in filterOut:
            filterObjects.update(set(mc.ls(':%s:*' % ns, type=filterItem)))
        # remove the filterObjects from allObjects and push them into the objects set
        objects.update(allObjects.difference(filterObjects))
        
    return objects
        

def exists(namespace):
    namespace = cleanNS(namespace)
    return mc.namespace(exists=':%s' % namespace)


def addNS(namespace):
    #logger.warning('DEPRECATED METHOD: namespacer.addNS(): use createNS() instead')
    return createNS(namespace)

    
def createNS(namespace):
    '''
    Add a namespace to the scene. This namespace can be nested and already exist.
    
    @param namespace: a namespace to create
    @type namespace: str
    '''
    # clean the namespace provided
    namespace = cleanNS(namespace)
    
    # check that the namespace exists
    if mc.namespace(exists=':%s' % namespace):
        return namespace
        
    # see if there is a maya node with the same name as the namespace (as this will cause your namespace to increment)
    if mc.objExists(namespace):
        raise NamespacerError('Unable to add namespace "%s" to your scene since a node exists with the same name' % namespace)
    
    # get the current namespace
    curNS = mc.namespaceInfo(cur=True)
    mc.namespace(set=":")
    
    # split the namespace apart
    parts = namespace.split(":")
    # create each part
    for part in parts:
        # see if it exists (under our current namespace
        if not mc.namespace(exists=part):
            # create it
            mc.namespace(add=part)
        # set the current namespace to the part created
        mc.namespace(set=part)
            
    # set it back
    mc.namespace(set=':%s' % curNS)
    
    # check that it was made
    if not mc.namespace(exists=":%s" % namespace):
        raise NamespacerError('The namespace "%s" was not created, current namespaces: %s' % (namespace, getAllNS()))
    
    return namespace            
    

def pushNS(namespace=':'):
    '''
    Stores the current namespace in HISTORY_STACK stack, and sets the current namespace to value of "namespace" arg.  
    Original namespace can be restored using popNS().  Note: this does not append to the actual namespace, but acts
    more like a history of full namespaces.
    '''
    HISTORY_STACK.append(':'+mc.namespaceInfo(cur=True))
    namespace = ':' + namespace if namespace[0] != ':' else namespace
    mc.namespace(set=namespace)
    

def popNS():
    '''
    Restore previous namespace from HISTORY_STACK stack (see pushNS).
    '''
    if HISTORY_STACK:
        mc.namespace(set=HISTORY_STACK.pop(-1))
    else:
        logger.warning('popNS() failed - the namespace history stack is empty.  Current namespace has been set to ":"')
        mc.namespace(set=':')
        
    
    
def setLiveNS(namespace):
    '''
    Set the current namespace, this will cause all items created to be in this namespace.
    @note: this namespace does not need to exist, it will be created otherwise
    
    @param namespace: the namespace to create/set
    @type namespace: str
    '''
    namespace = cleanNS(namespace)
    # if setting to world
    if namespace == ":":
        mc.namespace(set=":")
    else:
        addNS(namespace)
        mc.namespace(set=":%s" % namespace)
    # confirm it
    curNS =  mc.namespaceInfo(cur=True)
    if not curNS == namespace:
        raise NamespacerError('The namespace "%s" was not set, current namespace is "%s"'\
                              % (namespace, curNS))
                              
    return True

                              
def removeUnusedNS(namespace=None):
    '''
    Remove all namespaces that have no children
    '''
    curNS = mc.namespaceInfo(cur=True)
    
    if namespace:
        namespaces = getRelatedNS(namespace)
    else:
        namespaces = getAllNS()
    
    namespaces.reverse()
    
    for ns in namespaces:
        try:
            mc.namespace(rm=ns)
        except (SystemError, KeyboardInterrupt):
            raise
        except:
            pass
            
    mc.namespace(set=':')
    if mc.namespace(exists=curNS):
        mc.namespace(set=curNS)
    
    
def cleanNS(origNamespace):
    '''
    Clean the namespace provided (removes additional colons)
    
    Example:
        ":jack::bar:fred:"  --->   jack:bar:fred
    
    @param origNamespace: the dirty namespace to clean
    @type origNamespace: str
    
    @return: a correctly coloned namespace "foo:bar"
    @rtype: str
    
    '''
    # handle namespace of None, False, ""
    origNamespace = origNamespace if origNamespace else ""
    
    cleaned = ":".join([x for x in origNamespace.split(":") if x])
    if cleaned:
        return cleaned
    else:
        return ":"
    

def renameNS(origNamespace, newNamespace):
    '''
    Move the objects in one namespace to another namespace
    
    @note: this will handle renaming the world namespace but world ":" can never be deleted. This means that it will always return
    False when renaming world. It will however do its best to rename everything in the world namespace to the name specified
    
    @param origNamespace: the name of the namespace you want to rename
    @type origNamespace: str
    @param newNamespace: the new name for your namespace
    @type newNamespace: str
    
    @return: success
    @rtype: boolean
    '''
    # clean the namespaces
    origNamespace = cleanNS(origNamespace)
    newNamespace = cleanNS(newNamespace)
    
    # check
    if origNamespace == newNamespace:
        logger.info('You are attempting to rename a namespace to the same name... nothing to move')
        return True
    
    if not mc.namespace(exists=":"+origNamespace):
        logger.error('The namespace provided "%s" for renaming does not exist, unable to continue')
        return False
        
    # get the current namespcae
    curNS = mc.namespaceInfo(cur=True)
    mc.namespace(set=":")
    
    # create the new namespace
    addNS(newNamespace)
    
    # if renaming the world namespace ":", we have to use append since it will not allow you to move world into a child ns
    if origNamespace == ':':
        setNS(mc.ls(), newNamespace, force=True)
        return False
    else:
        # move it
        mc.namespace(force=True, mv=[origNamespace, newNamespace])
    
        # delete the origional
        deleteNS(origNamespace)
        
        # set the namespace back
        if exists(curNS):
            mc.namespace(set=curNS)
        
        stillExists = exists(origNamespace)
        
        if stillExists:
            logger.warning('The namespace "%s" was renamed to "%s" but it was not successfully deleted, some nodes may still be in origional namespace' % origNamespace, newNamespace)
        
        # return False if the namespace was not fully renamed
        return not stillExists
    

def deleteAllNS():
    '''
    '''
    namespaces = getAllNS()
    for namespace in namespaces:
        deleteNS(namespace)
        
    return True
    
    
def deleteNS(namespace):
    '''
    Delete a namespace from the scene, move all objects into world namespace during delete
    
    @return: all the object in the namespace after moving it - may be renamed
    @rtype: list(str)
    '''
    # clean the namespace provided
    namespace = cleanNS(namespace)
    
    # if world, stop
    if namespace == ":":
        return []
        
    # get the current namespace
    curNS = mc.namespaceInfo(cur=True)
    setLiveNS(":")
    
    # see if the namespace provided exists
    if not mc.namespace(exists=namespace):
        logger.debug('the namespace "%s" is not in your scene, that means its deleted!' % namespace)
        return []
        
    # get all the nodes currently in world namespace
    preSet = set(mc.ls(":*", dag=True, dep=True))
    
    # move
    logger.debug('attempting to move namespace "%s"' % namespace)
    mc.namespace(mv=(namespace, ":"), force=True)
    
    # get all the node after the move (includes renames
    postSet = set(mc.ls(":*", dag=True, dep=True))
    
    # get the ones that are new
    diffSet = postSet.difference(preSet)
    
    # remove the origional namespace
    mc.namespace(rm=namespace, force=True)
    
    # set the namespace back
    if mc.namespace(exists=curNS):
        setLiveNS(curNS)
        
    if exists(namespace):
        logger.warning('The namespace %s was not successfully deleted (likely due to references in namespace' % namespace)
    
    # return them
    return list(diffSet)


def stripNS(nodes, force=True, autoExpandShapes=True):
    '''
    '''
    if not nodes:
        return {}
        
    curNS = mc.namespaceInfo(cur=True)
    setLiveNS(":")
    
    mapping = {}
    
    # process the nodes
    nodes = _processNodes(nodes, autoExpandShapes)
    
    # cycle through the objects
    for node in nodes:
        
        # check if default
        if node in DEFAULT_NODES:
            continue
        
        # split the namespace
        ns, baseNode = splitNS(node)
        
        # if node isn't namespaced, key == value == node
        if not ns:
            mapping[node] = node
            continue
            
        # see if the non-namespaced node exists
        if mc.objExists(baseNode) and not force:
            continue
        
        newName = mc.rename(node, baseNode)
        mapping[node] = newName
        
        
    setLiveNS(curNS)
    return mapping


def appendNS(nodes, namespace, force=True, autoExpandShapes=True):
    '''
    Append Namespace takes the namespace provided and sets it as the namespace
    on the list of objects provided. This does flatten the namespace to the one
    provided. It will detect whether or not a name conflict will result. If the
    force flag is set to true, it will rename the object and allow maya to number
    it to resolve the conflict. If false, it will not change the namespace.
    
    This will return the names of the nodes that were renamed with the new namespace.
    This will include any shape nodes for the nodes provided.
    
    @param objList: a list of objects to have their namespace altered
    @type objList: list(str)
    @param namespace: the namespace to apply to the objList
    @type namespace: str
    @param force: whether or not to force the namespace in the event it will result in a name conflict
    @type force: bool
    
    @return: dictionary of origional nodes to new names
    @rtype: dict
    '''
    logger.warning('DEPRECATED: namespacer.appendNS: use setNS() instead')
    return setNS(nodes, namespace, force=force, autoExpandShapes=autoExpandShapes)
    
    
def setNS(nodes, namespace, force=True, autoExpandShapes=True, prefix=False):
    '''
    Set Namespace takes the namespace provided and sets it as the namespace
    on the list of objects provided. This does flatten the namespace to the one
    provided. It will detect whether or not a name conflict will result. If the
    force flag is set to true, it will rename the object and allow maya to number
    it to resolve the conflict. If false, it will not change the namespace.
    
    @param objList: a list of objects to have their namespace altered
    @type objList: list(str)
    @param namespace: the namespace to apply to the objList
    @type namespace: str
    @param force: whether or not to force the namespace in the event it will result in a name conflict
    @type force: bool
    @param prefix: whether to use the namespace provided to prefix existing namespaces as opposed to flat out replacing
    @type prefix: bool
    
    @return: dictionary of origional nodes to new names
    @rtype: dict
    '''
    if not nodes:
        return {}
        
    namespace = addNS(namespace)
    curNS = mc.namespaceInfo(cur=True)
    setLiveNS(":")
    
    mapping = {}
    
    # process the nodes
    nodes = _processNodes(nodes, autoExpandShapes)
    # cycle through the objects
    for node in nodes:
        
        # check if default
        if node in DEFAULT_NODES:
            continue
        
        # split the namespace
        ns, baseNode = splitNS(node)
        
        if prefix:
            applyNamespace = namespace + ":" + ns
            applyNamespace = addNS(applyNamespace)
        else:
            applyNamespace = namespace
        
        # generate the new name
        newNode = applyNamespace + ":" + baseNode
            
        # see if the non-namespaced node exists
        if mc.objExists(newNode) and not force:
            logger.warning('namespacer.setNS(): skipping renaming "%s" to "%s" because a name conflict will result, use force flag to apply change'
                        % (node, newNode))
            continue
        
        try:
            newNode = mc.rename(node, newNode)
        except Exception, e:
            logger.warning('unable to change namespace on %s to %s: %s' % (node, namespace, e))
            continue
        mapping[node] = newNode
        
        
    setLiveNS(curNS)
    return mapping


def prefixNS(nodes, namespace, force=True, autoExpandShapes=True):
    '''
    Prefix a namespace on a list of nodes, while maintining their current namespace after the one being added.
    '''
    raise NotImplementedError('Not yet created')
    

def searchReplaceNS(nodes, search, replace, force=True, autoExpandShapes=True):
    '''
    '''
    curNS = mc.namespaceInfo(cur=True)
    setLiveNS(":")
    
    mapping = {}
    
    search = cleanNS(search)
    replace = cleanNS(replace)
    
    if search == ":":
        logger.error('You are attempting to searchReplaceNS without any search string.. use appendNS for this functionality')
        return {}
    
    # process the nodes
    nodes = _processNodes(nodes, autoExpandShapes)
    
    for node in nodes:
        # check if default
        if node in DEFAULT_NODES:
            continue
        
        # split the namespace
        ns, baseNode = splitNS(node)
            
        if ns.count(search):
            newNS = cleanNS(ns.replace(search, replace))
            newNode = newNS + ":" + baseNode
            if mc.objExists(newNode) and not force:
                continue
            addNS(newNS)
            newNode = mc.rename(node, newNode)
            mapping[node] = newNode
            
    return mapping
            
    
def _processNodes(nodes, autoExpandShapes=True):
    newNodes = set()
    # if expanding to shapes
    for node in nodes:
        # check
        if not mc.objExists(node):
            logger.warning('Unable to process the namespace on "'+node+'" since it does not exist')
            continue
        if mc.referenceQuery(node, isNodeReferenced=True):
            logger.warning('Unable to process the namespace "'+node+'" since it is referenced')
            continue
        # add the node
        newNodes.add(node)
            
        # handle shapes
        if autoExpandShapes:
            shapes = mc.listRelatives(node, shapes=True, pa=True)
            if shapes:
                newNodes.update(set(shapes))
    
    # sort the nodes so we rename them in the right order
    nodes = sorted(mc.ls(list(newNodes), long=True))
    nodes.reverse()
    return nodes

    
# This converts a namespace to a list (removes empty spots that a split might leave behind) (":set:asset:" >> ['set', 'asset'])
def namespaceToList(namespace):
    '''
    Take a namespace and convert it to a list of parts (like a split but ensures that it is clean, no empty elements)
    
    @param namespace: the namespace to turn into a list
    @type namespace: str
    
    @return: list of elements in the namespace (split on the :)
    @rtype: list(str)
    '''
    return [x for x in namespace.split(":") if x]


def listToNamespace(namespaceList):
    '''
    Take a list of names and turn them into a namespace. This will ensure that if your list has empty elements, that they are
    removed.
    @param namespaceList: a list of strings to turn into a namespace
    @type namespaceList: list(str)
    
    @return: the namespace
    @rtype: str
    '''
    return ':'.join([str(x) for x in namespaceList if x])


def importToNamespace(filePath, namespace, group=False, removeExistingNamespaces=False):
    '''
    Import a file into maya with the namespace provided
    
    @todo: could using the mc.file(rnn) flag which returns new nodes be used to optimize this?
    @note: nested namespaces are supported
    
    @param filepath: the filepath to imported into your scene
    @type filepath: str
    @param namespace: the namespace to imported into
    @type namespace: str
    @param removeExistingNamespaces: remove namespaces that were in the file your are importing as opposed to just adding
                                     a namespace in front of all the nodes imported
    #type removeExistingNamespaces: bool
    
    @return: success
    @rtype: boolean
    '''
    # clean the namespace
    namespace = cleanNS(namespace)
    
    # checks
    if not os.path.isfile(filePath):
        raise ika.exceptions.MissingDataError('The filepath "%s" does not exist, unable to reference into the "%s" namespace'\
                                              % (filePath, namespace))
                                              
    # record the current objects in the namespace we are importing to
    origObjects = set(mc.ls())
    # get the current namespace
    curNS = mc.namespaceInfo(cur=True)
    mc.namespace(set=":")
    
    # create a temp namespace
    tempNS = generateTmpNamespace('importToNamespaceTmp', create=False)
    
    # now impot into the namespace provided
    mc.file(filePath, i=True, namespace=tempNS, groupReference=group)
    
    # find all namespaces in the tempNS (if imported nodes were already in namespace it will be like tmpNS:foo:bar)
    if removeExistingNamespaces:
        namespaces = sorted(getRelatedNS(tempNS))
        namespaces.reverse()
    else:
        namespaces = [tempNS]
    
    # now move the namespaces to the desired one
    for crap in namespaces:
        renameNS(crap, namespace)
    removeUnusedNS()
    
    # cleanup
    setLiveNS(curNS)
    
    # get all the new objects in the namespace
    diffObjects = set(mc.ls()).difference(origObjects)
    
    #logger.info('importToNamespace() took %s seconds' % mc.timerX(startTime=timer))
    return diffObjects
    
    
def generateTmpNamespace(base='tmpNS', create=False):
    '''
    Create a temp namespace in your scene.
    
    @param base: the base of the namespace
    @type base: str
    @return: the new namespace name
    @rtype: str
    '''
    cnt = 1
    while mc.namespace(exists=base):
        base+=str(cnt)
        cnt+=1
        
    if create:
        base = addNS(base)
        
    return base
    
    
def referenceToNamespace(filepath, namespace=None):
    '''
    Reference a file into maya with the namespace provided
    
    @note: nested namespaces are supported
    @todo: add groupReference flag to reference to create a group automatically
    
    @param filepath: the filepath to reference into your scene
    @type filepath: str
    @param namespace: the namespace to reference into
    @type namespace: str
    
    @return: The reference node created from the reference
    @rtype: str
    '''
    if not os.path.isfile(filepath):
        raise ika.exceptions.MissingDataError('The filepath "%s" does not exist, unable to reference into the "%s" namespace'\
                                              % (filepath, namespace))
    
    # get the current namespace
    curNS = mc.namespaceInfo(cur=True)
    mc.namespace(set=":")
    
    # split the namespace, set current one, and reference the file
    namespace = namespaceToList(cleanNS(namespace))
    if not namespace:
        referencedNodes = mc.file(filepath, r=True, dns=True, rnn=True)
    elif len(namespace) > 1:
        setLiveNS(listToNamespace(namespace[:-1]))
        referencedNodes = mc.file(filepath, r=True, namespace=namespace[-1], rnn=True)
    else:
        referencedNodes = mc.file(filepath, r=True, namespace=namespace[0], rnn=True)
        
    # cleanup
    setLiveNS(curNS)
    
    refNodes = mc.ls(referencedNodes, type='reference', long=True)
    if refNodes:
        return refNodes[0]      
    else:
        raise NamespacerError('No reference node created from reference to %s' % filepath)

    
def nukeNamespace(namespace):
    '''
    Remove a namespace and all the nodes in it from your scene. This will delete all nodes possible as well as remove any referenced
    ones in the namespace before removing the namespace
    '''
    # get the namespace from the castMember name
    namespace = cleanNS(namespace)
    if namespace == ':':
        raise NamespacerError('You can not nuke the world ":" namespace!')
       
    import ika.apps.maya.common.nukeReference
    _nukeRef = ika.apps.maya.common.nukeReference.NukeReference()
        
    # get the nodes in the namespace
    nodes = getObjectsOfNS(namespace)
    if not nodes:
        deleteNS(namespace)
        return True
    
    # create a problem flag for the deleteing non referenced nodes
    problemFlag = False
    
    # see if the namespace is referenced - must check all nodes in that namespace (faster way anyone?)
    for node in nodes:
        # check if the node is referenced
        if mc.referenceQuery(node, isNodeReferenced=True):
            # nuke the reference
            nukeMessage = 'A problem occured while attempting to unload the referenced namespace "' + namespace + '" from your scene.'
            try:
                if not _nukeRef.nukeReference(namespace):
                    raise NamespacerError(nukeMessage)
            except NamespacerError:
                raise
            except Exception, e:
                raise NamespacerError('%s Exception: %s' % (nukeMessage, e))
            break
    
    # after unloading reference re-aquire all the nodes in the namespace
    nodes = getObjectsOfNS(namespace)
    # cycle through the nodes in the namespace to delete them
    for n in nodes:
        if mc.objExists(n):
            try:
                mc.delete(n)
            except:
                logger.debug('unloadNamespace was unable to delete the namespaced node "' + str(n) + '" during unload procedure..')
                problemFlag = True
    
    # delete the namespace
    deleteNS(namespace)
    
    # timer
    if problemFlag:
        logger.info('nukeNamespace encountered some issues while deleting nodes in the namespace "'+namespace+\
                      '". However, your scene should still be usable.')
    else:
        logger.info('nukeNamespace successfully unloaded the namespace "' + namespace + '" from your scene.')
    
    return True


def findAssemblies(namespace):
    '''
    Return a list of assemblies in the given namespace.
    This is a quick method of identifying the "top level" nodes to be parented in display groups.
    When a castMember is loaded it is parented to the WORLD in Maya.
    When a castMember is re-loaded it is deleted, then loaded, again parented to the WORLD.
    '''
    namespace = cleanNS(namespace)
    if namespace != ":":
        namespace += ":"
    assemblies = mc.ls(':%s*' % namespace, assemblies=True)
    return assemblies


