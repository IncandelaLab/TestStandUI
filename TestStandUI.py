from PyQt4 import QtCore as core, QtGui as gui
from interface.mainWindow import Ui_MainWindow
import sys
import time

# Further routine imports here as more are added
from routines.dummyRoutine import dummyRoutineInstance, dummyRoutineValidateParameters

# The order of items in this list correspond to the order of the routines in the UI
ROUTINES = [
	[dummyRoutineInstance,dummyRoutineValidateParameters],
	]

TIMERINTERVAL = 50 # Interval in milliseconds between timer_event calls while the UI is running


class mainDesigner(gui.QMainWindow,Ui_MainWindow):
	def __init__(self):
		super(mainDesigner,self).__init__(None)
		self.setupUi(self)

		self.routineRunningID = None # None means no routine is running
		                             # If a routine is running, this will be equal to the routine's ID (position in the ROUTINES list)
		self.routineRunning = None # Same as above, None means no routine is running
		                           # If there is a routine running, this will be the routine object itself

		self.paused = None # None if no routine is running, otherwise True or False determines whether the running routine is paused at the moment.
		self.firstAdvanceCall = None    # None if in setup mode, otherwise stores whether the next advance call is the first one of this routine instance
		self.lastAdvanceCallTime = None # None if in setup mode or the advance hasn't been called yet, otherwise the system time at which advance was last called.

		self.rig()
		self.validateRoutineSetup() # Validate the default settings so that the proper message is displayed
		self.start()


	def rig(self):
		self.tabRoutineSetup.currentChanged.connect(self.listRoutines.setCurrentRow)
		self.tabRoutinePerform.currentChanged.connect(self.listRoutines.setCurrentRow)

		############################
		## Attribute lists by tab ##
		############################
		self.btnStart = [
			self.btnRtn0Start,
			#self.btnRtn1Start, 
			# etc...
			]
		self.lblSetupStatus = [
			self.lblRtn0SetupStatus,
			#self.lblRtn1SetupStatus,
			# etc...
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

		#################################
		##  Individual routine rigging ##
		#################################

		# dummyRoutine
		self.sbRtn0NumPoints.valueChanged.connect(self.validateRoutineSetup) # Here we are connecting all of the parameter input fields' valueChanged functions to the validateRoutine function.
		self.sbRtn0StepDelay.valueChanged.connect(self.validateRoutineSetup) # This will ensure that any time the routine's parameters are changed, the validity of the new set of parameters
		self.sbRtn0XInitial.valueChanged.connect(self.validateRoutineSetup)  # is checked, and that the status and start button are updated accordingly.
		self.sbRtn0XFinal.valueChanged.connect(self.validateRoutineSetup)    # 
		self.sbRtn0G1a.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G1b.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G1c.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G1d.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G1e.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G1f.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G2a.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G2b.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G2c.valueChanged.connect(self.validateRoutineSetup)       # 
		self.sbRtn0G2d.valueChanged.connect(self.validateRoutineSetup)       # 

		self.btnRtn0Start.clicked.connect(self.startRoutine) # Here we connect the "start" button to the startRoutine function

		# Add rigging for other routines as they are implemented


	#####################
	## Setup functions ##
	#####################
	def validateRoutineSetup(self,*args,**kwargs):
		"""Validates the parameters of whichever routine is selected"""
		if not (self.routineRunningID is None):
			print("Error: validateRoutineSetup called with running routine")
			return

		whichRoutine = self.tabRoutineSetup.currentIndex()
		parameters   = self.getSetupParameters(whichRoutine)
		validity     = ROUTINES[whichRoutine][1](*parameters)

		if validity is True:
			self.btnStart[whichRoutine].setEnabled(True)
			self.lblSetupStatus[whichRoutine].setText("Settings are valid")
		else:
			self.btnStart[whichRoutine].setEnabled(False)
			self.lblSetupStatus[whichRoutine].setText(validity)

		# Case structure for each different routine
		# When we have more complicated setup, beyond a simple status and valid/invalid
		# For instance, checking the location of a part when the user selects the ID of the module / component being tested
		# Then we will use other routine functions (or modify the validateRoutine function) to get the data we need (part location, etc) 
		# And update the setup UI elements accordingly here.

	def getSetupParameters(self,whichRoutine):
		if not (self.routineRunningID is None):
			print("Error: getSetupParameters called with running routine")
			return

		if whichRoutine == 0:
			return [
				self.sbRtn0NumPoints.value(),
				self.sbRtn0StepDelay.value(),
				self.sbRtn0XInitial.value(),
				self.sbRtn0XFinal.value(),
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

	def startRoutine(self,*args,**kwargs):
		"""Starts the currently selected routine"""
		if not (self.routineRunningID is None):
			print("Error: startRoutine called with running routine")
			return

		whichRoutine = self.tabRoutineSetup.currentIndex()
		parameters   = self.getSetupParameters(whichRoutine)

		self.routineRunningID = whichRoutine
		self.routineRunning   = ROUTINES[whichRoutine][0](*parameters)

		# disable routine selection lists
		self.listRoutines.setEnabled(False)
		self.listRoutineStatus.setEnabled(False)

		# disable all other tabs
		for tabID in range(len(self.tabRoutineSetup)):
			if not (tabID == whichRoutine):
				self.tabRoutineSetup.setTabEnabled(tabID,False)
		for tabID in range(len(self.tabRoutinePerform)):
			if not (tabID == whichRoutine):
				self.tabRoutinePerform.setTabEnabled(tabID,False)

		# disable setup region altogether
		self.tabRoutineSetup.setEnabled(False)

		# Control of setup / selection can be regained by completing or cancelling the routine
		# With this choice we have limited ourselves to one routine running at a time
		# If we want to be able to run multiple in parallel, we'll have to remove this tab-switching restriction.
		# Disabling the contents of the setup tab for running routines is still needed in this case.

		self.paused = False             # start unpaused
		self.firstAdvanceCall = True    # since we just initialized the routine, the next advance call is the first
		self.lastAdvanceCallTime = None # there hasn't been an advance call yet, so this is None




	###############################
	## Routine running functions ##
	###############################

	def routinePause(self):
		pass

	def routineResume(self):
		pass

	def routineCancel(self):
		pass

	def routineCleanup(self,*args,**kwargs):
		"""Returns to setup mode and deletes the previous routine object"""
		# Routines should be set up to:
		# 1) before reporting completion, do EVERYTHING that they need to do, including saving data and cleaning up
		# 2) have their cancel function set up to clean all loose ends, since if the routine is canelled, it will be deleted immediately after the cancel function completes.
		# 
		# This function will be called either:
		# 1) when the timer_event discovers that the routine has set self.complete to true
		# 2) when cancellation is requested, after the routine's cancel function completes
		pass




	def start(self):
		self.setWindowTitle("UI test")

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
