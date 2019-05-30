import maya.cmds as cmds
import maya.mel as mel
import xgenm as xg
import rfm.passes

import rmAssetDB_cmd as dbcmds
reload(dbcmds)
import rmAssetNode_cmds
reload(rmAssetNode_cmds)
import rmAnimationTools as rmAT
reload(rmAT)
import rmAssetDB_cmd as ass_cmds
reload(ass_cmds)

import rlf_utils
import buildWorkDirectory as bWD
import gdata.docs.service
import gdata.spreadsheet.service

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

import httplib2

import xml.etree.ElementTree as ET

import _XgExternalAPI

import os
import shutil

import shelfTools as st





  
def testVis(set):
    assetVis = True
    if ':' in set:
        digit = ''
        setNamespace = set.split(':')[0]
        print setNamespace
        iRange = range(len(setNamespace))
        #print iRange
        for i in iRange:
            if setNamespace[i].isdigit():
                digit = digit + setNamespace[i]
        assetName = setNamespace + 'Asset'
        if len(digit) != 0: 
            assetName = setNamespace[:len(digit) * -1] + 'Asset' + digit
            
        assetVis = cmds.getAttr(assetName + '.visibility')
        print "\033[32;1mStatus:\033[0m Visibility tested on :"+assetName+ ":" +str(assetVis)+ "\r\n"
    return assetVis
        

def resetAttr(transform):
    cmds.setAttr(transform + '.tx', 0)
    cmds.setAttr(transform + '.ty', 0)
    cmds.setAttr(transform + '.tz', 0)
    cmds.setAttr(transform + '.rx', 0)
    cmds.setAttr(transform + '.ry', 0)
    cmds.setAttr(transform + '.rz', 0)
    cmds.setAttr(transform + '.scaleX', 1)
    cmds.setAttr(transform + '.scaleY', 1)
    cmds.setAttr(transform + '.scaleZ', 1)
        

def cleanChar(preChar):
    newchar = ''
    for char in preChar:
        if not char.isdigit():
            newchar += char
    return newchar
    
def isCharacterwithHair(char):
    tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
    root = tree.getroot()
    characters = []
    for character in root.findall('character'):
        hasHair = character.find('hasHair').text
        if int(hasHair):
            characters.append(character.get('name'))
    if char in characters:
        return True
    else:
        return False

    
def isCharacter(char):
    tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
    root = tree.getroot()
    characters = []
    for character in root.findall('character'):
        characters.append(character.get('name'))
    if cleanChar(char) in characters:
        print 'Character: ' + char
        return True
    else:
        return False

def envLookup(environment):
    tree = ET.parse('/job/silly_seasons/common/etc/environments.xml')
    root = tree.getroot()
    env = root.find('.//*[@name="' + environment.strip() + '"]/..')
    return env.get('name')

        
def listCharacters():
    groups = cmds.ls('*_GRP', type='transform')
    chars = []
    for item in groups:
        if isCharacter(item.replace('_GRP','')):
            chars.append(item.replace('_GRP',''))
    return chars

def listCharactersDisk():
    version = 0
    chars = []
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    if show == "" or cat == "" or seq == "" or shot == "":
        cmds.error("Please make sure your shot env is set correctly!");
    path = '/job/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/assets/alembic/'
    if version == 0:
        versionList = cmds.getFileList(folder=path, filespec='v*')
        if versionList != None:
            for ver in versionList:
                tmpVer = int(ver[2:4])
                if tmpVer > version:
                    version = tmpVer
    path = '%sv%03d/'%(path,version) 
    print path
    alembicFiles = cmds.getFileList(folder=path, filespec='*.abc')
    for alembicFile in alembicFiles:
        name = alembicFile.split('.')[0]
        if isCharacter(name):
            chars.append(name)
    return chars   
    
def getFrames():
    ep = os.getenv('EPISODE')
    shot = os.getenv('SHOT')
    epNum = int(ep.replace('ep',''))
    
    #doc_name = 'SS_EDIT_EP' + str(epNum)
    doc_name = 'RB_Edit_rb01'
  
    email = '101871047421-29849q8pr4j38oee12fcak6rmqu8olfn@developer.gserviceaccount.com'
    f = open('/job/common/etc/APIProject-c91280e31618.p12', 'rb')
    key = f.read()
    f.close()

    scope = 'https://spreadsheets.google.com/feeds'
    credentials = SignedJwtAssertionCredentials(email, key, scope)
    http = httplib2.Http()
    http = credentials.authorize(http)
    build('drive', 'v2', http=http)
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.additional_headers = {'Authorization': 'Bearer %s' % http.request.credentials.access_token}
    
    print 'Having a chat with google...'
    print 'from doc: ' + doc_name
    print 'for shot: ' + shot
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = doc_name
    q['title-exact'] = 'true'
    feed = client.GetSpreadsheetsFeed(query=q)
    spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    feed = client.GetWorksheetsFeed(spreadsheet_id)
    worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    rows = client.GetListFeed(spreadsheet_id, worksheet_id).entry
    for row in rows:
        for key in row.custom:
            if row.custom[key].text != None:
                if row.custom[key].text.lower() == shot:
                    #startFrame = int(row.custom['framein'].text.lower())
                    startFrame = int(row.custom['framein-8'].text.lower())
                    #endFrame = int(row.custom['frameout'].text.lower())
                    endFrame = int(row.custom['frameout8'].text.lower())
                print " %s: %s" % (key, row.custom[key].text.lower())
    print 'Retrieved from google:'
    print 'StartFrame: %d'% (startFrame)
    print 'EndFrame: %d'% (endFrame)
    print 'Done.'
    return [startFrame, endFrame]

def getEnv():
    ep = os.getenv('EPISODE')
    shot = os.getenv('SHOT')
    epNum = int(ep.replace('ep',''))
    
    #doc_name = 'SS_EDIT_EP' + str(epNum)
    doc_name = 'RB_Edit_rb01'
    print "\033[32;1mStatus:\033[0m Retrieving from Google Sheets: "+doc_name+ "\r\n"
    
    email = '101871047421-29849q8pr4j38oee12fcak6rmqu8olfn@developer.gserviceaccount.com'
    f = open('/job/common/etc/APIProject-c91280e31618.p12', 'rb')
    key = f.read()
    f.close()

    scope = 'https://spreadsheets.google.com/feeds'
    credentials = SignedJwtAssertionCredentials(email, key, scope)
    http = httplib2.Http()
    http = credentials.authorize(http)
    build('drive', 'v2', http=http)
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.additional_headers = {'Authorization': 'Bearer %s' % http.request.credentials.access_token}
    print 'Having a chat with google...'
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = doc_name
    q['title-exact'] = 'true'
    feed = client.GetSpreadsheetsFeed(query=q)
    spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    feed = client.GetWorksheetsFeed(spreadsheet_id)
    worksheet_id = feed.entry[0].id.text.rsplit('/',1)[1]

    rows = client.GetListFeed(spreadsheet_id, worksheet_id).entry
    for row in rows:
        for key in row.custom:
            if row.custom[key].text != None:
                if row.custom[key].text.lower() == shot:
                    location = row.custom['location'].text.lower()
            #    print " %s: %s" % (key, row.custom[key].text.lower())
    print 'Retrieved from google:'
    #print 'Environment: %s'% (location)
    #print 'Done.'
    print "\033[32;1mStatus:\033[0m Returned from Google Sheets: "+str(location)+ "\r\n"
    return location

def loadAnimation():
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    assetPath = '/' + show + '/tv/' + ep + '/' + seq + '/' + shot + '/assets'
    catID = 9
    assetName = 'Animation_finalAnimation'
    print "\033[32;1mStatus:\033[0m Loading Animation scene: "+assetPath+ "\r\n"
    db = dbcmds.connectAssetDB()
    dbExists = dbcmds.assetExists(db, assetPath, assetName, catID)
    if not dbExists:
        assetName = 'Animation_Final Animation'
        dbExists = dbcmds.assetExists(db, assetPath, assetName, catID)
    if not dbExists:
        assetName = 'Animation_FinalAnimation'
        dbExists = dbcmds.assetExists(db, assetPath, assetName, catID)
    if dbExists:
        assetID = dbcmds.get_assetID(db, catID, assetPath , assetName)
        version = dbcmds.get_latestVersion(db, assetID)
        versionData = dbcmds.get_versionData(db, assetID, version)
        #print versionData
        #print "\033[32;1mStatus:\033[0m Version Data: "+versionData+ "\r\n"
        scene = versionData[0][0]
        cmds.file(scene, open=True, force=True)
    else:
        print 'No final animation found!'
            
    dbcmds.closeAssetDB(db)

def preBakeChecks():
    rigs1 = cmds.ls('*_rigAsset')
    rigs2 = cmds.ls('*_rigAsset?')
    rigs = rigs1 + rigs2
    db = dbcmds.connectAssetDB()
    for rig in rigs:
        #if isCharacter(rig.split('_')[0]):
            #check if rig is up to date
            assetID = cmds.getAttr(rig + '.assetID')
            currentVersion =  cmds.getAttr(rig + '.version')
            latestVersion = dbcmds.get_latestVersion(db, assetID)
            versionID = dbcmds.get_versionID(db, assetID, latestVersion)
            #print versionID[0][0]
            print "\033[32;1mStatus:\033[0m Checking for latest rig on: "+rig+ "\r\n"
            if currentVersion < latestVersion:
                namespace = rig.replace('Asset','')
                #print namespace
                connectionList = rmAT.getAnimNodeConnections(namespace)
                rmAT.deleteConnections(connectionList)
                nodeList = cmds.ls(namespace + ":*")
                if len(nodeList) != 0:
                    cmds.lockNode(nodeList, lock=False)
                    cmds.delete(nodeList)
                results = ass_cmds.get_data(db, versionID[0][0])
                assetResults = ass_cmds.get_assetListFromID(db, results[1])
                category = ass_cmds.get_categoryFromID(db, assetResults[0][1])
                rmAssetNode_cmds.updateAssetNode(rig, assetResults[0][0], results[0], assetResults[0][2], category, assetResults[0][3], assetResults[0][4], results[3], results[2], False )
                cmds.file(results[3], force=True, i=True, ns=namespace, mnc=True)
                rootNodes = cmds.ls("|" + namespace + ":*", tr=True)
                cmds.parent(rootNodes, rig, relative=True)
                rmAT.reconnect(connectionList)
    models = cmds.ls('*_modelAsset')
    for model in models:
        assetID = cmds.getAttr(model + '.assetID')
        currentVersion =  cmds.getAttr(model + '.version')
        latestVersion = dbcmds.get_latestVersion(db, assetID)
        versionID = dbcmds.get_versionID(db, assetID, latestVersion)
        #print versionID[0][0]
        print "\033[32;1mStatus:\033[0m Checking for latest model on: "+model+ "\r\n"
        if currentVersion < latestVersion:
            namespace = model.replace('Asset','')
            nodeList = cmds.ls(namespace + ":*")
            if len(nodeList) != 0:
                cmds.lockNode(nodeList, lock=False)
                cmds.delete(nodeList)
            results = ass_cmds.get_data(db, versionID[0][0])
            assetResults = ass_cmds.get_assetListFromID(db, results[1])
            category = ass_cmds.get_categoryFromID(db, assetResults[0][1])
            rmAssetNode_cmds.updateAssetNode(model, assetResults[0][0], results[0], assetResults[0][2], category, assetResults[0][3], assetResults[0][4], results[3], results[2], False )
            cmds.file(results[3], force=True, i=True, ns=namespace, mnc=True)
            rootNodes = cmds.ls("|" + namespace + ":*", tr=True)
            cmds.parent(rootNodes, model, relative=True)
    dbcmds.closeAssetDB(db)              
    setList = cmds.ls(type='objectSet')
    for set in setList:
        if 'geo_set' in set.lower():
            #print 'Checking ' + set + ' for duplicates.'
            print "\033[32;1mStatus:\033[0m Checking: "+set+"for duplicates..." "\r\n"
            geom = cmds.sets(set, q=True)
            iterate = range(0,len(geom) - 1)
            for j in iterate:
                for i in iterate:
                    if geom[j].split(':')[-1] == geom[i].split(':')[-1] and j != i:
                        #print 'Duplicate geometry found. ' + geom[j].split(':')[-1] + '==' + geom[i].split(':')[-1]
                        #print "\033[31;1mWarning:\033[0m Duplicate geometry found on :"+j+ "\r\n"
                        namespace = geom[i].split(':')[0]
                        cmds.namespace( set=namespace )
                        geom[i] = cmds.rename(geom[i], geom[i] + str(i) + str(j))
                        cmds.namespace( set=':' )
                        #geom[i] = geom[i] + str(i) + str(j)
                        #print 'New name: ' + geom[i]
            
def bakeAnimation():
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    if show == "" or cat == "" or seq == "" or shot == "":
        cmds.error("Please make sure your shot env is set correctly!");
    path = '/job/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/assets/'
    if not os.path.exists( path + 'alembic'):
        print 'Creating: ' +   path + 'alembic'
        cmds.sysFile(path + 'alembic', makeDir=True)
    version = 0
    versionList = cmds.getFileList(folder=path + 'alembic/', filespec='v*')
    if versionList != None:
        for ver in versionList:
            tmpVer = int(ver[2:4])
            if tmpVer > version:
                version = tmpVer
    cmds.sysFile(('%salembic/v%03d')%(path,version+1) , makeDir=True)         
    path = '%salembic/v%03d'%(path,version+1) 
    #print path
    print "\033[32;1mStatus:\033[0m Alembic bake path :"+path+ "\r\n"
    frameRange = getFrames()  
    startFrame = frameRange[0]
    print "\033[32;1mStatus:\033[0m Start Frame :"+str(startFrame)+ "\r\n"
    endFrame = frameRange[1]
    print "\033[32;1mStatus:\033[0m End Frame :"+str(endFrame)+ "\r\n"
    setList = cmds.ls(type='objectSet')
    bakes = []
    alembicList = {}
    for set in setList:
        if 'geo_set' in set.lower():
            if testVis(set):
                if '_rig' in set.lower():
                    bakes.append(set.replace('_rig', '').split(':')[len(set.split(':')) -2])
                    alembicList[set.replace('_rig', '').split(':')[len(set.split(':')) -2]] = set
                if '_model' in set.lower():
                    bakes.append(set.replace('_model', '').split(':')[len(set.split(':')) -2])
                    alembicList[set.replace('_model', '').split(':')[len(set.split(':')) -2]] = set
    print "\033[32;1mStatus:\033[0m Geometry that will bake to Alembic :"+str(bakes)+ "\r\n"
    for bake in bakes:
        cmds.select(alembicList[bake])
        geom = cmds.ls(sl=True, l=True)
        #print geom
        cmd = '-frameRange ' + str(startFrame) + ' ' + str(endFrame) + ' -uv -ws -wv -dataFormat ogawa '
        for geo in geom:
            cmd = cmd + '-root ' + geo + ' '
        cmd = cmd + '-file ' + path + '/' + bake + '.abc'
        #print cmd
        cmds.AbcExport(j=cmd)  
        print "\033[32;1mStatus:\033[0m Baking :"+str(bake)+ "\r\n"
        #cmds.AbcExport(j='-frameRange ' + str(startFrame) + ' ' + str(endFrame) + ' -sl -uv -ws -wv -file ' + path + '/' + bake + '.abc')


def addAttributes(nodes):
    for node in nodes:
	print "\033[32;1mStatus:\033[0m Adding Subdiv Scheme to: "+str(node)+ "\r\n"
        shape = cmds.listRelatives(node, s=True)
        mel.eval('rmanAddAttr ' + shape[0] + ' "rman__torattr___subdivScheme" "";')
        if 'Eyeball' in shape[0]:
             mel.eval('rmanAddAttr ' + shape[0] + ' "rman__torattr___subdivFacevaryingInterp" "";')

def loadAlembic(version=0):    
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    startFrame = 1
    endFrame = 24
    if show == "" or cat == "" or seq == "" or shot == "":
        cmds.error("Please make sure your shot env is set correctly!");
    path = '/job/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/assets/alembic/'
    if version == 0:
        versionList = cmds.getFileList(folder=path, filespec='v*')
        if versionList != None:
            for ver in versionList:
                tmpVer = int(ver[2:4])
                if tmpVer > version:
                    version = tmpVer
    path = '%sv%03d/'%(path,version) 
    #print path
    print "\033[32;1mStatus:\033[0m Alembic path: "+path+ "\r\n"
    alembicFiles = cmds.getFileList(folder=path, filespec='*.abc')
    


    for alembicFile in alembicFiles:
        name = alembicFile.split('.')[0]
        #print 'Importing: ' + name
        print "\033[32;1mStatus:\033[0m Importing: "+name+ "\r\n"
        cmds.group(name=name + '_GRP', em=True, w=True)
        cmds.namespace( add=name )
        cmds.AbcImport(path + alembicFile, ftr=True, rpr=name + '_GRP')
        nodes = cmds.listRelatives(name + '_GRP')
        for node in nodes:
            cmds.rename(node, name + ':' + node)
        nodes = cmds.listRelatives(name + '_GRP')
        addAttributes(nodes)
        if isCharacter(name):
	    print "\033[32;1mStatus:\033[0m Adding to SSS set for: "+name+ "\r\n"
            if cmds.objExists(name + ':Body_GEO_Alembic') and cmds.objExists(name + ':Head_GEO'):
                if cmds.objExists(cleanChar(name) + ':sss_SET'):
                    cmds.sets(name + ':Body_GEO_Alembic', name + ':Head_GEO', include=cleanChar(name) + ':sss_SET')
                else:
                    if not cmds.namespace(ex=cleanChar(name)):
                        cmds.namespace(add=cleanChar(name))
                    set = cmds.sets(name + ':Body_GEO_Alembic', name + ':Head_GEO', n=cleanChar(name) + ':sss_SET')
                    mel.eval('rmanAddAttr ' + set + ' "rman__torattr___traceSet" "1";')
            elif cmds.objExists(name + ':Body_GEO') and cmds.objExists(name + ':Head_GEO'):
                if cmds.objExists(cleanChar(name) + ':sss_SET'):
                    cmds.sets(name + ':Body_GEO', name + ':Head_GEO', include=cleanChar(name) + ':sss_SET')
                else:
                    if not cmds.namespace(ex=cleanChar(name)):
                        cmds.namespace(add=cleanChar(name))
                    set = cmds.sets(name + ':Body_GEO', name + ':Head_GEO', n=cleanChar(name) + ':sss_SET')
                    mel.eval('rmanAddAttr ' + set + ' "rman__torattr___traceSet" "1";')
            elif cmds.objExists(name + ':Body_GEO'):
                if cmds.objExists(cleanChar(name) + ':sss_SET'):
                    cmds.sets(name + ':Body_GEO', include=cleanChar(name) + ':sss_SET')
                else:
                    if not cmds.namespace(ex=cleanChar(name)):
                        cmds.namespace(add=cleanChar(name))
                    set = cmds.sets(name + ':Body_GEO', n=cleanChar(name) + ':sss_SET')
                    mel.eval('rmanAddAttr ' + set + ' "rman__torattr___traceSet" "1";') 
            elif cmds.objExists(name + ':Head_GEO'):
                if cmds.objExists(cleanChar(name) + ':sss_SET'):
                    cmds.sets(name + ':Head_GEO', include=cleanChar(name) + ':sss_SET')
                else:
                    if not cmds.namespace(ex=cleanChar(name)):
                        cmds.namespace(add=cleanChar(name))
                    set = cmds.sets(name + ':Head_GEO', n=cleanChar(name) + ':sss_SET')
                    mel.eval('rmanAddAttr ' + set + ' "rman__torattr___traceSet" "1";')
            elif cmds.objExists(name + ':Tail_GEO_Alembic') and cmds.objExists(name + ':Face_GEO_Alembic'):
                if cmds.objExists(cleanChar(name) + ':sss_SET'):
                    cmds.sets(name + ':Tail_GEO_Alembic', name + ':Face_GEO_Alembic', include=cleanChar(name) + ':sss_SET')
                else:
                    if not cmds.namespace(ex=cleanChar(name)):
                        cmds.namespace(add=cleanChar(name))
                    set = cmds.sets(name + ':Tail_GEO_Alembic', name + ':Face_GEO_Alembic', n=cleanChar(name) + ':sss_SET')
                    mel.eval('rmanAddAttr ' + set + ' "rman__torattr___traceSet" "1";')
        if isCharacter(name):
            cleanName = cleanChar(name)
            db = dbcmds.connectAssetDB()
            tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
            root = tree.getroot()
            lightrig = root.find('.//*[@name="' + cleanName + '"]/lightrig')
            charID = dbcmds.get_assetID(db, 3, '/' + show + '/assets' , 'lighting_' + lightrig.get('name'))
            if charID != 0:
                charVersion = dbcmds.get_latestVersion(db, charID)
                #print charVersion
                charVersionID = dbcmds.get_versionID(db, charID, charVersion)
                #print charVersionID
                assetName = rmAssetNode_cmds.createNewAsset(charVersionID[0][0], reference = False)
                #print assetName
            dbcmds.closeAssetDB(db)
            if cmds.objExists(assetName):
                cmds.parent(assetName, name + '_GRP')
            else:
                cmds.parent(assetName, name + '_GRP')
            attachLights(name,assetName) 

    #Set Playback Range from Edit Sheet
    frameRange = getFrames()  
    startFrame = frameRange[0]
    print "\033[32;1mStatus:\033[0m Start Frame :"+str(startFrame)+ "\r\n"
    endFrame = frameRange[1]
    print "\033[32;1mStatus:\033[0m End Frame :"+str(endFrame)+ "\r\n"
    cmds.playbackOptions( minTime=startFrame, maxTime=endFrame )


	
	

def loadRenderCamera():
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    if show == "" or cat == "" or seq == "" or shot == "":
        cmds.error("Please make sure your shot env is set correctly!");
    db = dbcmds.connectAssetDB()
    cameraID = dbcmds.get_assetID(db, 8, '/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/assets' , 'camera_renderCamera')
    #print cameraID
    if cameraID != 0:
	print "\033[32;1mStatus:\033[0m Loading Render Camera" "\r\n"
        cameraVersion = dbcmds.get_latestVersion(db, cameraID)
        #print charVersion
        cameraVersionID = dbcmds.get_versionID(db, cameraID, cameraVersion)
        #print charVersionID
        rmAssetNode_cmds.createNewAsset(cameraVersionID[0][0], reference = False)
    dbcmds.closeAssetDB(db)
    
def loadHair():
    tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
    root = tree.getroot()
    characters = listCharacters()
    for char in characters:
        if isCharacterwithHair(char):
	    print "\033[32;1mStatus:\033[0m Loading hair for: "+char+ "\r\n"
            #print 'Loading hair for.... ' + char
            for xgenfiles in root.findall('.//*[@name="' + char + '"]/xgen'):
                xg.importPalette('/job/silly_seasons/assets/hair/xgen/' + xgenfiles.get('name'), '', nameSpace=str(char))

    
def loadPalettes():
    show = os.getenv('SHOW')
    tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
    root = tree.getroot()
    db = dbcmds.connectAssetDB()
    characters = listCharactersDisk()
    for char in characters:
	print "\033[32;1mStatus:\033[0m Fetching shader palette for "+char+ "\r\n"
        paletteName = root.find('.//*[@name="' + cleanChar(char) + '"]/palette')
        if not cmds.objExists(paletteName.get('name') + '_paletteAsset'):
            charID = dbcmds.get_assetID(db, 7, '/' + show + '/assets', 'characters_' + paletteName.get('name'))
            if charID != 0:
                charVersion = dbcmds.get_latestVersion(db, charID)
                #print charVersion
                charVersionID = dbcmds.get_versionID(db, charID, charVersion)
                #print charVersionID
                rmAssetNode_cmds.createNewAsset(charVersionID[0][0], reference = False)
                print "\033[32;1mStatus:\033[0m Loaded shader palette for "+char+ "\r\n"
    dbcmds.closeAssetDB(db)

def attachLights(character, assetName):
    print "\033[32;1mStatus:\033[0m Attaching lights to: "+str(character)+ "\r\n"
    tree = ET.parse('/job/silly_seasons/common/etc/characters.xml')
    root = tree.getroot()
    faceGeo = root.find('.//*[@name="' + cleanChar(character) + '"]/faceLights')
    bodyGeo = root.find('.//*[@name="' + cleanChar(character) + '"]/bodyLights')
    cmds.connectAttr(character + ':' + faceGeo.get('name') + '.outMesh', assetName.replace('Asset','') + ':faceLight_FLCShape.inputMesh',f=True)
    cmds.connectAttr(character + ':' + faceGeo.get('name') + '.worldMatrix[0]', assetName.replace('Asset','') + ':faceLight_FLCShape.inputWorldMatrix', f=True)
    cmds.connectAttr(character + ':' + bodyGeo.get('name') + '.outMesh', assetName.replace('Asset','') + ':charLight_FLCShape.inputMesh',f=True)
    cmds.connectAttr(character + ':' + bodyGeo.get('name') + '.worldMatrix[0]', assetName.replace('Asset','') + ':charLight_FLCShape.inputWorldMatrix', f=True)
    

def updatePaletteRules():
    palettes = cmds.ls(type='palette')
    rlf_utils.clearRules()
    rlf_utils.updateRules(palettes)

def rulesClean():
    partitions = cmds.ls(type='partition')
    keep = {'mtorPartition', 'characterPartition', 'renderPartition'}
    print "\033[32;1mStatus:\033[0m Cleaning Rules" "\r\n"
    for partition in partitions:
        if partition not in keep:
            cmds.delete(partition)

def reloadFix():
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    user = os.getenv('USER')
    projectPath = '/job/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/work/' + user + '/maya/'
    #print('Project path: ' + projectPath)
    print "\033[32;1mStatus:\033[0m Project path:" + projectPath+ "\r\n"
    if not os.path.exists(projectPath):
        bWD.buildWorkDirectory()
    mel.eval('setProject("' + projectPath + '");')
    cmds.file(rename=shot + '_lighting_newBuild.mb')
    cmds.file( save=True, force=True)
    mel.eval('putenv "RMSPROJ" "' + projectPath + '";')
    cmds.file( shot + '_lighting_newBuild.mb', open=True )
            
def setRenderer():
    print "\033[32;1mStatus:\033[0m Setting Renderer" "\r\n"
    mel.eval('setCurrentRenderer("renderMan");')

def defaultSettings():
    print "\033[32;1mStatus:\033[0m Adding Render Global settings" "\r\n"
    cmds.setAttr("frontShape.renderable", 0)
    cmds.setAttr("perspShape.renderable", 0)
    cmds.setAttr("sideShape.renderable", 0)
    cmds.setAttr("topShape.renderable", 0)
    cmds.setAttr("defaultRenderGlobals.animation", 1)
    cmds.setAttr('renderCamera_camera:renderCameraShape.renderable', 1)
    cmds.setAttr('renderCamera_camera:renderCameraShape.nearClipPlane', 0.1)
    cmds.setAttr('renderCamera_camera:renderCameraShape.farClipPlane', 100000000)
    cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 1)
    cmds.setAttr('defaultRenderGlobals.imageFormat', 51)
    cmds.setAttr('defaultRenderGlobals.imfPluginKey','exr', type='string')
    cmds.setAttr('defaultResolution.width', 1920)
    cmds.setAttr('defaultResolution.height', 1080)
    cmds.setAttr('renderManGlobals.rman__riopt__Format_resolution0', 1920)
    cmds.setAttr('renderManGlobals.rman__riopt__Format_resolution1', 1080)
    cmds.setAttr('defaultResolution.deviceAspectRatio', 1.777)
    startFrame = cmds.playbackOptions(q=True, minTime=True)
    cmds.setAttr("defaultRenderGlobals.startFrame", startFrame)
    endFrame = cmds.playbackOptions(q=True, maxTime=True)
    cmds.setAttr("defaultRenderGlobals.endFrame", endFrame)
    
    cmds.setAttr("renderManGlobals.rman__toropt___shaderCleanupJob", 1)
    cmds.setAttr("renderManGlobals.rman__toropt___renderDataCleanupJob", 1)
    cmds.setAttr("renderManGlobals.rman__toropt___textureCleanupJob", 1)
    cmds.setAttr("renderManGlobals.rman__toropt___ribCleanupJob", 1)
    
    cmds.setAttr('renderManGlobals.rman__riopt__statistics_xmlfilename', '[file join $RMSPROJ [AssetRef -cls rmanstat]]', type='string')
    #cmds.setAttr('defaultRenderGlobals.preRenderMel', '', type='string')
    cmds.setAttr('defaultRenderGlobals.postRenderMel', '', type='string')

    #cmds.setAttr("renderManGlobals.rman__riattr__trace_bias", 0.01)
    #cmds.setAttr("renderManGlobals.rman__riattr___ShadingRate", 3)
    #cmds.setAttr("renderManGlobals.rman__riopt__shading_directlightingsamples", 400)
    #cmds.setAttr("renderManGlobals.rman__riattr___ShadingRate", 3)
    #cmds.setAttr("renderManGlobals.rman__riopt__shading_directlightingsamples", 500)
    cmds.setAttr("renderManGlobals.rman__riattr___ShadingRate", 2)
    cmds.setAttr("renderManGlobals.rman__riopt__shading_directlightingsamples", 600)

    cmds.setAttr("renderManGlobals.rman__riopt___PixelSamples0", 5)
    cmds.setAttr("renderManGlobals.rman__riopt___PixelSamples1", 5)
    cmds.setAttr("rmanFinalOutputGlobals0.rman__riopt__Display_filterwidth0", 3)
    cmds.setAttr("rmanFinalOutputGlobals0.rman__riopt__Display_filterwidth1", 3)
    #cmds.setAttr("renderManGlobals.rman__toropt___renderDataCleanupFrame", 1)
    cmds.setAttr("renderManGlobals.rman__riopt__hair_minwidth", 1)               
                      
       
def loadEnv():
    show = os.getenv('SHOW')
    env = getEnv()
    #print 'test2:' + env
    tree = ET.parse('/job/silly_seasons/common/etc/environments.xml')
    root = tree.getroot()
    envAsset = envLookup(env)
    db = dbcmds.connectAssetDB()
    #print 'sets_' + envAsset
    print "\033[32;1mStatus:\033[0m Loading environment: "+str(envAsset)+ "\r\n"
    setID = dbcmds.get_assetID(db, 2,  '/' + show + '/assets' , 'sets_' + envAsset)
    if setID != 0:
        setVersion = dbcmds.get_latestVersion(db, setID)
        setVersionID = dbcmds.get_versionID(db, setID, setVersion)
        rmAssetNode_cmds.createNewAsset(setVersionID[0][0], reference = False)
    palette = root.find('.//*[@name="' + envAsset + '"]/palette')
    #print palette
    print "\033[32;1mStatus:\033[0m Loading environment palette: "+palette.get('name')+ "\r\n"
    paletteID = dbcmds.get_assetID(db, 7, '/' + show + '/assets', 'env_' + palette.get('name'))
    if paletteID != 0:
        paletteVersion = dbcmds.get_latestVersion(db, paletteID)
        paletteVersionID = dbcmds.get_versionID(db, paletteID, paletteVersion)
        rmAssetNode_cmds.createNewAsset(paletteVersionID[0][0], reference = False)  
    lightrig = root.find('.//*[@name="' + envAsset + '"]/lightrig')
    lightsID = dbcmds.get_assetID(db, 3, '/' + show + '/assets' , 'lighting_' + lightrig.get('name'))
    print "\033[32;1mStatus:\033[0m Loading environment light rig: "+ lightrig.get('name')+ "\r\n"
    if lightsID != 0:
        lightsVersion = dbcmds.get_latestVersion(db, lightsID)
        lightsVersionID = dbcmds.get_versionID(db, lightsID, lightsVersion)
        rmAssetNode_cmds.createNewAsset(lightsVersionID[0][0], reference = False)
    props = root.find('.//*[@name="' + envAsset + '"]/props')
    propsID = dbcmds.get_assetID(db, 7, '/' + show + '/assets' , 'props_' + props.get('name'))
    print "\033[32;1mStatus:\033[0m Loading environment props: "+props.get('name')+ "\r\n"
    if propsID != 0:
        propsVersion = dbcmds.get_latestVersion(db, propsID)
        propsVersionID = dbcmds.get_versionID(db, propsID, propsVersion)
        rmAssetNode_cmds.createNewAsset(propsVersionID[0][0], reference = False)
    dbcmds.closeAssetDB(db)
    if envAsset == 'Sillytown':
        #print 'Doing origin fix:'
        print "\033[32;1mStatus:\033[0m Creating environment Origin Fix for: "+envAsset+ "\r\n"
        chars = listCharacters()
        locator = cmds.spaceLocator(n='fix_LOC')
        cmds.parent(locator[0], 'renderCamera_camera:renderCamera')
        resetAttr(locator[0])
        cmds.parent(locator[0], w=True)
        x = cmds.getAttr(locator[0] + '.tx')
        z = cmds.getAttr(locator[0] + '.tz')
        cmds.delete(locator[0])
        assets = cmds.ls('|*_GRP')
        assets += cmds.ls('|*_cameraAsset')
        assets += cmds.ls('|*_rigAsset')
        assets += cmds.ls('|*_modelAsset')
        cmds.group(assets, n='originFix')
        cmds.setAttr('originFix.tx', (x* -1))
        cmds.setAttr('originFix.tz', (z* -1))
        for char in chars:
            lightrig = cmds.ls('|originFix|' + char + '_GRP|*', type='rmAsset')
            cmds.parent(lightrig[0], w=True)
            resetAttr(lightrig[0])
        print 'done.'
	
    if envAsset == 'Desert':
        print "\033[32;1mStatus:\033[0m Creating environment Origin Fix for: "+envAsset+ "\r\n"
        chars = listCharacters()
        locator = cmds.spaceLocator(n='fix_LOC')
        cmds.parent(locator[0], 'renderCamera_camera:renderCamera')
        resetAttr(locator[0])
        cmds.parent(locator[0], w=True)
        x = cmds.getAttr(locator[0] + '.tx')
        z = cmds.getAttr(locator[0] + '.tz')
        cmds.delete(locator[0])
        assets = cmds.ls('|*_GRP')
        assets += cmds.ls('|*_cameraAsset')
        assets += cmds.ls('|*_rigAsset')
        assets += cmds.ls('|*_modelAsset')
        cmds.group(assets, n='originFix')
        cmds.setAttr('originFix.tx', (x* -1))
        cmds.setAttr('originFix.tz', (z* -1))
        for char in chars:
            lightrig = cmds.ls('|originFix|' + char + '_GRP|*', type='rmAsset')
            cmds.parent(lightrig[0], w=True)
            resetAttr(lightrig[0])
        print 'done.'

    if envAsset == 'UnicornSchoolOfMagic_ext':
        print "\033[32;1mStatus:\033[0m Creating environment Origin Fix for: "+envAsset+ "\r\n"
        chars = listCharacters()
        locator = cmds.spaceLocator(n='fix_LOC')
        cmds.parent(locator[0], 'renderCamera_camera:renderCamera')
        resetAttr(locator[0])
        cmds.parent(locator[0], w=True)
        x = cmds.getAttr(locator[0] + '.tx')
        z = cmds.getAttr(locator[0] + '.tz')
        cmds.delete(locator[0])
        assets = cmds.ls('|*_GRP')
        assets += cmds.ls('|*_cameraAsset')
        assets += cmds.ls('|*_rigAsset')
        assets += cmds.ls('|*_modelAsset')
        cmds.group(assets, n='originFix')
        cmds.setAttr('originFix.tx', (x* -1))
        cmds.setAttr('originFix.tz', (z* -1))
        for char in chars:
            lightrig = cmds.ls('|originFix|' + char + '_GRP|*', type='rmAsset')
            cmds.parent(lightrig[0], w=True)
            resetAttr(lightrig[0])
        print 'done.'

	
    
def publish(passname):
    #scene lighting render
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    db = dbcmds.connectAssetDB()
    scene = ''
    assetPath = '/' + show + '/tv/' + ep + '/' + shot.split('_')[0] + '/' + shot + '/assets'
    catID = 9
    assetName = 'lighting_' + passname
    dbExists = dbcmds.assetExists(db, assetPath, assetName, catID)
    if not dbExists:
        dbcmds.add_asset(db, assetPath, assetName, 'Auto publish lighting for ' + shot, os.getenv('USER'), catID)
        
    DBPath = '/job' + assetPath + '/.assetDB'
    newAssetID = dbcmds.get_assetID(db, catID, assetPath, assetName)
    currentVersion = dbcmds.get_latestVersion(db, newAssetID)
    if currentVersion == None:
        currentVersion = 0
    currentVersion = currentVersion + 1
    newAssetPath = '/' + str(catID) + '/' + assetName.split('_')[0] + '/' + assetName.split('_')[-1] + '/' + str(currentVersion) + '/'
    filename = assetName + '_' + str(currentVersion) + '.mb'
    dirPath = DBPath + newAssetPath
    fullPath = DBPath + newAssetPath + filename
    if not os.path.exists(dirPath):
        cmds.sysFile(dirPath, makeDir=True)
    cmds.file(fullPath, force=True, type='mayaBinary', options='v=0;', preserveReferences=True, exportAll=True)
    dbcmds.add_Version(db, newAssetID, currentVersion , fullPath, os.getenv('USER'), 'Auto publish')    
    dbcmds.closeAssetDB(db)   
    path = '/job/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/work/' + os.getenv('USER') + '/maya/scenes/'   
    xgenFiles = cmds.getFileList(folder=path, filespec=shot + '_lighting_newBuild_*.xgen')
    xgenFiles = xgenFiles + cmds.getFileList(folder=path, filespec=shot + '_lighting_newBuild_*.abc')
    for file in xgenFiles:
        print file
        print path
        print dirPath
        shutil.copyfile(path + file, dirPath + file) 
        shutil.copyfile(path + file, dirPath + assetName + '_' + str(currentVersion) + file.replace(shot + '_lighting_newBuild',''))

def addAOVs():
    print "\033[32;1mStatus:\033[0m Adding AOVs" "\r\n"
    mel.eval('rmanCreateGlobals')
    # same issue here, we need to make sure it exists
    rfm.rmanPassEditor.createPassEditor()
    
    mel.eval('rmanAddAttr  "rmanFinalOutputGlobals0" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutputGlobals0" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "z";') 
    mel.eval('rmanAddAttr  "rmanFinalOutput1" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput1" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "Diffuse";')
    mel.eval('rmanAddAttr  "rmanFinalOutput2" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput2" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "DiffuseShadow";') 
    mel.eval('rmanAddAttr  "rmanFinalOutput3" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput3" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "Specular";')
    mel.eval('rmanAddAttr  "rmanFinalOutput4" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput4" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "SpecularShadow";') 
    mel.eval('rmanAddAttr  "rmanFinalOutput5" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput5" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "Incandescence";')
    mel.eval('rmanAddAttr  "rmanFinalOutput6" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput6" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "Subsurface";')
    mel.eval('rmanAddAttr  "rmanFinalOutput7" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput7" "rman__riopt__Display_exrpixeltype" "half";')

    mel.eval('rmanAddOutput rmanFinalGlobals "Refraction";')
    mel.eval('rmanAddAttr  "rmanFinalOutput8" "rman__riopt__Display_exrcompression" "zip";')
    mel.eval('rmanAddAttr  "rmanFinalOutput8" "rman__riopt__Display_exrpixeltype" "half";')


    AOVs = ['id1', 'id2', 'id3', 'id4']

    for aov in AOVs:
	rfg = mel.eval('rmanGetDefaultPass "Final"') 
	channel = mel.eval('rmanAddChannel("' + rfg + '", "color ' + aov + '", "", 0)')
	display = mel.eval('rmanAddDisplay("' + rfg + '","Secondary", "")')
	cmds.setAttr(display + '.rman__riopt__Display_mode', aov, type='string')
	mel.eval('rmanAddAttr ' +display+ '"rman__riopt__Display_exrcompression" "zip";')
	mel.eval('rmanAddAttr ' +display+ '"rman__riopt__Display_exrpixeltype" "half";')
    

def submitRender(passname, version=0):
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    user = os.getenv('USER')
    #load render pub
    if version == 0:
        db = dbcmds.connectAssetDB()
        sceneID = dbcmds.get_assetID(db, 9, '/' + show + '/' + cat + '/' + ep + '/' + seq + '/' + shot + '/assets' , 'lighting_' + passname)
        #print cameraID
        if sceneID != 0:
            sceneVersion = dbcmds.get_latestVersion(db, sceneID)
            #print charVersion
            #sceneVersionID = dbcmds.get_version(db, sceneID, sceneVersion)
            versionData = dbcmds.get_versionData(db, sceneID, sceneVersion)
            #print charVersionID
            print versionData[0][0]
            cmds.file(versionData[0][0] , open=True, force=True)
        dbcmds.closeAssetDB(db)
    else:
        pass
    #cmds.file( save=True, force=True)
    mel.eval('optionVar -sv "rmanAlfredEnvKey" "rms-19.0-maya-2015 prman-19.0 SHOW=' + show + ' CAT=' + cat + ' EPISODE=' + ep + ' SEQ=' + seq + ' SHOT=' + shot + ' USER=' + user + '";')
    mel.eval('optionVar -sv "rmanQueuingSystem" 1')
    mel.eval('renderManAlfredSpool("remote rib, remote render", 20, "")')

    
def loadCrowds():
    show = os.getenv('SHOW')
    cat = os.getenv('CAT')
    ep = os.getenv('EPISODE')
    seq = os.getenv('SEQ')
    shot = os.getenv('SHOT')
    assetPath = '/' + show + '/tv/' + ep + '/' + seq + '/' + shot + '/assets'
    catID = 9
    assetName = 'Animation_crowds'
    db = dbcmds.connectAssetDB()
    dbExists = dbcmds.assetExists(db, assetPath, assetName, catID)
    if dbExists:
	print "\033[32;1mStatus:\033[0m Loading crowds: "+assetPath+ "\r\n"
        assetID = dbcmds.get_assetID(db, catID, assetPath , assetName)
        assetVersion = dbcmds.get_latestVersion(db, assetID)
        assetVersionID = dbcmds.get_versionID(db, assetID, assetVersion)
        #print charVersionID
        rmAssetNode_cmds.createNewAsset(assetVersionID[0][0], reference = False)
        cmds.namespace(rm='crowds_scene',mnr=True)
        #cmds.setAttr('crowdProxyRMSShape.characterFiles','/job/silly_seasons/assets/Crowds/Character_Files_GCHA/Male_Flower_Pink.gcha;/job/silly_seasons/assets/Crowds/Character_Files_GCHA/Male_Flower_Orange.gcha;/job/silly_seasons/assets/Crowds/Character_Files_GCHA/Female_Flower_Pink.gcha;/job/silly_seasons/assets/Crowds/Character_Files_GCHA/Female_Flower_Orange.gcha', type='string')
        shaders = cmds.ls('*_Crowds_*SHR', type="RMSGPSurface")
        for shader in shaders:
            cmds.setAttr(shader + '.sssMix', 0, 0, 0, type='double3')
        startFrame = int(cmds.playbackOptions(q=True, ast = True))
        endFrame = int(cmds.playbackOptions(q=True, aet=True))
        for frame in range(startFrame, endFrame):
            cmds.currentTime(frame, edit=True)
            mel.eval('crowdProxyRendermanStudioEvalAttributes')
        cmds.setAttr('defaultRenderGlobals.preRenderMel', 'crowdProxyRendermanStudioEvalAttributes;', type='string') 
        cmds.setAttr('renderManGlobals.rman__torattr___defaultRiOptionsScript', 'crowdProxyRendermanStudioRiOptions;', type='string')
        fileNodes = cmds.ls('*_Crowds_*', type='file')
        for fileNode in fileNodes:
            texName = cmds.getAttr(fileNode + '.fileTextureName')
            if texName.split('.')[-1] == 'tif':
                texName = texName.replace('.tif','.tex')
                cmds.setAttr(fileNode + '.fileTextureName', texName, type='string')
    else:
        print "\033[31;1mWarning:\033[0m No crowds found!" "\r\n"
    dbcmds.closeAssetDB(db)

def bakeScene():
    loadAnimation()
    preBakeChecks()
    bakeAnimation()
    
def buildScene(pub=True,render=False, passname='btyRender'):
    setRenderer()
    loadPalettes()
    loadAlembic()
    loadHair()
    loadRenderCamera()
    loadEnv()
    loadCrowds()
    rulesClean()
    reloadFix()
    updatePaletteRules()
    addAOVs()
    defaultSettings()
    if pub == True:
        publish(passname)
    if render == True:
        submitRender(passname)
        
    st.getLatestRenderScene()

def test():
    defaultSettings()
    publish()
    submitRender()

#publish('btyRender')
#bakeAnimation()
#buildScene()
#test()

################################
#maya -batch -command "python(\"import lightingTools as lt\nlt.bakeScene()\")"
#maya -batch -command "python(\"import lightingTools as lt\nlt.buildScene()\")"
