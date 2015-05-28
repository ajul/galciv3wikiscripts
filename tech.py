import xml.etree.ElementTree as ET
import re
import os
import loc

datadir = 'D:/Steam/steamapps/common/Galactic Civilizations III/data'
gamedatadir = os.path.join(datadir, 'Game')

def processTechTree(techList, filename):
    filebase, _ = os.path.splitext(filename)
    techSpecializationList = ET.parse(os.path.join(gamedatadir,
                                                   filename.replace('Defs', 'SpecializationDefs'))).getroot()
    locSources = ['%sText.xml' % filebase]
    # item : [leads to, ...]
    prereqs = {}
    # specialization : techs
    specializations = {}
    # techs: unlocks
    unlocks = {}

    # returns the tech itself if not specialization, otherwise returns the corresponding specialization
    def getItem(tech):
        specialization = tech.findtext('Specialization')
        if specialization is None:
            return tech
        else:
            return techSpecializationList.find("TechSpecialization[InternalName='%s']" % specialization)

    def getTechByGenericName(genericName):
        return techList.find("Tech[GenericName='%s']" % genericName)

    # gets the tech or specialization corresponding to a given name
    def getItemByGenericName(genericName):
        tech = getTechByGenericName(genericName)
        if tech is None: return None
        return getItem(tech)
        
    # compute specializations
    for tech in techList.findall('Tech'):
        if tech.findtext('RootNode') == 'true':
            rootTech = tech
        
        item = getItem(tech)
        if item != tech:
            # is a specialization
            if item not in specializations:
                specializations[item] = []
            specializations[item].append(tech) 
        prereqs[item] = []
        unlocks[tech] = []

    # compute prereqs
    for tech in techList.findall('Tech'):
        item = getItem(tech)
        for prereqTechName in tech.findall('Prerequ/Techs/Option'):
            prereqItem = getItemByGenericName(prereqTechName.text)
            if prereqItem is None:
                print('Tree has no prereq tech %s' % prereqTechName.text)
                continue
            if item not in prereqs[prereqItem]:
                prereqs[prereqItem].append(item)

    # compute unlocks
    unlockSources = [
        ('Improvement', 'Improvement'),
        ('InvasionStyle', 'Invasion Tactic'),
        ('PlanetaryProject', 'Planetary Project'),
        ('ShipComponent', 'Ship Component'), 
        ('SpecialShipComponent', 'Ship Component'),
        ('ShipHullStat', 'Hull Size'),
        ('StarbaseModule', 'Starbase Module'),
        ('UPResolution', 'United Planets Resolution'),
        ]

    for unlockType, unlockTypeName in unlockSources:
        unlockRoot = ET.parse(os.path.join(gamedatadir, '%sDefs.xml' % unlockType))
        unlockLocSources = ['%sText.xml' % unlockType]
        for unlockable in unlockRoot.findall('*'):
            unlockName = loc.english(unlockable.findtext('DisplayName'), unlockLocSources) or '???'
            unlockText = '%s: %s' % (unlockTypeName, unlockName)
            for techName in unlockable.findall('Prerequ/Techs/Option'):
                tech = getTechByGenericName(techName.text)
                if tech is None:
                    # print('Tree has no unlock tech %s' % techName.text)
                    continue
                unlocks[tech].append(unlockText)

    # TODO: planet traits
    # output
    
    def techInfo(tech):
        info = {}
        info['Name'] = loc.english(tech.findtext('DisplayName'), locSources)
        age = tech.findtext('Prerequ/TechAge/Option') or ''
        info['Age'] = age.replace('AgeOf', '')
        info['ResearchCost'] = int(tech.findtext('ResearchCost'))
        statInfo = []
        for unlock in unlocks[tech]:
            statInfo.append(unlock)
        for stats in tech.findall('Stats'):
            effectType = loc.english('STATNAME_%s' % stats.findtext('EffectType'), ['StatText.xml'])
            effectType = re.sub('\[.*\]\s*', '', effectType)
            targetType = stats.findtext('Target/TargetType')
            if stats.findtext('BonusType') == 'Flat':
                value = '%0.1f' % float(stats.findtext('Value'))
            elif stats.findtext('BonusType') == 'Multiplier':
                value = '%+d%%' % (float(stats.findtext('Value')) * 100.0)
            
            statInfo.append('%s %s %s' % (targetType, effectType, value))
        return info, statInfo
    
    def wikiOutput(item, depth = 0):
        result = '|-\n'
        result += '| ' + '>' * depth
        if item.tag == 'Tech':
            info, statInfo = techInfo(item)
            result += ' %(Name)s || %(Age)s || %(ResearchCost)s \n' % info
            result += '| \n'
            for bonus in statInfo:
                result += '* %s \n' % bonus
        else:
            info, _ = techInfo(specializations[item][0])
            result += ' %(Name)s || %(Age)s || %(ResearchCost)s \n' % info
            result += '| \n'
            for tech in specializations[item]:
                _, statInfo = techInfo(tech)
                result += '* Specialization:\n'
                for bonus in statInfo:
                    result += ':* %s \n' % bonus
                
        for item in prereqs[item]:
            result += wikiOutput(item, depth + 1)

        return result

    result = ''
    for categoryTech in prereqs[rootTech]:
        result += '== %s ==\n' % loc.english(categoryTech.findtext('DisplayName'), locSources)
        result += '{|class = "wikitable"\n'
        result += '! Name !! Age !! Research cost !! Effects \n'
        result += wikiOutput(categoryTech)
        result += '|}\n'

    return result

for filename in os.listdir(gamedatadir):
    techList = ET.parse(os.path.join(gamedatadir, filename)).getroot()
    if techList.tag != 'TechList': continue
    result = processTechTree(techList, filename)
    filebase, _ = os.path.splitext(filename)
    outfile = open(os.path.join('out', '%s.txt' % filebase), 'w')
    outfile.write(result)
    outfile.close()
