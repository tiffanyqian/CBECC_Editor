import xml.etree.ElementTree as ET

nr_filename = "./files/r_testing_output.cibd22x"
r_filename = "./files/nr_testing_output.cibd22x"

output_filename = "./files/testing_output.cibd22x"

r_tree = ET.parse(r_filename)
r_root = r_tree.getroot()
r_proj = r_root.findall("./Proj")[0]
r_bldg = r_root.findall("./Proj/Bldg")[0]

nr_tree = ET.parse(nr_filename)
nr_root = nr_tree.getroot()

# This changes GeometryInpType to Detailed
for child in r_root.findall(".//GeometryInpType"):
    child.text = "Detailed"

# This finds where the BldgAz tag is in the Residential file
ba_ind = list(r_bldg).index(r_root.findall(".//BldgAz")[0]) + 1
# This copies over every NonRes Story level over to the Residential file at the above location
for nr_story in nr_root.findall(".//Story"):
    r_bldg.insert(ba_ind, nr_story)
    ba_ind += 1
# This copies over all NonRes Thermal Zones over to the Residential file below above Story copies
for nr_tz in nr_root.findall(".//ThrmlZn"):
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