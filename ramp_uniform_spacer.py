#This script will average out points on a ramp node

#rampUniformSpacer.py

import maya.cmds as cmds

def rampSpacer(rampName):
    
    keys = cmds.getAttr(rampName+'.colorEntryList', multiIndices=1)
    keyList = len(keys)
    spacing = 1. * 1/keyList

    for key in keys:
        keyNum = 1.*key
        mult = spacing*keyNum

        cmds.setAttr(rampName+'.colorEntryList['+str(key)+'].position', mult)
        
rampSpacer('ramp16')

