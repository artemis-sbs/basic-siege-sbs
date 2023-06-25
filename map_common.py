import sbs
import sbs_utils.query as query
import sbs_utils.names as names
import sbs_utils.scatter as scatter
import sbs_utils.faces as faces
import random
from sbs_utils.objects import Npc



class MapCommon:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly

    def spawn_friendly_npc(self):
        match self.friendly_select:
            case "many":
                max_hull_points=20
            case "lots":
                max_hull_points=15
            case "some":
                max_hull_points=10
            case "few":
                max_hull_points=5
            case "none":
                return


        total_hull_points = 0

        attempts = 0

        # grab the ship data for all ships on TSN side
        tsn_ship_data = names.filter_ship_data_by_side(None, "TSN", is_ship=True, ret_key_only=False)
        # pick a random tsn ship
        count = 0

        spawn_points = scatter.sphere(100, 0,0,0, 500, 5000, ring=True)
        while total_hull_points<max_hull_points:
            #
            ship = random.choice(tsn_ship_data)

            hull_points = ship["hullpoints"]

            if hull_points+total_hull_points > max_hull_points:
                attempts += 1
                # failed to find a small enough ship
                if attempts > 20:
                    break
                #
                # try again
                continue
            # reset attempts
            attempts = 0
            # OK add this ship
            spawn_point = next(spawn_points)
            friend = query.to_id(Npc().spawn(self.task.sim, *spawn_point, f"tsn{count}", "tsn, friendly", ship["key"], "behav_npcship"))
            count += 1
            total_hull_points += hull_points
            faces.set_face(friend, faces.random_terran())

            
            
            
                
