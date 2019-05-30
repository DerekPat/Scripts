################################
#                              #
# MASTER EFFECTS FOLDER SETUP  #
#                              #
#                              #
################################
import maya.cmds as mc
import os
path = mc.file(q=True, sn=True)

pathSplit = path.split("/")
ep = pathSplit[6]
sh = pathSplit[7]
mfName = pathSplit[10]
mfNameSplit = mfName.split(".")
mf = mfNameSplit[0]
#print ep
#print sh

cachePath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\" + "FX\\" + "maya\\" + "cache"
shotPath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\" + "FX\\" + "maya\\" + "cache\\" + mf + "\\"
nCachePath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\" + "FX\\" + "maya\\" + "cache\\" + mf + "\\" + "nCache"
rsProxyPath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\" + "FX\\" + "maya\\" + "cache\\" + mf + "\\" + "rsProxy"
vdbPath = "\\\\jfpstorage\\Work\\team_dennis\\episodes\\" + ep + "\\" + sh + "\\" + "FX\\" + "maya\\" + "cache\\" + mf + "\\" + "vdb"
#print cachePath

def createCacheFolder():
    if os.path.exists(cachePath) == False:
       os.makedirs(cachePath)

def createShotFolder():
    if os.path.exists(shotPath) == False:
       os.makedirs(shotPath)

def createnCacheFolder():
    if os.path.exists(nCachePath) == False:
       os.makedirs(nCachePath)
       
def creatersProxyFolder():
    if os.path.exists(rsProxyPath) == False:
       os.makedirs(rsProxyPath)

def createvdbFolder():
    if os.path.exists(vdbPath) == False:
       os.makedirs(vdbPath)

doCreateFld = None

if os.path.exists(shotPath) == False:
    
    doCreateFld = mc.confirmDialog(title='Confirm', 
                     message='A folder (or folders) will be created to make the following path\n\n%s\n\nAre you sure you want to do this?' %cachePath, 
                     button=['Yes','No'], 
                     defaultButton='Yes', 
                     cancelButton='No', 
                     dismissString='No',
                     icn="warning")
                 
if doCreateFld == "Yes":
    createCacheFolder()
    print "Result: " + cachePath,
    if os.path.exists(shotPath) == False:
        doCreateFld = mc.confirmDialog(title='Confirm', 
                     message='A folder (or folders) will be created to make the following path\n\n%s\n\nAre you sure you want to do this?' %shotPath, 
                     button=['Yes','No'], 
                     defaultButton='Yes', 
                     cancelButton='No', 
                     dismissString='No',
                     icn="warning")
    if doCreateFld == "Yes":
        createShotFolder()
        
        print "Result: " + shotPath,
    if os.path.exists(nCachePath) == False:
        createnCacheFolder()
        print "Result: " + nCachePath,
    if os.path.exists(rsProxyPath) == False:
        creatersProxyFolder()
        print "Result: " + rsProxyPath,
    if os.path.exists(vdbPath) == False:
        createvdbFolder()
        print "Result: " + vdbPath, 
elif doCreateFld == "No":
    mc.warning("Action cancelled by user")
elif doCreateFld == None:
    mc.warning("The folder already exisited here: %s" %shotPath)
  