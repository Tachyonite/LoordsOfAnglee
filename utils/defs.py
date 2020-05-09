import random

from utils.helpers import p
from utils.helpers import tc

class Item():
    def __init__(self, defName, object):
        self.defName = defName
        self.label = defName
        self.description = defName
        self.value = 0
        self.weight = 0
        self.rarity = 'common'
        self.property = None
        self.moveable = True
        self.nutrition = None
        self.object = dict(object)

        for k, v in self.object.items():
            setattr(self, k, v)
        if hasattr(self,'storage'):
            self.storage = dict(self.storage)
            self.storage['filled'] = 0
            self.storage['fluid'] = ""
        if hasattr(self, 'durability'):
            self.durability['uses'] = self.durability['maxUses']

        self.rarityLabel = tc.rarity[self.rarity] + self.labelResolved() + tc.w
        '''
        try:
            self.t = rarity(self.rarity) + self.label + rarity("reset")
        except AttributeError as e:
            print(self.defname, "has no rarity!")
        '''
    def spawnDamage(self):
        if hasattr(self, 'durability'):
            self.durability['uses'] = random.randint(1, self.durability['maxUses'])

    def packableAdd(self,unpackItem,unpackAmount,boxLabel):
        self.label = boxLabel + " ({})".format(unpackAmount)
        self.openable = {"contents":{unpackItem.defName:unpackAmount}}
        self.value = int(self.value * unpackAmount)
        self.weight = int(self.weight * unpackAmount)

    def labelResolved(self,invamt=1):
        if hasattr(self, 'diffprop'):
            props = self.getDiffprop()

            if hasattr(self,'tool'):
                return "{} ({}%)".format(self.label, round(props[0]/props[1] * 100))
            if len(props) == 3 and props[2]:
                return "{} of {} ({}/{})".format(self.label, props[2].label, props[0], props[1])
            else:
                return "{} ({}/{})".format(self.label,props[0],props[1])
        if hasattr(self, 'isCrate') and self.isCrate:
            return "{}□{} ".format(tc.y,tc.rarity[self.rarity])+ self.label
        if hasattr(self, 'moveable') and not self.moveable:
            return self.label + " {}▼{}".format(tc.f,tc.rarity[self.rarity])
        else:
            return self.label

    def genPropName(self):
        if hasattr(self,'diffprop'):
            print(self.diffprop)
            input()
            if len(self.diffprop) == 2:
                return self.label + "({}/{})".format(eval(self.diffprop[0]),eval(self.diffprop[1]))
            elif len(self.diffprop) == 3:
                return self.label + "({} {}/{})".format(eval(self.diffprop[2]),eval(self.diffprop[0]),eval(self.diffprop[1]))
        else:
            return self.label

    def getWeight(self):
        if hasattr(self,'storage'):
            if self.storage['filled'] > 0:
                return self.storage['fluid'].weight * self.storage['filled']
        return self.weight

    def getNutrition(self,key):
        if hasattr(self,'storage') and 'filled' in self.storage:
            if self.storage['filled'] > 0:
                return self.storage['fluid'].getNutrition(key) * self.storage['filled']
        if self.nutrition:
            try:
                return self.nutrition[key]
            except KeyError:
                return 0
        else:
            return 0

    def getDiffprop(self):
        if hasattr(self,'diffprop'):
            props = [eval("self.{}".format(i),{"self":self}) for i in self.diffprop]
            return props
        else:
            return

    def tryGet(self, attr):
        try:
            return getattr(self, attr)
        except AttributeError:
            return False

    def tryGetDeep(self, attr, deep):
        try:
            toDeepSearch = getattr(self, attr)
            if type(getattr(self, attr)) == dict:
                if deep in toDeepSearch:
                    return toDeepSearch
                else:
                    return False
            else:
                return False
        except AttributeError:
            return False

    def tryGetParent(self, attr):
        try:
            return self
        except AttributeError:
            return False

    def tryGetDeepParent(self, attr, deep):
        try:
            toDeepSearch = getattr(self, attr)
            if type(getattr(self, attr)) == dict:
                if deep in toDeepSearch:
                    return self
                else:
                    return False
            else:
                return False
        except AttributeError:
            return False

class Set():
    def __init__(self, defName, object):
        self.defName = defName
        self.object = dict(object)
        for k, v in self.object.items():
            setattr(self, k, v)
    def add(self,player):
        for k,v in self.contents.items():
            player.inventory.addItem(k,v)

class Craft():
    def __init__(self, defName, object):
        self.defName = defName
        self.object = dict(object)
        for k, v in self.object.items():
            setattr(self,k,v)
        self.progress = 0
        self.favourite = False


    def tryGet(self, attr):
        try:
            return getattr(self, attr)
        except AttributeError:
            print(getattr(self,attr))
            return False

    def tryGetDeep(self, attr, deep):
        try:
            toDeepSearch = getattr(self, attr)
            if type(getattr(self, attr)) == dict:
                if deep in toDeepSearch:
                    return toDeepSearch
                else:
                    return False
            else:
                return False
        except AttributeError:
            return False

    def tryGetParent(self, attr):
        try:
            return self
        except AttributeError:
            return False

    def tryGetDeepParent(self, attr, deep):
        try:
            toDeepSearch = getattr(self, attr)
            if type(getattr(self, attr)) == dict:
                if deep in toDeepSearch:
                    return self
                else:
                    return False
            else:
                return False
        except AttributeError:
            return False
    def timeCost(self,inHours=0,creature=None):
        minutes = 60
        t = self.timeBase
        if 'm' in t:
            t0 = int(t.replace("m","")) / minutes
        elif 'h' in t:
            t0 = int(t.replace("h",""))
        else:
            t0 = int(t)
        # 30m = 0.5, which would be time / minutes
        if inHours:
            return inHours / t0
        if not creature:
            return t0


class Rarity():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)

    def getColor(self):
        return self.color


class Location():
    def __init__(self, defName, object):
        self.defName = defName
        self.linked = []
        self.looted = False
        self.intel = 0
        for k, v in object.items():
            setattr(self,k,v)

    def generateLinked(self,game):
        self.linked = set(game.locationDefs[i] for i in random.choices(population=list(self.connects.keys()),weights=list(self.connects.values()),k=random.randint(2,3)))


class Chapter():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)

    def getDescription(self):
        return self.description
    def getVignette(self):
        return self.vignette

class Crate():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)
    def generateContents(self,game):
        self.contents = {}
        for k,v in self.items.items():
            pop = [[kk,1/1+game.itemDefs[kk].value] for kk in game.itemDefs.keys() if game.itemDefs[kk].moveable and game.itemDefs[kk].rarity == k and not hasattr(game.itemDefs[kk],'isCrate') and game.itemDefs[kk].weight < self.maxContentsWeight]
            if pop:
                self.contents[k] = random.choices(population=[i[0] for i in pop],weights=[i[1] for i in pop],k=v)
        return self.contents
    def provideContents(self,game):
        self.generateContents(game)
        return self.contents

class Work():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)
    def getLabel(self):
        return self.label
    def timeCost(self,creature=None):
        minutes = 60
        t = self.timeBase
        if 'm' in t:
            t0 = int(t.replace("m","")) / minutes
        elif 'h' in t:
            t0 = int(t.replace("h",""))
        # 30m = 0.5, which would be time / minutes
        if not creature:
            return t0

class Table():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)

    def getLabel(self):
        return self.label

    def rollTable(self,rolls):
        for i in range(rolls):
            item = random.choice(list(self.contents.keys()))
            vals = self.contents[item].split("~")
            amt = random.randint(int(vals[0]),int(vals[1]))
            return [item,amt]


class Fluid():
    def __init__(self, defName, object):
        self.defName = defName
        for k, v in object.items():
            setattr(self,k,v)

    def getUnit(self,container):
        if container.storage['filled'] >= 1:
            return "L"
        else:
            return "mL"

    def getNutrition(self,key):
        if self.nutrition:
            try:
                return self.nutrition[key]
            except KeyError:
                return 0
        else:
            return 0

    def getWeight(self):
        return self.weight

    def fillContainer(self,container,litres):
        '''
        This function tries to place liquids into containers, and returns the amount is successfully placed.

        First:
            We need to check if it's empty.
            If it is, put as much liquid in as you can and return the amount placed.
            If it isn't, we need to check if this container has an existing liquid in it.
            Then:
                Check if the liquid is the one we want to place.
                If it is, check how much space it has and place as much as you can.
                If it isn't, return '0' as we couldn't place anything.
        '''
        if not hasattr(container,'storage'): return 0
        if hasattr(self,'sealed') and self.sealed \
                and 'sealable' in  container.storage \
                and not container.storage['sealable']:
                    return
        cs = container.storage
        if 'fluid' in cs and cs['fluid']:
            if cs['filled'] == cs['volume']: return 0
            if cs['fluid'] == self:
                empty = cs['volume'] - cs['filled']
                if empty >= litres:
                    cs['filled'] = cs['filled'] + litres
                    p(" └ Filled {}L into {}".format(litres,container.labelResolved()))
                    return litres
                elif empty < litres:
                    cs['filled'] = cs['filled'] + empty
                    p(" └ Filled {}L into {}".format(empty, container.labelResolved()))
                    return empty
            else:
                return 0
        else: #It's empty
            difference = cs['volume'] - litres
            # If we're trying to fill a container of vol 3 with 5L of water, difference will be 2L that we can't place
            # placed will be 3L that we *can* place, which is what we want to return
            if litres > cs["volume"]:
                cs['filled'] += cs["volume"]
                cs['fluid'] = self
                p(" └ Filled {}L into {}".format(cs["volume"], container.labelResolved()))
                return cs["volume"]
            elif litres <= cs["volume"]:
                cs['filled'] += litres
                cs['fluid'] = self
                p(" └ Filled {}L into {}".format(litres, container.labelResolved()))
                return litres
        return litres




















