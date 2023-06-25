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
        elif query.has_roles(self.task.SPAWNED_ID, "tsn, friendly"):
            yield self.jump(self.ai_task_friendly)
        elif query.has_role(self.task.SPAWNED_ID, "Raider"):
            yield self.jump(self.npc_targeting)


    @label()
    def npc_targeting(self):
        if not query.object_exists(self.task.sim, self.task.SPAWNED_ID):
            yield self.task.end()

        the_target = query.closest(self.task.SPAWNED_ID, query.role("__PLAYER__"), 2000)
        if the_target is None:
            the_target = query.closest(self.task.SPAWNED_ID, query.role("Station"))
        if the_target is not None:
            query.target(self.task.sim, self.task.SPAWNED_ID, the_target, True)

        yield self.delay(5)
        yield self.jump(self.npc_targeting)

    #
    # AI for friendly tsn ships (not citizen ships)
    #
    @label()
    def ai_task_friendly(self):
        if not query.object_exists(self.task.sim, self.task.SPAWNED_ID):
            yield self.task.end()

        #
        # Comms can give orders to attack a target (or approach another friendly) 
        #
        the_target = query.get_inventory_value(self.task.SPAWNED_ID, "TARGET_ID", None)

        scanned = query.get_inventory_value(self.task.SPAWNED_ID, "SCANNED")
        #
        # This is naive and assume players are on one side
        #
        if not scanned: 
            should_scan = query.closest(self.task.SPAWNED_ID, query.role("__PLAYER__"), 5000)
            if should_scan is not None:
                pass
                #self.follow_route_science_select(self.task.SPAWNED_ID)
                #follow route science select should_scan SPAWNED_ID

        #
        # Only shoot raiders
        #            
        if the_target is not None:
            shoot = query.has_role(the_target, "raider")
            query.target(self.task.sim, self.task.SPAWNED_ID, the_target, shoot)

        #
        # call this logic every 5 seconds
        #
        yield self.delay(seconds=5)
        yield self.jump(self.ai_task_friendly)



