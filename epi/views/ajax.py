# -*- coding: utf-8 -*-
from pyramid.view import view_config
from epi.views.dashboard import BaseView
from epi.presencia import Presencia
from pyramid.response import Response

@view_config(name="consultarPresencia")
class ConsultarPresenciaAJAX(BaseView):
    """
    """

    def  __init__(self,context,request):
        """
        """
        super(ConsultarPresenciaAJAX, self).__init__(context,request)
        self.marcatges_avui = []

    def __call__(self):
        """
        """

        eid,tid = self.epiUtility.getUserCodes(self.request, self.username)

        try:
            presencia = Presencia(self.request, self.username,self.password)
        except:
            return {}

        persones_raw = presencia.getPresencia()

        presencia.closeBrowser()
        persones = '[{%s}]' % ('},{'.join([','.join(['"%s":"%s"' % (a,dd[a]) for a in dd.keys()]) for dd in persones_raw]))
        total_persones =len([a for a in persones_raw if u'Direcció' not in a['equip']])
        total_online = len([a for a in persones_raw if a['online']])
        #self.context.plone_log('################ %d %% de persones treballant' % ((total_online*100)/total_persones))
        #self.context.plone_log('################ %d  de %d de persones treballant' % (total_online,total_persones))

        return Response(persones.replace('"True"','true').replace('"False"','false').replace('None',''))
