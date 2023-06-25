import sbs
import sbs_utils.query as query
import sbs_utils.faces as faces
from sbs_utils.pymast.pymasttask import label
from sbs_utils.pymast.pymastcomms import receive


class ExtraGui:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        self.route_weapons_select(self.weapons_select_route)

    def friendly_give_orders(self):
        #
        # Get the comms selected, the NPC ship 
        # dispaly the weapons screen of that ship to aid in 
        # select the orders
        #
        comms_selected = query.get_inventory_value(self.task.page.client_id, "COMMS_TARGET_UID", 0)
        # Get the comms selected face
        station_face = faces.get_face(comms_selected)
        #
        # We get and remember the player ship we are on
        # and its name
        #

        ship = query.get_inventory_value(self.task.page.client_id, "assigned_ship")
        player = query.to_object(ship)

        if player:
            player_name = player.name
        else:
            player_name = "Terran"

        #
        # Switch to the friendly ship
        #
        sbs.assign_client_to_ship(self.task.page.client_id,comms_selected)
        #
        # Make a limit weapons console
        #
        self.gui_activate_console("weapons")
        self.gui_section("area: 25, 4, 100, 80;")
        self.gui_console_widget("2dview")
        #
        # Draw a face and interaction text
        #
        self.gui_section("area:0,4,25,80;")
        self.gui_face(station_face)
        self.gui_row()
        self.gui_text(f"""text: Hello {player_name} tell us what to do""")

        
        yield self.await_gui({
            "Apply": self.apply_give_orders,
            "Cancel": None,
        })
            #
        # Get back on the right ship
        #
        sbs.assign_client_to_ship(self.task.client_id,ship)
        yield self.jump(self.show_console_selected)


    def apply_give_orders(self):
        #
        # The selection will be made in parallel
        # and set in inventory
        #
        message = None
        ship = query.get_inventory_value(self.task.page.client_id, "assigned_ship")
        comms_selected = query.get_inventory_value(self.task.page.client_id, "COMMS_TARGET_UID", 0)
        target_id = query.get_inventory_value(comms_selected, "WEAPONS_SELECTED_ID", None)
        target_point = query.get_inventory_value(comms_selected, "WEAPONS_SELECTED_POINT", None)
        if target_id is not None:
            target_obj = query.to_object(target_id)
            if target_obj is not None:
                shoot = query.has_role(target_id, "raider")

                query.set_inventory_value(comms_selected, "TARGET_ID", target_id)
                if shoot:
                    message = "OK {player_name} - going to attack {target_obj.name}"
                else:
                    message = "OK {player_name} - going to rendezvous with {target_obj.name}"

                
                query.target(self.task.sim, comms_selected, target_id, shoot)
            
        elif target_point is not None:
            message = "Heading to designated waypoint"
            query.target_pos(self.task.sim, comms_selected, target_point.x, target_point.y, target_point.z )

        if message is not None:
            receive(message, ship, comms_selected)
            

    def weapons_select_route(self):
        #
        # Handles the 2dView selection for friendlies
        #
        if query.has_role(self.task.WEAPONS_ORIGIN_ID, "friendly"):
            self.task.end()

        nav = query.get_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_NAV", None)
        if nav:
            self.task.sim.delete_navpoint_by_reference(nav)
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_NAV", None)

        # Handle initial clicks
        if self.task.EVENT.selected_id != 0:
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_POINT", None)
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_ID", self.task.EVENT.selected_id)
        else:
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_POINT", self.task.EVENT.source_point)
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_ID", None)
            
            nav = self.task.sim.add_navpoint(self.task.EVENT.source_point.x,self.task.EVENT.source_point.y, self.task.EVENT.source_point.z, "goto", "white")
            nav.visibleToShip = self.task.WEAPONS_ORIGIN_ID
            query.set_inventory_value(self.task.WEAPONS_ORIGIN_ID, "WEAPONS_SELECTED_NAV", nav)



