REST = ['O',0]
NEUTRAL = ['O',1]
FDBK = ['O',2]
LIN = ['O',3]
SIN = ['O',4]

TYPES = {'Vconst':LIN,'Fconst':FDBK,'Zconst':NEUTRAL}

try:
    import epz as tempEpz
    import inspect
    _,_keys,_ = inspect.getargspec(tempEpz.CMD.__init__())
    if 'tag' not in keys:
        from libs.epz import epz as tempEpz
    epz = tempEpz
except:
    from libs.epz import epz

# N set the triggers. The triggers are, in order, adc (deflection), dac (z position), time
# 1 = used, 0 = not used

#Triggers
# K = set adc (deflection) stop trigger (Volts)
# L = set dac (z position) stop trigger (Volts)
# M = set time stop trigger in microseconds
# P = set the setpoint for the feedback (-1, +1)
# Q = set the proportional gain for the feedback (0.0 to 1.0)
# R = set the integral gain for the feedback (0.0 to 1.0)
# S = set the differential gain for the feedback (0.0 to 1.0)
# B = set DAC output (Volts)
# D = set the piezo speed (Volt/s)
# C = set the piezo speed sign

class Interpreter(object):

    def __init__(self,env,device=None,tag='CMD'):

        if device is not None:
            env.device = device
        self.cmd = epz.CMD(env,tag=tag)


    ## Start the SPI communication
    def startDev(self):

        self.cmd.send('g',1)


    ## Set the Z piezo position
    # @param value The new wanted z position in Volt
    def setZ(self,value):

        self.cmd.send('B',value)


    ## Set the speed at which the piezo has to move
    # @param value The wanted speed in Volt/s
    def setZspeed(self,value):

        self.cmd.send('D',value)


    ## Set the speed sign
    # @param value The wanted speed sign (0 = positive, 1 = negative)
    def setZspeedSign(self,value):

        self.cmd.send('C',value)


    ## Set the PI feedback integral gain
    # @param value The new integral gain
    def setI(self,value):

        self.cmd.send('R',value)

    ## Set the PI feedback proportional gain
    # @param value The new proportional gain
    def setP(self,value):

        self.cmd.send('Q',value)


    ## Set the PI feedback set point
    # @param value The new set point in Volt
    def setSetPoint(self,value):

        self.cmd.send('P',value)


    ## Set the deflection stop trigger
    # @param value The stop trigger value in Volt for the deflection
    # @param sign 0 = greathern than, 1 = less than
    def setDeflStopTrig(self,value,sign):

        self.cmd.send('K',[value,sign])


    ## Set the z position stop trigger
    # @param value The stop trigger value in Volt for the z position
    # @param sign 0 = greathern than, 1 = less than
    def setZposStopTrig(self,value,sign):

        self.cmd.send('L',[value,sign])


    ## Set the time stop trigger
    # @param value The time stop trigger value in microseconds
    # @param sign 0 = greathern than, 1 = less than
    def setTimeStopTrig(self,value,sign):

        self.cmd.send('M',[value,sign])

    ## Set which trigger you want to use
    # @param t 1 = time trigger in use, 0 = time trigger not in use
    # @param z 1 = z trigger in use, 0 = z trigger not in use
    # @param d 1 = deflection trigger in use, 0 = deflection trigger not in use
    def setTriggersSwitch(self,t,z,d):

        self.cmd.send('N',[d,z,t])


    ## Start a chosen type of segment, determined by "type"
    # @param type The type of segment that has to be started
    def startSegment(self,type):

        self.cmd.send(*TYPES[type])


    ## Turns on the feedback
    def feedbackOn(self):

        self.cmd.send('E',2)


    def setSine(self):
        pass


    ## Brings he system to the "rest" state
    def goToRest(self):

        self.cmd.send(*REST)

