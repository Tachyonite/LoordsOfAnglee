from utils.helpers import *

def clearSidebar():
    s = [" "*50]
    return

def itemFormat(item,itemDef,amount,**kwargs):
    details = \
"""
{}
--------------
{}
--------------
amount: {}
value: {}¤ (total: {}¤)
weight: {}kg (total: {}kg)
rarity: {}""".format(item.labelResolved() + tc.w,
                     "\n".join(tw.wrap(itemDef.description.lower(), 40)), amount, itemDef.value,
                     round(itemDef.value * amount, 3), item.getWeight(), round(item.getWeight() * amount, 3),
                     itemDef.rarity)
    if hasattr(item, 'storage'):
        if item.storage['filled'] > 0:
            details += \
"""
--------------
stored: {}{} of {} (total: {})""".format(item.storage['filled'], item.storage['fluid'].getUnit(item),
                             item.storage['fluid'].label,item.storage['filled'] * amount)
        else:
            details += \
"""
--------------
stored: empty"""

    nutritions = [item.getNutrition('food'),item.getNutrition('water'),item.getNutrition('alcohol')]
    if nutritions != [0,0,0]:
        details += \
"""
--------------
nutrition:
"""
        if nutritions[0]:
            details += \
"""- {}: {} (total: {})
""".format('food', nutritions[0], nutritions[0] * amount)
        if nutritions[1]:
            details += \
"""- {}: {} (total: {})
""".format('water', nutritions[1], nutritions[1] * amount)
        if nutritions[2]:
            details += \
"""- {}: {}
""".format('alcohol', nutritions[2])

    if hasattr(item,'tool'):
        details += \
"""
--------------
as tool:
"""
        for k,v in item.tool.items():
            details += \
"""- {}: {}
""".format(k,v)
    details += \
"""
""" * 2
    if hasattr(item, 'openable'):
        details += \
"""
{}u | unpack{}
""".format(tc.y,tc.w)
        if 'tool' in item.openable:
            for k, v in item.openable['tools'].items():
                details += \
"""- {}: {}
""".format(k, v)
    if hasattr(item, 'moveable') and not item.moveable:
        details += \
"""{}▼{} item can't be taken with you
""".format(tc.f, tc.w)
    details += \
"""
""" * 18
    return details

def craftFormat(craft,formText,game,canDo=0,canTool=()):
    outputs = craft.output.items()
    opString = []
    for k,v in outputs:
        if k.startswith("~"):
            opString.append("{} {}L".format(game.fluidDefs[k[1:]].label,v))
        else:
            opString.append("{} x{}".format(game.itemDefs[k].label, v))
    details = \
"""
{}
--------------
{}
--------------
costs:                                                                                                                                                                    
{}                                                             
makes:                                                                                                            
{}                                                                                                                             
""".format(craft.label,
                     "\n".join(tw.wrap(craft.description.lower(), 40)), formText,"\n └ ".join(opString))
    if hasattr(craft, 'tools'):
        details += \
"""                                                                                                        
--------------                                                                                    
tools:                                                                                            
"""
        count = 0
        for k, v in craft.tools.items():
            color = tc.w
            if canTool:
                if not canTool[count]:
                    color = tc.f
            details += \
"""- {}{}: {}{}                                                                                       
""".format(color,k, v,tc.w)
            count+=1
    if canDo == 2 and (not canTool or all(canTool)):
        details +=\
"""                                                                                                               
craftable now: yes
""".format(tc.c,tc.w)
    else:
        details += \
"""                                                                                                                     
craftable now: {}no{}
""".format(tc.f, tc.w)
    details += \
""" 
"""*20
    return details

'''
    details += \
"""
--------------
value: {}¤ (total: {}¤)
weight: {}kg (total: {}kg)
rarity: {}





""".format(outItem.value,round(outItem.value * amount, 3), outItem.getWeight(), round(outItem.getWeight() * amount, 3),
                     outItem.rarity)
'''