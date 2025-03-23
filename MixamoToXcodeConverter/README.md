# FuFight's Scripts
Use these character and animation scripts to prepare .dae files downloaded from mixamo. It is important to have ConvertToXcodeCollada workflow downloaded

## Use mixamoCharactersToXcode.py for characters
`python3 mixamoCharactersToXcode.py`

#### This script will:
1. Unzip files and properly rename its files and folders, and create an animations folder
2. Update the .dae file's texture files
3. Run the ConvertToXcodeCollada script to the .dae files and delete unneeded generated .dae-e file

#### Each dae.zip file will: 
1. Update the .dae's name in fighterPath
2. Update the textures folder to assets in fighterPath
3. Create an animations folder and more folders for each animation categories
4. Update the name of the .png files in fighterPath/assets
5. Rename the root fighter's path to its name
6. Delete old fighterPath
7. Update .dae file's contents to still point to the updated assets
8. Run the script ConvertToXcodeCollada on the .dae file

## Use mixamoAnimToXcode.py for animations
This script is used to prepare animations to Xcode.
 
Note: This script will perform differently depending on the arguments passed

#### Options based on inputs
1. If zip file is passed, unzip and convert into a usable .dae file

    `python3 "mixamoAnimToXcode.py" <path_to_zip> <optional_new_name>`
    
    e.g. `python3 "mixamoAnimToXcode.py" '~/Downloads/Hard Head Nod.zip' idleStand`

2. If folder is passed, unzip the contents and convert into a usable .dae files

    `python3 "mixamoAnimToXcode.py" <path_to_folder>`
    
    e.g. `python3 "mixamoAnimToXcode.py" '~/Downloads/samuel/animations'`

License under [MIT License](https://github.com/SamuelFolledo/FuFight/blob/master/LICENSE)
