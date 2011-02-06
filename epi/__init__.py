# -*- coding: utf-8 -*-
from pyramid.config import Configurator
import pyramid_zcml

from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid_beaker import set_cache_regions_from_settings, session_factory_from_settings

from repoze.zodbconn.finder import PersistentApplicationFinder
from epi.models import appmaker

from beaker.util import parse_cache_config_options
import beaker.cache

EPI_OPTIONS = dict(descomptar_30=True,
                   hores_diaries=7,
                   dies_setmana=5

                   )
EPI_OPTIONS_TYPES = dict(descomptar_30='bool',
                   hores_diaries='int',
                   dies_setmana='int'
                   )
MONTH_NAMES = dict(January=u'Gener',February=u'Febrer',March=u'Març',April=u'Abril',May=u'Maig',June=u'Juny',July=u'Juliol',August=u'Agost',September=u'Setembre',October=u'Octubre',November=u'Novembre',December=u'Desembre')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    session_factory = session_factory_from_settings(settings)
    
    whoconfig_file = 'who.ini'
    identifier_id = 'auth_tkt'
    authn_policy = WhoV2AuthenticationPolicy(whoconfig_file, identifier_id)
    authz_policy = ACLAuthorizationPolicy()    
    
    set_cache_regions_from_settings(settings)
    
    zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    config = Configurator(root_factory=get_root,
                          settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    
    config.set_session_factory(session_factory)
    
    config.add_static_view('static', 'epi:static')
    config.add_static_view('css', 'epi:css')
    config.add_static_view('js', 'epi:js')
    config.add_static_view('images', 'epi:images')
    
    config.add_route('login', '/login',
                     view='epi.login.login',
                     view_renderer='epi:templates/login.pt')
    config.add_view('epi.login.login',
                     renderer='epi:templates/login.pt',
                     context='pyramid.exceptions.Forbidden')
    config.add_route('logout', '/logout',
                     view='epi.login.logout')
    config.scan('epi')
    config.include(pyramid_zcml)
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config.load_zcml(zcml_file)
    
    cache_config=parse_cache_config_options(config.registry.settings)
    beaker.cache.cache_regions.update(cache_config["cache_regions"])
    
    return config.make_wsgi_app()
