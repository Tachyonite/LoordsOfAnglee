import tabulate as tb
import random
import glob

from utils.helpers import *
from utils.translator import Translate
from core import Find, Player, Leeani

from utils.saveLoad import saveAllInformation
from utils.saveLoad import loadAllInformation

from math import ceil

def generateActionList(context,player,game):

    actions = []

    actionsToWork = {
        "fisher":"FisherWorkAction()",
        "hunter":"HunterWorkAction()",
        "scavenger":"ScavengerWorkAction()",
        "looter":"LooterWorkAction()",
        "lumberfox":"LumberfoxWorkAction()"
    }


    if context == "nomad_day":

        actions.append(ForageWorkAction())
        actions.append(ExploreWorkAction())
        if hasattr(player.location,'enableWork'):
            for i in player.location.enableWork:
                if player.inventory.collateTools(i):
                    actions.append(eval(actionsToWork[i]))
        actions.append(ViewDetailInventoryAction())
        actions.append(ViewCraftsAction())
        actions.append(ViewCharAction())

        if player.location.linked[0].intel == 100:
            actions.append(RelocateAction())
        actions.append(SaveGameAction(player=player,game=game))
        actions.append(NextHourAction())
        actions[1].exploreArea(player=player)

    return actions

class Action():
    def __init__(self, name, description):
        self.name = name
        self.desc = description

    def __str__(self):
        return self.name


class BlankAction(Action):
    def __init__(self, name, desc):
        super().__init__(name, desc)

    def perform(self):
        pass

class NewGameAction(Action):
    def __init__(self, name, desc):
        super().__init__(name, desc)

    def perform(self, player, game):
        u()
        print(Find.ChapterDef("nomad").getVignette())
        print()
        p(Find.ChapterDef("nomad").getDescription())
        player.SpawnLeeani()
        player.SpawnLeeani()
        player.SpawnLeeani()
        player.SpawnLeeani()
        player.SpawnLeeani()
        # for i in range(300):
        #     player.inventory.addItem(random.choice(list(game.itemDefs.keys())), 1)
        game.setDefs["normal"].add(player)
        player.location = random.choice(list(game.locationDefs.values()))
        player.location.generateLinked(game)

class SaveGameAction(Action):
    def __init__(self,player,game):
        super().__init__(name="Save Game", description="Save Game")

    def perform(self,player,game):
        u()
        p(Translate("save_game_prompt"))
        savename  = input("  ")
        saveAllInformation(savename,player,game)
        print(player.location)


class LoadGameAction(Action):
    def __init__(self):
        super().__init__(name="Load Game", description="Load Game")

    def perform(self,playerold,gameold):
        global player
        global game
        table = glob.glob("saves/*.dat")
        print(tb.tabulate([[i+1,x.replace(".dat","")] for i,x in enumerate(table)],headers=["#","filename"], tablefmt="simple"))
        print("--")
        gamesave = a(Translate("load_game_prompt"),table)+1
        player, game = loadAllInformation(table[gamesave-1])
        print(game.chapterDefs[player.chapter].getVignette())
        print()
        p(game.chapterDefs[player.chapter].getDescription())
        return player, game


class RelocateAction(Action):
    def __init__(self):
        super().__init__(name=Translate('relocate_action'),description=Translate('relocate_action'))
    def perform(self,player):
        p("You'll be moving to the {}.".format(player.location.linked[0].label))
        p("Relocating will empty any non-sealed containers, and any items that are not moveable.")
        p("You won't be able to return to this location.")
        p("These things will be left behind:")
        for k, v in player.inventory.contents.items():
            if not game.itemDefs[k].moveable:
                p(" - " + v[0].label)
        p("Proceed? y/n")
        act = getch()
        if act == "y":
            p("Everyone is packing up and getting ready to move to the {}.".format(player.location.linked[0].label))
            self.checkWorldEvents()
            p("Press any key to continue.")
            msvcrt.getch()
            player.location = player.location.linked[0]
            player.location.generateLinked(game)
    def checkWorldEvents(self):
        pass

class NextHourAction(Action):
    def __init__(self):
        super().__init__(name=Translate('next_hour_action'),description=Translate('next_hour_action'))
    def perform(self,player):
        if not player.addTime(): # THE DAY IS OVER
            p("Everyone's back for the night. They will keep their assigned jobs and do them as many times as they can in the day unless you change them when they next come back.")
            for lee in player.group.values():
                if lee.afk:
                    if lee.jobTimeLeft <= 2:
                        p(tc.c+"{} returned from {}".format(lee.fullName, lee.job.labelDo)+tc.w)
                        if lee.job.defName == "explorer":
                            gainedIntel = lee.stats.learning + random.randint(0,5)
                            player.location.linked[0].intel += gainedIntel
                            if player.location.linked[0].intel > 100: player.location.linked[0].intel = 100
                            p("+ Scouted {}% on the  {}".format(gainedIntel,player.location.linked[0].label))
                        lee.rollWorkResults()
                        lee.afk = False

                    else:
                        p(tc.y+"{} returned early from {} {}".format(lee.fullName, lee.job.labelDo,lee.jobTimeLeft)+tc.w)
                        lee.afk = False
                else:
                    if lee.job != Find.WorkTypeByName("idle"):
                        p(tc.c + "{} stopped {} for tonight".format(lee.fullName, lee.job.labelDo) + tc.w)
                lee.satisfyNutrition()
            msvcrt.getch()
        else: # AN HOUR PASSES
            textDisp = False
            for lee in player.group.values():

                if lee.job == Find.WorkTypeByName("crafter"):
                    lee.calculateCrafts()

                if not lee.afk:
                    if lee.job == Find.WorkTypeByName("idle"):
                        pass
                    else:
                        lee.jobTimeLeft = lee.job.timeCost() - 1
                        if not hasattr(lee.job,'goesAfk') or (hasattr(lee.job,'goesAfk') and lee.job.goesAfk):
                            lee.afk = True

                else:
                    lee.jobTimeLeft -= 1
                    if lee.jobTimeLeft == 0:
                        textDisp = True
                        p(tc.c+"{} returned from {}".format(lee.fullName, lee.job.labelDo)+tc.w)
                        if lee.job.defName == "explorer":
                            gainedIntel = lee.stats.learning + random.randint(0,5)
                            player.location.linked[0].intel += gainedIntel
                            if player.location.linked[0].intel > 100: player.location.linked[0].intel = 100
                            p("+ Scouted {}% on the {}".format(gainedIntel,player.location.linked[0].label))
                        lee.rollWorkResults()
                        lee.afk = False
            if textDisp:
                msvcrt.getch()




class ListStatsAction(Action):
    def __init__(self, name, desc):
        super().__init__(name, desc)

    def perform(self,chars):
        table = []
        for i in range(len(chars)):
            table.append(
                [tc.w + str(i), chars[i].fn, chars[i].vigour, chars[i].utility, chars[i].logic, chars[i].perception,
                 chars[i].eloquence, chars[i].strength, chars[i].job + tc.y])

class ListAction(Action):
    def __init__(self, name, desc):
        super().__init__(name, desc)

    def perform(self, actions, headers, player=False,game=False):
        alphas = getAlphas(actions)
        table = [[alphas[i],x.name] for i,x in enumerate(actions)]
        print(tb.tabulate(table, headers, "simple"))
        print("--")
        ac = a(Translate('choose_string'),table)
        acTodo = actions[ac]
        if 'group' in acTodo.perform.__code__.co_varnames:
            return acTodo.perform(player.group)
        elif 'player' in acTodo.perform.__code__.co_varnames and 'game' in acTodo.perform.__code__.co_varnames:
            return acTodo.perform(player,game)
        elif 'playerold' in acTodo.perform.__code__.co_varnames and 'gameold' in acTodo.perform.__code__.co_varnames:
            return acTodo.perform(player,game)
        elif 'player' in acTodo.perform.__code__.co_varnames:
            return acTodo.perform(player)
        else:
            return acTodo.perform()

class WorkAction(Action):
    def __init__(self, name, description, workName):
        super().__init__(name, description)
        self.workType = Find.WorkTypeByName(workName)

    def perform(self,player):
        act = ListJobAssignAction()
        lee = True
        while lee != False:
            u()
            lee = act.perform(player, workType=self.workType, returnLeeani=True) #type: Leeani
            if not lee: break
            if lee.afk: lee = True
            elif lee.job == self.workType:
                lee.job = Find.WorkTypeByName("idle")
            else:
                lee.job = self.workType
                lee.jobAssignedHour = player.hour
                lee.jobTimeLeft = self.workType.timeCost() - 1

class ForageWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_forage'), Translate('action_forage_desc'),"forager")
class FisherWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_fisher'), Translate('action_fisher_desc'),"fisher")
class HunterWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_hunter'), Translate('action_hunter_desc'),"hunter")
class ScavengerWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_scavenger'), Translate('action_scavenger_desc'),"scavenger")
class LooterWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_looter'), Translate('action_looter_desc'),"looter")
class LumberfoxWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_lumberfox'), Translate('action_lumberfox_desc'),"lumberfox")

class ExploreWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_explore'), Translate('action_explore_desc'),"explorer")
    def exploreArea(self,player):
        self.linked = player.location.linked[0]
        self.name = "{} {}".format(Translate('action_explore'),self.linked.label.title())


class CraftingWorkAction(WorkAction):
    def __init__(self):
        super().__init__(Translate('action_craft'), Translate('action_craft_desc'),"crafter")

class ListJobAssignAction(Action):
    def __init__(self):
        super().__init__('listjob', 'lists jobs for assignment')
    def perform(self,player,workType,returnLeeani=True):
        u()
        group = player.group
        headers = ["#",
            Translate('fullname'),
            Translate('hitpoints'),
            Translate('vitality_short'),
            Translate('utility_short'),
            Translate('learning_short'),
            Translate('perception_short'),
            Translate('eloquence_short'),
            Translate('strength_short'),
            Translate('work_header')
        ]
        favoured = [
            "vitality",
            "utility",
            "learning",
            "perception",
            "eloquence",
            "strength"
        ]
        if hasattr(workType,'skills'):
            f1 = [k for k,v in workType.skills.items() if v==1][0]
            f2 = [k for k,v in workType.skills.items() if v==2][0]
            p(dv.header(Translate('job_choose_string').format(workType.label.upper())))
            print()
            p(workType.description)
            p("There are {} hours left in the day.{}".format(tc.f + str(player.dayLength - player.hour) if player.dayLength - player.hour < workType.timeCost() else tc.w + str(player.dayLength - player.hour),tc.w))
            if 8 - player.hour < workType.timeCost():
                p("They may return with less resources than expected.")
            p("{0} favours {1}» and {2}›".format(workType.labelDo.title(),tc.y + f2.title() + tc.w,tc.y + f1.title() + tc.w))
            p(Translate('assignment_suggestion'))

            for i,skill in enumerate(iter(favoured)):
                if skill == f1:
                    headers[i + 3] = tc.y + headers[i + 3] + tc.w + "›"
                if skill == f2:
                    headers[i + 3] = tc.y + headers[i + 3] + tc.w + "»"
        table = [[
            value.fullName,
            value.hp
        ] + value.stats.getWorkFormatted(workType) + [value.job.labelDo] for key,value in group.items()] #type: str, Leeani
        table.append(["[[BACK]]"])
        tableView = [[
            value.fullName if not value.afk else value.fullName + " (away)",
            value.hp
        ] + value.stats.getWorkFormatted(workType) + [value.job.labelDo] for key,value in group.items()]
        tableView.append(["[[BACK]]"])
        for i,x in enumerate(iter(tableView)): #type: int, list
            x.insert(0,i+1)
            if "idling" not in x and i != len(tableView)-1:
                for z in x:
                    zz = x[x.index(z)]
                    if group[table[i][0]].job == workType:
                        x[x.index(z)] = tc.b + tc.bg_w + str(zz)
                    else:
                        x[x.index(z)] = tc.b + str(zz)
            x[-1] = x[-1] + tc.w + tc.bg_b
        print()
        print(tb.tabulate(tableView,headers))
        ## KEY ##
        p("{}={}, {}={}, {}={}, {}={}".format(
            tc.y + "X" + tc.w,Translate("bonus_key"),
            tc.f + "X" + tc.w,Translate("penalty_key"),
            tc.b + tc.bg_w + "X" + tc.bg_b + tc.w,Translate("assigned_key"),
            tc.b + "X" + tc.w,Translate("elsewhere_key")
        ),wrap=False,gap=True)
        p("Select a leeani for this job:",gap=True)
        sel = a(Translate('choose_string'),table)
        if sel == len(table) or sel == "":
            return False
        try:
            lee = group[table[sel][0]]
        except KeyError:
            return False
        return lee

class ViewCraftsAction(Action):
    def __init__(self):
        super().__init__(name=Translate('view_craft_action'), description=Translate('view_craft_action'))
    def calculateCrafts(self,player):
        for k,v in game.craftingDefs.items():
            print()


    def inv(self, player, tab, page, selectedItemIndex, maxpage):
        print("\033[{};{}H".format(len(tab[4][page]) + 4, 1))
        p("{} {}/{}".format(Translate('page'), page + 1, maxpage + 1))
        p("w | {}".format(Translate('up_item')))
        p("s | {}".format(Translate('down_item')))
        p("d | {}".format(Translate('next_page')))
        p("a | {}".format(Translate('prev_page')))
        p("f | {}".format(Translate('favourite_item')))
        p("# | {}".format(Translate('page_number')))
        p("+ | {}".format(Translate('add_craft')))
        p("- | {}".format(Translate('remove_craft')))
        print(selectedItemIndex)
        print()
        p(tc.c+"e | {}".format(Translate('assign_crafter'))+tc.w)
        print()
        p("Esc/Return | {}".format(Translate('escape')))
        print()
        print("..|")
        maxwidth = max([len(i.label) for i in tab[4][page]]) + 45
        player.inventory.displayCraftDetailsXY(tab[4][page][selectedItemIndex],player.inventory.makeCraft(tab[4][page][selectedItemIndex]),
                                              1, maxwidth,tab[2][page][selectedItemIndex][3],tab[2][page][selectedItemIndex][4])
        print("\033[{};{}H".format(len(tab[4][page]) + 15, 1))

    def perform(self, player):
        u()
        act = True
        page = 0
        selectedItemIndex = 0
        tab = player.inventory.craftTabulate(selectedItemIndex,page=page)
        if not tab:
            print("No recipes available yet. Find more resources or research more.")
            print("Press any key to continue.")
            msvcrt.getch()
            return
        minpage = 0
        maxpage = ceil(tab[1] / player.tableLength) - 1

        print(tab[0], "\n")
        while act:
            self.inv(player, tab, page, selectedItemIndex, maxpage)
            print(tc.bg_w + "\033[{};{}H>".format(selectedItemIndex + 2 + 2, 1) + tc.bg_b)
            act = getch()
            o = 4
            if act == "?":
                return True
            elif act == "e":
                a = CraftingWorkAction()
                u()
                a.perform(player)
                u()
                print(tab[0], "\n")
            elif act == "d" or act == "M":
                if page + 1 <= maxpage:
                    page += 1
                    if selectedItemIndex > len(tab[3][page]) - 1:
                        selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o

                    tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                    u()
                    print(tab[0], "\n")
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "a" or act == "K":
                if page - 1 >= minpage:
                    page -= 1
                    if selectedItemIndex > len(tab[3][page]) - 1:
                        selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o
                    tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                    u()
                    print(tab[0], "\n")
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "s" or act == "P":
                if selectedItemIndex + 1 < len(tab[3][page]):
                    selectedItemIndex += 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(offset - 1, 1))
                else:
                    selectedItemIndex = 0
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(len(tab[3][page]) + o - 1, 1))
            elif act == "w" or act == "H":
                if selectedItemIndex - 1 >= 0:
                    selectedItemIndex -= 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(offset + 1, 1))
                else:
                    selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(len(tab[3][page]) + o - 1, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(o, 1))
            elif act == "f":
                isfav = tab[4][page][selectedItemIndex].favourite
                tab[4][page][selectedItemIndex].favourite = not isfav
                u()
                tab = player.inventory.craftTabulate(selectedItemIndex, page=page)
                offset = selectedItemIndex + o
                print(tab[0], "\n")
                print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "+":

                try:
                    player.queuedCrafts[tab[4][page][selectedItemIndex].defName] += 1
                except KeyError:
                    player.queuedCrafts[tab[4][page][selectedItemIndex].defName] = 1
                u()
                tab = player.inventory.craftTabulate(selectedItemIndex, page=page)
                offset = selectedItemIndex + o
                print(tab[0], "\n")
                print(tc.bg_w +"\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "-":

                if player.queuedCrafts[tab[4][page][selectedItemIndex].defName] > 0:
                    player.queuedCrafts[tab[4][page][selectedItemIndex].defName] -= 1
                    u()
                    offset = selectedItemIndex + o
                    tab = player.inventory.craftTabulate(selectedItemIndex, page=page)
                    print(tab[0], "\n")
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            else:
                if act == "":
                    return False
                try:
                    if int(act) in range(minpage + 1, maxpage + 2):
                        page = int(act) - 1
                except:
                    return False

class ViewInventoryAction(Action):
    def __init__(self):
        super().__init__(name=Translate('view_inventory_action'),description=Translate('view_inventory_action'))
    def perform(self, player):
        act = True
        page = 0
        while act:
            u()
            tab = player.inventory.tabulate(page=page,sort="rarity")
            minpage = 0
            maxpage = ceil(tab[1]/player.tableLength)-1
            print(tab[0],"\n")
            if tab[2] >= player.carryWeight:
                p("{}: {}/{}kg".format(Translate('carry_weight'), tc.f + str(round(tab[2])),
                                       str(player.carryWeight)) + tc.w)
            else:
                p("{}: {}/{}kg".format(Translate('carry_weight'), str(round(tab[2])), player.carryWeight))
            print()
            p("Days of food: {}".format(player.inventory.calcFoodDays(player.group)))
            p("Days of water: {}".format(player.inventory.calcWaterDays(player.group)))
            print()
            p("{} {}/{}".format(Translate('page'), page + 1, maxpage + 1))
            p("d | {}".format(Translate('next_page')))
            p("a | {}".format(Translate('prev_page')))
            p("# | {}".format(Translate('page_number')))
            p("? | {}".format(Translate('detail_mode')))
            print()
            p("Esc/Return | {}".format(Translate('escape')))
            print()
            print("..| ")
            act = getch()
            if act == "?":
                newAct = ViewDetailInventoryAction()
                r = newAct.perform(player)
                if not r:
                    return
            elif act == "d" or act == "M":
                if page + 1 <= maxpage:
                    page += 1
            elif act == "a" or act == "K":
                if page - 1 >= minpage:
                    page -= 1
            else:
                if act == "":
                    return
                try:
                    if int(act) in range(minpage+1,maxpage+2):
                        page = int(act)-1
                except:
                    return

class ViewDetailInventoryAction(Action):
    def __init__(self):
        super().__init__(name=Translate('view_inventory_action'),description=Translate('view_inventory_action'))
    def inv(self,player,tab,page,selectedItemIndex,maxpage):
        print("\033[{};{}H".format(len(tab[2][page]) + 5, 1))
        if tab[4] >= player.carryWeight:
            p("{}: {}/{}kg".format(Translate('carry_weight'), tc.f + str(round(tab[4])),
                                   str(player.carryWeight)) + tc.w)
        else:
            p("{}: {}/{}kg".format(Translate('carry_weight'), str(round(tab[4])), player.carryWeight))
        print()
        p("Days of food: {}".format(player.inventory.calcFoodDays(player.group)))
        p("Days of water: {}".format(player.inventory.calcWaterDays(player.group)))
        print()
        p("{} {}/{}".format(Translate('page'), page + 1, maxpage + 1))
        p("w | {}".format(Translate('up_item')))
        p("s | {}".format(Translate('down_item')))
        p("d | {}".format(Translate('next_page')))
        p("a | {}".format(Translate('prev_page')))
        p(tc.f+"x | {}".format(Translate('drop_item'))+tc.w)
        p("# | {}".format(Translate('page_number')))
        p("? | {}".format(Translate('simple_mode')))
        print()
        p("Esc/Return | {}".format(Translate('escape')))
        print()
        print("..|")
        maxwidth = max([len(i.labelResolved()) for i in tab[2][page]]) + 18
        try:
            player.inventory.displayItemDetailsXY(tab[2][page][selectedItemIndex], tab[3][page][selectedItemIndex][1], 1, maxwidth)
        except IndexError:
            player.inventory.displayItemDetailsXY(tab[2][page][-1], tab[3][page][-1][1],
                                                  1, maxwidth)
            selectedItemIndex = len(tab[2][page]) - 1
        print("\033[{};{}H ".format(len(tab[2][page]) + 4, 1))
        print("\033[{};{}H".format(len(tab[2][page]) + 15, 1))
        return selectedItemIndex

    def perform(self,player):
        u()
        act = True
        page = 0
        selectedItemIndex = 0
        tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
        if not tab:
            u()
            p("Nothing in the inventory! Maybe get some items and then come back.")
            msvcrt.getch()
            return
        minpage = 0
        maxpage = ceil(tab[1] / player.tableLength) - 1

        print(tab[0])
        while act:
            selectedItemIndex = self.inv(player,tab,page,selectedItemIndex,maxpage)
            print(tc.bg_w + "\033[{};{}H>".format(selectedItemIndex+ 2 + 2, 1) + tc.bg_b)
            act = getch()
            o = 4
            if act == "?":
                newAct = ViewInventoryAction()
                r = newAct.perform(player)
                if not r:
                    return
            elif act == "d" or act == "M":
                if page + 1 <= maxpage:
                    page += 1
                    if selectedItemIndex > len(tab[3][page]) - 1:
                        selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o
                    tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                    u()
                    print(tab[0], "\n")
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "a" or act == "K":
                if page - 1 >= minpage:
                    page -= 1
                    if selectedItemIndex > len(tab[3][page]) - 1:
                        selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o
                    tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                    u()
                    print(tab[0], "\n")
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "s" or act == "P":
                if selectedItemIndex + 1 < len(tab[3][page]):
                    selectedItemIndex += 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(offset-1, 1))
                else:
                    selectedItemIndex = 0
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(len(tab[3][page]) + o - 1, 1))
            elif act == "w"or act == "H":
                if selectedItemIndex - 1 >= 0:

                    selectedItemIndex -= 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(offset + 1, 1))
                else:
                    selectedItemIndex = len(tab[3][page]) - 1
                    offset = selectedItemIndex + o
                    print(tc.bg_w + "\033[{};{}H>".format(len(tab[3][page]) + o-1, 1) + tc.bg_b)
                    print("\033[{};{}H|".format(o, 1))
            elif act == "x":
                player.inventory.removeItem(tab[2][page][selectedItemIndex].defName,1)
                offset = selectedItemIndex + o
                tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                if not tab:
                    u()
                    p("Nothing in the inventory! Maybe get some items and then come back.")
                    msvcrt.getch()
                    return
                u()
                print(tab[0], "\n")
                print(tc.bg_w + "\033[{};{}H>".format(offset, 1) + tc.bg_b)
            elif act == "u" and hasattr(tab[2][page][selectedItemIndex],'openable'):
                selItem = tab[2][page][selectedItemIndex]
                for k,v in selItem.openable['contents'].items():
                    if k.startswith("$"):
                        for vv in range(v):
                            player.inventory.openCrate(selItem)
                            player.inventory.removeItem(game.crateDefs[k[1:]].crateItemDef,1)
                    else:
                        player.inventory.addItem(k,v)
                        player.inventory.removeItem(selItem.defName, 1)
                tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                u()
                print(tab[0], "\n")

            else:
                if act == "":
                    return False
                try:
                    if int(act) in range(minpage+1,maxpage+2):
                        page = int(act)-1
                        tab = player.inventory.nameTabulate(selectedItemIndex, page=page, sort="rarity")
                        u()
                        print(tab[0], "\n")
                except:
                    return False

class ViewCharAction(Action):
    def __init__(self):
        super().__init__(name=Translate('view_character_action'),description=Translate('view_character_action'))

    def perform(self, group, *pos):
        try:
            group = list(group.values())
        except AttributeError:
            pass
        u()
        print(dv.header("Character Biography"))
        if pos:
            group[pos[0]].printOut()
        else:
            group[0].printOut()
        print("\n\n")
        headers = ["#", ""]
        table = []
        for i in range(len(group)):
            table.append([i, group[i].fullName])
        table.append(["\n", ""])
        table.append([tc.w + str(len(group)), "["+Translate('back_string')+"]" + tc.w])
        print(tb.tabulate(table, headers) + "\n")
        ac = a(Translate('choose_string'), table)
        if ac < len(group):
            self.perform(group,ac)
