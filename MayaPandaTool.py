"""
MayaPandaTool MEL script but converted into python

"""

import maya.cmds as cmds
def pandaExporterUI():

  if (cmds.window("PandaExporter2", exists=True)):
      cmds.deleteUI("PandaExporter2")
  
  unit = 'currentUnit -q linear'
  unitFull = 'currentUnit -q -linear -fullName'
  cmds.window("PandaExporter2", title="Panda Exporter", widthHeight=(280, 575), sizeable=False)

  form = cmds.formLayout("mainForm", numberOfDivisions=575, width=275, height=550)
  cmds.button("exportButton", label="--- E X P O R T ---", command="exportButton")
  cmds.button("browseTexPathButton", label="Browse", enable=False, command="browseForFolder {}".format(texPath))

def exportOptionsUI():
  pass

def animationOptionsUI():
  pass

def texPathOptionsUI():
  pass

def outputPathOptionsUI():
  pass

def outputFilenameOptionsUI():
  pass

def transformModeUI():
  pass

def browseForFolder(destination):
  pass

def browseForFolderCallback(destination, result, type):
  pass

def browseForFile(destination):
  pass

def browseForFileCallback(destination, result, type):
  pass

def filePart(path):
  filePart = match( "[^/\\]*$", path)
  return filePart

def pathPart(path):
  dir = match("^.*/", path)
  return dir

def exportScene(selection):
  pass

def argsBuilder():
  pass

def export2Egg(mbfile, destPath, destFilename, transformMode, ARGS):
  pass

def exportButton():
  pass

def send2Piew(file):
  pass

def getFile2Pview():
  pass

def getFile2Bam():
  pass

def getFile2Egg():
  pass

def exportPrep(workFile, fileName):
  pass

def export2Bam(eggFile):
  pass

