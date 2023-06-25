import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.pymast.pymasttask import label
from sbs_utils.pymast.pymastcomms import receive
from sbs_utils.gridobject import GridObject
import random


class InternalDamage:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_damage_internal(self.take_internal_damage)


    @label()
    def take_internal_damage(self) :

        # This called when there is damage being taken internally
        #
        # The DAMAGE_ORIGIN_ID is the ship being damaged
        # EVENT has the event data sub_float has the amount, source_point has the point
        #

        # Make sure you don't take further damage
        if query.has_role(self.task.DAMAGE_ORIGIN_ID, "exploded"):
            self.task.end()

        # pick a random system 
        system_hit = random.randint(0,3)
        blob = query.get_engine_data_set(self.task.sim, self.task.DAMAGE_ORIGIN_ID)

        damage_amount = self.task.EVENT.sub_float
        #
        # Deal damage evenly, but start at a random system
        #
        # Get open hull points
        points = query.get_inventory_value(self.task.DAMAGE_ORIGIN_ID, "undamaged")
        #
        # I we haven't set it then get the valid grid points
        #
        if points is None:
            points = query.get_open_grid_points(self.task.sim,self.task.DAMAGE_ORIGIN_ID)
            #
            # Maybe remove some?
            #
            query.set_inventory_value(self.task.DAMAGE_ORIGIN_ID, "undamaged", points)

        icons = [40,59,33,27]
        colors = ["red", "red", "red", "red"]

        if len(points)>0:
            point = random.choice(points)
            #do print(f"point {point}")
            points.remove(point)
            query.set_inventory_value(self.task.DAMAGE_ORIGIN_ID, "undamaged", points)

            dam_go = GridObject().spawn(self.task.sim, self.task.DAMAGE_ORIGIN_ID, f"damage", "", point[0],point[1], icons[system_hit], colors[system_hit], "damage")
            #
            # Keep track of the type of damage
            #
            query.set_inventory_value(dam_go, "system", system_hit)
            #
            # The damage needs to be linked to the ship
            #
            query.link(self.task.DAMAGE_ORIGIN_ID, "damage", query.to_id(dam_go)) 
            dam_go.blob.set("icon_scale", 0.75, 0)

        #
        # Apply damage even if you can't find a spot
        #
        #do print(f"Applying internal damage {damage_amount}")

        max_dam = blob.get('system_max_damage', system_hit)
        current = blob.get('system_damage', system_hit)
        if current <= max_dam:
            blob.set('system_damage', current+0.5 ,  system_hit)
        else:
            blob.set('system_damage', max_dam ,  system_hit)
        #    do print(f"system_damage {system_hit} dam {current+1}")


        # Is this the end?
        should_explode = True

        for sys in range(4):
            max_damage = blob.get('system_max_damage', sys)
            current = blob.get('system_damage', sys)
            if current < max_damage:
                should_explode = False
                break


        if should_explode:
            #
            # type, subtype, source_id, target_id, x, y, z, side
            #
            pos = query.get_pos(self.task.sim, self.task.EVENT.origin_id)
            if pos:
                sbs.create_transient(1, 0, self.task.EVENT.origin_id, 0, pos.x, pos.y, pos.z, "")  

            query.add_role(self.task.EVENT.origin_id, "exploded")

            so = query.to_object(self.task.EVENT.origin_id)
            engine_obj = so.space_object(self.task.sim)
            art_id = so.art_id
            so.set_art_id(self.task.sim,"invisible")

            # Reset the systems to max
            for sys in range(4):
                blob.set('system_damage', 0, sys)
            
            yield self.delay(seconds=5, use_sim=True)
            #
            # Reuse the score update by spawning it ourselves
            # (because the player isn't actually destroyed)
            #
            t = self.scheduler.schedule_task(self.update_score)
            t.DESTROYED_ID = self.task.EVENT.origin_id

            self.task.sim.reposition_space_object(engine_obj, so.spawn_pos.x, so.spawn_pos.y, so.spawn_pos.z)
            so.set_art_id(self.task.sim,art_id)
            query.remove_role(self.task.EVENT.origin_id, "exploded")
        self.task.end()