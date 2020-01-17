import colorama
from utils.loader import *
from utils.actions import *
from utils.translator import Translate

from core import *

colorama.init(autoreset=True)

def displayDay(day,hour):
    u()
    p("Day {} | {} (Hour {}/{})".format(player.day,player.formTime(),player.hour,player.dayLength))
    p("")
    listAction.perform(actions=generateActionList("nomad_day"), headers=["", ""], player=player)

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
player.calcCarryWeight()
for i in range(100):
    player.inventory.addItem(random.choice(list(game.itemDefs.keys())), 1)
player.inventory.addItem('berries',20)
player.inventory.addItem('plasticBottle',5)
player.inventory.addItem('plasticJug',2)
player.inventory.addItem('hacksaw',1)
player.inventory.addItem('cannedFoodBeans',3)
player.inventory.addItem('cannedFoodMysteryMeat',3)
hour = 0
while True:
    displayDay(1,hour)