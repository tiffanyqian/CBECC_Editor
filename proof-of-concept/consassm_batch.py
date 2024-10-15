import xml.etree.ElementTree as ET
import re
import os
import datetime

## ** USER INPUT ** -------------------
# File Name (relative/absolute path):
input_filename = input(r"Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
# (NOTE: batch files will be created in same folder as input file)
## ------------------------------------

# ** FILE OUTPUT: Can Edit if Necessary ** -----
# Batch Folder - folder with the input filename, date created, and "-BATCH" appended.
# Leave as is unless a specific format is required
dt = datetime.datetime.now()
date = str(dt.year)+str(dt.month)+str(dt.day)
batchfolder = re.findall(r"(.*)\.", input_filename)[0]+"_BATCH-"+date

# Checks to see if the batchfolder as defined exists, and if it does, if the user wants to overwrite it or not.
if os.path.exists(batchfolder):
    print("Batch file path already exists, you may have run this already.\nOverwrite batch folder? (NO to make a different path, anything else to overwrite)")
    overwrite = input()
    if overwrite == "NO":
        # If overlapping and user wants to keep previous folder, add hour, minute, second to batch file path name.
        batchfolder = batchfolder + "-" + str(dt.hour) + str(dt.minute) + str(dt.second)
        os.makedirs(batchfolder)
else:
    os.makedirs(batchfolder)

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()

# --- External Wall Cons Selection --
ext_walls = list()
for e_wall in root.findall(".//ConsAssm"):
    if e_wall[1].text == "ExteriorWall":
        ext_walls.append(e_wall)

# --- Continuous Insulation Selection ---
ctnsins = list()
for mat in root.findall(".//Mat/Name"):
    if len(re.findall(r"(Ctns Ins .*)",mat.text)) > 0:
        ctnsins.append(mat.text)

print(ctnsins)
print("Enter Lower Index of all Ctns Ins values to step through (index starts at 0, no input for full string)")
ctnsins_ind_low = input()
if len(ctnsins_ind_low) == 0:
    ctnsins_ind_low = "0"
    ctnsins_ind_up = str(len(ctnsins))
else:
    print("Enter Upper Index of all Ctns Ins values to step through (index starts at 0)")
    ctnsins_ind_up = input()

if len(ctnsins_ind_low) > len(ctnsins_ind_up):
    exit("Invalid input. Lower bound is higher than Upper bound.")
elif int(ctnsins_ind_low) > len(ctnsins) or int(ctnsins_ind_up) > len(ctnsins):
    exit("Out of bounds- entered a number greater than insulations defined in file.")
elif int(ctnsins_ind_low) == int(ctnsins_ind_up):
    exit("Invalid input, lower and upper indices are equal and no insulation values were chosen.")
else:
    ctnsins_ind_low = int(ctnsins_ind_low)
    ctnsins_ind_up = int(ctnsins_ind_up)
    ctnsins = ctnsins[ctnsins_ind_low:ctnsins_ind_up]
    print("You entered:",ctnsins,"\nCreating files now...")

# --------

for wall in ext_walls:
    wall_ctn_ind = -1
    
    for i, child in enumerate(wall):
        if len(re.findall(r"(Ctns Ins .*)",child.text)) > 0:
            wall_ctn_ind = i

            if child.text in ctnsins:
                print("Skipping base case:",child.text,"...")
                ctnsins.remove(child.text)

    if wall_ctn_ind > 0:
        for ci in ctnsins:
            b_file = ci.split(" ")[-1] + "_" + input_filename.split("/")[-1]
            b_folder = batchfolder + "/" + ci.split(" ")[-1] + "/"
            b_path = b_folder + b_file

            wall[wall_ctn_ind].text = ci
            if os.path.isdir(b_folder) == False:
                os.makedirs(b_folder)
            # This writes the changes made to the output file
            ET.indent(tree)
            tree.write(b_path)
