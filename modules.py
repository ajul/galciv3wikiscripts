import xml.etree.ElementTree as ET
import os
import loc

datadir = 'D:/Steam/steamapps/common/Galactic Civilizations III/data'

tree = ET.parse(os.path.join(datadir, 'Game', 'ShipComponentDefs.xml'))

def manufacturingCost(shipComponent):
    result = 0.0
    for stats in shipComponent.findall('Stats'):
        if 'ManufacturingCost' in stats.findtext('EffectType'):
            result += float(stats.findtext('Value'))
    return '%d' % result

def techRequired(shipComponent):
    techs = [loc.english('Generic%s_Name' % option.text, ['TechDefsText'])
             for option in shipComponent.findall('./Prerequ/Techs/Option')]
    return '<br/>'.join(techs)

for shipComponent in tree.findall('ShipComponent'):
    print(techRequired(shipComponent))
