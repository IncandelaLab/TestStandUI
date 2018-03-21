# This is a dummy routine that serves as an example of how routines operate
# and how to connect routines to the UI

# These modules aren't needed for all routines, we just happen to use them here
import numpy
import math




# Availability Checker (funcions)
# Inputs: dictionary of servers {"name":server, ...} and dictionary of devices that are available
# Returns whether or not this routine is available given the set of detected servers and devices
def dummyRoutineCheckAvailable(servers,devices):
	return True # The dummy routine doesn't need any servers, so it's always available.




# routine setup handler (class)
# used to get feedback on a given set of parameters for the routine
# when given a set of parameters, it determines whether the set of parameters is valid,
# a list of any issues that are making the set of parameters invalid, as well as any other
# feedback based on the parameter set.
class dummyRoutineSetupHandler(object):

	# When we initialize an instance, we don't take the first set of values as inputs.
	# We just set all values to None, for both parameters and feedback.
	# 
	# To give it the first set of parameters, we instead use the updateParameters function
	# This is so that the values of the feedbacks are calculated properly for the first set of parameters
	def __init__(self):
		self.nParameters = 15
		self.numPoints = None # parameters
		self.stepDelay = None # 
		self.xInitial  = None # 
		self.xFinal    = None # 
		self.g1order   = None # 
		self.g1a       = None # 
		self.g1b       = None # 
		self.g1c       = None # 
		self.g1d       = None # 
		self.g1e       = None # 
		self.g1f       = None # 
		self.g2a       = None # 
		self.g2b       = None # 
		self.g2c       = None # 
		self.g2d       = None # 

		# feedbacks
		self.validity   = None # feedback 0 must be validity
		self.issues     = None # feedback 1 must be issues
		self.g1yInitial = None # other feedbacks are routine dependent
		self.g1YFinal   = None # 
		self.secret     = None # 

	# this function is how we give the setup handler the values for each parameter
	# when we first call this function, we should set the input forceAllChanged to True;
	# what this does is force the function to assume all values have changed, which makes it
	# calculate the values of all feedbacks.
	# 
	# On subsequent calls, we leave this parameter in its default state (False)
	# what this does is make the function only calculate the values of those feedbacks for which
	# relevant parameters have been changed. If no relevant parameters for a particular feedback
	# have changed, there is no need to recalculate its value.
	def updateParameters(self,*parameters,forceAllChanged = False):
		changed = [True for _ in range(self.nParameters)]
		if not forceAllChanged:
			changed[ 0] = parameters[ 0] != self.numPoints # Check new values against old values
			changed[ 1] = parameters[ 1] != self.stepDelay # to determine which paramters have been changed
			changed[ 2] = parameters[ 2] != self.xInitial  # 
			changed[ 3] = parameters[ 3] != self.xFinal    # 
			changed[ 4] = parameters[ 4] != self.g1order   # 
			changed[ 5] = parameters[ 5] != self.g1a       # 
			changed[ 6] = parameters[ 6] != self.g1b       # 
			changed[ 7] = parameters[ 7] != self.g1c       # 
			changed[ 8] = parameters[ 8] != self.g1d       # 
			changed[ 9] = parameters[ 9] != self.g1e       # 
			changed[10] = parameters[10] != self.g1f       # 
			changed[11] = parameters[11] != self.g2a       # 
			changed[12] = parameters[12] != self.g2b       # 
			changed[13] = parameters[13] != self.g2c       # 
			changed[14] = parameters[14] != self.g2d       # 

		self.numPoints = parameters[ 0] # Next change old values to new values
		self.stepDelay = parameters[ 1] # 
		self.xInitial  = parameters[ 2] # 
		self.xFinal    = parameters[ 3] # 
		self.g1order   = parameters[ 4] # 
		self.g1a       = parameters[ 5] # 
		self.g1b       = parameters[ 6] # 
		self.g1c       = parameters[ 7] # 
		self.g1d       = parameters[ 8] # 
		self.g1e       = parameters[ 9] # 
		self.g1f       = parameters[10] # 
		self.g2a       = parameters[11] # 
		self.g2b       = parameters[12] # 
		self.g2c       = parameters[13] # 
		self.g2d       = parameters[14] # 

		# Now calculate new values for feedbacks if relevant values have changed
		if any([changed[_] for _ in [2,3,4,5,6,7,8,9,10]]):
			xInitialPowers = numpy.array([self.xInitial ** n for n in range(6)])
			xFinalPowers   = numpy.array([self.xFinal   ** n for n in range(6)])
			orders         = numpy.array([n<=self.g1order    for n in range(6)])
			coefficients   = numpy.array([self.g1a,self.g1b,self.g1c,self.g1d,self.g1e,self.g1f])
			self.g1yInitial = float((xInitialPowers * orders * coefficients).sum())
			self.g1YFinal   = float((xFinalPowers   * orders * coefficients).sum())

		if changed[11]:
			if self.g2a == 42.0:
				self.secret = "You found it!"
			else:
				self.secret = ""

		if any([changed[_] for _ in [0,1]]):
			self.validity = True
			self.issues   = []

			if not (self.numPoints >= 2):
				self.validity = False
				self.issues.append("number of points must be at least 2")
			if self.stepDelay < 0:
				self.validity = False
				self.issues.append("step delay cannot be negative")

	# this function simply returns a list of all of the feedbacks
	# element 0 must be validity,
	# element 1 must be the list of issues,
	# further elements are all routine-specific feedbacks.
	def getFeedbacks(self):
		return [
			self.validity,
			self.issues,
			self.g1yInitial,
			self.g1YFinal,
			self.secret,
			]




# routine performer
# an instance of this class is created when a routine is started
# the instance is used to perform the routine, and upon completion (or cancellation) the instance is deleted.
class dummyRoutinePerformer(object):

	# the __init__ function takes two special arguments, SERVERS and DEVICES, in positions 0 and 1
	# SERVERS is a dictionary of all available servers {"name":server, ...}
	# DEVICES is a dictionary of the devices available to each server {"name":[devices], ...}
	#
	# the rest of the arguments are the parameters for the routine
	# the order of these arguments must be the same as the order of arguments used in the routine setup handler class
	def __init__(self,
		SERVERS,
		DEVICES,
		numPoints,
		stepDelay,
		xInitial,
		xFinal,
		g1order,
		g1a,
		g1b,
		g1c,
		g1d,
		g1e,
		g1f,
		g2a,
		g2b,
		g2c,
		g2d,
		):

		self.SERVERS = SERVERS
		self.DEVICES = DEVICES

		self.numPoints = numPoints      # total number of points
		self.numSteps  = numPoints - 1  # number of steps before completion
		self.stepDelay = stepDelay      # delay in milliseconds between steps

		self.xInitial  = xInitial  # X value at beginning 
		self.xFinal    = xFinal    # X value at end
		                           # X scales linearly between these two values during the routine

		# Graph 1 variables. Graph 1 is a polynomial (order 5)
		self.g1order = g1order
		self.g1a = g1a # order 0 coefficient (constant)
		self.g1b = g1b # order 1 coefficient (linear term)
		self.g1c = g1c # order 2 coefficient (quadratic term)
		self.g1d = g1d #       3
		self.g1e = g1e #       4
		self.g1f = g1f #       5

		               # Graph 2 is sinusoidal, a combination of a sine and cosine wave.
		self.g2a = g2a # sine   wave amplitude
		self.g2b = g2b # sine   wave frequency
		self.g2c = g2c # cosine wave amplitude
		self.g2d = g2d # cosine wave frequency

		self.pointsDone  = 0    # Number of steps completed so far
		self.nextPoint   = 0    # index of the next point to be calculated
		self.timeElapsed = 0.0  # Time elapsed since last step was performed

		self.g1Data = numpy.zeros([self.numPoints,2]) # [x,y] pairs for graph 1. Starts out empty.
		self.g2Data = numpy.zeros([self.numPoints,2]) # for graph 2

		# required property: self.complete
		# this value is accessed by the UI and used to determine whether the routine has finished.
		# As soon as the UI finds this value is True, it will delete the routine instance.
		# Make sure all loose ends (saving data, resetting equipment, etc) are taken care of by the routine before this is set to True.
		self.complete = False



	# Required function: advance
	# This function always be given as input the number if milliseconds since the last time the function has been called.
	# The first time this function is called for an instance of a routine class, it will be given a value of 0 for msSinceLastCall.
	# This function will be called by the UI at approximately (see below) even intervals while the routine is running.
	#
	# This function should be used to manage the routine based on the amount of time that has passed.
	# It should take care of tasks such as controlling and querying euipment, updating internal variables, etc.
	# 
	# Routines can be paused in the UI, in which case this function will not be called while the routine is paused.
	# When it is unpaused, <advance> will still be given the total time since last it was called, which can easily be seconds or minutes.
	# Routines that manage equipment that is sensitive to large jumps in parameters should be careful to account for this possibility.
	# The simplest way to do this is to enforce a maximum value on msSinceLastCall by having the following line of code at the beginning of this function:
	# msSinceLastCall = min([msSinceLastCall, msMax])
	def advance(self,msSinceLastCall):
		
		if self.complete: # If the routine has finished,
			return        # we don't do anything when <advance> is called.
		
		# Add ms to the time elapsed since the last point we calculated
		self.timeElapsed += msSinceLastCall

		# If timeElapsed >= stepDelay, it's time to do a step
		if self.timeElapsed >= self.stepDelay:

			self.timeElapsed = 0.0
			self.addPoint()
			self.pointsDone += 1
			self.nextPoint  += 1

			# If all the points have been done
			if self.pointsDone >= self.numPoints:
				self.complete = True



	# required function: updateControl
	# this function is used to pass new values of control variables to the routine
	def updateControl(self):
		pass



	# Required function: getDisplayData
	# This function is called by the UI to retrieve data for the routine's display
	# 
	# The most basic data that this function returns are the progress (percent completion, from 0 to 1) and the status, a short descriptive string.
	# Element 0 of the returned list is assumed to be the progress, and element 1 is the status.
	# It also returns any other data that the UI uses for displays (temperature and humidity values for readouts, arrays for making graphs, etc)
	def getDisplayData(self):
		progress = self.pointsDone / self.numPoints
		status   = "all points complete" if self.complete else "{pointsDone} / {numPoints} points done".format(pointsDone = self.pointsDone, numPoints = self.numPoints)
		return [
			progress,
			status,
			self.g1Data[:self.pointsDone], # Only return values for the points that have been completed, not for the whole (incomplete) data set
			self.g2Data[:self.pointsDone], # 
			]



	# Required function: cancel
	# This function is called if the user cancels the routine while it is in operation
	# It should take care of all loose ends
	# The instance of the routine will be deleted by the UI IMMEDIATELY after this function completes.
	def cancel(self):
		pass # Since the dummy routine doesn't interact with any hardware, we don't need to do anything.



	def addPoint(self):
		p = self.nextPoint / (self.numPoints-1)
		x = p*self.xFinal + (1-p)*self.xInitial

		self.g1Data[self.nextPoint] = numpy.array([x,self.calcY1(x)])
		self.g2Data[self.nextPoint] = numpy.array([x,self.calcY2(x)])

	def calcY1(self,x):
		return self.g1a + self.g1b*x + self.g1c*x**2 + self.g1d*x**3 + self.g1e*x**4 + self.g1f*x**5

	def calcY2(self,x):
		return self.g2a * math.sin(self.g2b*2*math.pi*x) + self.g2c * math.cos(self.g2d*2*math.pi*x)
