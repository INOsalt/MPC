# Python module for the TRNSYS Type calling Python using CFFI
# Data exchange with TRNSYS uses a dictionary, called TRNData in this file (it is the argument of all functions).
# Data for this module will be in a nested dictionary under the module name,
# i.e. if this file is called "MyScript.py", the inputs will be in TRNData["MyScript"]["inputs"]
# for convenience the module name is saved in thisModule
#
# MKu, 2022-02-15

import numpy
import os
from main import MPC

thisModule = os.path.splitext(os.path.basename(__file__))[0]


# Initialization: function called at TRNSYS initialization
# ----------------------------------------------------------------------------------------------------------------------
def Initialization(TRNData):
    # This model has nothing to initialize

    return


# StartTime: function called at TRNSYS starting time (not an actual time step, initial values should be reported)
# ----------------------------------------------------------------------------------------------------------------------
def StartTime(TRNData):
    # Define local short names for convenience (this is optional)
    time = TRNData[thisModule]["inputs"][0] #Time
    step = TRNData[thisModule]["inputs"][1] #step
    a1 = TRNData[thisModule]["inputs"][2]
    a2 = TRNData[thisModule]["inputs"][3]

    # Calculate the outputs
    y = MPC.mpccal(time, step)

    # Set outputs in TRNData
    TRNData[thisModule]["outputs"][0] = y

    return


# Iteration: function called at each TRNSYS iteration within a time step
# ----------------------------------------------------------------------------------------------------------------------
def Iteration(TRNData):
    # Define local short names for convenience (this is optional)
    x = TRNData[thisModule]["inputs"][0]
    a0 = TRNData[thisModule]["inputs"][1]
    a1 = TRNData[thisModule]["inputs"][2]
    a2 = TRNData[thisModule]["inputs"][3]

    # Calculate the outputs
    y = a0 + a1 * total_sum * x + a2 * numpy.power(x, 2)

    # Set outputs in TRNData
    TRNData[thisModule]["outputs"][0] = y

    return


# EndOfTimeStep: function called at the end of each time step, after iteration and before moving on to next time step
# ----------------------------------------------------------------------------------------------------------------------
def EndOfTimeStep(TRNData):
    # This model has nothing to do during the end-of-step call

    return


# LastCallOfSimulation: function called at the end of the simulation (once) - outputs are meaningless at this call
# ----------------------------------------------------------------------------------------------------------------------
def LastCallOfSimulation(TRNData):
    # NOTE: TRNSYS performs this call AFTER the executable (the online plotter if there is one) is closed.
    # Python errors in this function will be difficult (or impossible) to diagnose as they will produce no message.
    # A recommended alternative for "end of simulation" actions it to implement them in the EndOfTimeStep() part,
    # within a condition that the last time step has been reached.
    #
    # Example (to be placed in EndOfTimeStep()):
    #
    # stepNo = TRNData[thisModule]["current time step number"]
    # nSteps = TRNData[thisModule]["total number of time steps"]
    # if stepNo == nSteps-1:     # Remember: TRNSYS steps go from 0 to (number of steps - 1)
    #     do stuff that needs to be done only at the end of simulation

    return