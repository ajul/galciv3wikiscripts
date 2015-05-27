import xml.etree.ElementTree as ET
import os

datadir = 'D:/Steam/steamapps/common/Galactic Civilizations III/data'

trees = {}

def english(key, sources):
    for source in sources:
        if source not in trees:
            trees[source] = ET.parse(os.path.join(datadir, 'English', 'Text', '%s.xml' % source))
        result = trees[source].findtext("StringTable[Label='%s']/String" % key)
        if result is not None: return result
    print('Missing localization: %s' % key)
    return key
