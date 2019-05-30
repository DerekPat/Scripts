# This script will add all the necessary AOV's and PuzzleMattes

import maya.cmds as mc
import maya.mel as mel

def createPuzzleMatteScene():
    mel.eval('rsCreateAov -type "Puzzle Matte" -name "rsAov_Scene_PuzzleMatte" ;')
    mel.eval("redshiftUpdateActiveAovList;")

    mc.setAttr("rsAov_Scene_PuzzleMatte.enabled", False)
    mc.setAttr("rsAov_Scene_PuzzleMatte.name", "char_ID", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte.filePrefix", "<BeautyPath>/<BeautyFile>_<RenderPass>", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte.mode", 1)
    mc.setAttr("rsAov_Scene_PuzzleMatte.redId", 101)
    mc.setAttr("rsAov_Scene_PuzzleMatte.greenId", 102)
    mc.setAttr("rsAov_Scene_PuzzleMatte.blueId", 103)

    mel.eval('rsCreateAov -type "Puzzle Matte" -name "rsAov_Scene_PuzzleMatte1" ;')
    mel.eval("redshiftUpdateActiveAovList;")

    mc.setAttr("rsAov_Scene_PuzzleMatte1.enabled", False)
    mc.setAttr("rsAov_Scene_PuzzleMatte1.name", "set_ID", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte1.filePrefix", "<BeautyPath>/<BeautyFile>_<RenderPass>", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte1.mode", 1)
    mc.setAttr("rsAov_Scene_PuzzleMatte1.redId", 201)
    mc.setAttr("rsAov_Scene_PuzzleMatte1.greenId", 202)
    mc.setAttr("rsAov_Scene_PuzzleMatte1.blueId", 203)

    mel.eval('rsCreateAov -type "Puzzle Matte" -name "rsAov_Scene_PuzzleMatte2" ;')
    mel.eval("redshiftUpdateActiveAovList;")

    mc.setAttr("rsAov_Scene_PuzzleMatte2.enabled", False)
    mc.setAttr("rsAov_Scene_PuzzleMatte2.name", "prop_ID", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte2.filePrefix", "<BeautyPath>/<BeautyFile>_<RenderPass>", typ="string")
    mc.setAttr("rsAov_Scene_PuzzleMatte2.mode", 1)
    mc.setAttr("rsAov_Scene_PuzzleMatte2.redId", 301)
    mc.setAttr("rsAov_Scene_PuzzleMatte2.greenId", 302)
    mc.setAttr("rsAov_Scene_PuzzleMatte2.blueId", 303)
    
def createPropObjIdSet():
    mel.eval('redshiftCreateObjectIdNode();')
    cmds.rename('rsObjectId1', 'prop_rsObjectId_301')
    mc.setAttr("prop_rsObjectId_301.objectId", 301)

    mel.eval('redshiftCreateObjectIdNode();')
    cmds.rename('rsObjectId1', 'prop_rsObjectId_302')
    mc.setAttr("prop_rsObjectId_302.objectId", 302)

    mel.eval('redshiftCreateObjectIdNode();')
    cmds.rename('rsObjectId1', 'prop_rsObjectId_303')
    mc.setAttr("prop_rsObjectId_303.objectId", 303)
    
createPuzzleMatteScene()
createPropObjIdSet()