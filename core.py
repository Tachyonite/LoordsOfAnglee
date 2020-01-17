import random
import textwrap as tw
import tabulate as tb
import colorama as cr
import cursor
import yaml


from utils.defs import *
from utils.loader import *
from utils.helpers import *
from utils.itemFormat import itemFormat, craftFormat
from utils.translator import Translate

from math import ceil


class Find():
    def ItemDef(defName):
        try:
            item = next(v for k, v in game.itemDefs.items() if v.defName == defName) #type: Item
            return item
        except StopIteration:
            return False
    def FluidDef(defName):
        try:
            return next(v for k, v in game.fluidDefs.items() if v.defName == defName) #type: Item
        except StopIteration:
            return False
    def ChapterDef(defName):
        try:
            return next(v for k, v in game.chapterDefs.items() if v.defName == defName) #type: Item
        except StopIteration:
            return False
    def DefsByToolUtility(utility):
        try:
            return [v.tryGetDeepParent("tool", utility) for k, v in game.itemDefs.items() if v.tryGetDeepParent("tool", utility) != False]
        except StopIteration:
            return False
    def GetCategoryItems(category):
        try:
            return [v.tryGetDeepParent("categories", category) for k, v in game.itemDefs.items() if v.tryGetDeepParent("categories", category) != False]
        except StopIteration:
            return False
    def CrateDefAndContents(rarity):
        try:
            return next(v for k, v in game.crateDefs.items() if v.defName == rarity) #type: Crate
        except StopIteration:
            return False
    def ColorByRarity(rarity,returnTC = True):
        try:
            if returnTC:
                return tc.lookup[next(v for k, v in game.rarityDefs.items() if v.defName == rarity).color]  # type: str
            return next(v for k, v in game.rarityDefs.items() if v.defName == rarity).color  # type: str
        except StopIteration:
            return False
    def WorkTypeByName(defName):
        try:
            return next(v for k, v in game.workDefs.items() if v.defName == defName) #type: Item
        except StopIteration:
            return False


class Sort():
    def ByRarity(sort,reverse=True):
        raritySorted = [Find.ItemDef(x) for x in sort]
        rarityList = list(game.rarityDefs.keys())
        raritySorted = sorted(raritySorted,key=lambda x: (rarityList.index(x.rarity),x.label),reverse=reverse)
        # reverses the order of rarity, as we can't reverse order by strings
        return raritySorted
    def ListByRarity(sort,rarityIndex,reverse=False):
        outsort = []
        rarityList = {key:[] for key in reversed(list(game.rarityDefs.keys()))}
        for i in sort:
            rarityList[i[rarityIndex]].append(i)
        for k,v in rarityList.items():
            v = sorted(v, key= lambda x: x[1])
            for i in v:
                outsort.append(i)
        outsort = [x[1:] for x in outsort]
        return outsort
    def Paginate(seq, rowlen):
        for start in range(0, len(seq), rowlen):
            yield seq[start:start + rowlen]



class GameProperties():pass

class Player():
    def __init__(self):
        self.inventory = Inventory()
        self.inv = self.inventory.contents
        self.group = {}
        self.day = 1
        self.dayLength = 12
        self.hour = 0
        self.tableLength = 30
        self.carryWeight = 0
        self.queuedCrafts = {}
    def SpawnLeeani(self):
        temp = Leeani()
        self.group[temp.fullName] = temp
        del temp
    def Group(self):
        return list(self.group.values())
    def formTime(self):
        return "{}:00".format(str(7+self.hour))
    def addTime(self):
        if self.hour == self.dayLength:
            self.hour = 0
            self.day += 1
            return False
        else:
            self.hour += 1
            return True

    def calcCarryWeight(self):
        cw = 0
        for i in self.group.values():
            cw+= i.stats.strength
            cw+= round(i.stats.vitality / 2)
            print(cw)
        self.carryWeight = cw

class StatBlock():
    def __init__(self,statlist):
        self.statlist = statlist
        self.vitality = statlist[0]
        self.utility = statlist[1]
        self.learning = statlist[2]
        self.perception = statlist[3]
        self.eloquence = statlist[4]
        self.strength = statlist[5]
        self.dictFormat = {
            "vitality" : statlist[0],
            "utility" : statlist[1],
            "learning" : statlist[2],
            "perception" : statlist[3],
            "eloquence" : statlist[4],
            "strength" : statlist[5]
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

    def getWorkFormatted(self,workType,thresholdPenalty=4,threshold=8):
        out = self.statlist
        if hasattr(workType,'skills'):
            types = workType.skills
            out = []
            for k,v in self.dictFormat.items():
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
    def __init__(self,race,points):
        self.race = race
        statlist = self.generateStats(points)
        self.stats = StatBlock(statlist)

        self.gender = random.choice(["Male","Female"]) #TaKe ThAt LiBeRaLs!11!
        self.face = self.genFace()

        name = self.generateName(self.gender)
        self.fn = name[0]
        self.ln = name[1]
        self.fullName = " ".join(name)

        del name
        del statlist

    def generateStats(self, points):
        stats = [0]*6
        for i in range(points):
            stats[random.randint(0,5)] += 1
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
            [Translate('vitality'), preForm[0]],
            [Translate('utility'), preForm[1]],
            [Translate('learning'), preForm[2]],
            [Translate('perception'), preForm[3]],
            [Translate('eloquence'), preForm[4]],
            [Translate('strength'), preForm[5]],
        ]

        print(tw.indent(tb.tabulate(table), " " * 5))

    def generateName(self,gender):

        if gender == "Male":
            first = random.choice(nameInfo["maleFirst"])
            last = random.choice(nameInfo["last"])[:3] + random.choice(nameInfo["maleFirst"] + nameInfo["femaleFirst"])[3:]
        else:
            first = random.choice(nameInfo["femaleFirst"])
            last = random.choice(nameInfo["last"])[:3] + random.choice(nameInfo["maleFirst"] + nameInfo["femaleFirst"])[3:]

        return [first,last]

    def genFace(self):
        return "".join(random.choice(list(faceInfo[x])) + "\n" for x in
            ["ears", "eyes", "cheeks", "nose", "expressions", "necks"])


class Leeani(Creature):
    def __init__(self):
        super().__init__("leeani",35)
        self.hp = 10
        self.job = Find.WorkTypeByName("idle")
        self.afk = False
        self.jobAssignedHour = 0
        self.jobTimeLeft = 0
    def rollWorkResults(self):
        if hasattr(self.job,'outputTables'):
            for k,v in self.job.outputTables.items():
                f = False
                for i in range(v):
                    found = game.tableDefs[k].rollTable(v)
                    if found[1] > 0:
                        f = True
                        if found[0].startswith("$"):
                            items = list(game.crateDefs.keys())
                            weights = [vv.weight for vv in game.crateDefs.values()]
                            crate = game.crateDefs[random.choices(items,weights)[0]]
                            p("- Found a {}!".format(crate.label))
                        elif found[0].startswith("~"):
                            item = game.fluidDefs[found[0][1:]]
                            amt = found[1]
                            p("- Found {}L of {}".format(amt, item.label))
                            remainder = player.inventory.addFluid(item, amt)
                            if remainder == amt:
                                p(" ! However, there was no container to accept it.")
                            elif amt - remainder < amt:
                                p(" ! Only {}L could be put into containers.".format(amt - remainder))
                        else:
                            item = found[0]
                            idef = game.itemDefs[item]
                            amt = found[1]
                            p("- Found {} x{}".format(idef.label,int(amt)))
                            player.inventory.addItem(item,amt)
                if not f:
                    p("x {} didn't find anything.".format("He" if self.gender == "Male" else "She"))

class Inventory():
    def __init__(self):
        self.contents = {}
    def addItem(self,item,amount,**kwargs):
        if item in game.itemDefs:
            itemToAdd = game.itemDefs[item]
            c = itemToAdd.__class__
            try:
                self.contents[item].extend([c(itemToAdd.defName,dict(itemToAdd.object)) for x in range(amount)])
            except KeyError:
                self.contents[item] = [c(itemToAdd.defName,dict(itemToAdd.object)) for x in range(amount)]
    def addFluid(self, fluid, amount):
        containers = []
        for k,v in self.contents.items():
            for vv in v:
                if hasattr(vv,'categories') and 'liquid storage' in vv.categories and hasattr(vv,'storage') and (
                            ('filled' in vv.storage and 'fluid' in vv.storage and vv.storage['fluid'] == fluid.label) or
                            ('filled' in vv.storage and vv.storage['filled'] != vv.storage['volume'] or
                            ('filled' not in vv.storage and ('pourable' in vv.storage and vv.storage['pourable']))
                    )):
                    containers.append(vv)
        if hasattr(fluid,'fillPriority') and fluid.fillPriority == 'smallest':
            containers = sorted(containers, key=lambda x: x.storage['volume'])
        else:
            containers = sorted(containers, key=lambda x: x.storage['volume'], reverse=True)
        if len(containers) == 0:
            return amount
        for i in containers:
            if amount != 0:
                amount -= fluid.fillContainer(i,amount)
            else:
                return amount
        return amount

    def testAmount(self,item,amount,returnAmt=False):
        try:
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

    def testItem(self, item, amount,remove=False):
        try:
            if self.contents[item] + amount < 0:
                return False
            else:
                return True
            if remove:
                self.removeItem(item,amount)
        except KeyError:
            return False

    def removeItem(self,item,amount):
        for i in range(amount):
            self.contents[item].pop()
        if self.contents[item] == []:
            self.contents.pop(item)

    def findToolCapacity(self,capacity,level):

        toolDefs = Find.DefsByToolUtility(capacity)
        invDefs = [t for t in toolDefs if t.tool[capacity] > level and t.defName in self.contents.keys()]

        return invDefs

    def displayItemDetailsXY(self,item,amount,y,x):
        itemDef = game.itemDefs[item.defName]
        details = itemFormat(item,itemDef,amount)

        for dY,i in enumerate(details.splitlines()):
            print("\033[{};{}H {}".format(y+dY,x,i.ljust(50)))

    def displayCraftDetailsXY(self,craft,formText,y,x,craftable,tools):
        itemDef = game.craftingDefs[craft.defName]
        details = craftFormat(craft,formText,itemDef,craftable,tools)

        for dY,i in enumerate(details.splitlines()):
            print("\033[{};{}H {}".format(y+dY,x,i.ljust(50)))

    def collateIngredientsAndCheck(self,craft):
        itemIng = craft.ingredients
        items = []
        for i, iv in itemIng.items():
            for j in iv:
                itemGroup = []
                for k in j:
                    itemGroup.append([list(k.keys())[0],list(k.values())[0]])
                items.append(itemGroup)
        itemChecks = []
        for group in items:
            if any(self.testAmount(x[0],x[1]) for x in group):
                itemChecks.append(True)
            else:
                itemChecks.append(False)

        if all(itemChecks):
            return 2
        elif any(itemChecks):
            return 1
        else:
            return 0

    def collateTools(self,craft):
        caps = []
        if hasattr(craft,'tools'):
            for toolCap,level in craft.tools.items():
                if self.findToolCapacity(toolCap,level):
                    caps.append(True)
                else:
                    caps.append(False)
        return caps



    def makeCraft(self,craft):
        itemIng = craft.ingredients

        midStr = []
        for i, iv in itemIng.items():
            items = []
            for j in iv:
                orItems = []
                for item in j:
                    color = tc.f
                    key,amount = next(iter(item.items()))
                    canDo = self.testAmount(key,amount,returnAmt = False)
                    if canDo:
                        color = tc.c
                    outStr = color + "{}".format(Find.ItemDef(key).label) + tc.w + " x{} ({})".format(amount,self.testAmount(key,amount,returnAmt = True))

                    orItems.append(outStr)
                orItems = " OR ".join(orItems)
            items = "{}: ".format(i) + orItems + " "*50
            midStr.append(items)
        return " └ "+"\n └ ".join(midStr)

    def getOutput(self,craft):

        outputs = craft.output

        return " + ".join(["{} ({})".format(game.itemDefs[k].label, v) for k,v in outputs.items()])

    def checkCraft(self,defName):
        try:
            a = player.queuedCrafts[defName]
            return a
        except KeyError:
            return 0

    def craftTabulate(self,selectedItemIndex,page=0,sort=False):
        table = []
        defTable = []
        craftTable = []
        possibles = []
        headers = ["craft","time","craft per hr","queued"]

        for craft,obj in game.craftingDefs.items():
            canDo = self.collateIngredientsAndCheck(obj)
            canTool = self.collateTools(obj)
            if canDo:
                if canDo == 1:
                    color = tc.lg
                elif canDo == 2:
                    if all(canTool):
                        color = tc.c
                    else:
                        color = tc.lg
            else:
                continue
            tabItem = game.itemDefs[obj.defName]
            defTable.append([tabItem.rarity] + [tabItem.labelResolved()] + [tabItem] + [canDo] + [canTool])
            craftTable.append(obj)
            table.append([Find.ColorByRarity(tabItem.rarity) + color + tabItem.labelResolved() + tc.w,round(obj.timeCost(),2),str(int(obj.timeCost(1))) + "/hr",self.checkCraft(tabItem.defName)])
        tman = list(Sort.Paginate(table, player.tableLength))
        defTable = list(Sort.Paginate(defTable, player.tableLength))
        craftTable = list(Sort.Paginate(craftTable, player.tableLength))
        if len(table) == 0:
            return
        return (tb.tabulate(tman[page], headers, tablefmt='orgtbl'), len(table), defTable, tman, craftTable)

    def nameTabulate(self,selectedItemIndex,page=0,sort=False):
        table = []
        totalWeight = 0
        defTable = []
        headers = ['item','amount']
        preloadLabels = {}
        for k,v in self.contents.items():
            tabItem = game.itemDefs[k]
            if hasattr(tabItem,'diffprop'):
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
                        table.append([tabItem.rarity]+[x for x in tp.values()])
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
                headers[0] = tc.y + headers[0] + " *"+ tc.w
                table = Sort.ListByRarity(table,0)
                defTable.sort(key=lambda x: (sorted(game.rarityDefs.keys(), reverse=True)[list(game.rarityDefs.keys()).index(x[0])],x[1]))
                defTable = [row[2] for row in defTable]
            else:
                headers[sort] = tc.y + headers[sort]+ " *" + tc.w
                table.sort(key=lambda x: (x[sort],x[0]))
        tman = list(Sort.Paginate(table,player.tableLength))
        defTable = list(Sort.Paginate(defTable, player.tableLength))
        #tman[page][selectedItemIndex][0] = tc.bg_w + tman[page][selectedItemIndex][0] + tc.bg_b
        #tman[page][selectedItemIndex][0] = tc.bg_w + tc.f+ ">" + tc.w + tc.bg_b + tman[page][selectedItemIndex][0]
        '''for x,i in enumerate(tman[page]):
            if x != selectedItemIndex:
                tman[page][x][0] = tc.b + "." + tman[page][x][0]
        '''
        return (tb.tabulate(tman[page],headers,tablefmt='orgtbl'),len(table),defTable,tman,totalWeight)

    def tabulate(self,page=0,sort=False):
        table = []
        headers = ['item','amount','weight','value','food','water']
        totalWeight = 0
        preloadLabels = {}
        for k,v in self.contents.items():
            tabItem = game.itemDefs[k]
            if hasattr(tabItem,'diffprop'):
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
                    'weight': "{0:.2f}".format(tabItem.weight * len(v)),
                    'value': "{0:.2f}".format(tabItem.value * len(v)),
                    'nutFood': "{0:.2f}".format(
                        tabItem.getNutrition('food') * len(v)),
                    'nutWater': "{0:.2f}".format(
                        tabItem.getNutrition('water') * len(v))
                }
                if sort:
                    if sort == 'rarity':
                        table.append([tabItem.rarity]+[x for x in tp.values()])
                    else:
                        table.append([x for x in tp.values()])
                totalWeight += int(tabItem.getWeight() * len(v))
        for kk, vv in preloadLabels.items():
            i = vv[0]
            tp = {
                'tbLabel': kk,
                'amt': len(vv),
                'weight': "{0:.2f}".format(i.weight * len(vv)),
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
            totalWeight += int(i.getWeight() * len(vv))
        if sort:
            if sort == 'rarity':
                headers[0] = tc.y + headers[0] + " *"+ tc.w
                table = Sort.ListByRarity(table,0)
            else:
                headers[sort] = tc.y + headers[sort]+ " *" + tc.w
                table.sort(key=lambda x: (x[sort],x[0]))
        tman = list(Sort.Paginate(table,player.tableLength))
        return (tb.tabulate(tman[page],headers,tablefmt='orgtbl'),len(table),totalWeight)

    def calcNutrition(self):
        runningTotal = 0
        runningNutrition = [Find.ItemDef(x)['nutrition'] for x in self.contents.items() if hasattr(Find.ItemDef(x),'nutrition')]
        for i in runningNutrition:
            if 'food' in list(i.keys()):
                runningTotal += i['food']
        return runningTotal

    def calcFoodDays(self,group):
        return self.calcNutrition() / len(group)




#######################################################################################################################

game = GameProperties()
player = Player()

cr.init(autoreset=False)
tb.PRESERVE_WHITESPACE = True
cursor.hide()

with open("data/names.yaml") as STREAM:
    nameInfo = yaml.safe_load(STREAM)

with open("data/fexgen.yaml") as STREAM:
    faceInfo = yaml.safe_load(STREAM)
