import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label
from docking_tasks import task_player_docking

class SpawnRouter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_spawn(self.handle_spawn)

    @label()
    def handle_spawn(self):
        # handle_spawn
        # This while start a task 
        # Each ship will have its of thread for comms
        # this enables them to have a unique path
        if query.has_role(self.task.SPAWNED_ID, "__player__"):
            yield self.jump(task_player_docking)
        elif query.has_role(self.task.SPAWNED_ID, "Raider"):
            yield self.jump(self.npc_targeting)


    @label()
    def npc_targeting(self):
        # if self.task.SPAWNED_ID:
        #     yield PollResults.

        the_target = query.closest(self.task.SPAWNED_ID, query.role("__PLAYER__"), 2000)
        if the_target is None:
            the_target = query.closest(self.task.SPAWNED_ID, query.role("Station"))
        if the_target is not None:
            query.target(self.task.sim, self.task.SPAWNED_ID, the_target, True)

        yield self.delay(5)
        yield self.jump(self.npc_targeting)

