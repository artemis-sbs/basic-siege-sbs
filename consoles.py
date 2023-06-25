import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label
import functools

class ClientGui:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This style of init makes it more mixin friendly
        

    @label()
    def start_client(self):
        self.route_change_console(self.start_client)
        console_select = "helm"
        client_select_ship = "artemis"
        yield self.jump(self.select_console)

    
    @label()
    def select_console(self):
        
        players = []
        pick_player = None
        player_index = 0
        i=0
        for player in self.player_list:
            players.append(player.name)
            if pick_player is not None and player.name == pick_player.value:
                player_index = i
            i+=1
            # if i >= self.player_count:
            #     break
            


        if len(players):
            player = players[player_index]
            players = ",".join(players)
            self.gui_section("area: 25, 55, 39, 90;")
            pick_player = self.gui_radio(players, player, True, "row-height: 55px;")

        self.gui_section("area: 75, 55, 99, 90;")
        console = self.gui_radio("Helm, Weapons, Comms, Engineering, Science", "Helm", True)
        self.task.PLAYER_NAME = "artemis"
        self.task.CONSOLE_SELECT = "helm"



        def on_message(sim, event):
            #
            # Not sure I like passing data this way
            # but it is similar to mast
            # maybe inventory should be used on client_id
            #
            if pick_player is not None and event.sub_tag == pick_player.tag:
                self.task.PLAYER_NAME = pick_player.value
                return True
            elif event.sub_tag.startswith(console.tag):
                self.task.CONSOLE_SELECT = console.value
                return True
            return False

        #, pick_player, console
        yield self.await_gui({
            "Accept": self.show_console_selected
        }, on_message=on_message)

            
    
    def show_console_selected(self):
        

        if self.task.PLAYER_NAME is None or self.task.CONSOLE_SELECT is None:
            yield self.jump(self.select_console)

        for player_ship in query.to_object_list(query.role("__PLAYER__")):
            if player_ship.name.lower() == self.task.PLAYER_NAME:
                has_ship = True
                sbs.assign_client_to_ship(self.task.page.client_id, player_ship.id)
                query.set_inventory_value(self.task.page.client_id, "assigned_ship", player_ship.id)


        if not has_ship:
            yield self.jump(self.select_console)

        
        # Keep running the console
        while True:
            self.assign_player_ship(self.task.PLAYER_NAME)
            self.gui_console(self.task.CONSOLE_SELECT)

            yield self.await_gui()