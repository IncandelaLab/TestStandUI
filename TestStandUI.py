from PyQt4 import QtCore as core, QtGui as gui
from interface.mainWindow import Ui_MainWindow
import sys


class mainDesigner(gui.QMainWindow,Ui_MainWindow):
	def __init__(self):
		super(mainDesigner,self).__init__(None)
		self.setupUi(self)

		self.rig()
		self.start()

	def rig(self):
		self.tabRoutineSetup.currentChanged.connect(self.listRoutines.setCurrentRow)
		self.tabRoutinePerform.currentChanged.connect(self.listRoutines.setCurrentRow)
		#self.tabRoutineSetup.setCurrentIndex(1)

		# When a routine is running:
		# Disable the routine selection lists
		# Disable all other tabs in tabRoutineSetup and tabRoutinePerform
		# Disable the contents in the tabRoutineSetup tab for the routine
		# 
		# Should not be able to change tabs or interact with anything except
		# the tabRoutinePerform tab that is running the routine
		#
		# Control of setup / selection can be regained by completing or cancelling the routine
		# With this choice we have limited ourselves to one routine running at a time
		# If we want to be able to run multiple in parallel, we'll have to remove this tab-switching restriction.
		# Disabling the contents of the setup tab for running routines is still needed in this case.
		# 
		# This will disable all but routine 1
		##for i in range(1,4):
		##	self.tabRoutinePerform.setTabEnabled(i,False)
		##	self.tabRoutineSetup.setTabEnabled(i,False)
		##self.listRoutines.setEnabled(False)

	def start(self):
		self.setWindowTitle("UI test")

		self.timer = core.QTimer(self)               # Create timer object
		self.timer.setInterval(1000)                 # Set 1000 ms interval
		self.timer.timeout.connect(self.timer_event) # Connect timer to the timer_event function
		self.timer.start()                           # Start the timer

	def timer_event(self):
		"""Runs each time the timer times out"""
		pass
		#print("{interval} ms have passed!".format(interval = self.timer.interval()))
		
class mainDefault(gui.QMainWindow):
	def __init__(self):
		super(mainDefault,self).__init__(None)


if __name__ == '__main__':
	app = gui.QApplication(sys.argv)
	m = mainDesigner()
	m.show()
	sys.exit(app.exec_())
