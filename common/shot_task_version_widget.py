'''
shot_task_version_widget.py
'''
#$Id$

import ika.id.widgets
import ika.id.base
from PyQt4 import QtCore
from PyQt4 import QtGui

from ika.id.widgets.model_view.item.ctx_tree_node_item import CtxTreeNodeItem

class ShotTaskVersionWidget(QtGui.QWidget):
    '''
    Creates the custom shot task version widget 
    
    @param Inherits from QWidget
    @type param: subclass of QWidget
    
    G{classtree ShotTaskVersionWidget}
    '''
    def __init__(self, stage=None, model=None, parentWidget=None):
        '''
        Constructor for the widgets which contains the seq information
        and shot tree.
        
        @param stage: the stage object available to the current object
        @type stage: AppStage or MayaStage object
        
        @param model: default model associated with class
        @type model: Always passed None
        
        @param parentWidget: parent widget of the class
        @type parentWidget: IdMainWindow
        '''
        super(ShotTaskVersionWidget, self).__init__(parentWidget)
        self.seqLabel = ika.id.widgets.IdLabel('Seq:')
        self.seqLabel.setFixedWidth(30)
        self.seqLabel.setAlignment(QtCore.Qt.AlignRight)
        self.seqComboBox = ika.id.widgets.IdComboBox(self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.seqLabel)
        layout.addWidget(self.seqComboBox)
        
        self.tree = ShotTaskVersionTree(stage, model, self)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setMargin(0)
        mainLayout.addLayout(layout)
        mainLayout.addWidget(self.tree)
        
        self.setLayout(mainLayout)
        
        
class ShotTaskVersionTree(ika.id.widgets.BasicTreeView):
    '''
    Creates the shot task version tree widget
    
    @param Inherits from an id tree view
    @type param: subclass of ika.id.widgets.BasicTreeView
    
    G{classtree ShotTaskVersionTree}
    '''
    def __init__(self, stage=None, model=None, parentWidget=None):
        '''
        TreeView widget constructor to show only versions under shots.
        
        @param stage: the stage object available to the current object
        @type stage: AppStage or MayaStage object
        
        @param model: model associated with tree view
        @type model: model passed from parent widget
        
        @param parentWidget: parent widget of the treeview 
        @type parentWidget: ShotTaskVersionWidget
        '''
        super(ShotTaskVersionTree, self).__init__(model, parentWidget)
        self.headerItem().renameColumn('Main', 'Shot')
        #self.setRootIsDecorated(False)
        
        if stage:
            self._stage = stage
        else:
            import ika.apps.stage
            self._stage = ika.apps.stage.AppStage()
    
        # Get the job (if we're at "/" warn user and use the first job we can find)
        jobTn = self._stage.getJob()
        if jobTn:
            self._jobName = jobTn.name
        else:
            jobs = self._stage.getObj('/').treeChildren.objects()
            if not jobs:
                print 'WARNING: no jobs found - ShotTaskVersionTree cannot continue'
                return
            else:
                self._jobName = jobs[0].name
                #print 'WARNING: context is "/" - using job "%s"' % self._jobName
                
        self.setColumnDecorated(0, False)
        

        
                
    def _getSeqObj(self, sequenceName):
        sequenceName = str(sequenceName)
        
        # find sequence's inheritance map obj
        try:
            seq = self._stage.getObj('/%s/sequences/%s/sequence' % (self._jobName, sequenceName))
        except:
            print 'WARNING: could not find sequence named "%s"' % sequenceName
            return
            
        return seq
        
        
    def populateFromImap(self, sequenceName):
        '''
        Populate list from sequence's inheritance map.
        
        @param sequenceName: name of selected sequence
        @type sequenceName: str
        '''
        seq = self._getSeqObj(sequenceName)
        
        try:
            iMap = self._stage.getObj('%s/inheritance_map' % (seq.getPath(), sequenceName))
        except:
            print 'WARNING: could not find inheritance_map for sequence "%s"' % sequenceName
            return
        
        # read sequence's shots from inheritance map
        shots = iMap.master.value.keys()
        shots.extend(iMap.intermediate.value.keys())
        shots.extend(iMap.leaf.value)
        
        # clear the model's current data
        self.model().clear()
        
        # load the model with new shots
        prefix = len('/%s/shots/' % self._jobName)
        for shot in sorted(shots):
            item = CtxTreeNodeItem(self._stage.getObj(shot))
            item.setText(shot[prefix:], 'name')
            #item.setIcon(QtGui.QIcon(), 'name')
            self.model().addTopLevelItem(item)
        self.model().reset()
        
    
    def populateFromSeqName(self, sequenceName, includeMaster=True):
        '''
        populates top level of view with shots which link to specified sequence
        
        @param sequenceName: name of sequence
        @type sequenceName: str
        @param includeMaster: (optional) if False, shots under the shots/master tree node will
                              not be displayed
        @type includeMaster: bool
        '''
        # clear the model's current data
        self.model().clear()
        
        # get a list of sequence's dependent shots
        seq = self._getSeqObj(sequenceName)
        dependents = self._stage._getContextDependents(seq)
        shots = [x.treeParent.getPath() for x in dependents if x.name=='shot']
        prefix = len('/%s/shots/' % self._jobName)
        
        # add shots to the model as top level items
        for shot in sorted(shots):
            text = shot[prefix:]
            if includeMaster == False and text.startswith('master'):
                continue
            item = ika.id.widgets.CtxTreeNodeItem(self._stage.getObj(shot))
            item.setText(shot[prefix:], 'name')
            #item.setIcon(QtGui.QIcon(), 'name')
            item._hasChildren = True
            self.model().addTopLevelItem(item)
        self.model().reset()
            
        
    def populate(self, index, force=False):
        '''
        handles population of expanded items.  BasicTreeView connects the expanded(QModelIndex) signal
        to this method by default.
        
        @param index: model index of expanded item
        @type index: QtCore.QModelIndex
        @param force: (optional) forces re-population of items
        @type force: bool
        '''
        item = index.internalPointer()
        if hasattr(item, 'getObj'):
            obj = item.getObj()
            if isinstance(obj, ika.data_model.task_ctx.TaskCtx):
                if item._populated and not force:
                    return
                else:
                    self.model().removeRows(0, item.rowCount(), index)
                versionInfo = self._stage.getVersionInfo(obj.getPath())
                revKeys = versionInfo.keys()
                revKeys.reverse() # so that the versions appear latest first
                for version in revKeys:
                    versionItem = ika.id.widgets.BasicTreeItem()
                    versionItem.setText(str(version))
                    item.addChild(versionItem)
                item._populated = True
            elif isinstance(item, ika.id.widgets.CtxTreeNodeItem):
                item.populate(force)
                for n in item.children():
                    n._hasChildren = True
                    
            self.model().emit(QtCore.SIGNAL('layoutChanged()'))
        else:
            print 'cant populate %s (%s)' % (item.text(0), index)
