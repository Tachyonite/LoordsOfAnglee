from core import *
import utils.translator as translator

#######################################################################################################################

attrs = {
    'itemDefs': "Item",
    'craftingDefs': "Craft",
    'traitDefs' : "Trait",
    'crateDefs' : "Crate",
    'rarityDefs' : "Rarity",
    'chapterDefs' : "Chapter",
    'fluidDefs' : "Fluid",
    'workDefs' : "Work",
    'tableDefs' : "Table",
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

with open("dictcalls.txt") as f:
    dictcalls = [x.strip("\n") for x in f.readlines()]

for file in dictcalls:
    if file.startswith("#"):
        continue
    with open("{}.yaml".format(file)) as STREAM:
        itemLoader = yaml.safe_load(STREAM)
        loadDef(itemLoader,game)

## REPLACE WITH ACTUAL SEARCHER LATER
with open("loc/eng-uk/localisation.yaml") as STREAM:
    localisation = yaml.safe_load(STREAM)
    translator.loadStrings(localisation)