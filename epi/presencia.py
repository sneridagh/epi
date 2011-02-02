# -*- coding: utf-8 -*-
from cookielib import Cookie,LWPCookieJar
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
from DateTime import DateTime
from epi.dateutils import HMaMinuts,TTToDateTime,DateTimeToTT,addDays
from epi.decorators import *
from epi.interfaces import IEPIUtility
from zope.app.cache.interfaces.ram import IRAMCache
from zope.component import getUtility
from copy import deepcopy
import logging
from beaker.cache import cache_region

MOTIUS_PERMISOS = {'Permis sense sou': {'compta_hores':False,'imatge': 'permis.jpg'},
'Permís per estudis': {'compta_hores':True,'imatge': 'permis.jpg'},
'Permís per presidents o vocals de les meses electorals': {'compta_hores':True,'imatge': 'permis.jpg'},
'Permís recuperable': {'compta_hores':False,'imatge': 'permis.jpg'},
'Hores sindicals': {'compta_hores':True,'imatge': 'permis.jpg'},
'Trasllat de domicili': {'compta_hores':True,'imatge': 'trasllat.gif'},
'Vacances': {'compta_hores':False,'imatge': 'vacances.jpg'},
'Vacances recuperables': {'compta_hores':False,'imatge': 'vacances.jpg'},
'Vacances/hores compensació horari': {'compta_hores':False,'imatge': 'vacances.jpg'},
'Hores/Vacances intervencions especials': {'compta_hores':True,'imatge': 'vacances.jpg'},
'Voluntariat': {'compta_hores':True,'imatge': 'voluntariat.jpg'},
'Examens prenatals i tècniques de preparació al part': {'compta_hores':True,'imatge': 'fills.png'},
'Lactància': {'compta_hores':True,'imatge': 'fills.png'},
'Maternitat/Paternitat': {'compta_hores':True,'imatge': 'fills.png'},
'Adopció': {'compta_hores':True,'imatge': 'fills.png'},
'Cura d\'un infant fins 18 mesos': {'compta_hores':True,'imatge': 'fills.png'},
'Naixement d\'un fill': {'compta_hores':True,'imatge': 'fills.png'},
'Paternitat': {'compta_hores':True,'imatge': 'fills.png'},
'Matrimoni': {'compta_hores':True,'imatge': 'matrimoni.jpg'},
'Visita metge': {'compta_hores':True,'imatge': 'metge.jpg'},
'Visita mèdica de fills': {'compta_hores':True,'imatge': 'metge.jpg'},
'Defunció parents fins 2on grau': {'compta_hores':True,'imatge': 'creu.jpg'},
'Formació': {'compta_hores':True,'imatge': 'formacio.jpg'},
'Teletreball': {'compta_hores':False,'imatge': 'teletreball.jpg'},
'E/S fora del lloc de treball': {'compta_hores':True,'imatge': 'esforalloctreball.jpg'},
'Deures d\'inexcusable compliment': {'compta_hores':True,'imatge': 'deures.jpg'},
'Examen': {'compta_hores':True,'imatge': 'examen.jpg'},
'Indisposició': {'compta_hores':True,'imatge': 'indisposicio.jpg'},
'Malaltia': {'compta_hores':True,'imatge': 'indisposicio.jpg'},
'Malaltia greu familiar fins 2on grau': {'compta_hores':True,'imatge': 'indisposicio.jpg' },}

ALTRES = {'Festa': {'compta_hores':True,'imatge': 'festa.jpg'},}
MOTIUS = deepcopy(MOTIUS_PERMISOS)
MOTIUS.update(ALTRES)

BASE_URL = 'https://liszt.upc.es/Upcnet/Administracio/presencia'
LOGIN_URL = '%s/presencia.nsf' % BASE_URL
PERSONES_URL = '%s/presencia.nsf/VPersones?OpenView' % BASE_URL
FITCHA_URL = '%s/presencia.nsf/EntrarSortirW?openagent' % BASE_URL
MARCATGES_URL = '%s/presencia.nsf/VMarcatges?OpenView&Start=1&Count=1000' % BASE_URL
MARCATGES_HISTORIC_URL = '%s/presenciaH01%%s.nsf/VMarcatges?OpenView&Start=1&count=1000' % BASE_URL
PRESENCIA_URL = '%s/presencia.nsf/VPersones?OpenView&Start=1&Count=1000' % BASE_URL
PERMISOS_URL = '%s/presencia.nsf/VPermisos?OpenView&Start=1&Count=1000' % BASE_URL
PERMISOS_HISTORIC_URL = '%s/presenciaH01%%s.nsf/VPermisos?OpenView&Start=1&Count=1000' % BASE_URL

class Presencia(object):
    """
    """
    def __init__(self, request, username,password,context=''):
        """
        Al instanciar la classe, es loguejarà utilitzant el nom d'usuari i password proporcionats,
        Si browser_login conté algo són les cookies guardades de la última sessio loguejada que s'ha fet.
        Recarregarem les cookies en un Browser nou, i aixi estalviarà uns segons que consumiria del login.
        """
        self.context=context
        self.request=request
        registry = self.request.registry
        self.epitool=registry.getUtility(IEPIUtility)

        self.username = username
        self.password = password
        self.browser_login, elk = self.epitool.recoverBrowserSession(self.request, self.username,'presencia')
        if self.browser_login:
          self.br=Browser()
          self.br.set_handle_robots(False)
          cj = LWPCookieJar()
          self.br.set_cookiejar(cj)
          for co in self.browser_login:
              ck = Cookie(version=co['version'], name=co['name'], value=co['value'], port=co['port'], port_specified=co['port_specified'], domain=co['domain'], domain_specified=co['domain_specified'], domain_initial_dot=co['domain_initial_dot'], path=co['path'], path_specified=co['path_specified'], secure=co['secure'], expires=co['expires'], discard=co['discard'], comment=co['comment'], comment_url=co['comment_url'], rest=co['rest'])
              cj.set_cookie(ck)
          print "Logging-in into presència via browser"
        else:
          self.br = Browser()
          self.br.set_handle_equiv(False)
          self.login(message="Logging-in into presència via regular login")
          return

    def log(self, message):
        """
        """
        logger = logging.getLogger('RUNNING')
        logger.info('%s - %s' % (self.username,message))

    def getBrowserSession(self):
        """
        Retorna la sessio actual del browser per a poderla guardar desde la utility
        """

        cookies = []
        for key in self.br._ua_handlers['_cookies'].cookiejar._cookies.keys():
           domain = self.br._ua_handlers['_cookies'].cookiejar._cookies[key]
           for key2 in domain.keys():
               cookie = domain[key2]
               for key3 in cookie:
                   co = cookie[key3]
                   cookies.append(dict(version=co.version, name=co.name, value=co.value, port=co.port, port_specified=co.port_specified, domain=co.domain, domain_specified=co.domain_specified, domain_initial_dot=co.domain_initial_dot, path=co.path, path_specified=co.path_specified, secure=co.secure, expires=co.expires, discard=co.discard, comment=co.comment, comment_url=co.comment_url, rest=co._rest))
        return (cookies,None)

    def closeBrowser(self):
        """
        """
        self.br.close()

    def saveSessionData(self):
        """
        """
        self.epitool.saveBrowserSession(self.request, self.username,self.getBrowserSession(),'presencia')
        return

    def login(self,message = "Logging-in into presència via regular login"):
        """
        Es logueja a presència amb el login tradicional web
        """
        self.log("Presència Login %s" % message)
        self.br.open(LOGIN_URL)
        self.br.select_form(nr=0)
        self.br['Username']=self.username
        self.br['Password']=self.password
        response = self.br.submit()
        response_html = response.read()
        response.close()
        self.saveSessionData()

    def checkBrowserExpired(self,html):
        """
        Comprova que el browser nou que hem generat en base a cookies guardades, continua actiu
        Per ferho, comprovem si l'html de la pagina que acavem de obrir conte el text de canvi de contrasenya
        Retorna cert si el browser esta caducat
        """
        return html.find("Introduïu nom d'usuari i contrasenya")>0

    @reloginIfCrashed
    def Marcar(self):
        """
        Canvia l'estat del marcatge actual
        """
        self.log("Marcar")
        persones = self.br.open(FITCHA_URL)
        persones_html = persones.read()
        if self.checkBrowserExpired(persones_html):
            return 'EXPIRED'
        persones.close()
        getUtility(IRAMCache).invalidate('getMarcatges')
        getUtility(IRAMCache).invalidate('getPresencia')
        return True
        print "S'ha canviat l'estat de marcatge"

    ##@reloginIfCrashedAndCache
    def getMarcatgesHistoric(self,year,fname='getMarcatgesHistoric'):
        """
        Recupera la pàgina de marcatges de presència de l'històric anual, on hi ha tot el que no surt a la pagina principal
        La pàgina no té cap mena de id's ni classes, el parsejat es una mica dur...
        """
        self.log("getMarcatges Historic %s" % year)
        return self.getMarcatgesBase(MARCATGES_HISTORIC_URL % year,year=int(year))

    ##@reloginIfCrashedAndCache
    def getMarcatges(self,fname='getMarcatges'):
        """
        Recupera la pàgina de marcatges de presència, on hi han els dos ultims mesos de marcatges.
        La pàgina no té cap mena de id's ni classes, el parsejat es una mica dur...
        """
        self.log("getMarcatges")
        return self.getMarcatgesBase(MARCATGES_URL)

    def getDiscountHoursForDay(self,dia,hores_dia):
        day = '%s-%s-%s' % (dia)
        years={'2010':[],'2011':[]}
        years['2010']= {
                       '01-01-2010':'F',
                       '04-01-2010':'I',
                       '05-01-2010':'I',
                       '06-01-2010':'F',
                       '07-01-2010':'I',
                       '08-01-2010':'I',
                       #===============
                       '29-03-2010':'I',
                       '30-03-2010':'I',
                       '31-03-2010':'I',
                       #===============
                       '01-04-2010':'I',
                       '02-04-2010':'F',
                       '05-04-2010':'F',
                       #===============
                       '01-05-2010':'F',
                       '24-05-2010':'F',
                       #===============
                       '24-06-2010':'F',
                       #===============
                       '11-09-2010':'F',
                       '24-09-2010':'F',
                       #===============
                       '12-10-2010':'F',
                       #===============
                       '01-11-2010':'F',
                       #===============
                       '06-12-2010':'F',
                       '08-12-2010':'F',
                       '25-12-2010':'F',

                       }
                       
        years['2011']= {
                       '01-01-2011':'F',
                       '03-01-2011':'I',                       
                       '04-01-2011':'I',
                       '05-01-2011':'I',
                       '06-01-2011':'F',
                       '07-01-2011':'I',
                       #===============
                       '07-03-2011':'F',
                       #===============
                       '18-04-2011':'I',
                       '19-04-2011':'I',
                       '20-04-2011':'I',
                       '21-04-2011':'I',                                                                     
                       '22-04-2011':'F',
                       '25-04-2011':'F',
                       #===============
                       '13-06-2011':'F',                       
                       '24-06-2011':'F',
                       #===============
                       '15-08-2011':'F',                       
                       #===============
                       '24-09-2011':'F',
                       #===============
                       '12-10-2011':'F',
                       #===============
                       '01-11-2011':'F',
                       #===============
                       '06-12-2011':'F',
                       '08-12-2011':'F',
                       '26-12-2011':'F',

                       }                       
        if dia[2] in years.keys():
          if day in years[dia[2]]:
            if years[dia[2]][day]=='F':
                hores = hores_dia
            else:
              if hores_dia==7:
                hores = 6
              else:
                hores = hores_dia
            return ({'F':'Festa','I':'Intensiva'}[years[dia[2]][day]],hores)
          else:
            return None
        else:
          return None

    def getMarcatgesBase(self,URL,**kwargs):
        """
        """
        self.now = DateTime().latestTime()
        
        current_year = self.now.year()
        historic_query_year = kwargs.get('year',None)        
        is_historic_query = historic_query_year!=None

        # Vik: Mocking days_of_past_year
        days_of_past_year = {('28', '01', '2011'): {'total': 0, 'permisos': [{'image': 'teletreball.jpg', 'minutes': 420, 'compta_hores': False, 'title': 'Teletreball'}], 'link_marcatge': '', 'marcatges': []}, ('19', '01', '2011'): {'total': 0, 'permisos': [{'image': 'teletreball.jpg', 'minutes': 420, 'compta_hores': False, 'title': 'Teletreball'}], 'link_marcatge': '', 'marcatges': []}}

        if is_historic_query:
            days_of_query_year = current_year==historic_query_year # and deepcopy(self.getPermisos(fname="getPermisos")) or deepcopy(self.getPermisosHistoric(historic_query_year,fname="getPermisosHistoric"))
            # Vik: treure l'ultim any
            #days_of_query_past_year = deepcopy(self.getPermisosHistoric(historic_query_year-1,fname="getPermisosHistoric"))
            dies = days_of_query_year
            dies.update(days_of_query_past_year)
        else:
            dies = deepcopy(self.getPermisos(self.username))
            if self.now.month()<3:
                #days_of_past_year = deepcopy(self.getPermisosHistoric(current_year-1,fname="getPermisosHistoric"))
                #Vik: punt conflictiu import ipdb; ipdb.set_trace()
                dies.update(days_of_past_year)
            
            
        marcatges = self.br.open(URL)
        marcatges_html = marcatges.read()
        if self.checkBrowserExpired(marcatges_html):
            return 'EXPIRED'

        marcatges.close()
        soup = BeautifulSoup(marcatges_html,fromEncoding='iso-8859-1')

        try:
            table = soup.findAll('table')[2]           # La tercera taula de l'html és on hi ha el que busquem
        except:
            #Si hem arribat a aquest punt vol dir que hi ha algun problema amb la pagina de presència de l'usuari
            #i no hi han ni marcatges ni l'estructura html que s'espera. retornem una llista de dies buida
            return dies

        # Hi han moltes taules aniuades dins d'altres taules, però les files que ens interessen sabem que
        # que són files que no tenen mes taules aniuades a tins i que tenen td, per tant, les busquem i parsejem
        # el tr **dia** per exteure els marcatges

        meves = False
        for dia in table.findChildren(recursive=False):
           # Per tenir en compte el cas de que una persona vegi els marcatges de varies,
           # Ens parem a les files on hi han 'collapse.gif' per investigar
           collapse = 'collapse.gif' in str(dia.find('img'))
           if collapse:
              dlow = dia.__str__().lower()
              lusername = self.username.replace('.',' ')
              # busquem el nom d'usuari a la fila, i si hi és a partir d'ara guardarem marcatges
              if lusername in dlow:
                  meves=True
              # Si ja estavem guardant marcatges, deixarem de guardarlos només si trobem
              # el colspan="15", que vol dir que hem passat tots els marcatges de l'usuari
              # i hem arrivat al seguent. Sense aquesta condicio no guardariem cap marcatge,
              # ja que el seguen tr despres del nom d'usuari tambe te collapse.gif i posariem meves a False per error.
              elif meves==True and 'colspan="15"' in dia.__str__().lower():
                  meves=False
           if not dia.findAll('table') and dia.td and meves:
               data,marcatge_dict = self.parseDia(dia)

               # Només continuarem si el parseDia ha retornat alguna cosa
               if data!=None:
                   ## Si no tenim res amb la data [data] a dintre de dies, guardem el
                   ## marcatge_dict com a inicialització de la variable

                   if data not in dies.keys():
                       dies[data]=marcatge_dict

                   ## Si ja tenim el dia, vol dir que tenim un permis en aquell dia per tant afegirem les dades de marcatges que vinguin

                   else:
                       dies[data]['total']=dies[data]['total']+marcatge_dict['total']
                       dies[data]['marcatgeobert']=marcatge_dict.get('marcatgeobert','0')
                       ## Concatenem les llistes de marcatges, per si hi han permisos avans que marcatges.
                       ## Els permisos no tenen marcatges, per tant, la majoria de cops concatenarem llistes buides
                       ## però així evitem el cas de que , per exemple, es tiguin el permis de teletreball avans del dia de ferlo
                       dies[data]['marcatges']=dies[data]['marcatges']+marcatge_dict['marcatges']
                       dies[data]['link_marcatge']=marcatge_dict.get('link_marcatge','')

        return dies

    def parseDia(self,dia):
        """
        Parseja un tr que conte un marcatge retornant-los en forma de dicionari
        """
        parsed = {}

        #Agafem els tds (fills de primer nivell del tr)
        children = dia.findChildren(recursive=False)

        #Seleccionem els td's que contenen marcatges amb alguna cosa (<a><font></font></a>) a dins
        marcatges_web = [a for a in children[7:15] if a.font]

        # només si tenim marcatges continuarem, ja que si no hi han marcatges
        # vol dir que és un permís i ja els extraiem de la seccio de permisos
        # avans de començar a parsejar els dies
        if marcatges_web:

            #Agafem el link del marcatge per possibles modificacions
            data_marcatge = children[3].a.string
            parsed['link_marcatge'] = 'https://liszt.upc.es'+children[3].a['href']
            parsed['link_marcatge'] = parsed['link_marcatge'].replace('OpenDocument','EditDocument')+'&AutoFramed'


            #Agafem la suma ja feta del total del dia, que ens servira en tots els casos
            #Menys en els marcatges oberts, que és 0, i la guardem en minuts
            total_dia = children[4].font.string
            parsed['total']=total_dia==None and 0 or HMaMinuts(total_dia,sep='.')

            parsed['marcatges']=[]
            parsed['permisos']=[]

            novamarca = []
            for marca in marcatges_web:
                if novamarca == []:
                    novamarca.append(DateTime('%s %s' % (data_marcatge,marca.font.string)))
                else:
                    novamarca.append(DateTime('%s %s' % (data_marcatge,marca.font.string)))
                    parsed['marcatges'].append(tuple(novamarca))
                    novamarca = []
            #Afegim els marcatge del dia actual si encara no el tenim tancat
            if len(novamarca)==1:
                novamarca_latest = novamarca[0].latestTime()
                # Si és el dia actual, posem None per tal que es compti fins a l'hora actual el marcatge parcial.
                # Qualsevol altre dia afegim la data ultima del dia com a ultim marcatge.
                # En tot cas marquem que és un marcatge obert
                ultimamarca = self.now!=novamarca_latest and novamarca_latest or None
                parsed['marcatgeobert']= '1'
                novamarca.append(ultimamarca)
                parsed['marcatges'].append(tuple(novamarca))

            mm,dd,aaaa = data_marcatge.split('/')
            return (dd,mm,aaaa),parsed
        else:
            return (None,None)

    ##@reloginIfCrashedAndCache
    def getPresencia(self,fname='getPresencia'):
        """
        Recupera la pàgina de persones de presència, on hi han els telèfons de cadascú i si esta o no presents
        La pàgina no té cap mena de id's ni classes, el parsejat es una mica dur...
        """
        self.log("getPresencia")
        personesbr = self.br.open(PRESENCIA_URL)
        persones_html = personesbr.read()
        if self.checkBrowserExpired(persones_html):
            return 'EXPIRED'
        personesbr.close()
        soup = BeautifulSoup(persones_html,fromEncoding='iso-8859-1')

        persones = {}
        try:
            table = soup.findAll('table')[2]           # La tercera taula de l'html és on hi ha el que busquem
        except:
            #Si hem arribat a aquest punt vol dir que hi ha algun problema amb la pagina de presència de l'usuari
            #i no hi han ni marcatges ni l'estructura html que s'espera. retornem una llista de dies buida

            return persones

        # Hi han moltes taules aniuades dins d'altres taules, però les files que ens interessen sabem que
        # que són files que no tenen mes taules aniuades a tins i que tenen td, per tant, les busquem i parsejem
        # el tr **dia** per exteure els marcatges

        for fila in table.findChildren(recursive=False):
           # Per poder escriure les dades de a quin equip pertany
           # Ens parem a les files on hi han 'collapse.gif' per agafar el nom de l'equip
           collapse = 'collapse.gif' in str(fila.find('img'))
           if collapse:
               team = fila.td.b.string
           # La resta seràn pesones, les parsejem i les incorporem a la llista
           else:
             if not fila.findAll('table') and fila.td:
               persona_dict = self.parsePersona(fila)
               persona_dict['equip']=team
               nompersona = persona_dict['nom']
               if nompersona in persones.keys():
                   persones[nompersona]['online'] = persones[nompersona]['online'] or persona_dict['online']
                   persones[nompersona]['equip'] = '%s, %s' % (persones[nompersona]['equip'],team)
               else:
                   persones[nompersona]=persona_dict

        self.saveSessionData()
        return [persones[a] for a in persones.keys()]


    def parsePersona(self,dia):
        """
        Parseja un tr que conte una persona amb els seus telefons retornant-los en forma de dicionari
        """
        parsed = {}

        #Agafem els tds (fills de primer nivell del tr)
        children = dia.findChildren(recursive=False)
        #recollim les dades de la persona
        nom = children[2].a.string
        online = 'vwicn160.gif' in children[1].__str__()
        telefon_intern = children[3].string
        telefon_mobil = children[4].string
        telefon_public = children[5].string
        telefon_public and telefon_public.split('.')[0] or telefon_public

        return dict(nom=nom,online=online,intern=telefon_intern,mobil=telefon_mobil,public=telefon_public)

    #@reloginIfCrashedAndCache
    def getPermisosHistoric(self,year,fname='getPermisosHistoric'):
        """
        """
        self.log("getPermisos Historic %s" % year)
        return self.getPermisosBase(PERMISOS_HISTORIC_URL % year)

    #@reloginIfCrashedAndCache
    @cache_region('default_term', 'getPermisos')
    def getPermisos(self, username):
        """
        """
        self.log("getPermisos")
        return self.getPermisosBase(PERMISOS_URL)

    def getPermisosBase(self,url,fname='getPermisos'):
        """
        """
        self.now = DateTime().latestTime()
        dies_permisos = []

        permisos = self.br.open(url)
        permisos_html = permisos.read()
        if self.checkBrowserExpired(permisos_html):
            return 'EXPIRED'

        permisos.close()
        soup = BeautifulSoup(permisos_html,fromEncoding='iso-8859-1')

        try:
            tables = soup.findAll('table')         
            table ='(hh:mm)' in tables[2].__str__() and tables[2] or tables[1]
        except:
          #La sessio del browser ha caducat, per tant refarem el login
            self.login(message="Re-Logging-in into presència via regular login")
            permisos = self.br.open(PERMISOS_URL)
            permisos_html = permisos.read()
            permisos.close()
            soup = BeautifulSoup(permisos_html,fromEncoding='iso-8859-1')
            try:
              table = soup.findAll('table')[2]
            except:
              #Si hem arribat a aquest punt vol dir que hi ha algun problema amb la pagina de presència de l'usuari
              #i no hi han ni permisos ni l'estructura html que s'espera. retornem una llista de dies buida
              return {}

        # Hi han moltes taules aniuades dins d'altres taules, però les files que ens interessen sabem que
        # que són files que no tenen mes taules aniuades a tins i que tenen td, per tant, les busquem i parsejem
        # el tr **dia** per exteure els permisos

        meves = False
        for dia in table.findChildren(recursive=False):
           # Per tenir en compte el cas de que una persona vegi els permisos de varies,
           # Ens parem a les files on hi han 'collapse.gif' per investigar
           collapse = 'collapse.gif' in str(dia.find('img'))
           if collapse:
              dlow = dia.__str__().lower()
              lusername = self.username.replace('.',' ')

              # busquem el nom d'usuari a la fila, i si hi és a partir d'ara guardarem permisos
              if lusername in dlow:
                  meves=True
              # Si ja estavem guardant permisos, deixarem de guardarlos només si trobem
              # el colspan="15", que vol dir que hem passat tots els permisos de l'usuari
              # i hem arrivat al seguent. Sense aquesta condicio no guardariem cap marcatge,
              # ja que el seguen tr despres del nom d'usuari tambe te collapse.gif i posariem meves a False per error.
              elif meves==True and 'colspan="5"' in dia.__str__().lower():
                  meves=False
           if not dia.findAll('table') and dia.td and meves:
               td = dia.findAll('td')[1]
               attrmap = td._getAttrMap()
               if 'colspan' in attrmap.keys():
                   if attrmap['colspan']=='4':
                       # si es compleixen les dues condicions, estem en un tr que marca el motiu del permis
                       motiu = td.b.font.string.encode('utf-8')
               elif 'colspan' not in str(dia):
                   # si no hi ha colspan, en tot el tr estem en una entrada de permis segons lultim tipus
                   permis_data = self.parsePermis(dia)
                   dies_permisos = dies_permisos+self.generarDiesPermisos(permis_data,motiu)
        # XXXXXXX TODO Aqui hauriem de repassar que no hi hagin duplicats a la llista, doncs el diccionari quedaria nomes amb l'ultim permis
        return dict(dies_permisos)

    def generarDiesPermisos(self,permis,motiu):
        """
        Donada la definicio d'un permis, si esta aprovat, genera els seus dies tal com si ens els haguessim trobat en el
        parseig de getMarcatgesBase. Els marcatges seran sempre [] llista buida, doncs els permisos no tenen un marcatge associat
        """

        days = []
        if permis['approved']:
            from_date = TTToDateTime(permis['from_date'])
            to_date = TTToDateTime(permis['to_date'])

            grow_days = True
            counter = 0

            while grow_days:
                current = addDays(from_date,counter)

                # Només afegirem el dia si no és cap de setmana
                # Tampoc l'afegirem si és un dia de festa, ja que si es festa no son vacances...

                dhfd = self.getDiscountHoursForDay(DateTimeToTT(current),7)
                es_festa = dhfd!=None and dhfd[0] or False
                if current.dow() not in [0,6] and es_festa!='Festa':
                    motiu_image = 'permis.jpg'
                    if motiu in MOTIUS.keys():
                        motiu_image = MOTIUS[motiu]['imatge']

                    permisdict = dict(compta_hores=MOTIUS[motiu]['compta_hores'],
                                      image=motiu_image,
                                      title=motiu,
                                      minutes=permis['minutes'])

                    diadict = dict(link_marcatge='',
                                   marcatges=[],
                                   total=0,
                                   permisos=[permisdict,])

                    daytuple = (DateTimeToTT(current),diadict)
                    days.append(daytuple)

                # Condició de final i incrementar l'iterador
                if current==to_date:
                    grow_days=False
                counter = counter +1

        return days

    def parsePermis(self,dia):
        """
        Parseja un tr que conte un permis retornant-los en forma de dicionari
        """
        parsed = {}
        tds = dia.findAll('td')

        approved = 'vwicn083.gif' in str(tds[2].img)
        fd = tds[3].font.a.string.split('/')
        td = tds[4].font.string.split('/')
        
        #Agafarem el td 6 o el 7 segons tingui els ':' , ja que l'historic te una columna de més
        minutestd = ':' in tds[6].__str__() and tds[6] or tds[7]        
        # S'ha de fer un replace 12: per 00: ja que l'html que revem a través del
        # mechanize si hi ha 00 es pensa que es una hora i ens ho transforma en 12 ...
        minutes = HMaMinuts(minutestd.string.split()[0].replace('12:','00:'))
        return dict(approved = approved,
                    from_date = (fd[1],fd[0],fd[2]),
                    to_date = (td[1],td[0],td[2]),
                    minutes = minutes)

