[![Coverage Status](https://coveralls.io/repos/Byron/shotgun-events/badge.png)](https://coveralls.io/r/Byron/shotgun-events)

The shotgun event daemon listens to all shotgun events, and distributes them to one or more plugin event handlers. These may register for a particular kind of event to only receive the ones they are interested in.

Thanks to the daemon, you may focus on what you are interested in: handling an event, without dealing with details such as:

* repeat events previously missed (due to system failure, for instance)
* maintain a shotgun connection and reconnect automatically
* run as system service


![under construction](https://raw.githubusercontent.com/Byron/bcore/master/src/images/wip.png)

Requirements
============

* python 2.6 or 2.7
* [bshotgun](https://github.com/Byron/bshotgun)
* a posix compatible platform (e.g. linux, osx) if you want to use the built-in daemonization
* **Development**
    - [nosetests](https://nose.readthedocs.org/en/latest)

Differences to Original Implementation
======================================

+ much more flexible configuration and plugin system, including environment variable expansion for paths
+ created using test-driven development to help assure it remains usable
+ make customizations and remix it with ease
- class based plugin's provide imperative means for customizations (but add complexity).
- no reloading of settings or plugins at runtime, until this is supported by the underlying frameworks
+ shares one shotgun connection across multiple event processors, only one shotgun connection per daemon


Installation
============

Please head over to the [distribution](https://github.com/Byron/shotgun-events) for installation instructions.

Infrastructure
===============

* **[Continuous Integration/Quality Assurance](https://travis-ci.org/Byron/shotgun-events)**
* **[Issue Tracker](https://github.com/Byron/shotgun-events/issues)**
* **[Documentation](http://byron.github.io/shotgun-events)**

License
=======

This software is provided under the MIT License that can be found in the LICENSE
file or here: <http://www.opensource.org/licenses/mit-license.php>