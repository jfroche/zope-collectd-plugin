.. contents::

Introduction
============

This little script is a simple Zope plugin for Collectd. It enables monitoring collection of zope instance metrics with Collectd.
It use the monitoring daemon available in zope with five.z2monitor (http://pypi.python.org/pypi/five.z2monitor)
and zc.monitor (http://pypi.python.org/pypi/zc.monitor).

Collectd configuration
======================

Collectd Configuration example::

  <Plugin python>
     ModulePath "/path/to/modules"
     Import "zope"
     <Module zope>
        hostname localhost
        port 8888
        name website-client1
        metric dbsize
        metric conflictcount
    </Module>
  </Plugin>

Available metrics
=================

 - dbsize: Size of the database
 - conflictcount: Number of all conflict errors since startup
 - objectcount: Number of object in the database (default=main)
 - requestqueue_size: Number of requests waiting in the queue to be handled by zope threads
 - load_count:  number of load on database (default=main) for the last 5 minutes (default=5)
 - store_count:  number of store on database (default=main) for the last 5 minutes (default=5)
 - connection_count:  number of connection on database (default=main) for the last 5 minutes (default=5)
 - uptime: uptime of the zope instance in seconds

Zope config
===========

For Zope 2, you will need the following packages:

 - ``five.z2monitor`` (http://pypi.python.org/pypi/five.z2monitor)
 - Products.ZNagios (http://pypi.python.org/pypi/Products.ZNagios)
 - zc.z3monitor (http://pypi.python.org/pypi/zc.z3monitor)
