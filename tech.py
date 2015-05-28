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

    # returns the tech itself if not specialization, otherwise returns the corresponding specialization
    def getItem(tech):
        specialization = tech.findtext('Specialization')
        if specialization is None:
            return tech
        else:
            return techSpecializationList.find("TechSpecialization[InternalName='%s']" % specialization)

    # gets the tech or specialization corresponding to a given name
    def getItemByGenericName(genericName):
        tech = techList.find("Tech[GenericName='%s']" % genericName)
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

    # output
    
    
    def techInfo(tech):
        info = {}
        info['Name'] = loc.english(tech.findtext('DisplayName'), locSources)
        info['ResearchCost'] = int(tech.findtext('ResearchCost'))
        statInfo = []
        for stats in tech.findall('Stats'):
            effectType = loc.english('STATNAME_%s' % stats.findtext('EffectType'), ['StatText.xml'])
            effectType = re.sub('\[.*\]\s*', '', effectType)
            targetType = stats.findtext('Target/TargetType')
            if stats.findtext('BonusType') == 'Flat':
                value = '%0.1f' % float(stats.findtext('Value'))
            elif stats.findtext('BonusType') == 'Multiplier':
                value = '%+d%%' % (float(stats.findtext('Value')) * 100.0)
            
            statInfo.append('%s %s %s' % (value, targetType, effectType))
        return info, statInfo
    
    def wikiOutput(item, depth = 0):
        result = '|-\n'
        result += '| ' + '>' * depth
        if item.tag == 'Tech':
            info, statInfo = techInfo(item)
            result += ' %(Name)s || %(ResearchCost)s \n' % info
            result += '| \n'
            for bonus in statInfo:
                result += '* %s \n' % bonus
        else:
            info, _ = techInfo(specializations[item][0])
            result += ' %(Name)s || %(ResearchCost)s \n' % info
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
        for tech in prereqs[categoryTech]:
            result += '{|class = "wikitable"\n'
            result += '! Name !! Reserach cost !! Effects \n'
            result += wikiOutput(tech)
            result += '|}\n'

    return result

for filename in os.listdir(gamedatadir):
    techList = ET.parse(os.path.join(gamedatadir, filename)).getroot()
    if techList.tag != 'TechList': continue
    result = processTechTree(techList, filename)
    #print(result)
