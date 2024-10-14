import xml.etree.ElementTree as ET
import re

## ** USER INPUT ** -------------------
# File Names:
# File Names:
nr_filename = input("Enter NON-RESIDENTIAL Input File Name/Path: ")
if len(nr_filename) == 0:
    exit("Enter a NR input file.")
r_filename = input("Enter RESIDENTIAL Input File Name/Path: ")
if len(r_filename) == 0:
    exit("Enter a R input file.")

output_filename = input("Enter Output File Name/Path: ")
if len(output_filename) == 0:
    exit("Enter an output filename.")
## ------------------------------------

r_tree = ET.parse(r_filename)
r_root = r_tree.getroot()
r_proj = r_root.findall("./Proj")[0]
r_bldg = r_root.findall("./Proj/Bldg")[0]

nr_tree = ET.parse(nr_filename)
nr_root = nr_tree.getroot()
nr_bldg = nr_root.findall("./Proj/Bldg")[0]

# Get a list of the storeys existing across both NR and R files -- will sort automatically with no duplicates.
combined_storeys = set()
for res_story in r_root.findall(".//ResZnGrp"):
    combined_storeys.add(str(res_story[0].text))
for nr_story in nr_root.findall(".//Story"):
    combined_storeys.add(str(nr_story[0].text))
combined_storeys = sorted(list(combined_storeys))

print("Enter index of NR/R split (index starts at 0, enter first R floor):")
print(combined_storeys)
story_split_ind = input()
if len(story_split_ind) == 0:
    exit("Invalid input. Enter a value.")
elif int(story_split_ind) > len(combined_storeys):
    exit("Out of bounds- entered a number greater than floors there are.")
else:
    story_split_ind = int(story_split_ind)
    print("You entered:",combined_storeys[story_split_ind],"... Running combination script now.")

# These lists contain what floors belong to NR and which belong to R
nr_story_list = combined_storeys[:story_split_ind]
r_story_list = combined_storeys[story_split_ind:]

# Remove all Res storeys from NR file
for nr_story in nr_root.findall(".//Story"):
    if str(nr_story[0].text) in r_story_list:
        nr_bldg.remove(nr_story)
# Remove all NonRes storeys from R file
for r_story in r_root.findall(".//ResZnGrp"):
    if str(r_story[0].text) in nr_story_list:
        r_bldg.remove(r_story)

# Updates NR space names to match those in R space to make sure references to zones stay defined
spc_r_to_nr = dict()
for ns in nr_root.findall(".//Spc"):
    spc_r_to_nr.update({ns[0].text: re.findall(r"(.*)_",ns[0].text)[0]})
    ns[0].text = re.findall(r"(.*)_",ns[0].text)[0]

for ns_ref in nr_root.findall(".//AdjacentSpcRef"):
    ns_ref.text = spc_r_to_nr[ns_ref.text]

# This changes Residential GeometryInpType to Detailed
for child in r_root.findall(".//GeometryInpType"):
    child.text = "Detailed"

# Find NR only thermal zones (so we can delete the R thermal zones)
nr_thrmzn = list()
for nr_tzr in nr_root.findall(".//ThrmlZnRef"):
    nr_thrmzn.append(nr_tzr.text)

# This finds where the BldgAz tag is in the Residential file
ba_ind = list(r_bldg).index(r_root.findall(".//BldgAz")[0]) + 1
# This copies over every NonRes Story level over to the Residential file at the above location
for nr_story in nr_root.findall(".//Story"):
    r_bldg.insert(ba_ind, nr_story)
    ba_ind += 1
# This copies over ONLY NonRes Thermal Zones over to the Residential file below above Story additions
for nr_tz in nr_root.findall(".//ThrmlZn"):
    if str(nr_tz[0].text) in nr_thrmzn:
        r_bldg.insert(ba_ind, nr_tz)
        ba_ind += 1

# The following copies over NonRes Material, Construction Assemblies, and Fenestration over to the Residential file
for nr_mat in nr_root.findall(".//Mat"):
    # Checking if there exists a Res and a NonRes Material with the same Name
    # (this aims to reduce duplicates in case IES to CBECC py file was run on both)
    r_mat = r_root.findall(".//Mat/Name")
    for count, mat in enumerate(r_mat):
        r_mat[count] = mat.text
    # If NonRes Material is unique, append to Res file. Otherwise, don't append.
    if nr_mat[0].text not in r_mat:
        r_proj.append(nr_mat)
for nr_ca in nr_root.findall(".//ConsAssm"):
    # Checking if there exists a Res and a NonRes Construction Assembly with the same Name
    # (this aims to reduce duplicates in case IES to CBECC py file was run on both)
    r_ca = r_root.findall(".//ConsAssm/Name")
    for count, ca in enumerate(r_ca):
        r_ca[count] = ca.text
    # If NonRes Construction Assembly is unique, append to Res file. Otherwise, don't append.
    if nr_ca[0].text not in r_ca:
        r_proj.append(nr_ca)
for fen in nr_root.findall(".//FenCons"):
    # Checking if there exists a Res and a NonRes Fenestration Construction with the same Name
    # (this aims to reduce duplicates in case IES to CBECC py file was run on both)
    r_fen = r_root.findall(".//FenCons/Name")
    for count, f in enumerate(r_fen):
        r_fen[count] = f.text
    # If NonRes Construction Assembly is unique, append to Res file. Otherwise, don't append.
    if fen[0].text not in r_fen:
        r_proj.append(fen)

# This writes the changes made to the output file
ET.indent(r_tree)
r_tree.write(output_filename)