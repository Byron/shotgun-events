# Installation

The following guide will help you setup shotgunEvents for your studio.

<a id="System_Requirements"></a>
## System Requirements

The daemon can run on any machine that has Python installed and has network
access to your Shotgun server. It does **not** need to run on the Shotgun server
itself. In fact, if you are using the hosted version of Shotgun, this isn't
an option. However, you may run it on your Shotgun server if you like. Otherwise,
any server will do.

- Python v2.4-v2.7
- [Shotgun Python API](https://github.com/shotgunsoftware/python-api) v3.0+
- Network access to your Shotgun server

<a id="Installing_Shotgun_API"></a>
## Installing the Shotgun API

Assuming Python is already installed on your machine, you now need to install
the Shotgun Python API so that the Shotgun Event Daemon can use it to connect to your
Shotgun server. You can do this in a couple of ways:

- place it in the same directory as the Shotgun Event Daemon
- place it in one of the directories specified by the [`PYTHONPATH` environment 
  variable](http://docs.python.org/tutorial/modules.html).

To test that the Shotgun API is installed correctly, from your terminal window:

```
$ python -c "import shotgun_api3"
```

You should see no output. If you see something like the output below then you 
need to make sure your `PYTHONPATH` is setup correctly or that the Shotgun API
is located in the current directory.

```
$ python -c "import shotgun_api3"
Traceback (most recent call last):
File "<string>", line 1, in <module>
ImportError: No module named shotgun_api3
```

<a id="Installing_shotgunEvents"></a>
## Installing shotgunEvents

The location you choose to install shotgunEvents is really up to you. Again, as
long as Python and the Shotgun API are installed on the machine, and it has
network access to your Shotgun server, it can run from anywhere. However, it
makes sense to install it somehwere that is logical to your studio, something
like `/usr/local/shotgun/shotgunEvents` seems logical so we'll use that as the
example from here on out.

The source and archives are available on GitHub at [https://github.com/shotgunsoftware/shotgunEvents]()

**Windows Note:** You could use `C:\shotgun\shotgunEvents` if you have a Windows server but for this documentation we will be using the Linux path.

<a id="Cloning_Source"></a>
### Cloning the source

The easiest way to grab the source if you have `git` installed on the machine
is to simply clone the project. This way you can also easily pull in any updates
that are committed to ensure you stay up to date with bug fixes and new 
features.

```
$ cd /usr/local/shotgun
$ git clone git://github.com/shotgunsoftware/shotgunEvents.git
```

**Warning:** Always make sure you backup your configuration, plugins, and any modifications
you make to shotgunEvents before pulling in updates from GitHub so you don't 
lose anything. Or, fork the project yourself so you can maintain your own
repository of changes :)

<a id="Downloading_Archive"></a>
### Downloading the archive

If you don't have `git` on your machine or you simply would rather download
an archive of the source, you can get things rolling following these steps.

- head over to [https://github.com/shotgunsoftware/shotgunEvents/archives/master]()
- download the source in the format you want
- save it to your machine
- extract the files to the `/usr/local/shotgun` directory
- rename the `/usr/local/shotgun/shotgunsoftware-shotgunEvents-xxxxxxx` directory 
  to `/usr/local/shotgun/shotgunEvents`

#### Extracting the archive into `/usr/local/shotgun`.

For .tar.gz archives

```
$ tar -zxvf shotgunsoftware-shotgunEvents-v0.9-12-g1c0c3eb.tar.gz -C /usr/local/shotgun
```

For .zip archives

```
$ unzip shotgunsoftware-shotgunEvents-v0.9-12-g1c0c3eb.zip -d /usr/local/shotgun
```

Then you can rename the GitHub-assigned directory name to `shotgunEvents`

```
$ mv shotgunsoftware-shotgunEvents-1c0c3eb shotgunEvents
```

Now you should now have something like this

```
$ ls -l /usr/local/shotgun/shotgunEvents
total 16
-rw-r--r--  1 kp  wheel  1127 Sep  1 17:46 LICENSE
-rw-r--r--  1 kp  wheel   268 Sep  1 17:46 README.mkd
drwxr-xr-x  9 kp  wheel   306 Sep  1 17:46 docs
drwxr-xr-x  6 kp  wheel   204 Sep  1 17:46 src
```

<a id="Windows_Specifics"></a>
### Windows specifics

You will need one of the following on your Windows system:

* Python with [PyWin32](http://sourceforge.net/projects/pywin32/) installed
* [Active Python](http://www.activestate.com/activepython)

Active Python ships with the PyWin32 module which is required for integrating the Shotgun Event Daemon with Windows' Service architecture.

You can then install the deamon as a service by running the following command (we are assuming that `C:\Python27_32\python.exe` is the path to your Python executable, adjust accrodingly):

```
> C:\Python27_32\python.exe shotgunEventDaemon.py install
```

Or remove it with:

```
> C:\Python27_32\python.exe shotgunEventDaemon.py remove
```

Starting and stopping the service can be achieved through the normal service management tools or via the command line with:

```
> C:\Python27_32\python.exe shotgunEventDaemon.py start
> C:\Python27_32\python.exe shotgunEventDaemon.py stop
```
