#$Id$
'''
class definition for stand-in logger to mimic original logging behavior in stage_hand
'''
import sys
import time
import ika.io.messenger
color = ika.io.messenger.AnsiColor()

def addColor(message):
    '''
    adds color formatting to simulate the "real" logger in the shell
    @param message: message to format
    @type message: str
    @return: formatted string
    @rtype: str
    '''
    if message.startswith('INFO:'):
        return color.GREEN + message + color.RESET
    elif message.startswith('WARNING:'):
        return color.YELLOW + message + color.RESET
    elif message.startswith('ERROR:'):
        return color.RED + color.BOLD + message + color.RESET

class Logger():
    '''
    handles logging for stage_hand - this should get replaced with the standard logger
    G{classtree Logger}
    '''
    def __init__(self, textColor=True, parentWidget=None):
        '''
        @param textColor: add color formatting during echo
        @type textColor: bool
        @param parentWidget: parent widget for the logger
        @type parentWidget: QtGui.QWidget
        '''
        # Create log file to simulate how logging is currently accomplished
        # with the stagehand.
        #tempTimeName = time.time() # this was the original way...pretty unreadable
        self.color = textColor
        tempTimeName = time.strftime("%4Y_%02m_%02d_%02H:%02M:%02S")
        self._logFile = '/var/tmp/stagehandLog.'+tempTimeName+'.log'
        self._loggerPrint("------------////INITIALIZING STAGEHAND LOGFILE////------------", 0)
        
    def fileName(self):
        '''
        Returns name of current log file
        
        @return: name of current log file
        @rtype: str
        '''
        return self._logFile

    def _loggerPrint(self, msg, echo):
        '''
        @param msg: message to enter in log
        @type msg: str
        @param echo: also echo message to shell
        @type echo: bool
        '''
        timestamp = time.strftime("%02H:%02M:%02S: ")
        try:
            fopen = open(self._logFile,"a")
            fopen.write(timestamp + msg + '\n')
        except IOError:
            print 'Error: Couldn\'t access file: ', self._logFile
            return
        fopen.close()
        if echo == True:
            if self.color:
                sys.stdout.write('%s\n' % addColor(msg))
            else:
                sys.stdout.write('%s\n' % msg)
                
    def info(self, msg, echo=True):
        '''
        @param msg: message to enter in log
        @type msg: str
        @param echo: also echo message to shell
        @type echo: bool
        '''
        self._loggerPrint("INFO: "+msg, echo)

    def warning(self, msg, echo=True):
        '''
        @param msg: message to enter in log
        @type msg: str
        @param echo: also echo message to shell
        @type echo: bool
        '''
        self._loggerPrint("WARNING: "+msg, echo)

    def error(self, msg, echo=True):
        '''
        @param msg: message to enter in log
        @type msg: str
        @param echo: also echo message to shell
        @type echo: bool
        '''
        self._loggerPrint("ERROR: "+msg, echo)
            
            
            
