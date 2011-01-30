# -*- coding: utf-8 -*-
from epi.interfaces import IEPIUtility
from epi import EPI_OPTIONS
from BTrees.OOBTree import OOBTree
from zope.interface import implements

class EPIUtility(object):
    """Utility per aconseguir i manipular l'objecte que guarda la informació a la ZODB"""
    implements(IEPIUtility)

    def get_storage(self, request):
        root = request.root
        return root['epiUtility']

    def saveUserCredentials(self,request):
        """
        """
        username = request.get('__ac_name')
        password = request.get('__ac_password')
        oldpassword = self.getUserPassword(username)
        if oldpassword!=password:
            self.setUserPassword(username,password)

    def getUserPassword(self, request, username):
        """
        """
        persistentobj = self.get_storage(request)

        if persistentobj.storage.has_key(username)>0:
          if persistentobj.storage[username].has_key('password'):
            return persistentobj.storage[username]['password']
        else:
            return None

    def setUserPassword(self, request, username, password):
        """
        """
        persistentobj = self.get_storage(request)
        
        userdata = OOBTree()
        if persistentobj.storage.has_key(username)>0:
            userdata=persistentobj.storage[username]
        userdata['password']=password
        persistentobj.storage[username]=userdata

    def getEPIOptions(self,username):
        """
        """
        options = EPI_OPTIONS
        if self.storage.has_key(username)>0:
          if self.storage[username].has_key('options'):
            options = self.storage[username]['options']
            #Refem el diccionari d'opcions per si n'haguessim afegit alguna al sistema
            #i el guarde,
            for option in EPI_OPTIONS.keys():
                if option not in options.keys():
                    options[option]=EPI_OPTIONS[option]
                    self.setEPIOptions(username,options)
        return options

    def setEPIOptions(self,username,options):
        """
        """
        useroptions = OOBTree()
        if self.storage.has_key(username)>0:
            useroptions=self.storage[username]
        useroptions['options']=options
        self.storage[username]=useroptions

    def getUserCodes(self, request, username):
        """
        """
        persistentobj = self.get_storage(request)

        ucodes = (None,None)
        if persistentobj.storage.has_key(username)>0:
          if persistentobj.storage[username].has_key('equipId'):
            eid = persistentobj.storage[username]['equipId']
            tid = persistentobj.storage[username]['tecnicId']
            ucodes = (eid,tid)
        return ucodes

    def setUserCodes(self, request, username, eid, tid):
        """
        """
        persistentobj = self.get_storage(request)
        
        userdata = OOBTree()
        if persistentobj.storage.has_key(username)>0:
            userdata=persistentobj.storage[username]
        userdata['equipId']=eid
        userdata['tecnicId']=tid
        persistentobj.storage[username]=userdata

    def recoverBrowserSession(self, request, username,web):
        persistentobj = self.get_storage(request)
        
        browser = None
        elk = None
        if persistentobj.sessions.has_key(username)>0:
          if persistentobj.sessions[username].has_key('browser'):
            if persistentobj.sessions[username]['browser'].has_key(web):
              browser = persistentobj.sessions[username]['browser'][web]
              if web=='operacions':
                  elk = persistentobj.sessions[username]['externalLoginKey']
        return (browser,elk)

    def saveBrowserSession(self,username,browser,web):
        """
        """
        br,ELK = browser
        if not self.sessions.has_key(username)>0:
            self.sessions[username]=OOBTree()
        if not self.sessions[username].has_key('browser'):
            self.sessions[username]['browser']= {}
        if web=='operacions' and not 'externalLoginKey' in self.sessions[username].keys():
            self.sessions[username]['externalLoginKey']=ELK
        self.sessions[username]['browser'][web]=br
        self.sessions[username]._p_changed= 1

    def saveLastAccessed(self,username,time_accessed):
        """
        """
        userdata = OOBTree()
        if self.storage.has_key(username)>0:
            userdata = self.storage[username]
        userdata['last_accessed']=time_accessed
        self.storage[username]=userdata

    def recoverLastAccessed(self,username):
        last = None
        if self.storage.has_key(username)>0:
          if self.storage[username].has_key('last_accessed'):
            last = self.storage[username]['last_accessed']
        return last


    def saveMarcadors(self,username,marcadors):
        """
        """
        userdata = OOBTree()
        if self.storage.has_key(username)>0:
            userdata = self.storage[username]
        userdata['marcadors']=marcadors
        self.storage[username]=userdata

    def recoverMarcadors(self,username):
        last = None
        if self.storage.has_key(username)>0:
          if self.storage[username].has_key('marcadors'):
            marcadors = self.storage[username]['marcadors']
        return marcadors
    