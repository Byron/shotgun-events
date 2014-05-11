# Technical Overview

<a id="Plugin_Processing_Order"></a>
## Plugin Processing Order

Each event is always processed in the same predictable order so if any plugins
or callbacks are co-dependant, your can safely organize their processing.

The configuration file specifies a `paths` config that contains one or multiple
plugin locations. The earlier the location in the list the earlier the contained
plugins will be processed.

Each plugin within a plugin path is then processed in ascending alphabetical order.

**Note:** Internally the filenames are put in a list and sorted.

Finally, each callback registered by a plugin is called in registration order.
First resgistered, first run.

It is suggested to keep any functionality that needs to share state somehow in
the same plugin as one or multiple callbacks.

<a id="Sharing_State"></a>
## Sharing state

If multiple callbacks need to share state many options may be used.

- Global variables. Ick. Please don't do this.
- An imported module that holds the state information. Ick, but a bit better
  than simple globals.
- A mutable passed in the `args` argument when calling
  [`Registrar.registerCallback`](API#wiki-registerCallback). A state object of your design or something
  as simple as a dict. Preferred.
- Implement callbacks as `__call__` on object instances and provide some shared
  state object at callback object initialization. Most powerful, most convoluted
  and might be a bit redundant vs. `args` argument method.


<a id="Error_Messages"></a>
## Error Messages

Here is a brief overview of some error and warning message that you may see appear in your logs depending on your configured logging level.

### Timeout elapsed on backlog event id

Each event that occurs in Shotgun (field update, entity creation, entity retirement, etc) has a unique id number to its event log entry. Sometimes there are gaps in the id number sequence. These gaps can occur for many reasons, one of them being a large database transaction that has yet to complete.

Every time a gap in the event log sequence is encountered the "missing" event ids are put into a backlog for later processing. This allows for the event daemon to process the events from a long database transaction once it has finished.

Sometimes the gap in the event log sequence will never be filled in such as a failed transaction or reverted page setting modifications. In this case the event log entry id number that was put in the backlog will eventually hit a timeout (5 minutes) and the system will stop waiting for this event to appear. It is at this time that you will see a "Timeout elapsed on backlog event id #####" message.