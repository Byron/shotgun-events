
import os
import logging
import pprint

import bapp
from butility import Path
from sgevents import EventEnginePlugin

try:
	import yaml
except ImportError:
	raise ImportError("The python yaml package is not available")
#END handle yaml


class EventRecordingEventEnginePlugin(EventEnginePlugin, bapp.plugin_type()):
	"""Record events taken from the daemon
	Configure the script using the invariants at the top of the file.
	Then take the recordings of the events as fixtures into your test suite.
	
	If your want to use this code, just import this module and derive from this type,
	overriding the configuration invariants accordingly.
	
	Then implement the registerCallbacks method using your type in your plugin accordingly."""

	#{ Configuration
	
	# directory at which to store the events
	storage_root_path = Path('.')
	
	# if true, events will be logged as well using debug priority
	debug_events = True

	# handled all events
	event_filters = dict()
	
	#}END configuration
	
	def handle_event(self, sg, log, event):
		"""Perform actual event recording."""
		name = "%s_%s.yaml" % (event.event_type, event.id)
		event_path = self.storage_root_path / name
		yaml.dump(event, open(event_path, 'wb'))
		log.info("Storing event at %s", event_path)
		
		if self.debug_events:
			log.debug(pprint.pformat(event))
		#END debug logging

# end class EventRecordingEventEnginePlugin
