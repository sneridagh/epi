from persistent.mapping import PersistentMapping
from persistent import Persistent
from BTrees.OOBTree import OOBTree
from epi.interfaces import IEPIUtility
from zope.interface import implements

class Root(PersistentMapping):
    __parent__ = __name__ = None

def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Root()
        epiUtility = EPIUtility()
        app_root['epiUtility'] = epiUtility
        epiUtility.__name__ = 'epiUtility'
        epiUtility.__parent__ = app_root
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()

    return zodb_root['app_root']

class EPIUtility(Persistent):
    """ The EPI utility
    """
    implements(IEPIUtility)
    
    storage = None
    sessions = None

    def __init__(self):
        """
        """
        self.storage = OOBTree()
        self.sessions = OOBTree()


