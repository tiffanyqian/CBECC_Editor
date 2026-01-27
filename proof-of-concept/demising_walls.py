import xml.etree.ElementTree as ET
import re
import os

## ** USER INPUT ** -------------------
# File Names:
input_filename = input(r"Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
else:
    file_str = re.findall(r"(.*)\.cibd22x", input_filename)[0]
    log_filename = file_str + ".log"
    output_filename = file_str + " - EDITED.cibd22x"
    
    if os.path.exists(log_filename) is False:
        log_filename = input(r"Enter Log File or Wall List File Name/Path: ")

demising_list = []

## ------------------------------------

with open(log_filename) as f:
    for line in f:
        walls = re.findall(r"Error:\s\sInterior\swall\s'(.*)'\sin\sspace\s'(.*)'\sis\sa\smetal\sframed\sdemising", line)
        if len(walls) > 0:
            print(walls[0])
            demising_list.append(walls[0][0])

## ------------------------------------

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()

for wall in root.findall(".//IntWall"):
    if wall[0].text in demising_list:
        wall[3].text = "Int Partition Demising"

## ------------------------------------

# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)