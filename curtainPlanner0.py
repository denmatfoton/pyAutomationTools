import os
import sys
import argparse
from datetime import datetime
from sunEventsCalculator import calculateSolarEvents

pathToRFCodeSender = "/home/pi/smarthome/433RF/RFCodeSender"
pathToRFCodes = "/home/pi/smarthome/433RF/rfcodes.bin"

#Time to open/close. May may be exatc time "9:20", sunrise/sunset "s", or twilight "t"
#                  | living room    | bedroom         |
curtainTiming    = [ ["s", "t"]     , ["8:30", "t"]   ] # [open_time, close_time]
curtainEnabled   = [ True           , True            ]
#RF codes names
curtainCodeNames = [ ["curtain1open", "curtain1close"], ["curtain2open", "curtain2close"]  ]

#location to calculate sun events
myLongitude = 27.694047
myLatitude = 53.930553
myTimezone = 3
twilightAngel = 4


def hours(time):
    return int(time[:time.find(':')])

def minutes(time):
    return int(time[time.find(':') + 1:])

def compareTime(time1, time2):
    t1 = hours(time1) * 100 + minutes(time1)
    t2 = hours(time2) * 100 + minutes(time2)
    
    if t1 > t2:
        return 1
    if t1 < t2:
        return -1
    return 0

def planTask(cmdline, time):
    taskFile = "task.sh"
    f = open(taskFile, "w")
    f.write(cmdline)
    f.close()

    atCmd = "at -f " + taskFile + " " + time
    os.system(atCmd)
    
    os.remove(taskFile)

def parseArgument(arg):
    defaultVal = (1, 1)
    
    if arg is None:
        return defaultVal
    if arg.find(':') != -1:
        return (0, arg)
    if arg == 's':
        return (1, 0)
    if arg == 't':
        return (1, 1)
    return defaultVal

def strTimeFromTuple(tuple):
    minutes = str(tuple[1])
    if len(minutes) == 1:
        minutes = '0' + minutes
    return str(tuple[0]) + ':' + minutes


date = datetime.now()
solarEvents = calculateSolarEvents(myLongitude, myLatitude, myTimezone, date, twilightAngel)

now = date.strftime("%H:%M")

tasks = []

for i in xrange(0, len(curtainEnabled)):
    if not curtainEnabled[i]:
        continue
    
    operationTime = ["0:0", "0:0"]
    for operation in xrange (0, 2): 
        time = parseArgument(curtainTiming[i][operation])
        
        if time[0] == 0:
            operationTime[operation] = time[1]
        else:
            solarTime = solarEvents[time[1] * 2 + operation]
            if solarTime is None:
                print "Solar event doesn't exist"
                continue
            operationTime[operation] = strTimeFromTuple(solarTime)
        
    curtainOpenCmd = '{} {} {}'.format(pathToRFCodeSender, curtainCodeNames[i][0], pathToRFCodes)
    curtainCloseCmd = '{} {} {}'.format(pathToRFCodeSender, curtainCodeNames[i][1], pathToRFCodes)
    
    if compareTime(operationTime[0], operationTime[1]) != -1:
        print "Incorrect time: curtainOpenTime >= curtainCloseTime"
        continue
    if compareTime(operationTime[0], now) == 1:
        #print "plan all tasks"
        tasks.append((operationTime[0], curtainOpenCmd))
        tasks.append((operationTime[1], curtainCloseCmd))
    elif compareTime(operationTime[1], now) == 1:
        #print "open now, plan closing"
        os.system(curtainOpenCmd)
        tasks.append((operationTime[1], curtainCloseCmd))
    else:
        #print "close now"
        os.system(curtainCloseCmd)

tasks = sorted(tasks, cmp = compareTime, key = lambda task: task[0])

prevTime = ""
cmd = ""

for i in xrange(0, len(tasks)):
    cmd += tasks[i][1] + "\n"
    if i + 1 == len(tasks) or tasks[i][0] != tasks[i + 1][0]:
        planTask(cmd, tasks[i][0])
        cmd = ""
