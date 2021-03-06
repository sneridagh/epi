# -*- coding: utf-8 -*-
from epi.views.api import TemplateAPI
from pyramid.view import view_config
from epi.views.dashboard import BaseView
from epi.presencia import Presencia
from pyramid.response import Response

from epi.operacions import Operacions,ACTIVITATS
import time
from DateTime import DateTime
from epi.dateutils import *

@view_config(name="consultarPresencia", renderer='json')
class ConsultarPresenciaAJAX(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ConsultarPresenciaAJAX, self).__init__(context,request)
        self.marcatges_avui = []

    def __call__(self):
        """
        """

        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)

        try:
            presencia = Presencia(self.request, self.username,self.password)
        except:
            return {}

        persones_raw = presencia.getPresencia()

        presencia.closeBrowser()
        persones = '[{%s}]' % ('},{'.join([','.join(['"%s":"%s"' % (a,dd[a]) for a in dd.keys()]) for dd in persones_raw]))
        total_persones =len([a for a in persones_raw if u'Direcció' not in a['equip']])
        total_online = len([a for a in persones_raw if a['online']])
        #self.context.plone_log('################ %d %% de persones treballant' % ((total_online*100)/total_persones))
        #self.context.plone_log('################ %d  de %d de persones treballant' % (total_online,total_persones))

        return Response(persones.replace('"True"','true').replace('"False"','false').replace('None',''))

@view_config(name="marcarPresencia", renderer='epi:templates/capcalera.pt')
class MarcarPresenciaAJAX(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(MarcarPresenciaAJAX, self).__init__(context,request)
        self.marcatges_avui = []

    def __call__(self):
        page_title = "%s Dashboard" % self.username
        api = TemplateAPI(self.context, self.request, page_title)
        return dict(api = api)

    def getMarcatgesDAvui(self):
        """
        """
        return [dict(entrada=DateTimeToHM(a[0]),sortida=DateTimeToHM(a[1])) for a in self.marcatges_avui]

    def getMarcatges(self):
        """
        """
        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)

        presencia = Presencia(self.request, self.username, self.password)

        presencia.Marcar()
        now = DateTime()
        self.now = DateTimeToTT(now)
        t0 = time.time()

        tm = time.time()
        marcatges = presencia.getMarcatges(self.username)
        ##############
        ##############
        print "%.3f segons per obtenir marcatges" % (time.time()-tm)

        dies = {}
        marcadors = {}
        self.presenciaStatus = 'down'
        for data in marcatges:
            dia = marcatges[data]
            if self.now == data:
                self.marcatges_avui = dia['marcatges']

            fitxats = dia['total']
            marcatgeObert=None
            if dia['total']==0:
                for f in dia['marcatges']:
                    if f[1]==None:
                        marcatgeObert=f[0].ISO()
                        fitxatsTemporal = fitxats
                        self.presenciaStatus = 'up'
                    fitxats = fitxats + minutsEntreDates(f[0],f[1])

        presencia.closeBrowser()
        return Response('OK')

    def getPresenciaStatus(self):
        """
        """
        if self.presenciaStatus=='up':
            return True
        else:
            return False

@view_config(name="modificarTempsImputacio", renderer='json')
class ImputacionsAJAXModificar(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ImputacionsAJAXModificar, self).__init__(context,request)

    def __call__(self):
        """
        """
        options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = options['descomptar_30'] and 30 or 0
        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)

        dia=self.request.params.get('dia',None)
        hores=self.request.params.get('hores','').replace(' ','')
        hores = hores=='' and '0' or hores
        minuts=self.request.params.get('minuts','').replace(' ','')
        minuts = minuts=='' and '0' or minuts
        horesold=self.request.params.get('horesold','').replace(' ','')
        horesold = horesold=='' and '0' or horesold
        minutsold=self.request.params.get('minutsold','').replace(' ','')
        minutsold = minutsold=='' and '0' or minutsold
        comentari = self.request.params.get('comentari','').encode('iso-8859-1')

        iid=self.request.params.get('iid',None)

        year,month,day = time.strptime(dia,'%d%m%Y')[0:3]
        year = year.__str__()
        month = month.__str__().rjust(2,'0')
        day = day.__str__().rjust(2,'0')

        marcadors = self.epiUtility.recoverMarcadors(self.request, self.username)

        data_marcador = (day,month,year)
        #Si estem imputant en un dia que encara no hem fitxat,
        #encara no tenim marcador, per tant el construïm
        if not data_marcador in marcadors.keys():
            marcadors[data_marcador]=dict(marcades=0,marcatgeObert=None,aimputar=0,imputades=0,pendents=0)
        marcador = marcadors[data_marcador]

        anteriorsminutsimputats = HMaMinuts('%s:%s' % (horesold,minutsold))
        nousminutsimputats = HMaMinuts('%s:%s' % (hores,minuts))
        diferenciaentreimputacions = nousminutsimputats - anteriorsminutsimputats

        marcador['imputades'] = marcador['imputades']+diferenciaentreimputacions
        marcador['pendents'] = marcador['pendents']-diferenciaentreimputacions

        last_marcades = marcador['marcades']
        if marcador['marcatgeObert']:
            minutsafegits = minutsEntreDates(marcador['marcatgeObert'],None)
            marcador['marcades']=marcador['marcades']+minutsafegits
            marcador['aimputar']=marcador['marcades']-self.descompte_descans


        data='%s-%s-%s%%2000:00:00.000' % (year,month,day)

        resultat = operacions.modificarImputacio(hores,minuts,iid,comentari=comentari)

        resultat['marcades']=MinutsAHM(marcador['marcades'])
        resultat['aimputar']=MinutsAHM(marcador['aimputar'])
        resultat['imputades']=MinutsAHM(marcador['imputades'])
        resultat['pendents']=MinutsAHM(marcador['pendents'])

        #Reiniciem el comptador de hores marcades si encara no hem desfitxat cap cop avui
        if marcador['marcatgeObert'] and last_marcades==0:
            marcador['marcades']=0;

        operacions.closeBrowser()

        #Si hem pogut imputar, guardem el nou marcador
        if resultat['confirm']=='ok':
           marcadors[data_marcador]=marcador
           marcadors = self.epiUtility.saveMarcadors(self.request, self.username, marcadors)
        return resultat

@view_config(name="moureImputacio", renderer='json')
class ImputacionsAJAXMoure(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ImputacionsAJAXMoure, self).__init__(context,request)

    def __call__(self):
        """
        """
        options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = options['descomptar_30'] and 30 or 0

        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)

        amount=self.request.params.get('amount',None)
        hh,mm=amount.split(':')
        iid=self.request.params.get('iid','').split('-')[-1]
        newdate=self.request.params.get('newdate','').split('-')[-1]

        year,month,day = time.strptime(newdate,'%d%m%Y')[0:3]
        novadata = '%s-%s-%s' % (day,month,year)

        operacions.canviarImputacio(novadata,hh,mm,iid)

        operacions.closeBrowser()
        return {}

@view_config(name="copiarImputacio", renderer='json')
class ImputacionsAJAXCopiar(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ImputacionsAJAXCopiar, self).__init__(context,request)

    def __call__(self):
        """
        """
        options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = options['descomptar_30'] and 30 or 0

        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)

        amount=self.request.params.get('amount',None)
        hh,mm=amount.split(':')
        iid=self.request.params.get('iid','').split('-')[-1]
        newdate=self.request.params.get('newdate','').split('-')[-1]

        year,month,day = time.strptime(newdate,'%d%m%Y')[0:3]
        novadata = '%s-%s-%s' % (day,month,year)

        #operacions.canviarImputacio(novadata,hh,mm,iid)

        operacions.closeBrowser()
        return {}

@view_config(name="esborrarImputacio", renderer='json')
class ImputacionsAJAXEsborrar(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ImputacionsAJAXEsborrar, self).__init__(context,request)

    def __call__(self):
        """
        """
        options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = options['descomptar_30'] and 30 or 0

        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)

        dia=self.request.params.get('dia',None)
        hores=self.request.params.get('hores','').replace(' ','')
        hores = hores=='' and '0' or hores
        minuts=self.request.params.get('minuts','').replace(' ','')
        minuts = minuts=='' and '0' or minuts

        iid=self.request.params.get('iid',None)

        year,month,day = time.strptime(dia,'%d%m%Y')[0:3]
        year = year.__str__()
        month = month.__str__().rjust(2,'0')
        day = day.__str__().rjust(2,'0')

        marcadors = self.epiUtility.recoverMarcadors(self.request, self.username)

        data_marcador = (day,month,year)
        #Si estem imputant en un dia que encara no hem fitxat,
        #encara no tenim marcador, per tant el construïm
        if not data_marcador in marcadors.keys():
            marcadors[data_marcador]=dict(marcades=0,marcatgeObert=None,aimputar=0,imputades=0,pendents=0)
        marcador = marcadors[data_marcador]
        minutsesborrats = HMaMinuts('%s:%s' % (hores,minuts))
        marcador['imputades'] = marcador['imputades']-minutsesborrats
        marcador['pendents'] = marcador['pendents']+minutsesborrats

        last_marcades = marcador['marcades']
        if marcador['marcatgeObert']:
            minutsafegits = minutsEntreDates(marcador['marcatgeObert'],None)
            marcador['marcades']=marcador['marcades']+minutsafegits
            marcador['aimputar']=marcador['marcades']-self.descompte_descans


        data='%s-%s-%s%%2000:00:00.000' % (year,month,day)

        resultat = operacions.esborrarImputacio(iid)

        resultat['marcades']=MinutsAHM(marcador['marcades'])
        resultat['aimputar']=MinutsAHM(marcador['aimputar'])
        resultat['imputades']=MinutsAHM(marcador['imputades'])
        resultat['pendents']=MinutsAHM(marcador['pendents'])

        #Reiniciem el comptador de hores marcades si encara no hem desfitxat cap cop avui
        if marcador['marcatgeObert'] and last_marcades==0:
            marcador['marcades']=0;

        #Si hem pogut imputar, guardem el nou marcador
        if resultat['confirm']=='ok':
           marcadors[data_marcador]=marcador
           resultat['hores']=hores
           resultat['minuts']=minuts.rjust(2,'0')
           marcadors = self.epiUtility.saveMarcadors(self.request, self.username, marcadors)

        operacions.closeBrowser()
        return resultat

@view_config(name="crearImputacio", renderer='json')
class ImputacionsAJAXCrear(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ImputacionsAJAXCrear, self).__init__(context,request)

    def __call__(self):
        """
        """
        options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = options['descomptar_30'] and 30 or 0

        dia=self.request.params.get('dia',None)
        hores=self.request.params.get('hores',None).replace(' ','')
        hores = hores=='' and '0' or hores
        minuts=self.request.params.get('minuts',None).replace(' ','')
        minuts = minuts=='' and '0' or minuts
        opcio=self.request.params.get('opcio',None)
        tipus=self.request.params.get('tipus',None)

        year,month,day = time.strptime(dia,'%d%m%Y')[0:3]
        year = year.__str__()
        month = month.__str__().rjust(2,'0')
        day = day.__str__().rjust(2,'0')


        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)
        marcadors = self.epiUtility.recoverMarcadors(self.request, self.username)

        data_marcador = (day,month,year)
        #Si estem imputant en un dia que encara no hem fitxat,
        #encara no tenim marcador, per tant el construïm
        if not data_marcador in marcadors.keys():
            marcadors[data_marcador]=dict(marcades=0,marcatgeObert=None,aimputar=0,imputades=0,pendents=0)
        marcador = marcadors[data_marcador]

        nousminutsimputats = HMaMinuts('%s:%s' % (hores,minuts))
        marcador['imputades'] = marcador['imputades']+nousminutsimputats
        marcador['pendents'] = marcador['pendents']-nousminutsimputats

        last_marcades = marcador['marcades']
        if marcador['marcatgeObert']:
            minutsafegits = minutsEntreDates(marcador['marcatgeObert'],None)
            marcador['marcades']=marcador['marcades']+minutsafegits
            marcador['aimputar']=marcador['marcades']-self.descompte_descans

        data='%s-%s-%s%%2000:00:00.000' % (year,month,day)
        if tipus=='ordre':
            orderId,orderItemSeqId = opcio.split(',')
            resultat = operacions.imputarOrdre(data,hores,minuts,orderId,orderItemSeqId)

        if tipus=='activitat':
            activitatId = opcio
            proces = [a['nomProces'] for a in ACTIVITATS if a['activitatId']==activitatId][0]
            resultat = operacions.imputarActivitat(data,hores,minuts,proces,activitatId)

        if tipus in ['tiquet','problema']:
            tiquetId = opcio
            funcioImputar = getattr(operacions,'imputar%s' % tipus.capitalize())
            resultat = funcioImputar('%s-%s-%s' % (day,month,year),hores,minuts,tiquetId)
        resultat['marcades']=MinutsAHM(marcador['marcades'])
        resultat['aimputar']=MinutsAHM(marcador['aimputar'])
        resultat['imputades']=MinutsAHM(marcador['imputades'])
        resultat['pendents']=MinutsAHM(marcador['pendents'])

        #Reiniciem el comptador de hores marcades si encara no hem desfitxat cap cop avui
        if marcador['marcatgeObert'] and last_marcades==0:
            marcador['marcades']=0;


        operacions.closeBrowser()

        #Si hem pogut imputar, guardem el nou marcador
        if resultat['confirm']=='ok':
           marcadors[data_marcador]=marcador
           marcadors = self.epiUtility.saveMarcadors(self.request, self.username, marcadors)
        return resultat

@view_config(name="comentariImputacio")
class ComentariImputacio(BaseView):
    """
    """
    def  __init__(self,context,request):
        """
        """
        super(ComentariImputacio, self).__init__(context,request)
        
    def __call__(self):
        """
        """
        iid = self.request.params.get('iid','')
        return Response(self.getComentariImputacio(iid))

    def getComentariImputacio(self,iid):

        operacions = Operacions(self.request, self.username, self.password, self.eid, self.tid)
        comentari = operacions.obtenirComentariImputacio(iid)

        operacions.closeBrowser()
        return comentari