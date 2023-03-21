import sbslibs
import sbs
import sbs_utils.query as query
from sbs_utils.pymast import PollResults

def task_player_docking(story):
    # self is the async story
    task_delay = 5
    while True:
        yield story.delay(task_delay)
        player_ships = query.role("basic_docking")
        if len(player_ships):
            return PollResults.OK_END
        
        for player_ship_id in player_ships:
            if story.sim.space_object_exists(player_ship_id):

                player = story.sim.get_space_object(player_ship_id)
                blob = query.get_engine_data_set(player_ship_id, story.sim)
                
                dock_state_string = blob.get("dock_state", 0)
                if "undocked" == dock_state_string:
                    #####################################
                    ## Have task run slower
                    
                    blob.set("dock_base_id", 0) # clear the dock-able id

                    dock_rng = 600

                    station_scan = sbs.broad_test(-dock_rng + player.pos.x, -dock_rng + player.pos.z, dock_rng + player.pos.x, dock_rng + player.pos.z, 1)
                    for thing in station_scan:
                        if "behav_station" == thing.tick_type:
                            # check to see if the player ship is close enough to be offered the option of docking
                            distance_value = sbs.distance(thing, player)
                            if distance_value <= dock_rng:
                                blob.set("dock_base_id", thing.unique_ID) # set the dock-able id of the player to this station

                dock_station_id = blob.get("dock_base_id", 0)
                if story.sim.space_object_exists(dock_station_id):
                    dock_station = story.sim.get_space_object(dock_station_id)
                    station_blob = dock_station.data_set

                    if "docking" == dock_state_string:
                        # check to see if the player ship is close enough to be docked
                        distance_value = sbs.distance(dock_station, player)
                        close_enough = dock_station.exclusion_radius + player.exclusion_radius
                        close_enough *= 1.1
                        if distance_value <= close_enough:
                            blob.set("dock_state", "docked")
                        else:
                            print("Docking dist: " + str(distance_value) + ",       close_enough: " + str(close_enough))


                    if "docked" == dock_state_string:
                        ################
                        ## Make task faster
                        task_delay = 1
                        # refuel
                        fuel_value = blob.get("energy", 0)
                        fuel_value += 20
                        if fuel_value > 1000:
                            fuel_value = 1000
                        blob.set("energy", fuel_value)

                        # resupply torps
                        for g in range(sbs.TORPEDO.MINE):
                            tLeft = station_blob.get("torpedo_count", g)
                            if tLeft > 0:
                                torp_max = blob.get("torpedo_max", g)
                                torp_now = blob.get("torpedo_count", g)
                                if torp_now < torp_max:
                                    torp_now = torp_now + 1
                                    blob.set("torpedo_count", torp_now,g)
                                    station_blob.set("torpedo_count", tLeft-1, g)


                        #repair shields (more than normal)
                        shield_coeff = blob.get("repair_rate_shields",0)
                        system_coeff = blob.get("repair_rate_systems",0)

                        s_count = blob.get("shield_count",0)
                        for g in range(s_count-1):
                            s_val = blob.get("shield_val", g)
                            s_val_max = blob.get("shield_max_val", g)
                            changed = (s_val < s_val_max)
                            s_val = max(0.0, min(s_val + shield_coeff, s_val_max)) # clamp the value
                            if changed:
                                blob.set("shield_val", s_val, g);

                        #repair systems (more than normal)
                        for g in range(sbs.SHPSYS.SHIELDS):
                            damage = blob.get("system_damage", g)
                            max_damage = blob.get("system_max_damage", g)
                            changed = (damage > 0.0)
                            damage = max(0.0, min(damage - system_coeff, max_damage)) # clamp the value
                            if changed:
                                blob.set("system_damage", damage, g)
        yield PollResults.RUN_NEXT_TICK