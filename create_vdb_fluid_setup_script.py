#OpenVDB creation and setup tool

#Version:001

#Author: Derek Patterson

import maya.cmds as cmds
import maya.mel as mel

def vdbsetup():
    
    #This is creating the VDB Node Network
    
    vdbFromFluidNode = cmds.createNode('BE_VDBFromMayaFluid', n='VdbFromFluid1')
    vdbWriteNode = cmds.createNode('BE_VDBWrite', n='VdbWrite1')
    vdbVisualizeNode = cmds.createNode('BE_VDBVisualize', n='vdbVisualizeShape1')
    cmds.setAttr(vdbFromFluidNode + '.FluidNodeName', 'fluidShape1', type='string')
    cmds.connectAttr(vdbFromFluidNode + '.VdbOutput', vdbWriteNode + '.VdbInput', force=True)
    cmds.connectAttr(vdbWriteNode + '.VdbOutput', vdbVisualizeNode + '.VDBInput', force=True)
    
vdbsetup()