import maya.cmds as cmds
import maya.mel as mel

#print(mel.eval('polyUVSet -allUVSets'))
for geomNode in cmds.ls(type='geometryShape'):
    uvSet = mel.eval('polyUVSet -q -cuv %s' % geomNode)
    if uvSet[0] != 'map1':
        mel.eval('polyUVSet -rename -uvSet %s -newUVSet "map1" %s;' % (uvSet[0], geomNode))
    # print(a[0] == ('map1'))
    # mel.eval('polyUVSet -rename -uvSet  UVMap -newUVSet "map1" %s;' % geomNode)
    