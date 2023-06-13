import sbs
import sbs_utils.query as query
from sbs_utils.pymast.pymasttask import label

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

        def console_selected():
            pass

        yield self.await_gui({
            "Accept": console_selected
        })

        if pick_player is None:
            yield self.jump(self.start_client)
        player_name = pick_player.value
        console_sel = console.value.lower()
        # Keep running the console
        while True:
            self.assign_player_ship(player_name)
            self.gui_console(console_sel)

            yield self.await_gui()
            
    