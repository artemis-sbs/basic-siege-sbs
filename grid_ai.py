import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.pymast.pymasttask import label
from sbs_utils.pymast.pymastcomms import receive
import random


class GridAi:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_grid_spawn(self.handle_grid_spawn)

    @label()
    def handle_grid_spawn(self) :
        # AI for the player is the docking logic
        if query.has_role(self.task.SPAWNED_ID, "damcons"):
            yield self.jump(self.damcon_ai)
        yield self.task.end()

    @label()
    def damcon_ai(self) :

        this_blob = query.get_engine_data_set(self.task.sim, self.task.SPAWNED_ID)

        # The damcons is no longer
        if this_blob is None:
            self.task.end()


        length = this_blob.get("path_length", 0)
        if length is None or length < 1:
            # check for garbage and mop up
            obj = query.to_object(self.task.SPAWNED_ID)
            x = this_blob.get("curx", 0)
            y = this_blob.get("cury", 0)
            
            # Damcon is no more
            if obj is None:
                self.task.end()

            # Host is no more 
            hm = self.task.sim.get_hull_map(obj.host_id)
            if hm is None:
                self.task.end()

            points = query.get_inventory_value(obj.host_id, "undamaged")
            #
            # I we haven't set it then get the valid grid points
            #
            if points is None:
                points = query.get_open_grid_points(self.task.sim,obj.host_id)
                #
                # Maybe remove some?
                #
                query.set_inventory_value(obj.host_id, "undamaged", points)


            at_point = hm.get_objects_at_point(x,y)
            
            for id in at_point:
                # Only deal with Damage
                if not query.has_role(id, "damage"):
                    continue


                go = query.to_object(id)
                if go is None:
                    continue

                eo = go.get_engine_object(self.task.sim)
                hm.delete_grid_object(eo)
                # Have to unlink this so it is no longer seen
                query.unlink(obj.host_id, "damage", id)
                system_heal = query.get_inventory_value(go, "system")
                query.unlink(self.task.SPAWNED_ID, "assigned", id )
                go.destroyed()
                #
                # Add point back into undamaged
                #
                points.append((x,y))
                query.set_inventory_value(obj.host_id, "undamaged", points)
            
                if system_heal is None:
                    system_heal = random.randint(0,3)
                

                ship_blob = query.get_engine_data_set(self.task.sim, go.host_id)
            
                current = ship_blob.get('system_damage', system_heal)
                if current >0:
                    ship_blob.set('system_damage', current-0.6 , system_heal)
                else:
                    ship_blob.set('system_damage', 0 ,  system_heal)
                
            # Then look for more work
            # Find damage that is not assigned to someone else
            the_target = query.grid_closest(self.task.sim, self.task.SPAWNED_ID, query.linked_to(obj.host_id, "damage")-query.has_link("assigned_to"))
            if the_target is not None:
                query.grid_target(self.task.sim, self.task.SPAWNED_ID, the_target)
                # Remove from available assignments
                query.link(the_target, "assigned_to", self.task.SPAWNED_ID)
                query.link(self.task.SPAWNED_ID, "assigned", the_target )
            else:
                query.grid_target_pos(self.task.sim, self.task.SPAWNED_ID, obj.spawn_pos.x, obj.spawn_pos.y)

        #
        # Loop while this damcon lives
        #
        yield self.delay(seconds=5, use_sim=True)
        yield self.jump(self.damcon_ai)


