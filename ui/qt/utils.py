import maya.OpenMayaUI as mui
import maya.OpenMayaUI as apiUI
from PySide import QtCore, QtGui
from shiboken import wrapInstance

################################################################################
#Functions
################################################################################
def getMayaWindow():
    '''
    Get the maya main window as a QMainWindow instance
    '''
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QWidget)

def toQtObject(mayaName):
    '''
    Given the name of a Maya UI element of any type,
    return the corresponding QWidget or QAction.
    If the object does not exist, returns None
    '''
    ptr = apiUI.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = apiUI.MQtUtil.findMenuItem(mayaName)
	if ptr is not None:
		return wrapInstance(long(ptr), QtGui.QWidget)

