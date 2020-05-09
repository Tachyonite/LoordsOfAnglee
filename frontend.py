import colorama
from utils.loader import *
from utils.actions import *
from utils.translator import Translate

from core import *

colorama.init(autoreset=True)

def displayDay(player):
    u()
    print(player.location.vignette)
    print("")
    p(tc.c+"{}".format(player.groupStatus+tc.w))
    p("Day {} | {} (Hour {}/{})".format(player.day,player.formTime(),player.hour,player.dayLength))
    p("{}: {}".format(player.location.label.capitalize(),player.location.description.capitalize()))
    for i in player.location.linked:
        p("A {} is close by ({}% scouted).".format(i.label,i.intel))
    listAction.perform(actions=generateActionList("nomad_day",player=player,game=game), headers=["", ""], player=player,game=game)

u()
print(Translate("title"))
print("\n")
print("  "+ Translate('splash',random=True))
listAction = ListAction(name="list",desc=None)
r = listAction.perform(actions=[
                            NewGameAction("New Game","Creates a new game."),
                            LoadGameAction()
                            ],
                            headers= [
                            "",""
                            ],
                   player=player,game=game)
if r:
    player, game = r
input(Translate('choose_string'))
player.calcCarryWeight()
while True:
    displayDay(player)