# This is a dummy routine that serves as an example of how routines operate
# and how to connect routines to the UI




# These modules aren't needed for all routines, we just happen to use them here
import numpy
import math


class deldep(object):
	def __init__(self,id):
		self.id=id
	def __del__(self):
		print("deldep with id {id} deleted".format(id=self.id))


# Required function: validateParamters. function name = routineNameValidateParameters
# Takes as inputs the same parameters that the routine takes
# Determines whether the given set of parameters is valid or not
# Returns True if they are valid
# Otherwise, returns a string describing what issues(s) it found with the parameters.
def dummyRoutineValidateParameters(
	numPoints,
	stepDelay,
	xInitial,
	xFinal,
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

	if numPoints < 1:
		return "number of points must be at least 1"

	if stepDelay < 0:
		return "step delay cannot be negative"

	# If we get to this point, there aren't any issues, so we return True, indicating that the set of parameter given is valid.
	return True




# The routine object itself. class name = routineNameInstance
#
class dummyRoutineInstance(object):

	def __init__(self,
		numPoints,
		stepDelay,
		xInitial,
		xFinal,
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


		self.numPoints = numPoints      # total number of points
		self.numSteps  = numPoints - 1  # number of steps before completion
		self.stepDelay = stepDelay      # delay in milliseconds between steps

		self.xInitial  = xInitial  # X value at beginning 
		self.xFinal    = xFinal    # X value at end
		                           # X scales linearly between these two values during the routine

		               # Graph 1 variables. Graph 1 is a polynomial (order 5)
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



	# Required function: getDisplayData
	# This function is called by the UI to retrieve data for the routine's display
	# 
	# The most basic data that this function returns are the progress (percent completion, from 0 to 1) and the status, a short descriptive string.
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
	# The instance of the routine will be deleted IMMEDIATELY after this function completes.
	def cancel(self):
		pass










	def addPoint(self):
		p = self.nextPoint / self.numPoints
		x = p*self.xFinal + (1-p)*self.xInitial

		self.g1Data[self.nextPoint] = numpy.array([x,self.calcY1(x)])
		self.g2Data[self.nextPoint] = numpy.array([x,self.calcY2(x)])

	def calcY1(self,x):
		return self.g1a + self.g1b*x + self.g1c*x**2 + self.g1d*x**3 + self.g1e*x**4 + self.g1f*x**5

	def calcY2(self,x):
		return self.g2a * math.sin(self.g2b*2*math.pi*x) + self.g2c * math.cos(self.g2d*2*math.pi*x)
