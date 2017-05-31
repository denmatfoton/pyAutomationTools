import math
from math import sin
from math import cos
from datetime import datetime

def jd_to_date(jd):
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year, month, day

def date_to_jd(year, month, day):
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)
        
    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)
        
    D = math.trunc(30.6001 * (monthp + 1))
    
    jd = B + C + D + day + 1720994.5
    
    return jd

def dayFraction2Time(days):
    fraction = (days % 1) * 24
    hours = int(math.floor(fraction))
    fraction = (fraction % 1) * 60
    minutes = int(math.floor(fraction + 0.5))
    return hours, minutes


def calculateSolarEvents(longitude, latitude, timezone, date, twilightAngel):
    initialJdate = 2451545.0
    perihelion = 102.9372 # may slitely change

    jDate = date_to_jd(date.year, date.month, date.day + 0.5)

    n = jDate - initialJdate + 0.0008

    #approximation of mean solar time
    Js = n - longitude / 360.0

    #solar mean anomaly
    M = (357.5291 + 0.98560028 * Js) % 360
    Mrad = M * math.pi / 180

    #equation of the center value needed to calculate lambda
    C = 1.9148 * math.sin(Mrad) + 0.02 * math.sin(2 * Mrad) + 0.0003 * math.sin(3 * Mrad)

    lambd = (M + C + 180 + perihelion) % 360
    lambdRad = lambd * math.pi / 180

    Jtransit = initialJdate + Js + 0.0053 * math.sin(Mrad) - 0.0069 * math.sin(2 * lambdRad)
    Jtransit += timezone / 24.0

    transitDate = jd_to_date(Jtransit)
    transitTime = transitDate[2]

    sinDelta = math.sin(lambdRad) * math.sin(23.44 * math.pi / 180)

    delta = math.asin(sinDelta)
    
    Fi = latitude * math.pi / 180
    sinFiSinDelta = sin(Fi) * sinDelta
    cosFiCosDelta = cos(Fi) * cos(delta)
    cosOmega = (sin(-0.83 * math.pi / 180) - sinFiSinDelta) / cosFiCosDelta
    cosKsi = -(sin(twilightAngel * math.pi / 180) + sinFiSinDelta) / cosFiCosDelta

    if math.fabs(cosOmega) < 1:
        omegaInTime = math.acos(cosOmega) / 2 / math.pi
        sunrizeTime = dayFraction2Time(transitTime - omegaInTime)
        sunsetTime = dayFraction2Time(transitTime + omegaInTime)
    else:
        sunrizeTime = sunsetTime = None
    
    if math.fabs(cosKsi) < 1:
        ksiInTime = math.acos(cosKsi) / 2 / math.pi
        morningTwilight = dayFraction2Time(transitTime - ksiInTime)
        eveningTwilight = dayFraction2Time(transitTime + ksiInTime)
    else:
        morningTwilight = eveningTwilight = None
    
    return sunrizeTime, sunsetTime, morningTwilight, eveningTwilight, dayFraction2Time(transitTime)
