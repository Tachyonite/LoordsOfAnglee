from core import *
import utils.translator as translator
import glob

#######################################################################################################################

attrs = {
    'itemDefs': "Item",
    'craftingDefs': "Craft",
    'traitDefs' : "Trait",
    'crateDefs' : "Crate",
    'rarityDefs' : "Rarity",
    'chapterDefs' : "Chapter",
    'fluidDefs' : "Fluid",
    'moveDefs' : "Move",
    'workDefs' : "Work",
    'tableDefs' : "Table",
    "locationDefs" : "Location",
    "setDefs" : "Set"
}

def loadDef(itemloader,properties):
    for k,v in itemLoader.items():
        try:
            loaded = getattr(properties,k)
        except AttributeError:
            setattr(properties,k,{})
            loaded = getattr(properties,k)
        for kk,vv in v.items():
            if kk.startswith("$$"): continue # ABSTRACT ITEM IGNORE
            loaded[kk] = eval(attrs[k] + "('{}',{})".format(kk,vv))
            if hasattr(loaded[kk],'packable'):
                properties.itemDefs["packet!"+kk] = Item("packet!"+kk,vv)
                properties.itemDefs["packet!"+kk].packableAdd(loaded[kk],loaded[kk].packable['amount'],loaded[kk].packable['label'])
                print()


################################################

dictcalls = glob.glob("data/**/*.yaml")

for file in dictcalls:
    with open(file) as STREAM:
        itemLoader = yaml.safe_load(STREAM)
        if not itemLoader:
            continue
        loadDef(itemLoader,game)

## REPLACE WITH ACTUAL SEARCHER LATER
with open("loc/eng-uk/localisation.yaml") as STREAM:
    localisation = yaml.safe_load(STREAM)
    translator.loadStrings(localisation)