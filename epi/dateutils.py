# -*- coding: utf-8 -*-
from DateTime import DateTime
import datetime
import time

def minutsEntreDates(t1,t2):
    """
    Calcula la diferencia entre minut entre dues dates en format DateTime de zope
    Si no es dona el segon paràmetre, es fa servir la data actual
    """
    t1 = t1.__class__==str and DateTime(t1) or t1
    if t2==None:
        t2=DateTime()
    tt1 = time.strptime(t1.ISO(),"%Y-%m-%d %H:%M:%S")
    tt2 = time.strptime(t2.ISO(),"%Y-%m-%d %H:%M:%S")
    difference = time.mktime(tt2) - time.mktime(tt1)
    return int(difference/60)

def HMaMinuts(hm,sep=':'):
    """
    Es calcula la quantita de minuts totals d'un temps en format hh:mm
    contingut en una cadena de text. Es pot passar al parametre sep una altra cadena per
    interpretar com a separador
    """
    h,m = hm.split(sep)
    return int(h)*60+int(m)

def MinutsAHM(m):
    """
    Es genera una cadena de text en format hh:mm a partir d'una quantitat de minuts
    """
    hores = int(m/60.0)
    horesenminuts = int(hores*60)
    minuts = m-horesenminuts

    minus = (hores<0 or minuts<0) and '-' or ''
    minuts = minuts<0 and minuts*-1 or minuts
    hores = hores<0 and hores*-1 or hores
    text = '%s:%s' % (str(hores).rjust(2,'0'),str(minuts).rjust(2,'0'))

    return '%s%s' % (minus,text)

def sumaHM(hm1,hm2):
    """
    Suma dues quantitats de temps en format hh:mm
    """
    m1 = HMaMinuts(hm1)
    m2 = HMaMinuts(hm2)
    mt = m1+m2
    return MinutsAHM(mt)

def DateTimeToTT(dt):
    """
    Agafa un DateTime i n'extreu la data en una tupla simple (dia,mes,any)
    """
    return (dt.dd(),dt.mm(),dt.year().__str__())

def TTToDateTime(tt):
    """
    Agafa una data en tupla simple (dia,mes,any) i la passa a DateTime
    """
    return DateTime('%s/%s/%s' % (tt[2],tt[1],tt[0]))

def DateTimeToHM(dt):
    """
    Agafa un datetime i n'extreu el temps en format hh:mm
    """
    if dt:
        return dt.strftime('%H:%M')
    else:
        return None

def addDays(date,days):
    """
    Suma tants dies com s'indica a days a date i retorna un DateTime
    """
    tdate = datetime.datetime(date.year(),date.month(),date.day())
    tdate = tdate + datetime.timedelta(days=days)
    return DateTime(tdate.strftime('%Y/%m/%d'))

def firstDayOfWeek(dtime=None):
    """
    """
    dt = dtime==None and DateTime() or dtime
    return addDays(dt,1-dt.dow())


def lastDayOfWeek(dtime=None):
    """
    """
    dt = dtime==None and DateTime() or dtime
    fdow = firstDayOfWeek(dt)
    return addDays(fdow,6)


def lastDayOfMonth(dtime=None):
    dt = dtime==None and DateTime() or dtime
    month = '%02d' % (dt.month())
    try:
        ldom = DateTime('31/%s/%d' % (month,dt.year()))
    except DateTime.DateError:
        try:
            ldom = DateTime('30/%s/%d' % (month,dt.year()))
        except DateTime.DateError:
            try:
                 ldom = DateTime('29/%s/%d' % (month,dt.year()))
            except:
                 ldom = DateTime('28/%s/%d' % (month,dt.year()))
    return ldom


def lastDayOfYear(dtime=None):
    """
    """
    dt = dtime==None and DateTime() or dtime
    ldoy = DateTime('31/12/%d' % (dt.year()))
    return ldoy

def daysBetweenDates(dt1,dt2):
    """
    """

    date1 = datetime.date(dt1.year(), dt1.month(), dt1.day())
    date2 = datetime.date(dt2.year(), dt2.month(), dt2.day())

    dateDiff = date2 - date1
    #
    return dateDiff.days
    
def monthsDiff(d1,d2):
    """
    """
    t1 = [int(a) for a in d1]
    t2 = [int(a) for a in d2]
    
    monthsdiff = 0
    
    while t1[2]!=t2[2] or t1[1]!=t2[1]:
        if t1[1]==1:
            t1[1]=12
            t1[2]=t1[2]-1
        else:
            t1[1]=t1[1]-1
        monthsdiff = monthsdiff + 1
    return monthsdiff
