from PyQt4 import QtCore as core, QtGui as gui
from interface.mainWindow import Ui_MainWindow
import sys
import time

# Load servers and create dicts
SERVERS = {}
DEVICES = {}

# Further routine imports here as more are added
from routines.dummyRoutine import dummyRoutinePerformer, dummyRoutineSetupHandler, dummyRoutineCheckAvailable

# make lists of performers, setup handlers, and availabilities
# The order of items in these lists correspond to the order of the routines in the UI
ROUTINE_PERFORMERS     = [dummyRoutinePerformer                      , ]
ROUTINE_SETUP_HANDLERS = [dummyRoutineSetupHandler                   , ]
ROUTINE_AVAILABILITIES = [dummyRoutineCheckAvailable(SERVERS,DEVICES), ]

# Other globals
TIMERINTERVAL     = 50     # Interval in milliseconds between timer_event calls while the UI is running
LOCATION          = "UCSB" # Location of the test stand from which this code is being run. For now assume UCSB; later, load from file.
DISPLAY_PRECISION = 6      # Number of decimal points to use on displays

# Database connection. For now just assume no connection; later, add connection support.
DB_CONNECTION_SUCCESS = False



class mainDesigner(gui.QMainWindow,Ui_MainWindow):
	def __init__(self):
		super(mainDesigner,self).__init__(None)
		self.setupUi(self)

		self.routineRunningID    = None # None means no routine is running
		                                # If a routine is running, this will be equal to the routine's ID (position in the ROUTINES list)
		self.routineRunning      = None # Same as above, None means no routine is running
		                                # If there is a routine running, this will be the routine object itself
		self.paused              = None # None if in setup mode, otherwise True or False determines whether the running routine is paused at the moment.
		self.firstAdvanceCall    = None # None if in setup mode, otherwise stores whether the next advance call is the first one of this routine instance
		self.lastAdvanceCallTime = None # None if in setup mode or the advance hasn't been called yet, otherwise the system time at which advance was last called.

		self.rig()
		self.start()


	def rig(self):
		############################
		## Attribute lists by tab ##
		############################
		self.btnStart = [
			self.btnRtn0Start,
			#self.btnRtn1Start, 
			# etc...
			]
		self.listSetupIssues = [
			self.listRtn0SetupIssues,
			]
		self.btnPause = [
			self.btnRtn0Pause,
			]
		self.btnResume = [
			self.btnRtn0Resume,
			]
		self.btnCancel = [
			self.btnRtn0Cancel,
			]
		self.pbProgress = [
			self.pbRtn0,
			]
		self.lblRunningStatus = [
			self.lblRtn0RunningStatus
			]

		for btn in self.btnStart:
			btn.clicked.connect(self.startRoutine)
		for btn in self.btnPause:
			btn.clicked.connect(self.routinePause)
		for btn in self.btnResume:
			btn.clicked.connect(self.routineResume)
		for btn in self.btnCancel:
			btn.clicked.connect(self.routineCancel)



		#################################
		##  Individual routine rigging ##
		#################################
		# dummyRoutine setup mode
		self.sbRtn0NumPoints.valueChanged.connect(self.updateSetup) # Here we are connecting all of the parameter input fields' valueChanged functions to the updateSetup function.
		self.sbRtn0StepDelay.valueChanged.connect(self.updateSetup) # This will ensure that any time the routine's parameters are changed, the validity of the new set of parameters
		self.sbRtn0XInitial.valueChanged.connect(self.updateSetup)  # is checked, along with all other setup feedbacks, and that the new values are applied to the corresponding UI elements.
		self.sbRtn0XFinal.valueChanged.connect(self.updateSetup)    # 
		self.cbRtn0G1Order.currentIndexChanged.connect(self.updateSetup)
		self.sbRtn0G1a.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G1b.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G1c.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G1d.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G1e.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G1f.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G2a.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G2b.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G2c.valueChanged.connect(self.updateSetup)       # 
		self.sbRtn0G2d.valueChanged.connect(self.updateSetup)       # 
		# dummy routine running mode

		# Add rigging for other routines as they are implemented


		####################
		## Setup handlers ##
		####################
		self.setupHandlers = [_() for _ in ROUTINE_SETUP_HANDLERS]
		for i in range(len(self.setupHandlers)):
			self.updateSetupByTab(i,forceAllChanged=True)


		##########################################################
		## Tab and region managing for UI (start in setup mode) ##
		##########################################################
		# Disable tabs for unavailable routines
		for i,_ in enumerate(ROUTINE_AVAILABILITIES):
			if not _:
				self.tabRoutineSetup.setTabEnabled(i,False)
				self.tabRoutinePerform.setTabEnabled(i,False)
		self.tabRoutinePerform.setEnabled(False)
		self.listRoutines.currentRowChanged.connect(self.switchTab)
		self.tabRoutineSetup.currentChanged.connect(self.switchTab)




	############################## 
	## function mode decorators ## These functions act as space-savers for checking that we're in the correct mode when calling a function.
	############################## They will prevent decorated functions from being executed when they're called from the wrong mode.
	def setupFunction(function):
		def wrapper(self,*args,**kwargs):
			if not (self.routineRunningID is None):
				print("Error: setup mode function called outside of setup mode. Not executing.")
				return
			return function(self,*args,**kwargs)
		return wrapper

	def runningFunction(function):
		def wrapper(self,*args,**kwargs):
			if (self.routineRunningID is None):
				print("Error: running mode function called outside of running mode. Not executing.")
				return
			return function(self,*args,**kwargs)
		return wrapper


	#####################
	## setup functions ##
	#####################
	@setupFunction
	def switchTab(self,newIndex):
		if newIndex >= len(ROUTINE_AVAILABILITIES):
			self.listRoutines.setCurrentRow(newIndex)
			self.tabRoutineSetup.setCurrentIndex(newIndex)
			self.tabRoutinePerform.setCurrentIndex(newIndex)
			return
		elif ROUTINE_AVAILABILITIES[newIndex]:
			self.listRoutines.setCurrentRow(newIndex)
			self.tabRoutineSetup.setCurrentIndex(newIndex)
			self.tabRoutinePerform.setCurrentIndex(newIndex)
		return

	@setupFunction
	def updateSetup(self,*args,**kwargs):
		whichTab = self.tabRoutineSetup.currentIndex()
		self.updateSetupByTab(whichTab)

	@setupFunction
	def updateSetupByTab(self,whichTab,forceAllChanged=False):
		if not(ROUTINE_AVAILABILITIES[whichTab]):
			print("Warning: updateSetupByTab called for unavailable routine.")
			return
		self.setupHandlers[whichTab].updateParameters(*self.getSetupParameters(whichTab),forceAllChanged)
		feedbacks = self.setupHandlers[whichTab].getFeedbacks()

		# feedbacks[0] is validity
		self.btnStart[whichTab].setEnabled(feedbacks[0])

		# feedbacks[1] is issues
		self.listSetupIssues[whichTab].clear()
		for item in feedbacks[1]:
			self.listSetupIssues[whichTab].addItem(item)

		# by-routine feedback handling
		if whichTab == 0:
			self.lblRtn0G1YInitial.setText(str(round(feedbacks[2],10)))
			self.lblRtn0G1YFinal.setText(  str(round(feedbacks[3],10)))
			self.lblRtn0Secret.setText(    feedbacks[4])

	@setupFunction
	def getSetupParameters(self,whichRoutine):
		if whichRoutine == 0:
			return [
				self.sbRtn0NumPoints.value(),
				self.sbRtn0StepDelay.value(),
				self.sbRtn0XInitial.value(),
				self.sbRtn0XFinal.value(),
				int(str(self.cbRtn0G1Order.currentText())[0]),
				self.sbRtn0G1a.value(),
				self.sbRtn0G1b.value(),
				self.sbRtn0G1c.value(),
				self.sbRtn0G1d.value(),
				self.sbRtn0G1e.value(),
				self.sbRtn0G1f.value(),
				self.sbRtn0G2a.value(),
				self.sbRtn0G2b.value(),
				self.sbRtn0G2c.value(),
				self.sbRtn0G2d.value(),
				]
		else:
			raise ValueError("invalid whichRoutine specified for getSetupParameters")

	@setupFunction
	def startRoutine(self,*args,**kwargs):
		"""Starts the currently selected routine"""
		whichRoutine = self.tabRoutineSetup.currentIndex()
		parameters   = self.getSetupParameters(whichRoutine)
		self.routineRunningID    = whichRoutine
		self.routineRunning      = ROUTINE_PERFORMERS[whichRoutine](SERVERS,DEVICES,*parameters)
		self.paused              = False
		self.firstAdvanceCall    = True
		self.lastAdvanceCallTime = None
		self.listRoutines.setEnabled(False)
		self.tabRoutineSetup.setEnabled(False)
		self.tabRoutinePerform.setEnabled(True)
		self.tabRoutinePerform.setCurrentIndex(whichRoutine)
		self.clearRunningTab(self.routineRunningID)
		self.updateControl()


	###############################
	## Routine running functions ##
	###############################
	@runningFunction
	def routinePause(self,*args,**kwargs):
		self.paused = True

	@runningFunction
	def routineResume(self,*args,**kwargs):
		self.paused = False

	@runningFunction
	def routineCancel(self,*args,**kwargs):
		self.routineRunning.cancel() # call the routine's cancel function
		del self.routineRunning      # explicitly delete the routine after the cancel function terminates

		#self.clearRunningTab(self.routineRunningID)

		self.routineRunning      = None # reset to setup mode
		self.routineRunningID    = None # 
		self.paused              = None # 
		self.firstAdvanceCall    = None # 
		self.lastAdvanceCallTime = None # 
		self.listRoutines.setEnabled(True)
		self.tabRoutineSetup.setEnabled(True)
		self.tabRoutinePerform.setEnabled(False)

	@runningFunction
	def updateControl(self,*args,**kwargs):
		whichTab = self.tabRoutinePerform.currentIndex()
		self.updateControlByTab(whichTab)

	@runningFunction
	def updateControlByTab(self,whichTab):
		controlParameters = self.getRunningControlParameters(whichTab)
		self.routineRunning.updateControl(*controlParameters)
		self.updateRunningDisplay()

	@runningFunction
	def updateRunningDisplay(self):
		displayData = self.routineRunning.getDisplayData()
		if type(displayData) is list:
			values  = displayData
			changed = [True for _ in values]
		elif type(displayData) is tuple:
			values, changed = displayData
		else:
			raise ValueError("output of routine.getDisplayData must be either a list of values, or a tuple containing a list of values and a list of which values have changed since last call")

		# values[0] is progress
		self.pbProgress[self.routineRunningID].setValue(int(100*values[0]))

		# values[1] is status
		self.lblRunningStatus[self.routineRunningID].setText(values[1])

		# routine-specific displays
		if self.routineRunningID == 0:
			y1 = values[2][...,1]
			y2 = values[3][...,1]

			if len(y1):
				self.lblRtn0G1RunningValue.setText(  str( round(y1[-1],   DISPLAY_PRECISION) ))
				self.lblRtn0G1RunningAverage.setText(str( round(y1.mean(),DISPLAY_PRECISION) ))
				self.lblRtn0G1RunningMaximum.setText(str( round(y1.max(), DISPLAY_PRECISION) ))
				self.lblRtn0G1RunningMinimum.setText(str( round(y1.min(), DISPLAY_PRECISION) ))

			if len(y2):
				self.lblRtn0G2RunningValue.setText(  str( round(y2[-1],             DISPLAY_PRECISION) ))
				self.lblRtn0G2RunningRms.setText(    str( round((y2**2).mean()**0.5,DISPLAY_PRECISION) ))
				self.lblRtn0G2RunningMaximum.setText(str( round(y2.max(),           DISPLAY_PRECISION) ))
				self.lblRtn0G2RunningMinimum.setText(str( round(y2.min(),           DISPLAY_PRECISION) ))


	@runningFunction
	def clearRunningTab(self,whichTab):
		"""reset control and display widgets to blank"""
		self.lblRunningStatus[whichTab].setText("")
		self.pbProgress[whichTab].setValue(0.0)

		if whichTab	== 0:
			pass

	@runningFunction
	def getRunningControlParameters(self,whichTab):
		if whichTab == 0:
			return []



	##################
	## UI functions ##
	##################
	def start(self):
		self.setWindowTitle("Test Stand User Interface")
		self.timer = core.QTimer(self)               # Create timer object
		self.timer.setInterval(TIMERINTERVAL)        # Set timer interval to global TIMERINTERVAL, defined at the top of this file
		self.timer.timeout.connect(self.timer_event) # Connect timer to the timer_event function
		self.timer.start()                           # Start the timer

	def timer_event(self):
		"""Runs each time the timer times out"""

		if self.routineRunningID is None: # If there's no routine running (IE we're in setup mode)
			return                        # do nothing

		if self.paused: # If the routine is paused
			return      # do nothing

		#########################
		## Advance the routine ##
		#########################
		if self.firstAdvanceCall:                  # If this is the first time advance is being called for this routine
			self.lastAdvanceCallTime = time.time() # use the time at calling advance as the lastAdvanceCallTime
			self.routineRunning.advance(0)         # call advance with zero time passed since last call
			self.firstAdvanceCall = False          # set firstAdvanceCall to False now that we've done the first call
		else: # not the first time advance has been called for this routine instance
			currentTime     = time.time()                                     # Get the time
			msSinceLastCall = (currentTime - self.lastAdvanceCallTime) * 1000 # Calculate the time since advance was last called; convert seconds to milliseconds
			self.routineRunning.advance(msSinceLastCall)                      # call advance with the elapsed time
			self.msSinceLastCall = currentTime                                # set last call time to the time at which advance was called
		self.updateRunningDisplay()

		if self.routineRunning.complete is True:
			del self.routineRunning      # explicitly delete the routine as soon as it reports completion
			#self.clearRunningTab(self.routineRunningID)
			self.routineRunning      = None # reset to setup mode
			self.routineRunningID    = None # 
			self.paused              = None # 
			self.firstAdvanceCall    = None # 
			self.lastAdvanceCallTime = None # 
			self.listRoutines.setEnabled(True)
			self.tabRoutineSetup.setEnabled(True)
			self.tabRoutinePerform.setEnabled(False)


		##############################################
		## Update displays and check for completion ##
		##############################################


		
class mainDefault(gui.QMainWindow):
	def __init__(self):
		super(mainDefault,self).__init__(None)


if __name__ == '__main__':
	app = gui.QApplication(sys.argv)
	m = mainDesigner()
	m.show()
	sys.exit(app.exec_())
