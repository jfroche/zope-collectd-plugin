"""
Collectd config example:

<Plugin python>
 ModulePath "/path/to/modules"
 Import "zope"
#
 <Module zope>
 hostname localhost
 port 8888
 name cirbsite-website-client1
 metric dbsize
 metric conflictcount
 </Module>
</Plugin>
"""
import socket
import collectd


class ZopeCollectd(object):

    name = 'zope'
    verbose = True
    metric_configs = dict()
    metric_configs['dbsize'] = {'type': 'bytes', 'type_instance': 'db_size'}
    metric_configs['conflictcount'] = {'type': 'gauge', 'type_instance': 'conflict_count'}
    metric_configs['objectcount'] = {'type': 'gauge', 'type_instance': 'objectcount'}
    metric_configs['requestqueue_size'] = {'type': 'gauge', 'type_instance': 'request_queue_size'}
    metric_configs['load_count'] = {'alias': 'dbactivity', 'type': 'gauge', 'type_instance': 'load_count', 'index': 0}
    metric_configs['store_count'] = {'alias': 'dbactivity', 'type': 'gauge', 'type_instance': 'store_count', 'index': 1}
    metric_configs['connection_count'] = {'alias': 'dbactivity', 'type': 'gauge', 'type_instance': 'connection_count', 'index': 2}
    metric_configs['uptime'] = {'type': 'gauge', 'type_instance': 'uptime'}

    def __init__(self):
        self._metrics = []
        self._zmonitor_port = None
        self._zmonitor_hostname = None
        self._cluster_name = None

    def zope_monitor_config(self, c):
        self.logger('verb', 'in zope_config')
        if c.values[0] != 'zope':
            return
        for child in c.children:
            if child.key == 'port':
                self._zmonitor_port = int(child.values[0])
            if child.key == 'hostname':
                self._zmonitor_hostname = child.values[0]
            if child.key == 'name':
                self._cluster_name = child.values[0]
            if child.key == 'metric':
                for v in child.values:
                    if v not in self._metrics:
                        self._metrics.append(v)
        self.logger('verb', 'configured metrics: %s' % self._metrics)
        self.logger('verb', 'cluster name: %s' % self._cluster_name)

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger('verb', 'connect on %s:%s' % (self._zmonitor_hostname, self._zmonitor_port))
        s.connect((self._zmonitor_hostname, self._zmonitor_port))
        return s

    def strip_data(self, data, metric):
        metric_config = self.metric_configs[metric]
        if 'alias' in metric_config:
            data = data.split()[metric_config.get('index')]
        return str(data).strip()

    def zope_read(self, data=None):
        self.logger('verb', 'read_callback')
        for metric in self._metrics:
            try:
                s = self.connect()
            except:
                collectd.error('Fail to connect to %s:%s' % (self._zmonitor_hostname,
                                                             self._zmonitor_port))
                return
            self.logger('verb', 'fetch %s' % metric)
            metricid = self.metric_configs[metric].get('alias', metric)
            s.sendall("%s\n" % metricid)
            output = None
            while 1:
                data = s.recv(1024)
                if data == "":
                    break
                else:
                    output = data
            s.close()
            if output is not None:
                data = self.strip_data(output, metric)
            self.logger('verb', 'got %s' % data)
            if data == '' or data is None:
                collectd.error('Recevied not data for %s' % metric)
                return
            values = collectd.Values(type=self.metric_configs[metric]['type'], plugin='zope')
            values.dispatch(plugin_instance='%s' % self._cluster_name,
                            type_instance=self.metric_configs[metric]['type_instance'],
                            values=(data, ))

    def logger(self, t, msg):
        if t == 'err':
            collectd.error('%s: %s' % (self.name, msg))
        if t == 'warn':
            collectd.warning('%s: %s' % (self.name, msg))
        elif t == 'verb' and self.verbose:
            collectd.info('%s: %s' % (self.name, msg))

zope_collectd_plugin = ZopeCollectd()
collectd.register_read(zope_collectd_plugin.zope_read)
collectd.register_config(zope_collectd_plugin.zope_monitor_config)
