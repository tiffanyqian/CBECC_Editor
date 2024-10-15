import xml.etree.ElementTree as ET
import hvac_components as hvac

# File Names:
# input_filename = input(r"Enter Input File Name/Path: ")
# if len(input_filename) == 0:
#     exit("Enter an input file.")
# output_filename = input(r"Enter Output File Name/Path (leave blank to overwrite input): ")
# if len(output_filename) == 0:
#     output_filename = input_filename
input_filename = r"hvac-generator\Seawall T3.cibd22x"
output_filename = "test.cibd22x"

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()
proj = root.findall("./Proj")[0]
bldg = root.findall("./Proj/Bldg")[0]

def SZHP(tz):
    tz_name = tz[0].text
    if len(tz.findall("PriAirCondgSysRef")) == 0:
        pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
        pri_ac.text = tz_name + " SZHP"
    if len(tz.findall("VentSysRef")) == 0:
        vsr = ET.SubElement(tz,"VentSysRef")
        vsr.text = tz_name + " SZHP"
    
    szhp_as = hvac.add_subelement(bldg,"AirSys")
    hvac.add_subelement(szhp_as,"Name",text=tz_name + " SZHP")
    hvac.add_subelement(szhp_as,"Type",text="SZHP")
    hvac.add_subelement(szhp_as,"CtrlZnRef",text=tz_name)
    hvac.add_subelement(szhp_as,"OptStart",text="0")
    hvac.add_subelement(szhp_as,"AirFlowPerSqFt",text="0.15")

    hvac.add_AirSeg(szhp_as, name=tz_name, type="Supply")
    hvac.add_AirSeg(szhp_as, name=tz_name, type="Return")
    hvac.add_OACtrl(szhp_as, name=tz_name)
    hvac.add_TermUnit(szhp_as, name=tz_name)

skip_add = input("Enter Y to add SZHP to all NR Zones, enter N to manually decide for each zone: ")
# Adding SZHP to all Conditioned NonRes Thermal Zones

if skip_add == "Y":
    for tz in root.findall(".//ThrmlZn"):
        if tz[1].text == "Conditioned":
            print("SZHP added to ", tz[0].text)
            SZHP(tz)
else:
    for tz in root.findall(".//ThrmlZn"):
        if tz[1].text == "Conditioned":
            szhp_str = "  Add SZHP to "+tz[0].text+" (Y/N): "
            add_szhp = input(szhp_str)
            if add_szhp == "Y":
                SZHP(tz)

# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)

