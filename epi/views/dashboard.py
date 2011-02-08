# -*- coding: utf-8 -*-
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from epi.views.api import TemplateAPI
from pyramid.view import view_config
from epi.models import Root
from epi.interfaces import IEPIUtility

from epi.presencia import Presencia
from epi.presencia import MOTIUS_PERMISOS as MOTIUS
from epi.operacions import Operacions,ACTIVITATS
import time

from DateTime import DateTime
from epi.dateutils import *
from epi import MONTH_NAMES, EPI_OPTIONS, EPI_OPTIONS_TYPES

from zope.app.cache.interfaces.ram import IRAMCache
from zope.component import getUtility
from copy import deepcopy

from beaker.cache import cache_region

@view_config(name="prova.html", renderer='epi:templates/mytemplate.pt')
def unaltre(context, request):
    page_title = getHola('svsdf')
    #page_title = "%s Dashboard" % "prova"
    api = TemplateAPI(context, request, page_title)
    hola = getHola('asd')
    return dict(api = api, project=page_title, hola=hola)  

@cache_region('default_term', 'paquillo')
def getHola(param):
    print param
    return 'True'

@view_config(name="prova2.html", renderer='epi:templates/mytemplate.pt')
class provaView(object):

    def  __init__(self,context,request):
        """
        """
        self.context = context
        self.request = request

    def __str__(self):
        return "%s.%s" % (self.__module__, self.__class__.__name__)
    
    def __call__(self):
        page_title = self.getHola('svsdf')
        #page_title = "%s Dashboard" % "prova"
        api = TemplateAPI(self.context, self.request, page_title)
        return dict(api = api, project=page_title, hola=self.getHola('asd'))
    
    @cache_region('default_term')
    def getHola(self, param):
        print param
        return 'True'

class BaseView(object):
    """ Classe base de totes les vistes
    """
    def  __init__(self,context,request):
        """
        """
        self.context = context
        self.request = request

        # Faig la utility disponible com atribut de la classe mare
        registry = self.request.registry
        self.epiUtility=registry.getUtility(IEPIUtility)
        
        self.username, self.password = self.getAuthenticationToken()

    def getAuthenticationToken(self):
        """
        """
        registry = self.request.registry
        epiUtility=registry.getUtility(IEPIUtility)
        
        self.username = authenticated_userid(self.request)
        self.password = epiUtility.getUserPassword(self.request, self.username)
        self.eid,self.tid = epiUtility.getUserCodes(self.request, self.username)
        return (self.username,self.password)

    def invalidateAll(self):
        """
        """
        ramcache = getUtility(IRAMCache)
        ramcache.invalidate('obtenirImputacions')
        ramcache.invalidate('obtenirPortalTecnic')
        ramcache.invalidate('getMarcatges')
        ramcache.invalidate('getPermisos')
        
    def currentDayNumber(self):
        return '%02d' % DateTime().day()
        
    def getMotius(self):
        """
        """
        return [dict(title=a,image=MOTIUS[a]['imatge']) for a in MOTIUS.keys()]

@view_config(name='vista-any', renderer='epi:templates/vista-any.pt', permission='view')
@view_config(name='vista-mes', renderer='epi:templates/vista-mes.pt', permission='view')
@view_config(context=Root, renderer='epi:templates/dashboard.pt', permission='view')
class dashboardView(BaseView):

    def  __init__(self,context,request):
        """
        """
        super(dashboardView, self).__init__(context,request)
        
        #Si estem identificats, comprovem que tinguem els codis d'usuari del gestor
        # sino, inicialitzem Operacions i seguidament els agafem i els guardem
        if self.eid==None or self.tid==None:
             operacions = Operacions(self.request, self.username, self.password)
             #Si inicialitzem operacions correctament, obtenim el codi d'usuari i els guardem
             if operacions.initialized:
                 self.eid, self.tid = operacions.obtenirCodisUsuari()
                 self.epiUtility.setUserCodes(self.request, self.username, self.eid, self.tid)
    
                 operacions.closeBrowser()
        
        self.marcatges_avui = []
        now = DateTime()
        self.now = DateTimeToTT(now)
        # if self.request.get('relogin',False):
        #     self.portal_epi_data.sessions=OOBTree()

    def __call__(self):
        """
        """
        
        # #Esborrem la cache si hem clicat al logo de l'epi
        # if self.request.get('refresh',False):
        #     self.invalidateAll()
        #     self.request.response.redirect(portal_url)
        #     return

        page_title = "%s Dashboard" % self.username
        api = TemplateAPI(self.context, self.request, page_title)
        return dict(api = api)

    def getPreviousMonth(self,actual):
        """
        """
        year = actual.year()
        month = actual.month()
        if month>1:
            month = month-1
        else:
            month = 12
            year = year -1
        return '%d-%s-01' % (year, month.__str__().rjust(2,'0'))

    def getNextMonth(self,actual):
        """
        """
        year = actual.year()
        month = actual.month()
        if month<12:
            month = month+1
        else:
            month = 1
            year = year +1
        return '%d-%s-01' % (year, month.__str__().rjust(2,'0'))

    def needHistoric(self,now,current):
        """
        """
        needHistoric=False

        # si la data que consultem no és futura i
        # si hi ha una diferencia de mes de 2 mesos necessitem historic
        if not (current[2]>now[2] or (current[2]==now[2] and current[1]>now[1])):
          if monthsDiff(now,current)>=2:
            needHistoric=True

        return needHistoric and current[2] or None

    def getMes(self,query_date=None, dies_param=None):
        """
        """
        self.options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = self.options['descomptar_30'] and 30 or 0


        query = query_date==None and self.request.get('query','%s-%s-%s' % (self.now[2],self.now[1],'01')) or query_date
        base = query==None and DateTime() or DateTime(query)
        base = base.earliestTime()

        fdom = DateTime('%d-%02d-%02d' % (base.year(), base.month(), base.day()) )
        fdom_dow = fdom.dow()==0 and 7 or fdom.dow()
        fdow = addDays(fdom,(fdom_dow*-1)+1)
        week = 0

        # Si estem executant la vista anual, ja haurem recollit els dies, i els tindrem a dies_param
        # d'aquesta manera ens evitem les inicialitzacions de presencia i gestor que es fan a getDies, (tot i cachejades, cnosumeixen algun segon)
        # i fem 1 única petició per tot l'historic
        dies = dies_param==None and self.getDies(self.needHistoric(self.now,DateTimeToTT(fdom)),first_day=fdom,last_day=lastDayOfMonth(fdom)) or dies_param

        setmanes = []

        mes = dict( id='%d%s' % (base.year(), base.month().__str__().rjust(2,'0')),
                    monthname=MONTH_NAMES[base.Month()],
                    year=base.year(),
                    horesatreballargeneriques='00:00',
                    horestreballades='00:00',
                    horesatreballar='00:00',
                    horesimputades='00:00',
                    horesimputables='00:00',
                    horespermisos='00:00',
                    horesvacances='00:00',
                    setmanes = [],
                    mesanterior = self.getPreviousMonth(fdom),
                    messeguent = fdom.year()!=self.now[2] and self.getNextMonth(fdom) or None
                    )
        while fdow.month()==base.month() or week==0:
            setmana = self.getSetmana(dies,fdow,day_filter=base)
            if setmana['dies']!=[]:
                setmanes.insert(0,setmana)
                mes['horesatreballar']=sumaHM(mes['horesatreballar'],setmana['horesatreballar'])
                mes['horesatreballargeneriques']=sumaHM(mes['horesatreballargeneriques'],setmana['horesatreballargeneriques'])
                mes['horestreballades']=sumaHM(mes['horestreballades'],setmana['horestreballades'])
                mes['horesimputables']=sumaHM(mes['horesimputables'],setmana['horesimputables'])
                mes['horesimputades']=sumaHM(mes['horesimputades'],setmana['horesimputades'])
                mes['horespermisos']=sumaHM(mes['horespermisos'],setmana['horespermisos'])
                mes['horesvacances']=sumaHM(mes['horesvacances'],setmana['horesvacances'])
            week = week+1
            fdow = addDays(fdow,7)
        mes['setmanes']=setmanes
        try:
            mes['percentatgeimputat']= '%.1f' % ( (HMaMinuts(mes['horesimputades'])*100)/HMaMinuts(mes['horesimputables']) )
        except:
            mes['percentatgeimputat']= 0
        mes['horespendents'] = MinutsAHM(HMaMinuts(mes['horesatreballar'])-HMaMinuts(mes['horestreballades']))
        return mes

    def getSetmanes(self):
        """
        """
        self.options = self.epiUtility.getEPIOptions(self.request, self.username)
        self.descompte_descans = self.options['descomptar_30'] and 30 or 0

        NUMSETMANES = 4
        setmanes = []
        now = DateTime()
        dow = now.dow()==0 and 7 or now.dow()
        #fdofw = primer dia de la primera setmana que mostrarem segons NUMSETMANES a mostrar
        fdofw = addDays(now,1-dow-(NUMSETMANES*7))
        dies = self.getDies(first_day = fdofw,last_day = lastDayOfWeek())
        for setmana in range(0,NUMSETMANES):
            diesarestar = 7*setmana
            fdow = addDays(now,1-dow-diesarestar)
            setmanes.append(self.getSetmana(dies,fdow))
        return setmanes

    def getSetmana(self,dies_data,fdow,day_filter=None):
        """
        """
        hores_diaries = self.options['hores_diaries']
        hores_setmanals = self.options['dies_setmana']*hores_diaries

        now = DateTime().earliestTime()
        dies = []
        horesvacances = 0
        minutstreballats = 0
        minutsimputats = 0
        minutsimputables = 0
        horesnotreballables = 0
        minutspermisos = 0
        minutsdiesdefesta = 0
        minutsdiesdeintensiva = 0
        minutsdiesdevacances = 0
        minutspermisforalloctreball = 0
        dies_fora_mes = 0
        dies_de_intensiva = 0

        #Per si consultem un mes que no s'ha treballat encara
        if dies_data==None:
            dies_data = {}
        for i in range(0,7):
            cday = addDays(fdow,i).earliestTime()
            if day_filter==None or ( cday.ISO()>=day_filter.ISO() and cday.month()==day_filter.month() ):
                sdia = (cday.dd(),cday.mm(),cday.year().__str__())

                if sdia in dies_data.keys():
                    dies.append(dies_data[sdia])

                    minutsvacancesdeldia = sum([a['minutes'] for a in dies_data[sdia]['especials'] if 'Vacances' in a['title']])
                    minutsdiesdevacances = minutsdiesdevacances + minutsvacancesdeldia

                    minutsdiesdefesta = minutsdiesdefesta + sum([a['minutes'] for a in dies_data[sdia]['especials'] if a['title'] in ['Festa']])

                    minutsintensivadeldia = sum([a['minutes'] for a in dies_data[sdia]['especials'] if a['title'] in ['Intensiva']])                    
                    minutsdiesdeintensiva = minutsdiesdeintensiva + minutsintensivadeldia
                    if minutsintensivadeldia>0:
                        dies_de_intensiva = dies_de_intensiva+1

                    # Si tenim vacances en un dia de intensiva, i fem 7 hores diaries les hores que fem 
                    # de vacances no seran les hores que treballem diaries, sino les
                    # hores que tenim de intensiva aquell dia. Els que fan reducció de jornada no els hi afecta
                    if minutsvacancesdeldia!=0 and minutsintensivadeldia!=0 and hores_diaries==7:
                        minutsdiesdevacances = minutsdiesdevacances - 60


                    minutspermisforalloctreball = minutspermisforalloctreball + sum([a['minutes'] for a in dies_data[sdia].get('especials',[]) if 'E/S fora del lloc de treball' in a['title']])

                    minutspermisos = minutspermisos + HMaMinuts(dies_data[sdia]['permisos'])
                    minutstreballats = minutstreballats + HMaMinuts(dies_data[sdia]['marcades'])
                    minutsimputats = minutsimputats + HMaMinuts(dies_data[sdia]['imputades'])
                    minutsimputables = minutsimputables + HMaMinuts(dies_data[sdia]['aimputar'])
                elif (cday.ISO()<=now.ISO() or day_filter!=None)  and i<5:

                    #Afegirem el nou dia buit si no té imputacions
                    # El dissabte i el diumenge només l'afegirem si te imputacions
                    datac = sdia
                    ndia = sdia[0]
                    dies.append(dict(data='%s%s%s' % datac,
                         dia=ndia,
                         marcades='00:00',
                         permisos='00:00',
                         total='00:00',
                         imputades='00:00',
                         aimputar='00:00',
                         pendents='00:00',
                         vacances='00:00',
                         imputacions = [],
                         especials=[],
                         link=''
                         ))
            elif i<5:
                # Només descomptarem el dia fora de mes si és un dia laborable
                dies_fora_mes +=1
        dies.reverse()


        minutsatreballargenerics = (hores_setmanals*60) - (hores_diaries*dies_de_intensiva*60)- (dies_fora_mes*hores_diaries*60) - minutsdiesdefesta + minutsdiesdeintensiva
        minutsatreballarreals = minutsatreballargenerics - minutsdiesdevacances - minutspermisos + minutspermisforalloctreball
        minutscomptabilitzables = minutstreballats+minutspermisos+minutsdiesdevacances
        minutspendents = minutsatreballarreals-minutstreballats
        try:
          percentatgeimputat = '%.1f' % ( (minutsimputats*100)/minutsimputables   )
        except:
          percentatgeimputat = '0'

        setmana_dict = dict(fdow = fdow.strftime('%d/%m/%Y'),
                       ldow = cday.strftime('%d/%m/%Y'),
                       id = fdow.strftime('%d%m%Y')+cday.strftime('%d%m%Y'),
                       dies = dies,

                       # Les hores a treballar en una setmana són
                       #   - les hores setmanals definides a les opcions
                       #   - MENYS els dies de la setmana que no son del mes (només en cas que hi hagi el filtre de mes activat)
                       #   - MENYS els dies de festa
                       #   - MENYS les hores de permisos que compten hores
                       #   - MES les hores de permisos de E/S fora del lloc de treball
                       horesatreballar = MinutsAHM(minutsatreballarreals),

                       # Les hores treballades en una setmana són
                       #   - les hores fitxades
                       #   - MÉS les hores en permisos que compten_hores
                       #
                       horestreballades = MinutsAHM(minutstreballats),

                       # Les hores de permisos que COMPTEN hores
                       # No comptarem els permisos de E/S fora del lloc de treball, ja que són els únics que tot i comptar hores, són hores que s'han de treballar
                       horespermisos = MinutsAHM(minutspermisos - minutspermisforalloctreball),

                       # Les hores que hem d'imputar segons les fitxades menys el descans si el tenim
                       horesimputables = MinutsAHM(minutsimputables),

                       # Les hores que hem imputat
                       horesimputades = MinutsAHM(minutsimputats),

                       horesvacances = MinutsAHM(minutsdiesdevacances),

                       horescomptabilitzables = MinutsAHM(minutscomptabilitzables),

                       horesatreballargeneriques = MinutsAHM(minutsatreballargenerics),

                       percentatgeimputat = percentatgeimputat,

                       horespendents = MinutsAHM(minutspendents))

        return setmana_dict


    def getDies(self,historic=None,first_day = None,last_day = None):
        """
        """
        t0 = time.time()

        operacions = Operacions(self.request, self.username,self.password,self.eid,self.tid)
        # Vik: Aqui inicialitza per primera vegada presencia
        presencia = Presencia(self.request, self.username,self.password)
        self.options = self.epiUtility.getEPIOptions(self.request, self.username)
        descompte_descans = self.options['descomptar_30'] and 30 or 0
        hores_diaries = self.options['hores_diaries']

        tm = time.time()
        marcatges = deepcopy(presencia.getMarcatges(self.username))
        if historic:
            marcatges.update(deepcopy(presencia.getMarcatgesHistoric(self.username, historic)))

        ##############
        ##############
        print "%.3f segons per obtenir marcatges" % (time.time()-tm)

        primer = DateTimeToTT(first_day)
        ultim  = DateTimeToTT(last_day)

        if historic:
            data_imputacio1 ='01-01-%s' % (primer[2])
            data_imputacio2 ='31-12-%s' % (primer[2])
        else:
            data_imputacio1 ='%s-%s-%s' % (primer)
            data_imputacio2 ='%s-%s-%s' % (ultim)

        di2 = DateTime('%s/%s/%s' % ultim[::-1])
        di1 = DateTime('%s/%s/%s' % primer[::-1])        

        dates_range = [DateTimeToTT(di1+a) for a in range(0,daysBetweenDates(di1,di2)+1)]

        tm = time.time()
        imputacions_entre_dates = operacions.obtenirImputacions(self.username, data_imputacio1, data_imputacio2)

        self.tiquets = self.getImputacionsRecents(imputacions_entre_dates,'TI')
        self.problemes = self.getImputacionsRecents(imputacions_entre_dates,'PB')

        print "%.3f segons per obtenir imputacions" % (time.time()-tm)

        dies = {}
        marcadors = {}
        self.presenciaStatus = 'down'
        if self.now in marcatges.keys():
            self.marcatges_avui = marcatges[self.now]['marcatges']
            if True in [None in m for m in self.marcatges_avui]:
                self.presenciaStatus = 'up'


        oberts = []
        for data in dates_range:
            # Estem iterant per totes les dates entre les quals s'han buscat imputacions
            # Si la data que processem no conte cap marcatge, insertarem un dia buit
            fitxats = 0
            marcatgeObert=None
            if data in marcatges.keys():
                dia = marcatges[data]
                fitxats = dia['total']
                if dia['total']==0:
                    for f in dia['marcatges']:
                        if f[1]==None:
                            marcatgeObert=f[0].ISO()
                            fitxatsTemporal = fitxats
                        fitxats = fitxats + minutsEntreDates(f[0],f[1])
            else:
                dia = dict(especial=[],
                           total=0,
                           permisos=[],
                           marcatges=[],
                           link_marcatge='')

            permisos = sum([permis['minutes'] for permis in dia['permisos'] if permis['compta_hores']])
            nch = [permis for permis in dia['permisos'] if not permis['compta_hores']]
            festa_o_intensiva = presencia.getDiscountHoursForDay(data,hores_diaries)
            #permisos = permisos + festa_o_intensiva

            especials = deepcopy(dia['permisos'])
            if festa_o_intensiva:
                especials.append(dict(image='festa.jpg',
                                      title=festa_o_intensiva[0],
                                      minutes=festa_o_intensiva[1]*60,
                                      compta_hores=False))
            minutspermisforalloctreball = sum([a['minutes'] for a in dia.get('permisos',[]) if 'E/S fora del lloc de treball' in a['title']])
            fitxats = fitxats+minutspermisforalloctreball

            total=fitxats
            imputacions = [imputacio for imputacio in imputacions_entre_dates if imputacio['date']==data]
            imputats = 0

            for i in imputacions:
                imputats = imputats + HMaMinuts(i['amount'])
            aimputar = (total-descompte_descans>=0) and (total-descompte_descans) or fitxats

            pendents = aimputar-imputats
            diadict=dict(data='%s%s%s' % data,
                     dia=data[0],
                     marcades=MinutsAHM(fitxats),
                     permisos=MinutsAHM(permisos),
                     total=MinutsAHM(total),
                     imputades=MinutsAHM(imputats),
                     aimputar=MinutsAHM(aimputar),
                     pendents=MinutsAHM(pendents),
                     imputacions=[dict(ref=imp['referencia'],iid=imp['iid'],amount=imp['amount'],type=imp['type']) for imp in imputacions],
                     especials=especials,
                     obert = dia.get('marcatgeobert','0'),
                     link=dia['link_marcatge']
                     )
            #Només afegirem el dia si té imputacions o estem fitxats o te permisos
            #Això inclou els casos:
            #  - Un dia que no hem fitxat pero hi tenim imputacions, les podem veure
            #  - Un dia que hem fitxat pero no tenim imputacions
            #  - Un dia fitxat amb imputacions
            #  - Els dies entre setmana sense fitxar ni imputacions, es pintaran en blanc a la funcio getSetmanes
            #    en canvi els cap de setmana si no tenen res no es pintaran, si tenen imputacions, sí (també al getSetmanes)
            #  - Si tenim algun permis, es mostrarà enara que no tinguem imputacions
            hi_han_imputacions = diadict['imputacions']
            sha_fitxat = diadict['total']!='00:00'

            # Casos de la condicio (('Festa' not in [a['title'] for a in dia['especials']]) or TTToDateTime(data).dow()<=5)
            # Si no hi han "especials" sempre evalua a False
            # Si hi han especials:
            #   - hi ha algun permis entre setmana - PINTEM
            #   - hi ha algun permis al finde - PINTEM
            #   - hi ha una festa entre setmana - PINTEM
            #   - hi ha una festa en finde - NO PINTEM
            #   - cap especial és festa i el dia es un cap de setmana
            es_entre_setmana = TTToDateTime(data).dow() not in [0,6]
            dia_de_festa_entre_setmana = diadict['especials'] and (('Festa' not in [a['title'] for a in diadict['especials']]) or es_entre_setmana)
            if hi_han_imputacions or sha_fitxat or dia_de_festa_entre_setmana :
                dies[data]=diadict

            if marcatgeObert:
               fitxatsbase = fitxatsTemporal
            else:
               fitxatsbase = fitxats

            marcadors[data]=dict(marcades=fitxatsbase,
                                 marcatgeObert=marcatgeObert,
                                 aimputar=aimputar,
                                 imputades=imputats,
                                 pendents=pendents)


        operacions.closeBrowser()

        presencia.closeBrowser()



        self.epiUtility.saveLastAccessed(self.request, self.username,DateTime().ISO())
        self.epiUtility.saveMarcadors(self.request, self.username,marcadors)
        print "%.3f segons TOTAL" % (time.time()-t0)
        return dies

    def getActivitats(self):
        """
        """
        activitats = ACTIVITATS
        return activitats

    def getMarcatgesDAvui(self):
        """
        """
        return [dict(entrada=DateTimeToHM(a[0]),sortida=DateTimeToHM(a[1])) for a in self.marcatges_avui]

    # Vik: refactoritzar per a que agafi una instanciació única de operacions de la classe
    def getTiquets(self):
        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)
        operacions = Operacions(self.request, self.username,self.password,eid,tid)
        tiquets = operacions.obtenirTiquetsAssignats()

        operacions.closeBrowser()

        #incorporar els tiquets imputats recentment:
        assignats = [tiquet['requirementId'] for tiquet in tiquets]
        no_repetits = [tiquet for tiquet in self.tiquets if tiquet['requirementId'] not in assignats]
        separador = [dict(requirementId='0',title="=== Altres tiquets on s'ha imputat recentment ==="),]
        return tiquets+separador+no_repetits

    # Vik: refactoritzar per a que agafi una instanciació única de operacions de la classe
    def getProblemes(self):
        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)
        operacions = Operacions(self.request, self.username,self.password,eid,tid)
        gpos = operacions.obtenirProblemesAssignats()

        operacions.closeBrowser()

        #incorporar els problemes imputats recentment:
        assignats = [gpo['requirementId'] for gpo in gpos]
        no_repetits = [gpo for gpo in self.problemes if gpo['requirementId'] not in assignats]
        separador = [dict(requirementId='0',title="=== Altres problemes on s'ha imputat recentment ==="),]
        return gpos+separador+no_repetits

    # Vik: refactoritzar per a que agafi una instanciació única de operacions de la classe
    def getOrdres(self):
        """
        """

        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)
        operacions = Operacions(self.request, self.username,self.password,eid,tid)
        ordres = operacions.obtenirOrdres(fname="obtenirOrdres")

        operacions.closeBrowser()
        return ordres

    def getImputacionsRecents(self,imputacions,tipus):
        """
        """
        #Recollir llista de tiquets imputats en els ultims dies
        filtrades = []
        afegits = []
        for imp in imputacions:
            tiquetId = imp['referencia'].split('-')[0].rstrip()
            if imp['type']==tipus and tiquetId not in afegits:
                afegits.append(tiquetId)
                filtrades.append(dict(requirementId=tiquetId,title=imp['referencia']))
        return filtrades

    def getPresenciaStatus(self):
        """
        """
        if self.presenciaStatus=='up':
            return True
        else:
            return False

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

@view_config(name='options', renderer='epi:templates/options.pt', permission='view')
class EPIOptions(BaseView):
    """
    """
    def __init__(self, context, request):
        super(EPIOptions, self).__init__(context,request)

    def __call__(self):
        """
        """
        page_title = "%s Opcions" % self.username
        api = TemplateAPI(self.context, self.request, page_title)
        
        if self.request.params.get('form.submitted','0')=='1':
            options = {}
            for option in EPI_OPTIONS.keys():
                options[option]=self.setField(option,EPI_OPTIONS_TYPES[option],EPI_OPTIONS[option])
            self.epiUtility.setEPIOptions(self.request, self.username, options)
            return HTTPFound(location=api.getAppURL())
        else:
            return dict(api = api)

    def setField(self,option,ftype,default):
        """
        """
        value = self.request.params.get(option,default)
        if ftype=='bool':
            return option in self.request.params.keys()
        if ftype=='int':
            return int(value)
        return value

    def getOptions(self):
        """
        """
        pa = self.epiUtility
        options = pa.getEPIOptions(self.request, self.username)
        return options
        
@view_config(name='manual', renderer='epi:templates/manual.pt', permission='view')
class EPIManual(BaseView):
    """
    """
    def __init__(self, context, request):
        super(EPIManual, self).__init__(context,request)

    def __call__(self):
        """
        """
        page_title = "%s Opcions" % self.username
        api = TemplateAPI(self.context, self.request, page_title)
        return dict(api = api)