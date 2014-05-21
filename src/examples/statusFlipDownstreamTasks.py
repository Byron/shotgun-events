"""
When a Task status is flipped to 'fin' (Final), lookup each downstream Task that is currently
'wtg' (Waiting To Start) and see if all upstream Tasks are now 'fin'. If so, flip the downstream Task
to 'rdy' (Ready To Start)

You can modify the status values in the logic to match your workflow.
"""

import bapp
from sgevents import EventEnginePlugin
from butility import DictObject

class FlipDownstreamTasks(EventEnginePlugin, bapp.plugin_type()):
    """Flip downstream Tasks to 'rdy' if all of their upstream Tasks are 'fin'"""
    __slots__ = ()

    event_filters = {
        'Shotgun_Task_Change': ['sg_status_list'],
    }

    def handle_event(self, shotgun, log, event):
        # we only care about Tasks that have been finalled
        if 'new_value' not in event.meta or event.meta.new_value != 'fin':
            return
        
        # downtream tasks that are currently wtg
        ds_filters = [
            ['upstream_tasks', 'is', event.entity],
            ['sg_status_list', 'is', 'wtg'],
            ]
        fields = ['upstream_tasks']
        
        for ds_task in sg.find("Task", ds_filters, fields):
            ds_task = DictObject(ds_task)
            change_status = True
            # don't change status unless *all* upstream tasks are fin
            if len(ds_task.upstream_tasks) > 1:
                logger.debug("Task #%d has multiple upstream Tasks", event.entity.id)
                us_filters = [
                    ['downstream_tasks', 'is', ds_task.id],
                    ['sg_status_list', 'is_not', 'fin'],
                    ]
                if len(sg.find("Task", filters)) > 0:
                    change_status = False
            
            if change_status:
                sg.update("Task",ds_task.id, data={'sg_status_list' : 'rdy'})
                logger.info("Set Task #%s to 'rdy'", ds_task.id)
        # end for each task

# end class FlipDownstreamTasks

    
    
