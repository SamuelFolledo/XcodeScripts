import os
import shutil
import subprocess
import sys
import zipfile

from enum import Enum
from os.path import abspath, expanduser


try:
    from subprocess import DEVNULL  # python3
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

# Custom Files
from mixamoToXcode import *
from Logger import *

#----------------------------------------------------------------------------------------------------------------
############################################### CUSTOMIZABLE SETTINGS ###########################################
#----------------------------------------------------------------------------------------------------------------
DELETE_TEXTURES = True #When True, it will delete animations with textures

#----------------------------------------------------------------------------------------------------------------
#################################################### Objects ####################################################
#----------------------------------------------------------------------------------------------------------------


#----------------------------------------------------------------------------------------------------------------
#################################################### Methods ####################################################
#----------------------------------------------------------------------------------------------------------------
def validateAndGetInput():
    """Validates inputs and returns the path to convert and new animation name"""
    if len(sys.argv) < 2:
        LOGE("Error Usage: python3 mixamoAnimToXcode.py <list_of_files> <optional_new_animation_name>")
        LOGW("Running this script requires 1-2 additional parameters")
        sys.exit(1)
    # Defaults to converting user's Downloads folder if path is not provided
    pathsToConvert = []
    newAnimationName = ""
    for (index, arg) in enumerate(sys.argv):
        if index == 0:
            continue
        isLastIndex = index == len(sys.argv) - 1
        if isLastIndex:
            if (isFolder(arg) or isFile(arg)) and exist(arg):
                pathsToConvert.append(arg)
            else:
                LOGD(f"New animation name is found: {arg}")
                newAnimationName = arg
        else:
            pathsToConvert.append(arg)
    LOGA(f"Converting paths: {pathsToConvert} and optionally renaming zip file to {newAnimationName}")
    return pathsToConvert, newAnimationName

def prepareDaeAnimation(daePath, newAnimationName):
    """Unzips daePath and returns the unzipped dae file's path"""
    if not getExtensionFromPath(daePath) == ".zip":
        LOGE(f"Failed to unzip path: {daePath}")
    destinationPath = unzipFile(daePath, isAnimation=True)
    folderName = getFolderFromPath(daePath)
    isNewNameEmpty = len(newAnimationName) == 0
    zipName = getNameFromPath(daePath)
    daeName = zipName if isNewNameEmpty else newAnimationName
    unzippedDaePath = f"{destinationPath}/{zipName}.dae"
    # LOG(f"DATA are {destinationPath}\t{newAnimationName}={zipName}={daeName} ISSS {unzippedDaePath}")
    if zipName != daeName:
        #Rename animation name
        tempPath = f"{destinationPath}/{daeName}.dae"
        LOG(f"Renaming .dae file from {unzippedDaePath} to a custom name: {tempPath}")
        moveFile(unzippedDaePath, tempPath)
        unzippedDaePath = tempPath
    elif not exist(unzippedDaePath):
        #It will go here if zip file was renamed. It does not work due to extracting 
        #Fix by updating unzippedDaePath to the first .dae found
        LOG(f"Looking for dae in {destinationPath} becase {zipName}=={daeName}")
        for root, dirs, files in os.walk(destinationPath):
            for file in files:
                filePath = os.path.join(root, file)
                if getExtensionFromPath(filePath) == ".dae":
                    # unzippedDaePath = filePath
                    LOGD(f"Found the animation file at {filePath} and renaming to {unzippedDaePath}")
                    moveFile(filePath, unzippedDaePath)
                    break
            break

    if not exist(unzippedDaePath):
        LOGE(f"Missing dae file {unzippedDaePath} from {daePath}")
        sys.exit(1)
    #Handle animations with textures
    LOGA(f"Unzipped .dae file has textures for {unzippedDaePath}. Deleting unneeded texture files = {DELETE_TEXTURES}")
    if DELETE_TEXTURES:
        # Move .dae file to the parent folder and delete the folder
        finalDaePath = f"{folderName}/{daeName}.dae"
        moveFile(unzippedDaePath, finalDaePath)
        # Delete unneeded folder and zip file
        deleteAllFromPath(f"{folderName}/{zipName}")
        deleteAllFromPath(f"{folderName}/{zipName}.zip")
        LOGD(f"Finished moving unzipped .dae from {unzippedDaePath} into {finalDaePath} and deleted unneeded files")
        unzippedDaePath = finalDaePath            
    executeConvertToXcodeColladaWorkflow(unzippedDaePath)
    LOG(f"Finished preparing dae animations from {daePath} into {unzippedDaePath}")
    return unzippedDaePath

def handleZippedDae(path, newAnimationName):
    # Handle zip file
    if getExtensionFromPath(path) == ".zip":
        prepareDaeAnimation(path, newAnimationName)
        print("\n\n")

def handleAnimationsFolder(path):
    """Unzipped and convert all zipped dae files including its subdirectories"""
    for root, dirs, files in os.walk(path):
        for file in files:
            filePath = os.path.join(root, file)
            handleZippedDae(filePath, newAnimationName)

#----------------------------------------------------------------------------------------------------------------
#################################################### Main #######################################################
#----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    Must have ConvertToXcodeCollada in Desktop/StreamCodes/scripts/ConvertToXcodeCollada/ConvertToXcodeCollada.workflow

    Execute by
    1. If zip file is passed, unzip and convert into a usable .dae file
        python3 "mixamoAnimToXcode.py" <path_to_zip> <optional_new_name>
        e.g. python3 "mixamoAnimToXcode.py" '~/Downloads/Hard Head Nod.zip' idleStand
    2. If folder is passed, unzip the contents and convert into a usable .dae files
        python3 "mixamoAnimToXcode.py" <path_to_folder>
        e.g. python3 "mixamoAnimToXcode.py" '~/Downloads/samuel/animations/idle'

        a. If the folder's name is "animations", then the script will convert .zip files including subdirectories
        b. Any other names of a folder will not convert subdirectories
    """
    pathsToConvert, newAnimationName = validateAndGetInput()
    for pathToConvert in pathsToConvert:
        if isFolder(pathToConvert):
            if getNameFromPath(pathToConvert) == "Characters":
                #Get all of the paths that contains "animations" folder and run the same thing as "animations" folders
                animationsPaths = []
                for root, dirs, files in os.walk(pathToConvert):
                    for dir in dirs:
                        if dir == "animations":
                            animationsPath = os.path.join(root, dir)
                            handleAnimationsFolder(animationsPath)
            elif getNameFromPath(pathToConvert) == "animations":
                handleAnimationsFolder(pathToConvert)
            else:
                #Handle zipped files in current directory only
                for filename in os.listdir(pathToConvert):
                    filePath = os.path.join(pathToConvert, filename)
                    handleZippedDae(filePath, newAnimationName)
        else:
            handleZippedDae(pathToConvert, newAnimationName)
    LOG(f"✅✅✅")
