import maya.cmds as mc
import os
import getpass

def saveimages():
    
    #print version
    path = mc.file(q=True, sn=True)
    pathSplit = path.split("/")
    ep = pathSplit[6]
    sh = pathSplit[7]
    #print ep
    #print sh
    getCurrentTime = mc.currentTime(q=True)
    timeSplit = str(getCurrentTime).split(".")
    time = timeSplit[0]
    #print time
    userName = getpass.getuser()
    nameSplit = userName.split(".")
    name = nameSplit[0]
    #print name
    pubPath = "\\\\jfpstorage\\Work\\team_dennis\\assets\\config\\" + ep + "\\ReadyToRenderStills\\"
    #epxxx_shxxx_Lighting_v00x_.xxxx.name of the lighter
    #savePath = "\\\\jfpstorage\\Work\\team_dennis\\assets\\config\\" + ep + "\\ReadyToRenderStills\\"+ sh + "_" + "Lighting" + "_" + "." + ""+ time +"" + "." + ""+ name +""
    if os.path.exists(pubPath) == True:
        if not "renderView" in cmds.getPanel(visiblePanels = True):
            cmds.RenderViewWindow() # open renderView window if closed to avoid color management problems
        version = 1
        while os.path.exists(pubPath + ""+ sh + "_" + "Lighting" + "_v" + str("{:03d}".format(version)) + "." + ""+ time +"" + "." + ""+ name +"" + ".png") == True:
            version += 1
            if not os.path.exists(pubPath + ""+ sh + "_" + "Lighting" + "_v" + str("{:03d}".format(version)) + "." + ""+ time +"" + "." + ""+ name +"" + ".png") == True:
                break
        mc.setAttr ('defaultRenderGlobals.imageFormat', 32)
        #editor = 'renderView'
        editor = mc.renderWindowEditor(q=True, en = True)
        mc.renderWindowEditor(editor, e=True, com=True, writeImage= pubPath + ""+ sh + "_" + "Lighting" + "_v" + str("{:03d}".format(version)) + "." + ""+ time +"" + "." + ""+ name +"" + ".png")
        mc.setAttr ('defaultRenderGlobals.imageFormat', 51)
        sys.stdout.write("ALAKAZAM! RENDER SAVED!.")

saveimages()