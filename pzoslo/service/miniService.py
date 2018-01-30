# -*- coding: utf-8 -*-
from oslo_config import cfg
from oslo_log import log as logging
from oslo_context import context
from webob import Request
from oslo_service import wsgi, service

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
logging.register_options(CONF)
logging.setup(CONF, 'm19k')

#mini·þÎñ
class MiniService:
    def __init__(self, host='0.0.0.0', port='9999', workers=1,
                 use_ssl=False, cert_file=None, ca_file=None):
        self.host = host
        self.port = port
        self.workers = workers
        self.use_ssl = use_ssl
        self.cert_file = cert_file
        self.ca_file = ca_file
        self._actions = {}
    
    def add_action(self, url_path, action):
        if (url_path.lower()=='default') or (url_path=='/') or (url_path==''):
            url_path = 'default'
        elif (not url_path.startswith('/')):
            url_path = '/' + url_path
        self._actions[url_path] = action
    
    def _app(self, environ, start_response):
        context.RequestContext()
        LOG.debug('start action.')
        request = Request(environ)
        action = self._actions.get(environ['PATH_INFO'])
        if action==None:
            action = self._actions.get('default')
        if action!=None:
            result = action(environ, request.method, request.path_info,
                            request.query_string, request.body)
            try:
                result[1]
            except Exception,e:
                result = ('200 ok', str(result))
            start_response(result[0], [('Content-Type', 'text/plain')])
            return result[1]
        start_response('200 ok', [('Content-Type', 'text/html')])
        return 'mini service is ok\n'
    
    def start(self):
        self.server = wsgi.Server(CONF,
                                  'm19k',
                                  self._app,
                                  host=self.host,
                                  port=self.port,
                                  use_ssl=self.use_ssl)
        launcher = service.ProcessLauncher(CONF)
        launcher.launch_service(self.server, workers=self.workers)
        LOG.debug('launch service(%s:%s).' % (self.host, self.port))
        launcher.wait()