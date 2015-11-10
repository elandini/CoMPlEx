INIT = 1

REST = ['START_MODSAFE',[0,0]]
NEUTRAL = ['START_MODSAFE',[1,INIT]]
FDBK = ['START_MODSAFE',[2,INIT]]
LIN = ['START_MODSAFE',[3,INIT]]
SIN = ['START_MODSAFE',[4,INIT]]

TYPES = {'Vconst':LIN,'Fconst':FDBK,'Zconst':NEUTRAL}

try:
    import epz as tempEpz
    import inspect
    _,_,keys,_ = inspect.getargspec(tempEpz.CMD.__init__())
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


'''
SET_DACSTEP:D
SET_NUMT6TRIG:T
SET_TIMETRIG:M
SET_DAC_SOFT:B
SET_DAC_HARD:U
SET_TRIGGERS:N
SET_ZTRIG:L
SET_FTRIG:K
SET_TIM8PER:8
SET_SETPOINT:P
SET_PGAIN:Q
SET_IGAIN:R
SET_DGAIN:S
START_MODSAFE:O
SET_DACMODE:F
SET_TESTPIN:H
INIT_SPI2:I
SET_RAMPSIGN:C
SET_USECIRCBUFF:G
SET_MODEDBG:E
SET_DACTO0:J
SET_DAC_2OR4:A
SWITCH_SPI2:g
KILL:k
'''


class Interpreter(object):

    def __init__(self,env,device=None,tag='CMD'):

        if device is not None:
            env.device = device
        self.cmd = epz.CMD(env,tag=tag)


    ## Start the SPI communication
    def startDev(self):

        self.cmd.send('SWITCH_SPI2',1)


    ## Close the communication between the PIC and the raspberry PI
    def stopDev(self):

        self.cmd.send('SWITCH_SPI2',0)


    ## Turns the DSPIC circula buffer on
    def circulaBufferOn(self):

        self.cmd.send('SET_USECIRCBUFF',1)


    ## Turns the DSPIC circula buffer off
    def circulaBufferOff(self):

        self.cmd.send('SET_USECIRCBUFF',0)


    ## Set the unipolar DAC mode
    def goUnipolar(self):

        self.cmd.send('SET_DACMODE',0)


    ## Set the bipolar DAC mode
    def goBipolar(self):

        self.cmd.send('SET_DACMODE',1)


    ## Kill the epizmq process on the target raspberry PI
    def killDev(self):

        self.cmd.send('KILL')


    ## Set the Z piezo position
    # @param value The new wanted z position in Volt
    def setZ(self,value):

        self.cmd.send('SET_Z',value)


    ## Set the speed at which the piezo has to move
    # @param dacStep The number of steps to perform every 'T6' microseconds
    # @param t6TickNum The number of 'T6'you have to wait before tacking another step
    def setZramp(self,dacStep,t6TicksTum):

        self.cmd.send('SET_DACSTEP',dacStep)
        self.cmd.send('SET_NUMT6TRIG',t6TicksTum)


    ## Set the speed sign
    # @param value The wanted speed sign (0 = positive, 1 = negative)
    def setZrampSign(self,value):

        self.cmd.send('SET_RAMPSIGN',value)


    ## Set the PI feedback integral gain
    # @param value The new integral gain
    def setI(self,value):

        self.cmd.send('SET_IGAIN',value)

    ## Set the PI feedback proportional gain
    # @param value The new proportional gain
    def setP(self,value):

        self.cmd.send('SET_PGAIN',value)


    ## Set the PI feedback set point
    # @param value The new set point in Volt
    def setSetPoint(self,value):

        self.cmd.send('SET_SETPOINT',value)


    ## Set the deflection stop trigger
    # @param value The stop trigger value in Volt for the deflection
    # @param sign 0 = greathern than, 1 = less than
    def setDeflStopTrig(self,value,sign):

        self.cmd.send('SET_FTRIG',[value,sign])


    ## Set the z position stop trigger
    # @param value The stop trigger value in Volt for the z position
    # @param sign 0 = greathern than, 1 = less than
    def setZposStopTrig(self,value,sign):

        self.cmd.send('SET_ZTRIG',[value,sign])


    ## Set the time stop trigger
    # @param value The time stop trigger value in microseconds
    # @param sign 0 = greathern than, 1 = less than
    def setTimeStopTrig(self,value,sign):

        self.cmd.send('SET_TIMETRIG',[value,sign])

    ## Set which trigger you want to use
    # @param t 1 = time trigger in use, 0 = time trigger not in use
    # @param z 1 = z trigger in use, 0 = z trigger not in use
    # @param d 1 = deflection trigger in use, 0 = deflection trigger not in use
    def setTriggersSwitch(self,t,z,d):

        self.cmd.send('SET_TRIGGERS',[d,z,t])


    ## Start a chosen type of segment, determined by "type"
    # @param type The type of segment that has to be started
    def startSegment(self,type):

        self.cmd.send(*TYPES[type])


    ## Turns on the feedback
    def feedbackOn(self):

        self.cmd.send('SET_MODESAFE',[2,0])


    def setSine(self):
        pass


    ## Brings he system to the "rest" state
    def goToRest(self):

        self.cmd.send(*REST)

