from epi.views.dashboard import dashboardView
from epi.views.api import TemplateAPI
from pyramid.view import view_config

from epi.presencia import Presencia
from epi.presencia import MOTIUS_PERMISOS as MOTIUS
from epi.operacions import Operacions,ACTIVITATS
import time
from DateTime import DateTime
import datetime
import transaction
from epi.dateutils import *
from epi import EPI_OPTIONS,EPI_OPTIONS_TYPES,MONTH_NAMES
from BTrees.OOBTree import OOBTree

from urllib2 import URLError
from copy import deepcopy


class MesView(dashboardView):
    """
    """
    def  __init__(self,context,request):
        """
        """
        super(MesView, self).__init__(context,request)


class AnyView(MesView):
    """
    """

    def __call__(self):
        """
        """
        portal_url = self.context.portal_url.getPortalObject().absolute_url()
        username, password = self.getAuthenticationToken()

        #Esborrem la cache si hem clicat al logo de l'epi
        if self.request.get('refresh',False):
            self.invalidateAll()
            self.request.response.redirect(portal_url)
            return

        #No estem identificats
        if username==None:
            self.request.response.redirect(portal_url+'/login_form')
            return ''
        else:
            #Si estem identificats, comprovem que tinguem els codis d'usuari del gestor
            # sino, els agafem i els guardem
            eid,tid = self.context.portal_epi_data.getUserCodes(username)
            if eid==None or tid==None:
                 operacions = Operacions(username,password)
                 #Si no podem inicialitzar operacions tornarem a demanar que es logini
                 #podria ser que estiguessim logats com a admin...
                 if operacions.initialized:
                     eid,tid = operacions.obtenirCodisUsuari()
                     self.context.portal_epi_data.setUserCodes(username,eid,tid)
                     operacions.closeBrowser()
                 else:
                     self.request.response.redirect(portal_url+'/login_form')
                     operacions.closeBrowser()
                     return ''

        self.template = ViewPageTemplateFile('vista-any.pt')
        try:
            return self.template()
        except URLError:
            self.request.response.redirect('http://epi.beta.upcnet.es/errors/111.html')
#        else:
#            self.request.response.redirect('http://epi.beta.upcnet.es/errors/epi.html')


    def  __init__(self,context,request):
        """
        """
        self.context = context
        self.request = request
        self.marcatges_avui = []
        now = DateTime()
        self.now = DateTimeToTT(now)


    def getAny(self,query_year=None):
        """
        """
        
        hores_s = ['horesatreballargeneriques','horesatreballar','horestreballades','horesimputables','horesimputades','horespendents','horesvacances','horespermisos']
        query = self.request.get('query',query_year)
        start_date = query==None and ('01','01',self.now[2]) or tuple(query.split('-')[::-1])
        year = start_date[2]
        start_month = int(start_date[1])
        start_day = start_date[0]
        
        fdom = DateTime('%s-01-01' % (year))
        fdom_dow = fdom.dow()==0 and 7 or fdom.dow()
        fdow = addDays(fdom,(fdom_dow*-1)+1)

        needHistoric = self.needHistoric(self.now,DateTimeToTT(fdom))
        dies = self.getDies(needHistoric,first_day=fdom,last_day=lastDayOfYear(fdom))

        
        mesos = []
        
        #inicialitzar totes les variables d'hores a 0
        totals = {}
        for hs in hores_s:
            totals[hs]='00:00'

        for nummonth in range(1,13):
            startday = start_month==nummonth and start_day or '01'
            query_date = '%s-%02d-%s' % (year,nummonth,startday)
            print query_date
            newneedHistoric = self.needHistoric(self.now,DateTimeToTT(DateTime(query_date)))
            if newneedHistoric!=needHistoric:
                needHistoric = newneedHistoric
                dtq = DateTime(query_date)
                dies = self.getDies(needHistoric,first_day=dtq,last_day=lastDayOfYear(dtq))
            mes = self.getMes(query_date=query_date,dies_param=dies)

            if nummonth<start_month:
                # incialitzar les varibles d'hores del mes a 0 si estem filtrant
                for hs in hores_s:
                    mes[hs]='00:00'                                                          

            mes['query_date']=query_date
            
            # suma totes les variables d'hores de cada mes als totals
            for hs in hores_s:
                totals[hs]=sumaHM(totals[hs],mes[hs])
       
            mesos.append(mes)

        totals['horespendents']=MinutsAHM(HMaMinuts(totals['horesatreballar'])-HMaMinuts(totals['horestreballades']))

        minutsvacances = HMaMinuts(totals['horesvacances'])
        diesvacances = minutsvacances/(7*60)
        restahoresvacances = (minutsvacances - (diesvacances*7*60))/60
        totals['dv']=diesvacances
        totals['hv']=restahoresvacances

        return dict(title=year,mesos=mesos,totals=totals)
