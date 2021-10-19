# https://forums.cgsociety.org/t/delete-multiple-attributes/1848055/2
import maya.cmds as cmds
from functools import partial

class MassDeleteAttrWindow(object):
    def __init__(self):
            self.window = 'massDeleteAttrWin'
            self.title = 'Mass Delete Attributes'
            self.size = (600, 800)

    def create(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        self.window = cmds.window(
            self.window,
            title = self.title,
            widthHeight = self.size
        )
        self.mainForm = cmds.paneLayout(configuration='horizontal3', ps=((1,100,80), (2,100,10)))
        self.uiList = cmds.textScrollList(allowMultiSelection=True)
        self.btnDelete = cmds.button(label='Delete!', command=partial(self.doDelete))
        self.btnRefresh = cmds.button(label='Refresh Selection', command=partial(self.doRefresh))

    def getSelection(self):
        self.selection = cmds.ls(selection=True)
        if self.selection == []:
            self.selection = cmds.ls(transforms=True, shapes=True)

    def listCustomAttrs(self):
        attrs = []
        for node in self.selection:
            customAttrs = cmds.listAttr(node, ud=True)
            if customAttrs:
                attrs.extend(customAttrs)
        return sorted(list(set(attrs)))

    def doDelete(self, *args):
        attrs = cmds.textScrollList(self.uiList, q=True, selectItem=True)
        for node in self.selection:
            for attr in attrs:
                if cmds.objExists(node) and cmds.attributeQuery(attr, node=node, exists=True):
                    cmds.deleteAttr(node + '.' + attr)
        for attr in attrs:
            cmds.textScrollList(self.uiList, e=True, removeItem=attr)

    def doRefresh(self, *args):
        self.getSelection()
        cmds.textScrollList(self.uiList, e=True, removeAll=True)
        cmds.textScrollList(self.uiList, e=True, append=self.listCustomAttrs())

    def show(self):
        cmds.showWindow(self.window)
        self.doRefresh()

win = MassDeleteAttrWindow()
win.create()
win.show()
