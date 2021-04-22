import random
import textwrap as tw
import tabulate as tb
import colorama as cr
import cursor
import yaml
import math
import time

from utils.defs import *
from utils.loader import *
from utils.helpers import *
from utils.itemFormat import itemFormat, craftFormat
from utils.translator import Translate

from math import ceil


class Find():
    def ItemDef(defName):
        try:
            item = next(v for k, v in game.itemDefs.items() if v.defName == defName)  # type: Item
            return item
        except StopIteration:
            return False

    def FluidDef(defName):
        try:
            return next(v for k, v in game.fluidDefs.items() if v.defName == defName)  # type: Item
        except StopIteration:
            return False

    def ChapterDef(defName):
        try:
            return next(v for k, v in game.chapterDefs.items() if v.defName == defName)  # type: Item
        except StopIteration:
            return False

    def DefsByToolUtility(utility):
        try:
            return [v.tryGetDeepParent("tool", utility) for k, v in game.itemDefs.items() if
                    v.tryGetDeepParent("tool", utility) != False]
        except StopIteration:
            return False

    def GetCategoryItems(category):
        try:
            return [v.tryGetDeepParent("categories", category) for k, v in game.itemDefs.items() if
                    v.tryGetDeepParent("categories", category) != False]
        except StopIteration:
            return False

    def CrateDefAndContents(rarity):
        try:
            return next(v for k, v in game.crateDefs.items() if v.defName == rarity)  # type: Crate
        except StopIteration:
            return False

    def ColorByRarity(rarity, returnTC=True):
        try:
            if returnTC:
                return tc.lookup[next(v for k, v in game.rarityDefs.items() if v.defName == rarity).color]  # type: str
            return next(v for k, v in game.rarityDefs.items() if v.defName == rarity).color  # type: str
        except StopIteration:
            return False

    def WorkTypeByName(defName):
        try:
            return next(v for k, v in game.workDefs.items() if v.defName == defName)  # type: Item
        except StopIteration:
            return False


class Sort():
    def ByRarity(sorts, reverse=True):
        raritySorted = [game.itemDefs[x] for x in sorts]
        rarityList = list(game.rarityDefs.keys())
        raritySorted = sorted(raritySorted, key=lambda x: (rarityList.index(x.rarity), x.label), reverse=reverse)
        # reverses the order of rarity, as we can't reverse order by strings
        return raritySorted

    def ListByRarity(sorts, rarityIndex, reverse=False):
        outsort = []
        rarityList = {key: [] for key in reversed(list(game.rarityDefs.keys()))}
        for i in sorts:
            rarityList[i[rarityIndex]].append(i)
        for k, v in rarityList.items():
            v = sorted(v, key=lambda x: x[1])
            for i in v:
                outsort.append(i)
        outsort = [x[1:] for x in outsort]
        return outsort

    def Paginate(seq, rowlen):
        for start in range(0, len(seq), rowlen):
            yield seq[start:start + rowlen]


class GameProperties(): pass


class Player():
    def __init__(self):
        self.inventory = Inventory()
        self.inv = self.inventory.contents
        self.group = {}
        self.day = 1
        self.dayLength = 12
        self.hour = 1
        self.tableLength = 30
        self.carryWeight = 0
        self.carried = 0
        self.queuedCrafts = {}
        self.craftsInProgress = {}
        self.location = None
        self.groupStatus = "Nomads"
        self.chapter = "nomad"

    def SpawnLeeani(self):
        temp = Provani(self)
        self.group[temp.fullName] = temp
        del temp

    def Group(self):
        return list(self.group.values())

    def formTime(self):
        return "{}:00".format(str(7 + self.hour))

    def addTime(self):
        if self.hour == self.dayLength:
            self.hour = 1
            self.day += 1
            return False
        else:
            self.hour += 1
            return True

    def calcCarryWeight(self):
        cw = 0
        for i in self.group.values():
            cw += round(i.stats.strength * 2)
            cw += round(i.stats.resource)
        self.inventory.clearNulls()
        for k, v in self.inventory.contents.items():
            if hasattr(v[0], 'carryweight'):
                for i in v:
                    cw += i.carryweight

        self.carryWeight = cw

    def calcCarried(self):
        self.carried = sum([sum([vv.getWeight() for vv in v]) for v in self.inventory.contents.values()])

    def calcCarriable(self, itemweight):
        self.calcCarried()
        if self.carried + itemweight <= self.carryWeight:
            return True
        else:
            return False


class StatBlock():
    def __init__(self, statlist):
        self.statlist = statlist
        self.agility = statlist[0]
        self.resource = statlist[1]
        self.intuition = statlist[2]
        self.eloquence = statlist[3]
        self.strength = statlist[4]
        self.dictFormat = {
            "agility": statlist[0],
            "resource": statlist[1],
            "intuition": statlist[2],
            "eloquence": statlist[3],
            "strength": statlist[4]
        }

    def getPreformatted(self):
        topList = [x for x in range(len(self.statlist)) if self.statlist[x] == max(self.statlist)]
        bottomList = [y for y in range(len(self.statlist)) if self.statlist[y] == min(self.statlist)]

        outList = self.statlist[:]

        for i in topList:
            outList[i] = tc.c + str(outList[i]) + tc.w
        for i in bottomList:
            outList[i] = tc.f + str(outList[i]) + tc.w

        return outList

    def getWorkFormatted(self, workType, thresholdPenalty=4, threshold=8):
        out = self.statlist
        if hasattr(workType, 'skills'):
            types = workType.skills
            out = []
            for k, v in self.dictFormat.items():
                preFormat = ""
                if k in types and v >= threshold:
                    preFormat = tc.y
                if k in types and v <= thresholdPenalty:
                    preFormat = tc.f
                out.append(preFormat + str(v) + tc.w)
            return out
        else:
            return out


class Creature():
    def __init__(self, race, points, genderSpecific = False):
        self.hp = 10
        self.race = race
        statlist = self.generateStats(points)
        self.stats = StatBlock(statlist)

        self.gender = random.choice(["Male", "Female"])  # TaKe ThAt LiBeRaLs!11!
        self.face = self.genFace(race, genderSpecific)

        name = self.generateName(self.race,self.gender)
        self.fn = name[0]
        self.ln = name[1]
        self.fullName = " ".join(name)

        self.dead = False

        del name
        del statlist

    def checkDeath(self):
        if self.hp == 0:
            self.dead = True

    def generateStats(self, points):
        stats = [0] * 6
        for i in range(points):
            stats[random.randint(0, 5)] += 1
        return stats

    def printOut(self):
        print(self.face)
        table = [
            [self.fullName],
            [self.gender]
        ]
        print(tw.indent(tb.tabulate(table), " " * 5))
        preForm = self.stats.getPreformatted()
        table = [
            [Translate('agility'), preForm[0]],
            [Translate('resource'), preForm[1]],
            [Translate('intuition'), preForm[2]],
            [Translate('eloquence'), preForm[3]],
            [Translate('strength'), preForm[4]],
        ]

        print(tw.indent(tb.tabulate(table), " " * 5))

    def generateName(self, race, gender, mashNames = False):

        if gender == "Male":
            first = random.choice(nameInfo[race]["maleFirst"])
            if mashNames:
                last = random.choice(nameInfo[race]["last"])[:3] + random.choice(nameInfo[race]["maleFirst"] + nameInfo[race]["femaleFirst"])[3:]
            else:
                last = random.choice(nameInfo[race]["last"])
        else:
            first = random.choice(nameInfo[race]["femaleFirst"])
            if mashNames:
                last = random.choice(nameInfo[race]["last"])[:3] + random.choice(nameInfo[race]["maleFirst"] + nameInfo[race]["femaleFirst"])[3:]
            else:
                last = random.choice(nameInfo[race]["last"])

        return [first, last]

    def genFace(self,race,genderSpecific = False):
        if genderSpecific:
            return "".join(random.choice(list(faceInfo[race][self.gender.lower()][x])) + "\n" for x in faceInfo[race][self.gender.lower()].keys())
        else:
            return "".join(random.choice(list(faceInfo[race][x])) + "\n" for x in faceInfo[race].keys())


class GetOutOfLoop(Exception):
    pass


class Provani(Creature):
    def __init__(self, player):
        super().__init__("provani", 35, genderSpecific=True)
        self.hp = 10
        self.job = Find.WorkTypeByName("idle")
        self.afk = False
        self.jobAssignedHour = 0
        self.jobTimeLeft = 0
        self.player = player
        self.craftWorkingOn = None
        self.location = None
        self.equippedItem = None
        self.wornItem = None

    def calculateCrafts(self, player, wwO=None, madeThisHour=None, done=False, dontshort=False, makeableQueue=None):
        if not madeThisHour:
            madeThisHour = {}
        if not makeableQueue:
            makeableQueue = {}
        inv = player.inventory
        qcrafts = player.queuedCrafts
        makeable = {}
        if not self.craftWorkingOn and not done:
            if not qcrafts: return
            for k, v in qcrafts.items():
                for i in range(v):
                    canDo = inv.collateIngredientsAndCheck(game.craftingDefs[k], i + 1)
                    canTool = inv.collateTools(game.craftingDefs[k])
                    if canDo:
                        if canDo == 1:
                            continue
                        elif canDo == 2:
                            if all(canTool):
                                try:
                                    makeable[k] += 1
                                except KeyError:
                                    makeable[k] = 1
                            else:
                                continue
                    else:
                        continue
            if not makeable: return
            if not wwO or wwO.defName not in list(makeable.keys()):
                key = random.choice(list(makeable.keys()))
            else:
                key = wwO.defName
            player.queuedCrafts[key] -= 1
            if player.queuedCrafts[key] == 0:
                player.queuedCrafts.pop(key)
            iMake = game.craftingDefs[key]
            iMC = iMake.__class__
            try:
                player.craftsInProgress[key] += 1
            except KeyError:
                player.craftsInProgress[key] = 1
            self.craftWorkingOn = iMC(iMake.defName, dict(iMake.object))
            self.calculateCrafts(player, wwO=self.craftWorkingOn, madeThisHour=madeThisHour, dontshort=True,
                                 makeableQueue=makeable)
        elif not done:
            if not makeableQueue:
                self.craftWorkingOn = None
                self.calculateCrafts(player, wwO=self.craftWorkingOn, madeThisHour=madeThisHour, done=True, dontshort=False,
                                     makeableQueue=makeableQueue)
            else:
                makePerHour = self.craftWorkingOn.timeCost()
                if self.craftWorkingOn.progress >= 1:
                    try:
                        madeThisHour[self.craftWorkingOn.defName] += 1
                    except KeyError:
                        madeThisHour[self.craftWorkingOn.defName] = 1
                    self.finishCraft(player,self.craftWorkingOn)
                    self.craftWorkingOn = None
                elif makePerHour < 1:
                    try:
                        madeThisHour[self.craftWorkingOn.defName] += 1
                    except KeyError:
                        madeThisHour[self.craftWorkingOn.defName] = 1
                    self.finishCraft(player,self.craftWorkingOn)
                    done2 = False

                    makeableQueue[wwO.defName] -= 1
                    if makeableQueue[wwO.defName] == 0:
                        makeableQueue.pop(wwO.defName)

                    if not dontshort:
                        try:
                            player.queuedCrafts[wwO.defName] -= 1
                        except:
                            pass
                    try:
                        if player.queuedCrafts[wwO.defName] == 0:
                            player.queuedCrafts.pop(wwO.defName)
                            self.craftWorkingOn = None
                            done2 = True
                    except:
                        self.craftWorkingOn = None
                        done2 = True
                    if qcrafts:
                        self.calculateCrafts(player, wwO=self.craftWorkingOn, madeThisHour=madeThisHour, done=False,
                                             dontshort=False, makeableQueue=makeableQueue)
                    else:
                        self.calculateCrafts(player, wwO=self.craftWorkingOn, madeThisHour=madeThisHour, done=done2,
                                             dontshort=False, makeableQueue=makeableQueue)
                elif makePerHour == 1:
                    try:
                        madeThisHour[self.craftWorkingOn.defName] += 1
                    except KeyError:
                        madeThisHour[self.craftWorkingOn.defName] = 1
                    self.finishCraft(player, self.craftWorkingOn)
                    self.craftWorkingOn = None
                else:
                    self.craftWorkingOn.progress += (1 / 1 + makePerHour) - 1
        if done:
            if madeThisHour:
                for k, v in madeThisHour.items():
                    for kk,vv in game.craftingDefs[k].output.items():
                        p("{} made {} x{}".format(self.fn, game.itemDefs[kk].labelResolved(), vv * v))
            msvcrt.getch()

    def finishCraft(self, player, craft):
        inv = player.inventory
        for k, v in craft.ingredients.items():
            for andInput in v:
                try:
                    for orInput in andInput:
                        for ingredient, amount in orInput.items():
                            if inv.testItem(ingredient, amount):
                                inv.removeItem(ingredient, amount)
                                raise GetOutOfLoop
                except:
                    continue
        for k, v in craft.output.items():
            inv.addItem(k, v)

    def rollWorkResults(self,player,game):
        if hasattr(self.job, 'outputTables'):
            mult = 0.5
            if self.job.defName in self.player.location.workMultipliers:
                mult = self.player.location.workMultipliers[self.job.defName]
            if self.job.defName == "explorer" and self.job.defName in self.location.workMultipliers:
                mult = self.location.workMultipliers[self.job.defName]
            if hasattr(self.job,"skills"):
                mult += (self.stats.dictFormat[list(self.job.skills.keys())[0]] ** list(self.job.skills.values())[0]) / 30
                mult += (self.stats.dictFormat[list(self.job.skills.keys())[1]] ** list(self.job.skills.values())[1]) / 30

            mult /= 2
            if player.location.looted and self.job.defName != "explorer": mult /= 10
            mult = round(mult, 2)

            for k, v in self.job.outputTables.items():
                f = False
                for i in range(v):
                    found = game.tableDefs[k].rollTable(v)
                    if found[1] > 0 and self.job.defName != "explorer":
                        if player.location.looted: found[1] -= 1
                    if found[1] > 0:
                        f = True
                        if found[0].startswith("$") and not player.location.looted:
                            items = list(game.crateDefs.keys())
                            weights = [vv.weight for vv in game.crateDefs.values()]
                            crate = game.crateDefs[random.choices(items, weights)[0]]
                            p("- Found a {}!".format(crate.label))
                            if player.calcCarriable(game.itemDefs[crate.crateItemDef].weight):
                                player.inventory.addItem(game.itemDefs[crate.crateItemDef].defName, 1)
                            else:
                                print("However, it was too heavy for your leeani to carry!")
                        elif found[0].startswith("~"):
                            item = game.fluidDefs[found[0][1:]]
                            if not found[2]:
                                amt = math.ceil(found[1] * mult)
                            else:
                                amt = found[1]
                            p("- Found {}L of {} ({}x)".format(amt, item.label, mult))
                            if player.calcCarriable(item.getWeight() * amt):
                                remainder = player.inventory.addFluid(item, amt)
                                if remainder == amt:
                                    p(" ! However, there was no container to accept it.")
                                elif amt - remainder < amt:
                                    p(" ! Only {}L could be put into containers.".format(amt - remainder))
                            else:
                                ileft = round((player.carryWeight - player.carried) / item.getWeight())
                                remainder = player.inventory.addFluid(item, ileft)
                                p(" ! You can only carry {}L of it.".format(amt - remainder))
                        else:
                            item = found[0]
                            idef = game.itemDefs[item]
                            if not found[2]:
                                amt = math.ceil(found[1] * mult)
                            else:
                                amt = found[1]
                            p("- Found {} x{} ({}x)".format(idef.labelResolved(), int(amt), mult))
                            if player.calcCarriable(idef.getWeight() * amt):
                                player.inventory.addItem(item, amt)
                            else:
                                ileft = (player.carryWeight - player.carried) / idef.getWeight()
                                player.inventory.addItem(item, ileft)
                if not f:
                    p("x {} didn't find anything.".format("He" if self.gender == "Male" else "She"))
        if hasattr(self.job, 'destructive') and self.job.destructive:
            if not random.randint(0, 2):
                p(
                    tc.f + "x {}'s looting depleted the resources in this area! Resources will be harder to find here now.".format(
                        self.fn) + tc.w)
                player.location.looted = True

    def satisfyNutrition(self):
        neededFoodNutrition = 1
        neededWaterNutrition = 1
        eaten = 0
        drank = 0
        haveEaten = {}
        haveDrank = {}
        while eaten < neededFoodNutrition or drank < neededWaterNutrition:
            waterItems = []
            foodItems = []
            waterLiquids = []
            foodLiquids = []
            for k, v in self.player.inventory.contents.items():
                items = list(v)
                for item in items:
                    if hasattr(item, 'storage') and item.storage['filled']:
                        if hasattr(item.storage['fluid'], 'nutrition') and item.storage['fluid'].nutrition:
                            if 'water' in list(item.storage['fluid'].nutrition.keys()):
                                waterLiquids.append(item)
                            if 'food' in list(item.storage['fluid'].nutrition.keys()):
                                foodLiquids.append(item)
                    if hasattr(item, 'nutrition') and item.nutrition:
                        if 'food' in list(item.nutrition.keys()):
                            foodItems.append(item)
                        if 'water' in list(item.nutrition.keys()):
                            waterItems.append(item)
            if not waterItems and not waterLiquids:
                p(tc.f + " x {} couldn't find anything to drink.".format(self.fn) + tc.w)
                self.hp -= 1
                self.checkDeath()
                return False
            if not foodItems and not foodLiquids:
                p(tc.f + " x {} couldn't find anything to eat.".format(self.fn) + tc.w)
                self.hp -= 1
                self.checkDeath()
                return False
            waterItems.sort(key=lambda x: x.nutrition['water'], reverse=True)
            waterLiquids.sort(key=lambda x: x.storage['fluid'].nutrition['water'], reverse=True)
            foodItems.sort(key=lambda x: x.nutrition['food'], reverse=True)
            foodLiquids.sort(key=lambda x: x.storage['fluid'].nutrition['food'], reverse=True)
            drink = next(iter(waterLiquids + waterItems))
            eat = next(iter(foodItems + foodLiquids))
            if drank < neededWaterNutrition:
                if hasattr(drink, 'storage'):
                    drinkNutritionPerLitre = drink.storage['fluid'].nutrition['water']
                    # = 2
                    toConsume = round(drinkNutritionPerLitre / neededWaterNutrition)

                    if drink.storage['filled'] >= toConsume:
                        drink.storage['filled'] -= toConsume

                    else:
                        toConsume = drink.storage['filled']
                        drink.storage['filled'] = 0
                    try:
                        haveDrank[drink.storage['fluid'].label] += toConsume
                    except KeyError:
                        haveDrank[drink.storage['fluid'].label] = toConsume
                    if not drink.storage['filled']:
                        drink.storage['fluid'] = None
                    drank += toConsume * drinkNutritionPerLitre
                else:
                    if self.player.inventory.testItem(drink.defName, 1, remove=True):
                        drank += drink.nutrition['water']
                        try:
                            haveDrank[drink.label] += 1
                        except KeyError:
                            haveDrank[drink.label] = 1
            if eaten < neededFoodNutrition:
                if hasattr(eat, 'storage'):
                    eatNutritionPerLitre = eat.storage['fluid'].nutrition['food']
                    # = 2
                    toConsume = round(eatNutritionPerLitre / neededFoodNutrition)

                    if eat.storage['filled'] >= toConsume:
                        eat.storage['filled'] -= toConsume
                    else:
                        toConsume = eat.storage['filled']
                        eat.storage['filled'] = 0
                    try:
                        haveEaten[eat.storage['fluid'].label] += toConsume * eatNutritionPerLitre
                    except KeyError:
                        haveEaten[eat.storage['fluid'].label] = toConsume * eatNutritionPerLitre
                    if not eat.storage['filled']:
                        eat.storage['fluid'] = None
                    eaten += toConsume * eatNutritionPerLitre
                else:
                    if self.player.inventory.testItem(eat.defName, 1, remove=True):
                        eaten += eat.nutrition['food']
                        try:
                            haveEaten[eat.label] += 1
                        except KeyError:
                            haveEaten[eat.label] = 1
                        '''
                        if eat.nutrition['food'] > (neededFoodNutrition - eaten):
                            leftover = game.itemDefs["leftovers"]
                            leftoversAmt = round((eat.nutrition['food'] - (neededFoodNutrition - eaten)) / leftover.nutrition['food'])
                            self.player.inventory.addItem("leftovers",leftoversAmt)
                        '''
        p(" - {} ate {}".format(self.fn, ", ".join(["{} x{}".format(k, v) for k, v in haveEaten.items()])))
        if eaten < neededFoodNutrition:
            p(tc.y + " ! There was nothing else to eat, but {} is still hungry.".format(self.fn) + tc.w)
            self.hp -= neededFoodNutrition - eaten
            self.checkDeath()
        p(" - {} drank {}".format(self.fn, ", ".join(["{} x{}".format(k, v) for k, v in haveDrank.items()])))
        if drank < neededWaterNutrition:
            p(tc.y + " ! There was nothing else to drink, but {} is still thirsty.".format(self.fn) + tc.w)
            self.hp -= neededWaterNutrition - drank
            self.checkDeath()



class Inventory():
    def __init__(self):
        self.contents = {}
        self.queuedCrafts = {}

    def addItem(self, item, amount, **kwargs):
        if item in game.itemDefs:
            itemToAdd = game.itemDefs[item]
            c = itemToAdd.__class__
            try:
                self.contents[item].extend([c(itemToAdd.defName, dict(itemToAdd.object)) for x in range(round(amount))])
            except KeyError:
                self.contents[item] = [c(itemToAdd.defName, dict(itemToAdd.object)) for x in range(round(amount))]
        else:
            print(item.defName)
            for k,v in game.itemDefs.items():
                print(k,v.defName)
            input()

    def getContainersWithFluid(self,fluid,amount=0):
        containers = []
        for k, v in self.contents.items():
            for vv in v:
                if hasattr(vv, 'categories') and 'liquid storage' in vv.categories and hasattr(vv, 'storage') and (
                                    'filled' in vv.storage and 'fluid' in vv.storage and vv.storage['fluid'] == game.fluidDefs[fluid].label):
                    if amount:
                        if vv.storage['filled'] >= amount:
                            containers.append(vv)
                    else:
                        containers.append(vv)
        return containers

    def addFluid(self, fluid, amount):
        containers = []
        for k, v in self.contents.items():
            for vv in v:
                if hasattr(vv, 'categories') and 'liquid storage' in vv.categories and hasattr(vv, 'storage') and (
                            ('filled' in vv.storage and 'fluid' in vv.storage and vv.storage['fluid'] == fluid.label) or
                            ('filled' in vv.storage and vv.storage['filled'] != vv.storage['volume'] or
                                 ('filled' not in vv.storage and ('pourable' in vv.storage and vv.storage['pourable']))
                             )):
                    containers.append(vv)
        if hasattr(fluid, 'fillPriority') and fluid.fillPriority == 'smallest':
            containers = sorted(containers, key=lambda x: x.storage['volume'])
        else:
            containers = sorted(containers, key=lambda x: x.storage['volume'], reverse=True)
        if len(containers) == 0:
            return amount
        for i in containers:
            if amount != 0:
                amount -= fluid.fillContainer(i, amount)
            else:
                return amount
        return amount

    def removeFluid(self, fluid, amount):
        containers = []
        for k, v in self.contents.items():
            for vv in v:
                if hasattr(vv, 'categories') and 'liquid storage' in vv.categories and hasattr(vv, 'storage') and (
                            ('filled' in vv.storage and 'fluid' in vv.storage and vv.storage['fluid'] == fluid.label) or
                            ('filled' in vv.storage and vv.storage['filled'] > 0)):
                    containers.append(vv)
        if hasattr(fluid, 'fillPriority') and fluid.fillPriority == 'smallest':
            containers = sorted(containers, key=lambda x: x.storage['volume'])
        else:
            containers = sorted(containers, key=lambda x: x.storage['volume'], reverse=True)
        if len(containers) == 0:
            return amount
        for i in containers:
            if amount != 0:
                amount -= fluid.emptyContainer(i, amount)
            else:
                return amount
        return amount

    def clearNulls(self):
        keys = list(self.contents.keys())
        for k in keys:
            if not self.contents[k]:
                self.contents.pop(k)

    def testAmount(self, item, amount, returnAmt=False):
        try:
            if item.startswith("~"):
                containers = self.getContainersWithFluid(item[1:],amount)
                if not containers:
                    if returnAmt:
                        return 0
                    else:
                        return False
                else:
                    if returnAmt:
                        return sum([i.storage['filled'] for i in containers])
                    else:
                        return True
            if len(self.contents[item]) >= amount:
                if returnAmt:
                    return len(self.contents[item])
                return True
            else:
                if returnAmt:
                    return len(self.contents[item])
                return False
        except KeyError:
            if returnAmt:
                return 0
            return False

    def testItem(self, item, amount, remove=False):
        try:
            if len(self.contents[item]) + amount < 0:
                return False
            else:
                if remove:
                    self.removeItem(item, amount)
                return True
        except KeyError:
            fluids = self.getContainersWithFluid(item)

            return False

    def removeItem(self, item, amount):
        for i in range(amount):
            self.contents[item].pop()
        if self.contents[item] == []:
            self.contents.pop(item)

    def removeItemDiff(self, item, amount):
        if hasattr(item,"diffprop"):
            evalDiffprop = item.getDiffprop()
            for i in range(amount):
                for v in self.contents[item.defName]:
                    if v.getDiffprop() == evalDiffprop:
                        self.contents[item.defName].remove(v)
                        break
        else:
            for i in range(amount):
                self.contents[item.defName].pop()
        if self.contents[item.defName] == []:
            self.contents.pop(item.defName)

    def findToolCapacity(self, capacity, level):

        toolDefs = Find.DefsByToolUtility(capacity)
        invDefs = [t for t in toolDefs if t.tool[capacity] >= level and t.defName in self.contents.keys()]

        return invDefs

    def displayItemDetailsXY(self, item, amount, y, x):
        itemDef = game.itemDefs[item.defName]
        details = itemFormat(item, itemDef, amount)

        for dY, i in enumerate(details.splitlines()):
            print("\033[{};{}H {}".format(y + dY, x, i.ljust(50)))

    def displayCraftDetailsXY(self, craft, formText, y, x, craftable, tools, game):
        details = craftFormat(craft, formText, game=game, canDo=craftable, canTool=tools)

        for dY, i in enumerate(details.splitlines()):
            print("\033[{};{}H {}".format(y + dY, x, i.ljust(50)))

    def collateIngredientsAndCheck(self, craft, amount=1):
        itemIng = craft.ingredients
        items = []
        for i, iv in itemIng.items():
            for j in iv:
                itemGroup = []
                for k in j:
                    itemGroup.append([list(k.keys())[0], list(k.values())[0]])
                items.append(itemGroup)
        itemChecks = []
        for group in items:
            if any(self.testAmount(x[0], x[1] * amount) for x in group):
                itemChecks.append(True)
            else:
                itemChecks.append(False)

        if all(itemChecks):
            return 2
        elif any(itemChecks):
            return 1
        else:
            return 0

    def collateTools(self, craft):
        caps = []
        if hasattr(craft, 'tools'):
            for toolCap, level in craft.tools.items():
                if self.findToolCapacity(toolCap, level):
                    caps.append(True)
                else:
                    caps.append(False)
        if not caps:
            return [True]
        return caps

    def openCrate(self, crate, player):
        u()
        for k, v in crate.openable['contents'].items():
            cc = game.crateDefs[k[1:]]
            contents = cc.provideContents(game)
        conOut = []
        for k, v in contents.items():
            for i in v:
                conOut.append(game.itemDefs[i])
        maxspeed = 0.5 + (random.randrange(-20, 20) / 100)
        speed = maxspeed
        bleed = 0
        ticker = random.randint(0,len(conOut)-1)
        p("Opening crate...")
        print()
        print("  " + "\n  ".join([x.rarityLabel for x in conOut]))
        prize = None
        while speed > 0:

            if ticker >= len(conOut):
                ticker = 0
                print("\033[{};{}H  ".format(len(conOut) + 3, 1))
            bleed += random.random()
            if bleed > 30:
                speed -= 0.001 * bleed
            print(tc.f + "\033[{};{}H=>".format(ticker + 4, 1) + tc.bg_b)
            print("\033[{};{}H  ".format(ticker + 3, 1))
            prize = conOut[ticker]
            ticker += 1
            time.sleep(maxspeed - (speed - .05))
        print("\033[{};{}H".format(len(conOut) + 4, 1))
        amt = round((1 / 1 + prize.value) * 10)
        p("The crate contains: {}".format(prize.rarityLabel, 1))
        player.inventory.addItem(prize.defName, 1)
        p("Press any key to continue...")
        msvcrt.getch()

    def makeCraft(self, craft):
        itemIng = craft.ingredients
        midStr = []
        for i, iv in itemIng.items():
            items = []
            for j in iv:
                orItems = []
                for item in j:
                    color = tc.f
                    key, amount = next(iter(item.items()))
                    canDo = self.testAmount(key, amount, returnAmt=False)
                    if canDo:
                        color = tc.c
                    if key.startswith("~"):
                        outStr = color + "{}".format(
                            game.fluidDefs[key[1:]].label.replace(" ", "\xa0")) + tc.w + "\xa0{}L\xa0({}L)".format(amount,
                                                                                                             self.testAmount(
                                                                                                                 key,
                                                                                                                 amount,
                                                                                                                 returnAmt=True))
                    else:
                        outStr = color + "{}".format(game.itemDefs[key].label.replace(" ","\xa0")) + tc.w + "\xa0x{}\xa0({})".format(amount,
                                                                                                      self.testAmount(
                                                                                                          key, amount,
                                                                                                          returnAmt=True))
                    orItems.append(outStr)
                orItems = " OR ".join(orItems)
            items = "{}: ".format(i) + orItems
            out = []
            for i in tw.wrap(items,100):
                out.append("{:<100}".format(i))
            midStr.append("\n   ".join(out))
        return " └ " + "\n └ ".join(midStr)

    def getOutput(self, craft):

        outputs = craft.output

        return " + ".join(["{} ({})".format(game.itemDefs[k].label, v) for k, v in outputs.items()])

    def checkCraft(self, player, defName):
        try:
            a = player.queuedCrafts[defName]
            return a
        except KeyError:
            return 0

    def craftTabulate(self, player, selectedItemIndex, page=0, sort=False):
        table = []
        defTable = []
        craftTable = []
        possibles = []
        headers = ["craft", "time", "craft per hr", "queued"]

        for craft, obj in game.craftingDefs.items():
            tabItem = game.craftingDefs[obj.defName]
            queuedAmt = self.checkCraft(player, tabItem.defName)
            if not queuedAmt: queuedAmt = 1
            canDo = self.collateIngredientsAndCheck(obj)
            canDoQueue = self.collateIngredientsAndCheck(obj, queuedAmt)
            canTool = self.collateTools(obj)
            txt = ""
            if canDo or obj.favourite:
                if canDo == 1:
                    color = tc.lg
                elif canDo == 2:
                    if all(canTool):
                        color = tc.c
                    else:
                        color = tc.lg
                elif obj.favourite:
                    color = tc.lg
                if obj.favourite:
                    txt = "~"
            else:
                continue
            if canDoQueue:
                if canDoQueue == 1:
                    qcolor = tc.f
                elif canDoQueue == 2:
                    if all(canTool):
                        qcolor = tc.w
                    else:
                        qcolor = tc.f
            else:
                qcolor = tc.f
            if not self.checkCraft(player, tabItem.defName): qcolor = tc.lg
            defTable.append([tabItem.rarity] + [tabItem.label] + [tabItem] + [canDo] + [canTool])
            craftTable.append(obj)
            table.append(
                [Find.ColorByRarity(tabItem.rarity) + color + txt + tabItem.label + tc.w,
                 round(obj.timeCost(), 2),
                 str(int(obj.timeCost(1))) + "/hr", "{}{}{}".format(qcolor, self.checkCraft(player, tabItem.defName), tc.w)])
        tman = list(Sort.Paginate(table, player.tableLength))
        defTable = list(Sort.Paginate(defTable, player.tableLength))
        craftTable = list(Sort.Paginate(craftTable, player.tableLength))
        if len(table) == 0:
            return
        return (tb.tabulate(tman[page], headers, tablefmt='orgtbl'), len(table), defTable, tman, craftTable)

    def nameTabulate(self, selectedItemIndex, page=0, sort=False):
        table = []
        totalWeight = 0
        defTable = []
        headers = ['item', 'amount']
        preloadLabels = {}
        for k, v in self.contents.items():
            tabItem = game.itemDefs[k]
            if len(v) == 0:
                continue
            if hasattr(tabItem, 'diffprop'):
                for i in v:
                    label = Find.ColorByRarity(i.rarity) + i.labelResolved() + tc.w
                    try:
                        preloadLabels[label].append(i)
                    except KeyError:
                        preloadLabels[label] = [i]
            else:
                tp = {
                    'tbLabel': Find.ColorByRarity(tabItem.rarity) + tabItem.labelResolved() + tc.w,
                    'amt': len(v),
                    'def': tabItem
                }
                if sort:
                    if sort == 'rarity':
                        table.append([tabItem.rarity] + [x for x in tp.values()])
                    else:
                        table.append([x for x in tp.values()])
                defTable.append([tabItem.rarity] + [tabItem.labelResolved()] + [tabItem])
                totalWeight += tabItem.getWeight() * len(v)
        for kk, vv in preloadLabels.items():
            i = vv[0]
            tp = {
                'tbLabel': kk,
                'amt': len(vv)
            }
            if sort:
                if sort == 'rarity':
                    table.append([i.rarity] + [x for x in tp.values()])
                else:
                    table.append([x for x in tp.values()])
            defTable.append([i.rarity] + [i.labelResolved()] + [i])
            totalWeight += i.getWeight() * len(vv)
        table = [row[0:3] for row in table]
        if sort:
            if sort == 'rarity':
                headers[0] = tc.y + headers[0] + " *" + tc.w
                table = Sort.ListByRarity(table, 0)
                defTable.sort(key=lambda x: (
                    sorted(game.rarityDefs.keys(), reverse=True)[list(game.rarityDefs.keys()).index(x[0])], x[1]))
                defTable = [row[2] for row in defTable]
            else:
                headers[sort] = tc.y + headers[sort] + " *" + tc.w
                table.sort(key=lambda x: (x[sort], x[0]))
        tman = list(Sort.Paginate(table, player.tableLength))
        defTable = list(Sort.Paginate(defTable, player.tableLength))
        # tman[page][selectedItemIndex][0] = tc.bg_w + tman[page][selectedItemIndex][0] + tc.bg_b
        # tman[page][selectedItemIndex][0] = tc.bg_w + tc.f+ ">" + tc.w + tc.bg_b + tman[page][selectedItemIndex][0]
        '''for x,i in enumerate(tman[page]):
            if x != selectedItemIndex:
                tman[page][x][0] = tc.b + "." + tman[page][x][0]
        '''
        try:
            return (tb.tabulate(tman[page], headers, tablefmt='orgtbl'), len(table), defTable, tman, totalWeight)
        except:
            print("Inventory is empty. Maybe get some stuff?")
            return False

    def tabulate(self, page=0, sort=False):
        table = []
        headers = ['item', 'amount', 'weight', 'value', 'food', 'water']
        totalWeight = 0
        preloadLabels = {}
        for k, v in self.contents.items():
            tabItem = game.itemDefs[k]
            if len(v) == 0:
                continue
            if hasattr(tabItem, 'diffprop'):
                for i in v:
                    label = Find.ColorByRarity(i.rarity) + i.labelResolved(len(v)) + tc.w
                    try:
                        preloadLabels[label].append(i)
                    except KeyError:
                        preloadLabels[label] = [i]
            else:
                tp = {
                    'tbLabel': Find.ColorByRarity(tabItem.rarity) + tabItem.labelResolved(len(v)) + tc.w,
                    'amt': len(v),
                    'weight': "{0:.2f}".format(tabItem.getWeight() * len(v)),
                    'value': "{0:.2f}".format(tabItem.value * len(v)),
                    'nutFood': "{0:.2f}".format(
                        tabItem.getNutrition('food') * len(v)),
                    'nutWater': "{0:.2f}".format(
                        tabItem.getNutrition('water') * len(v))
                }
                if sort:
                    if sort == 'rarity':
                        table.append([tabItem.rarity] + [x for x in tp.values()])
                    else:
                        table.append([x for x in tp.values()])
                totalWeight += tabItem.getWeight() * len(v)
        for kk, vv in preloadLabels.items():
            i = vv[0]
            tp = {
                'tbLabel': kk,
                'amt': len(vv),
                'weight': "{0:.2f}".format(i.getWeight() * len(vv)),
                'value': "{0:.2f}".format(i.value * len(vv)),
                'nutFood': "{0:.2f}".format(
                    i.getNutrition('food') * len(vv)),
                'nutWater': "{0:.2f}".format(
                    i.getNutrition('water') * len(vv))
            }
            if sort:
                if sort == 'rarity':
                    table.append([i.rarity] + [x for x in tp.values()])
                else:
                    table.append([x for x in tp.values()])
            totalWeight += i.getWeight() * len(vv)
        if sort:
            if sort == 'rarity':
                headers[0] = tc.y + headers[0] + " *" + tc.w
                table = Sort.ListByRarity(table, 0)
            else:
                headers[sort] = tc.y + headers[sort] + " *" + tc.w
                table.sort(key=lambda x: (x[sort], x[0]))
        tman = list(Sort.Paginate(table, player.tableLength))
        return (tb.tabulate(tman[page], headers, tablefmt='orgtbl'), len(table), totalWeight)

    def calcNutrition(self):
        runningFood = 0
        runningWater = 0
        for k, v in self.contents.items():
            items = list(v)
            for item in items:
                if hasattr(item, 'storage') and item.storage['filled']:
                    if hasattr(item.storage['fluid'], 'nutrition') and item.storage['fluid'].nutrition:
                        if 'water' in list(item.storage['fluid'].nutrition.keys()):
                            runningWater += item.storage['fluid'].nutrition['water'] * item.storage['filled']
                        if 'food' in list(item.storage['fluid'].nutrition.keys()):
                            runningFood += item.storage['fluid'].nutrition['food'] * item.storage['filled']
                if hasattr(item, 'nutrition') and item.nutrition:
                    if 'food' in list(item.nutrition.keys()):
                        runningFood += item.nutrition['food']
                    if 'water' in list(item.nutrition.keys()):
                        runningWater += item.nutrition['water']
        return (runningWater, runningFood)

    def calcFoodDays(self, group):
        return round(self.calcNutrition()[1] / len(group), 2)

    def calcWaterDays(self, group):
        return round(self.calcNutrition()[0] / len(group), 2)


#######################################################################################################################

cr.init(autoreset=False)
tb.PRESERVE_WHITESPACE = True
cursor.hide()

with open("data/names.yaml") as STREAM:
    nameInfo = yaml.safe_load(STREAM)

with open("data/fexgen.yaml") as STREAM:
    faceInfo = yaml.safe_load(STREAM)

game = GameProperties()
player = Player()

