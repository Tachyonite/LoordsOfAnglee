import colorama
from utils.loader import *
from utils.actions import *
from utils.translator import Translate

from core import *

colorama.init(autoreset=True)

def displayDay(day,hour):
    u()
    print(player.location.vignette)
    print("")
    p(tc.c+"{}".format(player.groupStatus+tc.w))
    p("Day {} | {} (Hour {}/{})".format(player.day,player.formTime(),player.hour,player.dayLength))
    p("{}: {}".format(player.location.label.capitalize(),player.location.description.capitalize()))
    p("A {} is close by ({}% scouted).".format(player.location.linked[0].label,player.location.linked[0].intel))
    listAction.perform(actions=generateActionList("nomad_day",player=player), headers=["", ""], player=player)

u()
print(Translate("title"))
print("\n")
print("  "+ Translate('splash',random=True))
listAction = ListAction(name="list",desc=None)
listAction.perform(actions=[
                            NewGameAction("New Game","Creates a new game.")
                            ],
                            headers= [
                            "",""
                            ]
                   )
input(Translate('choose_string'))

player.SpawnLeeani()
player.SpawnLeeani()
player.SpawnLeeani()
player.SpawnLeeani()
player.SpawnLeeani()
# for i in range(300):
#     player.inventory.addItem(random.choice(list(game.itemDefs.keys())), 1)
player.inventory.addItem('berries',20)
player.inventory.addItem('plasticBottle',5)
player.inventory.addItem('plasticJug3L',2)
player.inventory.addItem('hacksaw',1)
player.inventory.addItem('cannedFoodBeans',3)
player.inventory.addItem('cannedFoodMysteryMeat',3)
player.inventory.addItem('junkCrate',3)
player.inventory.addItem('commonCrate',3)
player.inventory.addItem('uncommonCrate',3)
player.location = random.choice(list(game.locationDefs.values()))
player.location.generateLinked(game)
player.calcCarryWeight()
hour = 1
while True:
    displayDay(1,hour)