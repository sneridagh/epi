# -*- coding: utf-8 -*-
from time import time
from plone.memoize.ram import cache
from DateTime import DateTime
from plone.memoize.volatile import ATTR,CONTAINER_FACTORY,_marker, DontCache, store_on_self
from plone.memoize.interfaces import ICacheChooser
from zope import component

def smartCacheKey(fn,*args,**kwargs):
    """
    """
    nkargs = [a for a in args]
    self = nkargs[0]
    nkargs = nkargs[1:]
    fname = kwargs.get('fname','')
    key = [fname]
    if fname in ['obtenirImputacions']:
        #Guarda caché de les imputacions durant una hora, la caché esta en funció de la cerca i l'usuari, per tant
        #cada conjunt de paràmetres de la seva pròpia caducitat
        key.extend([self.username,kwargs['di'],kwargs['df'],time() // (60*60)])
    if fname in ['getPresencia']:
        #Cacheja el resultat de la llista de persones de persència sense tenir en compte l'usuari
        # que la consulta. Es renova cada 10 minuts
        key.extend([time() // (60*10)])
    if fname in ['getMarcatgesHistoric','getPermisosHistoric']:
        #Cacheja els marcatges històrics diferenciats per any, per sempre
        key.extend([self.username,nkargs[0]])
    if fname in ['getMarcatges','obtenirPortalTecnic']:
        #Guarda caché durant una hora, la caché esta en funció l'usuari
        key.extend([self.username,time() // (60*60)])
    if fname in ['getPermisos']:
        #Guarda caché de les imputacions durant mig dia, la caché esta en funció  l'usuari
        key.extend([self.username,time() // (12*60*60)])
    return tuple(key)

def reloginIfCrashedBase(fn,self,*args,**kwargs):
    """
    Prova de executar la funció fn amb els parametres passats i en cas de retornar "EXPIRED"
    re-logueja al modul actual i torna a executar la funció.
    """
    value = fn(self,*args, **kwargs)
    if value=='EXPIRED':
        message = '%s INFO La funció %s ha fallat per culpa d''una cookie caducada. Refent el login...' % (DateTime().ISO(),fn.__name__)
        self.login(message=message)
        value = fn(self,*args, **kwargs)
    return value


def reloginIfCrashedAndCache(fn):
    """
    """
    @EPIcache(smartCacheKey)
    def wrapper(self,*args, **kwargs):
        return reloginIfCrashedBase(fn,self,*args,**kwargs)
    return wrapper

def reloginIfCrashed(fn):
    """
    """
    def wrapper(self,*args, **kwargs):
        return reloginIfCrashedBase(fn,self,*args,**kwargs)
    return wrapper

def store_in_cache(key, *args, **kwargs):
    cache_chooser = component.queryUtility(ICacheChooser)
    if cache_chooser is not None:
        return cache_chooser(key)
    else:
        return RAMCacheAdapter(global_cache, globalkey=key)

def EPIcache(get_key, get_cache=store_in_cache):
    def decorator(fun):
        def replacement(*args, **kwargs):
            try:
                keyo = get_key(fun, *args, **kwargs)
            except DontCache:
                return fun(*args, **kwargs)
            key = '%s:%s' % (keyo[0],keyo[1:])
            cache = get_cache(keyo[0], *args, **kwargs)
            cached_value = cache.get(key, _marker)
            if cached_value is _marker:
                cached_value = cache[key] = fun(*args, **kwargs)
            return cached_value
        return replacement
    return decorator
