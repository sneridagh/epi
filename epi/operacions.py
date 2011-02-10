# -*- coding: utf-8 -*-
from mechanize import Browser, FormNotFoundError
from cookielib import Cookie,LWPCookieJar
from urllib import quote
from BeautifulSoup import BeautifulSoup
from epi.dateutils import HMaMinuts,DateTimeToTT
from DateTime import DateTime
from epi.decorators import *
from epi.interfaces import IEPIUtility
import logging
from beaker.cache import cache_region, region_invalidate


LOGIN_URL = 'https://maul.upc.es:8444/inici/control/main?idEmpresa=1123'
ACTIVITATS = [
         {'abrProces': 'APE', 'title': u'APE - Gestionar persones: Atenció a persones i equips', 'activitatId': '42909', 'nomProces': 'PROCES_ACT_APE'},
         {'abrProces': 'FOR', 'title': u'FOR - Gestionar persones: Formació', 'activitatId': '42907', 'nomProces': 'PROCES_ACT_FOR'},
         {'abrProces': 'ABC', 'title': u'ABC - Costos ABC', 'activitatId': '100082', 'nomProces': 'PROCES_ACT_ABC'},
         {'abrProces': 'ADM', 'title': u'ADM - Administració', 'activitatId': '42905', 'nomProces': 'PROCES_ACT_ADM'},
         {'abrProces': 'ADS', 'title': u'ADS - Administrar Serveis', 'activitatId': '42894', 'nomProces': 'PROCES_ACT_ADS'},
         {'abrProces': 'APV', 'title': u'APV - APV - Aprovisionar serveis', 'activitatId': '75874', 'nomProces': 'PROCES_ACT_APV'},
         {'abrProces': 'AS TIC 2008', 'title': u'AS TIC 2008 - Coordinació AS TIC 2008', 'activitatId': '43540', 'nomProces': 'PROCES_ACT_QUA'},
         {'abrProces': 'CMI', 'title': u'CMI - Comunicació Interna', 'activitatId': '42910', 'nomProces': 'PROCES_ACT_APE'},
         {'abrProces': 'CMK', 'title': u'CMK - Comunicació i Marketing', 'activitatId': '72834', 'nomProces': 'PROCES_ACT_CMN'},
         {'abrProces': 'CMN', 'title': u'CMN - Comunicació corporativa', 'activitatId': '51132', 'nomProces': 'PROCES_ACT_CMN'},
         {'abrProces': 'CMP', 'title': u'CMP - Gestionar Compres', 'activitatId': '42900', 'nomProces': 'PROCES_ACT_CMP'},
         {'abrProces': 'COM', 'title': u'COM - Comptabilitat', 'activitatId': '100074', 'nomProces': 'PROCES_ACT_COM'},
         {'abrProces': 'DSO', 'title': u'DSO - Dissenyar Solucions', 'activitatId': '42893', 'nomProces': 'PROCES_ACT_DSO'},
         {'abrProces': 'EST', 'title': u'EST - Altres Processos Estratègics', 'activitatId': '42898', 'nomProces': 'PROCES_ACT_EST'},
         {'abrProces': 'FLC', 'title': u'FLC - Facturar a Clients', 'activitatId': '42903', 'nomProces': 'PROCES_ACT_FCL'},
         {'abrProces': 'FNC', 'title': u'FNC - Finances', 'activitatId': '42902', 'nomProces': 'PROCES_ACT_FNC'},
         {'abrProces': 'FPR', 'title': u'FPR - Facturar a Proveïdors', 'activitatId': '42904', 'nomProces': 'PROCES_ACT_FPR'},
         {'abrProces': 'GCO', 'title': u'GCO - Gestionar Cobraments', 'activitatId': '100068', 'nomProces': 'PROCES_ACT_GCO'},
         {'abrProces': 'GEC', 'title': u'GEC - Gestionar els Canvis', 'activitatId': '106258', 'nomProces': 'PROCES_ACT_GEC'},
         {'abrProces': 'GFI', 'title': u'GFI - Gestió Financera', 'activitatId': '100081', 'nomProces': 'PROCES_ACT_GFI'},
         {'abrProces': 'GNS', 'title': u'GNS - GNS - Gestionar nivells de servei', 'activitatId': '75873', 'nomProces': 'PROCES_ACT_GNS'},
         {'abrProces': 'GPA', 'title': u'GPA - Gestionar Pagaments', 'activitatId': '100071', 'nomProces': 'PROCES_ACT_COM'},
         {'abrProces': 'INN', 'title': u'INN - Innovar', 'activitatId': '42897', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'INN-AEI', 'title': u'INN-AEI - Innovar: Fer anàlisi extern i intern', 'activitatId': '122279', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'INN-CRE', 'title': u'INN-CRE - Innovar: Fomentar la creativitat', 'activitatId': '122282', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'INN-PDL', 'title': u'INN-PDL - Innovar: Participar en Premi Davyd Luque', 'activitatId': '149091', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'INN-PTE', 'title': u'INN-PTE - Innovar: Fer previsió tecnològica', 'activitatId': '122281', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'INN-VTE', 'title': u'INN-VTE - Innovar: Fer vigilància tecnològica', 'activitatId': '94975', 'nomProces': 'PROCES_ACT_INN'},
         {'abrProces': 'NTF-ADS', 'title': u'NTF-ADS - Notificar Esdeveniments dels Serveis', 'activitatId': '42899', 'nomProces': 'PROCES_ACT_NTFADS'},
         {'abrProces': 'PES', 'title': u'PES - Planificació Estratègica', 'activitatId': '42896', 'nomProces': 'PROCES_ACT_PES'},
         {'abrProces': 'QUA', 'title': u'QUA - Qualitat', 'activitatId': '42895', 'nomProces': 'PROCES_ACT_QUA'},
         {'abrProces': 'RET', 'title': u'RET - Gestionar persones: Retribució', 'activitatId': '42908', 'nomProces': 'PROCES_ACT_RET'},
         {'abrProces': 'SEL', 'title': u'SEL - Gestionar persones: Selecció', 'activitatId': '42906', 'nomProces': 'PROCES_ACT_SEL'},
         {'abrProces': 'SUB', 'title': u'SUB - Subvencions', 'activitatId': '100084', 'nomProces': 'PROCES_ACT_SUB'},
         {'abrProces': 'Suport guardies', 'title': u'Suport guardies - Suport tecnològic a les guardies de serveis cítics', 'activitatId': '113839', 'nomProces': 'PROCES_ACT_ADS'}
         ]

class Operacions(object):

    def __str__(self):
        return "%s.%s" % (self.__module__, self.__class__.__name__)

    def __init__(self, request, username, password, eid='', tid=''):
        """
        """
        self.request = request
        registry = request.registry
        self.epitool=registry.getUtility(IEPIUtility)

        self.initialized = True
        self.username = username
        self.password = password
        self.equipID=eid
        self.tecnicID=tid
        self.browser_login,self.externalLoginKey=self.epitool.recoverBrowserSession(request, self.username,'operacions')
        if self.browser_login:
          #Si tenim cookies anteriors, creem un browser nou i li passem les cookies guardades
          self.br=Browser()
          self.br.set_handle_robots(False)
          cj = LWPCookieJar()
          self.br.set_cookiejar(cj)
          for co in self.browser_login:
              ck = Cookie(version=co['version'], name=co['name'], value=co['value'], port=co['port'], port_specified=co['port_specified'], domain=co['domain'], domain_specified=co['domain_specified'], domain_initial_dot=co['domain_initial_dot'], path=co['path'], path_specified=co['path_specified'], secure=co['secure'], expires=co['expires'], discard=co['discard'], comment=co['comment'], comment_url=co['comment_url'], rest=co['rest'])
              cj.set_cookie(ck)

          print "Logging-in into operacions via browser"
        else:
          #self.br = Browser()
          try:
              self.login()
          except:
              self.initialized=False
        return

    def log(self, message):
        """
        """
        logger = logging.getLogger('RUNNING')
        logger.info('%s - %s' % (self.username,message))

    def getBrowserSession(self):
        cookies = []
        for key in self.br._ua_handlers['_cookies'].cookiejar._cookies.keys():
           domain = self.br._ua_handlers['_cookies'].cookiejar._cookies[key]
           for key2 in domain.keys():
               cookie = domain[key2]
               for key3 in cookie:
                   co = cookie[key3]
                   cookies.append(dict(version=co.version, name=co.name, value=co.value, port=co.port, port_specified=co.port_specified, domain=co.domain, domain_specified=co.domain_specified, domain_initial_dot=co.domain_initial_dot, path=co.path, path_specified=co.path_specified, secure=co.secure, expires=co.expires, discard=co.discard, comment=co.comment, comment_url=co.comment_url, rest=co._rest))

        return (cookies,self.externalLoginKey)

    def reloadExternalLoginKey(self):
        """
        """
        self.log("reloadExternalLoginKey")
        mainpage = self.getOperacionsMainPage()
        self.loadExternalLoginKey(mainpage.read())

    def getOperacionsMainPage(self):
        """
        """
        mainpage = self.br.open(LOGIN_URL)
        return mainpage


    def loadExternalLoginKey(self,html):
        """
        """
        key = html.split('externalLoginKey')[-1][1:15]
        self.externalLoginKey = key.startswith('EL') and key or ''

    def closeBrowser(self):
        """
        """
        self.br.close()

    def saveSessionData(self,):
        """
        """
        self.epitool.saveBrowserSession(self.request, self.username,self.getBrowserSession(),'operacions')
        return

    def login(self, message = "Logging-in into operacions via regular login"):
        """
        Es logueja a operacions amb el login tradicional web
        """
        self.log('Operacions Login %s' % message)
        self.br=Browser()
        self.br.set_handle_equiv(False)
        mainpage = self.getOperacionsMainPage()
        self.br.select_form(nr=0)
        self.br['username']=self.username
        self.br['password']=self.password
        login_response = self.br.submit()
        html = login_response.read()
        self.loadExternalLoginKey(html)
        self.saveSessionData()

    def checkBrowserExpired(self,html):
        """
        Comprova que el browser nou que hem generat en base a cookies guardades, continua actiu
        Per ferho, comprovem si l'html de la pagina que acavem de obrir conte el text de canvi de contrasenya
        Retorna cert si el browser esta caducat
        """
        return html.find("http://www.upcnet.es/CanviContrasenyaUPC")>0

    def obtenirCodisUsuari(self):
        """
        """
        self.log("obtenirCodisUsuari")
        imputacions = self.br.open('https://maul.upc.es:8444/imputacions/control/main?idEmpresa=1123&externalLoginKey=%s' % (self.externalLoginKey))
        ihtml = imputacions.read()
        fixedhtml = ihtml.replace('</form\n','</form>\n')
        soup = BeautifulSoup(fixedhtml.replace('value""','value=""'),fromEncoding='utf-8')
        equipId = dict(soup.find('input',type='hidden', id='equipId').attrs)['value']
        tecnicId = dict(soup.find('input',type='hidden', id='tecnicId').attrs)['value']

        return (equipId,tecnicId)

    @reloginIfCrashed
    def obtenirComentariImputacio(self,iid):
        """
        """
        self.log("obtenirComentariImputacio")
        detallimputacio = self.br.open('https://maul.upc.es:8444/imputacions/control/imputacioDetall?timeEntryId=%s&externalLoginKey=%s' % (iid,self.externalLoginKey))
        ihtml = detallimputacio.read()
        if self.checkBrowserExpired(ihtml):
            return 'EXPIRED'
        fixedhtml = ihtml.replace('</form\n','</form>\n')
        soup = BeautifulSoup(fixedhtml.replace('value""','value=""'),fromEncoding='utf-8')
        comentari = soup.find('table').findAll('td')[5].span.string
        return comentari and comentari.encode('utf-8') or ''


    def arreglarCometes(self,params):
        """
        """
        newparam=[]
        newparams = []
        for param in params:
            cometes = len(param.split('"'))
            if cometes>=3:
                newparams.append(param)
            if cometes==2:
                if newparam==[]:
                    newparam.append(param)
                else:
                    newparams.append(','.join(newparam))
            if cometes==1:
                newparam.append(param)

        return newparams

    def fixMalformed(self,html,sep,start,end):
        noucaixadiv = []
        actual = ''
        escriure = True
        for string in html.split(sep):
            actual = string

            if escriure:
               noucaixadiv.append(actual)
            else:
               acomulat = acomulat+string

            if start in string:
                escriure=False
                acomulat = ''
            elif end in string and not escriure:
               escriure=True
               noucaixadiv.append(acomulat.replace(' %s' % (end),'%s %s' % (sep,end)))

        fixedHTML = sep.join(noucaixadiv)

        return fixedHTML

    #@cache(smartCacheKey)
    #@reloginIfCrashedAndCache
    @cache_region('default_term', 'obtenirPortalTecnic')
    def obtenirPortalTecnic(self, username):
        self.log("obtenirPortalTecnic sense cachejar")
        return self.obtenirPortalTecnicBase(username)
        
    @reloginIfCrashed
    def obtenirPortalTecnicBase(self, username):
        """
        """
        self.reloadExternalLoginKey()
        self.log("obtenirPortalTecnic")
        base_url = 'https://maul.upc.es:8444/portal/control/portalTecnicConsulta?'
        #self.reloadExternalLoginKey()
        parts =  ['tipusCerca=',
                  'personaAssignada=%s' % (self.tecnicID),
                  'partyIdAss=%s' % (self.tecnicID),
                  'undefined=%s' % (self.tecnicID),
                  'statusId=ESTAT_OBERT_PENDENT',
                  'sensePaginacio=on',
                  'cercant=on',
                  'externalLoginKey=%s' % (self.externalLoginKey),
                 ]
        url = base_url+'&'.join(parts)
        html = self.br.open(url).read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'
        html = html.replace('")">',')">')
        soup = BeautifulSoup(html,fromEncoding='UTF-8')

        seccions = [div for div in soup.findAll('div') if '"caixa"' in str(div)[1:30]]
        self.saveSessionData()
        return dict(ordres = seccions[0],
                    tiquets = seccions[1],
                    problemes = seccions[2],
                    canvis = seccions[3],
#                    percepcions = seccions[4]
                    )


    def obtenirOrdres(self,fname='obtenirOrdres'):
        """
        """
        soup = self.obtenirPortalTecnic(self.username)['ordres']
        ordres = []
        if soup:
          for tr in soup.findAll('tr'):
            if tr.td:
               tds = tr.findAll('td')
               ordre = {}
               href = tds[4].span.a._getAttrMap()['href']
               params = dict([tuple(a.split('=')) for a in href.replace('&amp;','&').replace('"','').split('?')[1].split('&')])
               ordre['orderId']= params['orderId']
               ordre['orderItemSeqId']=params['orderItemSeqId']
               title = tds[4].span.a.string
               ordre['title']='%s - %s' % (ordre['orderId'],title)
               if ordre not in ordres:
                   ordres.append(ordre)

        ordres = sorted(ordres,key=lambda ordre: ordre['orderId'])
        ordres.reverse()
        return ordres

    def processarTaula(self,soup):
        """
        """
        items = []

        if soup:
          for tr in soup.findAll('tr'):
            if tr.td:
               tds = tr.findAll('td')
               item = {}
               item['requirementId'] = tds[3].a.span.string
               try:
                 item['title']='%s - %s' % (item['requirementId'],tds[4].a.span.string)
               except:
                 #import ipdb;ipdb.set_trace()
                 pass
               items.append(item)
        return items


    def obtenirTiquetsAssignats(self):
        """
        """
        soup = self.obtenirPortalTecnic(self.username)['tiquets']
        return self.processarTaula(soup)

    def obtenirProblemesAssignats(self):
        """
        """
        soup = self.obtenirPortalTecnic(self.username)['problemes']
        return self.processarTaula(soup)

    def obtenirCanvisAssignats(self):
        """
        """
        soup = self.obtenirPortalTecnic(self.username)['canvis']
        return self.processarTaula(soup)


    def obtenirTiquetsEquip(self):
        """
        """
        self.log("obtenirTiquetsEquip")
        self.reloadExternalLoginKey()
        base_url = 'https://maul.upc.es:8444/tiquets/control/tiquetsEquipConsulta?'
        parts =  ['tipusCerca=simple',
            'VIEW_INDEX=1',
            'VIEW_SIZE=30',
            'statusId=ESTAT_OBERT_PENDENT',
            'nomesTancats=on',
            'personaAssignada=%s' % (self.tecnicID),
            'undefined=%s' % (self.tecnicID),
            'sensePaginacio=on',
            'cercant=on',
            'externalLoginKey=%s' % (self.externalLoginKey)
            ]
        base_url = 'https://maul.upc.es:8444/tiquets/control//tiquetsAssignatsConsulta?'
        parts =  ['statusId=ESTAT_OBERT_PENDENT',
            'sensePaginacio=on',
            'externalLoginKey=%s' % (self.externalLoginKey)
            ]
        url = base_url+'&'.join(parts)
        cerca_tiquets = self.br.open(url)
        thtml = cerca_tiquets.read()
        soup = BeautifulSoup(thtml.replace('value""','value=""').replace('\n','').replace('\t',''),fromEncoding='utf-8')
        inicidiv = thtml.find('div class="caixa"')-1
        fidiv = thtml.find('div class="endcolumns"')
        caixadiv = thtml[inicidiv:fidiv]
        soup = BeautifulSoup(caixadiv,fromEncoding='utf-8')
        tiquets = []
        self.saveSessionData()
        return tiquets


    def getUrlConsultaImputacions(self,di,df):
        """
        """
        # Hem tret el equipId dels parametres, aixi surten les imputacions de tots els equips
        #params = dict(equipId=self.equipID,
        params = dict(equipId='',        
                      tecnicId=self.tecnicID,
                      dataInicial=di,
                      dataFinal=df,
                      sensePaginacio='on',
                      cercant='on',
                      tipusCerca='simple',
                      externalLoginKey=self.externalLoginKey)

        param_string = '&'.join(['%s=%s' % (key,params[key]) for key in params])
        url = 'https://maul.upc.es:8444/imputacions/control/imputacionsConsulta?%s' % param_string
        return url

    def getImputacionsRaw(self,html_raw):
        """
        """
        html= html_raw.replace('value""','value=""').replace('\n','').replace('\t','')
        # Aquesta adreça de correu al mig de l'html ens fa petar el beautifulsoup, la amaguem de moment, ja
        # que només és un cas aïllat d'un tiquet, si torna a passar, s'hauria de buscar una regex per filtrar
        # text amb aquest format avans de parsejar
        fixedhtml = html.replace('<xsf.suggerencies@upcnet.es>','')
        fixedhtml = fixedhtml.replace('form<!--','form><!--')
        soup = BeautifulSoup(fixedhtml,fromEncoding='utf-8')
        imputacions_raw = [a for a in soup.findAll('tr') if str(a).find('class="previsio"')>0][:-1]
        return imputacions_raw

    #@cache(smartCacheKey)
    #@reloginIfCrashedAndCache
    @cache_region('default_term', 'obtenirImputacions')
    def obtenirImputacions(self, username, di, df):
        self.log("obtenirImputacions sense cachejar")
        return self.obtenirImputacionsBase(username, di, df)
        
    @reloginIfCrashed
    def obtenirImputacionsBase(self, username, di, df):
        """
        """
        #import ipdb; ipdb.set_trace()
        self.reloadExternalLoginKey()
        self.log("obtenirImputacions entre %s i %s" % (di,df))
        if di==None and df==None:
            pass
        result = self.br.open(self.getUrlConsultaImputacions(di,df))
        html = result.read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'
        imputacions_raw = self.getImputacionsRaw(html)


        ## Si no obtenim cap resultat, provarem de recarregar el externalLoginKey, ja que canvia per alguna
        ## extranya raó, tot i que la sessió i les cookies encara són vàlides
        ## Si després d'això no retorna cap resultat, s'enten que realment no te imputacions dins el rang de dates
        if imputacions_raw == []:
            try:
                #self.reloadExternalLoginKey()
                result = self.br.open(self.getUrlConsultaImputacions(di,df))
                imputacions_raw = self.getImputacionsRaw(result.read())
            except:
                pass

        imputacions = []
        for imputacio in imputacions_raw:
            parts = imputacio.findAll('td')
            date = parts[0].span.string
            dd,mm,aaaa = date.split('-')
            iid = parts[0].a.attrs[0][1].split('timeEntryId=')[1].split('"')[0]
            amount = parts[3].span.string
            imp_type = parts[5].acronym.string.__str__().lstrip()
            try:
              referencia = parts[6].span.span.string
            except:
              referencia = parts[6].span.a.string
            if referencia==None:
                referencia = ' - (Sense referència)'

            tdict = dict(type=imp_type, date = (dd,mm,aaaa), iid = iid, amount = amount, referencia = referencia)
            imputacions.append(tdict)
        imputacions.reverse()
        # Guardem els dies que hem consultat a la utility per despres poder cridar correctament als invalidadors de cache
        self.epitool.saveObtenirImputacionsDays(self.request, username, di, df)
        self.saveSessionData()
        return imputacions

    @reloginIfCrashed
    def imputarOrdre(self,data,hores,minuts,orderId,orderItemSeqId,fname='imputarOrdre'):
        """
        """
        self.log("imputarOrdre")
        self.reloadExternalLoginKey()

        parts = ['dataImputacio=%s' % (data),
                 'horesImputades=%s' % (hores),
                 'minutsImputats=%s' % (minuts),
                 'orderId=%s' % (orderId),
                 'orderItemSeqId=%s' % (orderItemSeqId),
                 'cas=ORDRE',
                 'partyId=%s' % (self.tecnicID),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]

        url = 'https://maul.upc.es:8444/imputacions/control/imputacioAltaGraella?' + '&'.join(parts)

        response = self.br.open(url)
        html = response.read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'

        exitcode = eval(html)
        exitcode = eval(html)
        exitcode['hores']=hores
        exitcode['minuts']=minuts.rjust(2,'0')
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        self.saveSessionData()
        return exitcode

    @reloginIfCrashed
    def imputarActivitat(self,data,hores,minuts,proces,activitatId,fname='imputarActivitat'):
        """
        """
        self.log("imputarActivitat")
        #self.reloadExternalLoginKey()

        parts = ['dataImputacio=%s' % (data),
                 'horesImputades=%s' % (hores),
                 'minutsImputats=%s' % (minuts),
                 'proces=%s' % (proces),
                 'activitatId=%s' % (activitatId),
                 'cas=ACTIVITAT',
                 'partyId=%s' % (self.tecnicID),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]

        url = 'https://maul.upc.es:8444/imputacions/control/imputacioAltaGraella?' + '&'.join(parts)
        response = self.br.open(url)
        html = response.read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'
        exitcode = eval(html)
        exitcode['hores']=hores
        exitcode['minuts']=minuts.rjust(2,'0')
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        return exitcode

    def getCodiImputacio(self,data,minuts,ref,tipus):
        """
        Busquem una imputació filtrant per tipus d'imputació, minuts imputats, data i referència.
        D'entre tots els resultats, ens quedem amb la que tingui el iid més alt,
        que serà la última imputada.
        """
        self.log("getCodiImputacio")
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        
        imputacions = self.obtenirImputacions(self.username, data, data)

        tt = tuple(data.split('-'))
        imputacio = None
        newest=True
        for imp in imputacions:
            if imputacio!=None:
                newest = imp['iid']>imputacio['iid']

            if imp['date']==tt and ref in imp['referencia'] and HMaMinuts(imp['amount'])==minuts and newest and imp['type']==tipus:
                imputacio = imp

        if imputacio:
            return imputacio['iid']
        else:
            return ''

    @reloginIfCrashed
    def imputarTiquet(self,data,hores,minuts,tiquetId,fname='imputarTiquet'):
        """
        Imputa a un tiquet utilitzant el formulari del gestor d'operacions
        """
        self.log("imputarTiquet")
        today = '-'.join(DateTimeToTT(DateTime()))

        self.reloadExternalLoginKey()

        parts = ['requirementId=%s' % (tiquetId),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]

        url = 'https://maul.upc.es:8444/tiquets/control/tiquetDetallAssignacioHistoria?' + '&'.join(parts)
        self.br.open(url)
        try:
            self.br.select_form(name='afegirImputacio')
        except FormNotFoundError:
            return dict(hores='',
                    minuts='',
                    confirm='error',
                    code='No s''ha pogut imputar en un tiquet tancat.')
        except:
            return 'EXPIRED'
        self.br.form.action='https://maul.upc.es:8444/tiquets/control/imputarTempsTasca'
        self.br.form.find_control('minutsImputats').readonly=False
        minutsImputats = int(hores)*60 + int(minuts)
        self.br['minutsImputats']=str(minutsImputats)
        self.br['horesImputadesHelper']=hores
        self.br['minutsImputatsHelper']=minuts
        addtiquet_response = self.br.submit()
        #html = addtiquet_response.read()

        #Consultem el codi de la imputació
        iid = self.getCodiImputacio(today,minutsImputats,tiquetId,'TI')
        code = iid.encode('utf-8')
        if data!=today:
            code = self.canviarImputacio(data,hores,minuts,iid)
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        self.saveSessionData()
        return dict(hores=hores,
                    minuts=minuts.rjust(2,'0'),
                    confirm=iid=='' and 'error' or 'ok',
                    code=code)

    @reloginIfCrashed
    def imputarProblema(self,data,hores,minuts,tiquetId,fname='imputarProblema'):
        """
        Imputa a un problema utilitzant el formulari del gestor d'operacions
        """
        self.log("imputarProblema")
        today = '-'.join(DateTimeToTT(DateTime()))

        self.reloadExternalLoginKey()

        parts = ['requirementId=%s' % (tiquetId),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]

        url = 'https://maul.upc.es:8444/problemes/control/problemaDetallImputacions?' + '&'.join(parts)

        self.br.open(url)
        self.br.select_form(name='afegirImputacio')
        self.br.form.action='https://maul.upc.es:8444/problemes/control/imputarTemps'
        self.br.form.find_control('minutsImputats').readonly=False
        minutsImputats = int(hores)*60 + int(minuts)
        self.br['minutsImputats']=str(minutsImputats)
        self.br['horesImputadesHelper']=hores
        self.br['minutsImputatsHelper']=minuts
        addtiquet_response = self.br.submit()
        #html = addtiquet_response.read()

        #Consultem el codi de la imputació
        iid = self.getCodiImputacio(today,minutsImputats,tiquetId,'PB')
        code=iid.encode('utf-8')
        if data!=today:
            code = self.canviarImputacio(data,hores,minuts,iid)
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        self.saveSessionData()
        return dict(hores=hores,
                    minuts=minuts.rjust(2,'0'),
                    confirm=iid=='' and 'error' or 'ok',
                    code=code)

    @reloginIfCrashed
    def canviarImputacio(self,novadata,hores,minuts,iid,fname='canviarImputacio'):
        """
        """
        self.log("canviarImputacio")
        if iid!='':
            code = iid
            self.reloadExternalLoginKey()
            parts = ['timeEntryId=%s' % (iid),
                     'dataImputacio=%s' % (novadata),
                     'horesImputades=%s' % (hores),
                     'minutsImputats=%s' % (minuts),
                     'externalLoginKey=%s' % (self.externalLoginKey),
                    ]
            url = 'https://maul.upc.es:8444/imputacions/control/editarImputacio?' + '&'.join(parts)
            response = self.br.open(url)
            html = response.read()
            if self.checkBrowserExpired(html):
                return 'EXPIRED'
            # Invalidem la cache
            # getUtility(IRAMCache).invalidate('obtenirImputacions')
            day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
            region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
            self.saveSessionData()
        else:
            code = "No sha pogut imputar al dia %s. Refresca lepi i mou la imputacio manualment arrossegant-la al dia %s" % (novadata,novadata)
            code.decode('utf-8')
        return code.encode('utf-8')

    @reloginIfCrashed
    def modificarImputacio(self,hores,minuts,iid,comentari='',fname='modificarImputacio'):
        """
        """
        self.log("modificarImputacio")
        self.reloadExternalLoginKey()
        parts = ['timeEntryId=%s' % (iid),
                 'horesImputades=%s' % (hores),
                 'minutsImputats=%s' % (minuts),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]
        if comentari:
            parts.append('editComentari=%s' % quote(comentari))
        url = 'https://maul.upc.es:8444/imputacions/control/imputacioEdicioGraella?' + '&'.join(parts)
        response = self.br.open(url)
        html = response.read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'
        exitcode = eval(html)
        exitcode['hores']=str(int(hores))
        exitcode['minuts']=minuts.rjust(2,'0')
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        self.saveSessionData()
        return exitcode

    @reloginIfCrashed
    def esborrarImputacio(self,iid,fname='esborrarImputacio'):
        """
        """
        self.log("esborrarImputacio")
        self.reloadExternalLoginKey()
        parts = ['timeEntryId=%s' % (iid),
                 'externalLoginKey=%s' % (self.externalLoginKey),
                ]
        url = 'https://maul.upc.es:8444/imputacions/control/imputacioEsborrarGraella?' + '&'.join(parts)
        response = self.br.open(url)
        html = response.read()
        if self.checkBrowserExpired(html):
            return 'EXPIRED'
        exitcode = eval(html)
        # Invalidem la cache
        # getUtility(IRAMCache).invalidate('obtenirImputacions')
        day1, day2 = self.epitool.getObtenirImputacionsDays(self.request, self.username)
        region_invalidate('epi.operacions.obtenirImputacions', 'default_term', 'obtenirImputacions', 'epi.operacions.Operacions', self.username, day1, day2)
        self.saveSessionData()
        return exitcode
