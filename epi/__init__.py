from pyramid.config import Configurator

from pyramid.session import UnencryptedCookieSessionFactoryConfig

from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from repoze.zodbconn.finder import PersistentApplicationFinder
from epi.models import appmaker

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
    
    config.add_route('login', '/login',
                     view='epi.login.login',
                     view_renderer='epi:templates/login.pt')
    config.add_view('epi.login.login',
                     renderer='epi:templates/login.pt',
                     context='pyramid.exceptions.Forbidden')
    config.add_route('logout', '/logout',
                     view='epi.login.logout')
    config.scan('epi')
    return config.make_wsgi_app()
