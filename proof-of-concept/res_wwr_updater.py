import xml.etree.ElementTree as ET
import re

## ** USER INPUT ** -------------------
# File Names:
# File Name (relative/absolute path):
input_filename = input(r"Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
else:
    file_str = re.findall(r"(.*)\.cibd22x", input_filename)[0]
    output_filename = file_str + " - EDITED.cibd22x"

# Desired WWR
east_wwr = 0.57
west_wwr = 0.57
north_wwr = 0.70
south_wwr = 0.60
## ------------------------------------

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()
proj = root.findall("./Proj")[0]
bldg = root.findall(".//Bldg")[0]

east_list = dict()
west_list = dict()
north_list = dict()
south_list = dict()

for wall in root.findall(".//ResExtWall"):
    for win in wall.findall(".//ResWin"):
        ori = wall.find("Orientation").text
        if ori == "Left":
            east_list[win.find("WinType").text] = float(wall.find("Area").text)
        elif ori == "Right":
            west_list[win.find("WinType").text] = float(wall.find("Area").text)
        elif ori == "Back":
            south_list[win.find("WinType").text] = float(wall.find("Area").text)
        elif ori == "Front":
            north_list[win.find("WinType").text] = float(wall.find("Area").text)

for window in root.findall(".//ResWinType"):
    if east_list.get(window[0].text) is not None:
        window[2].text = str(east_list.get(window[0].text)*east_wwr)
    if west_list.get(window[0].text) is not None:
        window[2].text = str(west_list.get(window[0].text)*west_wwr)
    if south_list.get(window[0].text) is not None:
        window[2].text = str(south_list.get(window[0].text)*south_wwr)
    if north_list.get(window[0].text) is not None:
        window[2].text = str(north_list.get(window[0].text)*north_wwr)

# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)
