import xml.etree.ElementTree as ET
import re
import os
import loc

datadir = 'D:/Steam/steamapps/common/Galactic Civilizations III/data'
gamedatadir = os.path.join(datadir, 'Game')

improvementList = ET.parse(os.path.join(gamedatadir, 'ImprovementDefs.xml'))
locSources = ['ImprovementText.xml', 'StatText.xml']

result = '{|class = "wikitable sortable"\n'
result += '! Icon !! Improvement !! Type !! Cost !! Maintenance !! Effects !! Level effects !! Neighbor bonuses \n'

def statString(stats):
    effectType = stats.findtext('EffectType')
    targetType = stats.findtext('Target/TargetType')
    bonusType = stats.findtext('BonusType')
    if bonusType == 'Flat':
        value = '%0.1f' % float(stats.findtext('Value'))
    elif bonusType == 'Multiplier':
        value = '%+d%%' % (float(stats.findtext('Value')) * 100.0)
    return '%s %s %s' % (
        loc.english(targetType, locSources),
        re.sub('\[.*\]\s*', '', loc.english('STATNAME_%s' % effectType, locSources)),
        value,
        )

for improvement in improvementList.findall('Improvement'):
    data = {}
    data['Name'] = loc.english(improvement.findtext('DisplayName'), locSources)
    data['Icon'] = improvement.findtext('ListIcon')
    data['Type'] = improvement.findtext('ImprovementType')
    if data['Type'] in ('DurationalProject', 'TradeResource'): continue
    data['Maintenance'] = ''
    data['ManufacturingCost'] = ''
    
    data['Stats'] = []
    if improvement.findtext('IsGalacticWonder') == 'true':
        data['Stats'].append('Galactic wonder')
    if improvement.findtext('IsPlayerWonder') == 'true':
        data['Stats'].append('Player wonder')
    if improvement.findtext('IsColonyUnique') == 'true':
        data['Stats'].append('Colony unique')
    if improvement.findtext('LandPercentageMin') is not None:
        data['Stats'].append('Terraform: minimum land percentage %s' % improvement.findtext('LandPercentageMin'))
    
    for stats in improvement.findall('Stats'):
        effectType = stats.findtext('EffectType')
        if effectType == 'ManufacturingCost':
            data['ManufacturingCost'] = stats.findtext('Value')
        elif effectType == 'Maintenance':
            data['Maintenance'] = stats.findtext('Value')
        else:
            data['Stats'].append(statString(stats))

    for stats in improvement.findall('Triggers/Modifier'):
        data['Stats'].append(statString(stats))

    data['LevelEffectStats'] = []
    for stats in improvement.findall('LevelEffectStats'):
        data['LevelEffectStats'].append(statString(stats))

    for stats in improvement.findall('LevelEffectTriggers/Modifier'):
        data['LevelEffectStats'].append(statString(stats))

    data['NeighborBonuses'] = []
    for neighborBonuses in improvement.findall('NeighborBonuses'):
        neighborType = neighborBonuses.findtext('GiveBonusToNeighborType')
        neighborValue = neighborBonuses.findtext('NeighborBonusValue')
        data['NeighborBonuses'].append((neighborType, neighborValue))

    if improvement.findtext('Prerequ/Unavailable') == 'true':
        data['ManufacturingCost'] = ''

    result += '|- \n'
    result += '| [[File:%(Icon)s]] || [[%(Name)s]] || %(ManufacturingCost)s || %(Maintenance)s \n' % data
    result += '| \n'
    for stat in data['Stats']:
        result += '* %s \n' % stat

    result += '| \n'
    for stat in data['LevelEffectStats']:
        result += '* %s \n' % stat
        
    result += '| %(Type)s \n' % data
    result += '| \n'
    for neighborType, value in data['NeighborBonuses']:
        result += '* +%s %s \n' % (value, neighborType) 

result += '|}\n'
outfile = open(os.path.join('out', 'improvement.txt'), 'w')
outfile.write(result)
outfile.close()
    


