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
        players = []
        pick_player = None
        for player in query.to_object_list(query.role("__PLAYER__")):
            players.append(player.name)
        if self.player_count != players:
            if len(players):
                player = players[0]
                players = ",".join(players)
                self.gui_section("area: 25, 65, 39, 90;row-height: 45px;")
                pick_player = self.gui_radio(players, player, True)

        self.gui_section("area: 75, 65, 99, 90;")
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
            yield self.jump(self.start_client)
        
        # Keep running the console
        while True:
            self.assign_player_ship(self.task.PLAYER_NAME)
            self.gui_console(self.task.CONSOLE_SELECT)

            yield self.await_gui()