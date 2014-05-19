
import os
import logging
import pprint

try:
	import yaml
except ImportError:
	raise ImportError("The python yaml package is not available")
#END handle yaml

class EventRecorder(object):
	"""Record events taken from the daemon
	Configure the script using the invariants at the top of the file.
	Then take the recordings of the events as fixtures into your test suite.
	
	If your want to use this code, just import this module and derive from this type,
	overriding the configuration invariants accordingly.
	
	Then implement the registerCallbacks method using your type in your plugin accordingly."""
	#{ Authentication
	# script name which matches your api key
	script_name = None
	# api key which matches the script name
	api_key = None
	#} END authentication
	
	#{ Configuration
	
	# directory at which to store the events
	storage_root_path = "."
	
	# if true, events will be logged as well using debug priority
	debug_events = True
	
	#}END configuration
	
	@classmethod
	def register(cls, reg):
		"""Register with the registrar"""
		eventFilter = None
		reg.registerCallback(cls.script_name, cls.api_key, cls.record_events, eventFilter, None)
	
	@classmethod
	def record_events(cls, sg, logger, event, args):
		"""Perform actual event recording."""
		name = "%s_%s.yaml" % (event['event_type'], event['id'])
		event_path = os.path.join(cls.storage_root_path, name)
		yaml.dump(event, open(event_path, "w"))
		logger.info("Storing event at %s", event_path)
		
		if cls.debug_events:
			logger.debug(pprint.pformat(event))
		#END debug logging


#{ Plugin Interface

def registerCallbacks(reg):
    """Register all necessary or appropriate callbacks for this plugin."""
    EventRecorder.register(reg)
    

#} end plugin interface
