# -*- coding: utf-8 -*-
from pyramid.config import Configurator
import pyramid_zcml

from pyramid.session import UnencryptedCookieSessionFactoryConfig

from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from repoze.zodbconn.finder import PersistentApplicationFinder
from epi.models import appmaker

EPI_OPTIONS = dict(descomptar_30=True,
                   hores_diaries=7,
                   dies_setmana=5

                   )
EPI_OPTIONS_TYPES = dict(descomptar_30='bool',
                   hores_diaries='int',
                   dies_setmana='int'
                   )
MONTH_NAMES = dict(January='Gener',February='Febrer',March='Març',April='Abril',May='Maig',June='Juny',July='Juliol',August='Agost',September='Setembre',October='Octubre',November='Novembre',December='Desembre')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')

    whoconfig_file = 'who.ini'
    identifier_id = 'auth_tkt'
    authn_policy = WhoV2AuthenticationPolicy(whoconfig_file, identifier_id)
    authz_policy = ACLAuthorizationPolicy()    
    
    zodb_uri = settings.get('zodb_uri')
    if zodb_uri is None:
        raise ValueError("No 'zodb_uri' in application configuration.")

    finder = PersistentApplicationFinder(zodb_uri, appmaker)
    def get_root(request):
        return finder(request.environ)
    config = Configurator(root_factory=get_root,
                          settings=settings,
                          session_factory = my_session_factory,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    
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
    
    return config.make_wsgi_app()
