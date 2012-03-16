import socket

import maya.cmds as mc

maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def prankWindow(hardcoreMode=0):

    # Reset UI
	try: mc.deleteUI("prankWindow")
    except: pass
    
    # Create Window
    window = mc.window("prankWindow")
    mainLayout = mc.columnLayout("mainLayout", adj=1, p=window)
    mc.button("Disconnect", c='maya.close(); maya = socket.socket(socket.AF_INET, socket.SOCK_STREAM)', p=mainLayout)
    
    # Duplicate the following line to create quick connection shortcuts here
    mc.button("Connect: Nilouco-pc", c='maya.connect(("nilouco-pc or IP address here",12543))', p=mainLayout)
    
    # Do your stuff!
    mc.separator(h=10, p=mainLayout)
    mc.button("minimizeApp", c='maya.send("minimizeApp")', p=mainLayout)
    mc.button("restoreApp", c='maya.send("RaiseMainWindow")', p=mainLayout)
    mc.button("Clear selection", c='maya.send("select -cl")', p=mainLayout)
    mc.button("Select All", c='maya.send("select -all")', p=mainLayout)
    mc.button("fit Selected", c='maya.send("FrameSelected")', p=mainLayout)
    mc.button("frameAll", c='maya.send("FrameAll")', p=mainLayout)
    mc.button("fit Home", c='maya.send("viewSet -animate `optionVar -query animateRollViewCompass` -home")', p=mainLayout)
    mc.button("Toggle Component Mode", c='maya.send("toggleSelMode")', p=mainLayout)
    mc.button("TOOL: Translate", c='maya.send("setToolTo moveSuperContext")', p=mainLayout)
    mc.button("TOOL: Rotate", c='maya.send("setToolTo RotateSuperContext")', p=mainLayout)
    mc.button("TOOL: Scale", c='maya.send("setToolTo scaleSuperContext")', p=mainLayout)
    mc.button("Cycle BG color", c='maya.send("CycleBackgroundColor")', p=mainLayout)
    mc.button("Toggle Timeslider", c="maya.send('toggleUIComponentVisibility \"Time Slider\"')", p=mainLayout)
    mc.button("VIEWPORT: Toggle Viewcube", c="maya.send('ToggleViewCube')", p=mainLayout)
    mc.button("VIEWPORT: Wireframe", c="maya.send('DisplayWireframe')", p=mainLayout)
    mc.button("VIEWPORT: Shaded", c="maya.send('DisplayShaded')", p=mainLayout)
    mc.button("VIEWPORT: Toggle Views", c="maya.send('panePop')", p=mainLayout)
    mc.button("VIEWPORT: Maximize Viewport", c="maya.send('ToggleUIElements')", p=mainLayout)
    mc.button("Undo", c="maya.send('undo')", p=mainLayout)
    mc.button("Redo", c="maya.send('redo')", p=mainLayout)
    mc.button("Open Renderview", c="maya.send('RenderViewWindow')", p=mainLayout)
    mc.button("Open Rendernode", c="maya.send('createRenderNode \"-all\" \"\" \"\"')", p=mainLayout)
    mc.button("Open Help (F1)", c="maya.send('Help')", p=mainLayout)
    mc.button("Play forward timeline", c="maya.send('playButtonForward')", p=mainLayout)
    mc.button("Play backwards timeline", c="maya.send('playButtonBackward')", p=mainLayout)
    
    # Hardcore ?!
    mc.separator(h=10, p=mainLayout)
    mc.button("NEW SCENE", c='maya.send("file -new -f")', en=hardcoreMode, p=mainLayout)
    mc.button("CLOSE MAYA", c='maya.send("quit -f")', en=hardcoreMode, p=mainLayout)
    mc.button("SHOW HOTBOX", c='maya.send("hotBox")', en=hardcoreMode, p=mainLayout)
    mc.button("OPEN NOTEPAD", c="maya.send('system \"start notepad\"')", en=hardcoreMode, p=mainLayout)
    
    # Display window
    mc.showWindow(window)
