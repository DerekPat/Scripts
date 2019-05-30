import maya.cmds as mc
import maya.mel as mel
import os
import getpass

path = mc.file(q=True, sn=True)
pathSplit = path.split("/")
ep = pathSplit[6]
sh = pathSplit[7]
mf = pathSplit[10]
mfSplit = mf.split(".")
ve = mfSplit[0]
#print ve

tempPath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\Lighting\\maya\\images\\tmp\\"+ve+"\\"
#print tempPath

fileList = os.listdir(tempPath)
if not "renderView" in cmds.getPanel(visiblePanels = True):
        cmds.RenderViewWindow() # open renderView window if closed to avoid color management problems
for im in fileList:
    editor = mc.renderWindowEditor(q=True, en = True)
    mc.renderWindowEditor(editor, e=True, si=True, li= tempPath + im)
    sys.stdout.write("IF IMAGES DOESN'T APPEAR REOPEN RENDERVIEW")