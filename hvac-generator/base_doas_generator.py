import xml.etree.ElementTree as ET
import hvac_components as hvac
import re

# File Names:
input_filename = input(r"Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
output_filename = input(r"Enter Output File Name/Path (leave blank to overwrite input): ")
if len(output_filename) == 0:
    output_filename = input_filename
print()

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()
proj = root.findall("./Proj")[0]
bldg = root.findall("./Proj/Bldg")[0]

def DOAS(tz,**kwargs):
    name = kwargs.get("name", None)
    if name is None:
        doas_count = 1
        for airsys in root.findall(".//AirSys/Type"):
            if "DOASVAV" in airsys.text:
                doas_count += 1
        name = "DOAS "+str(doas_count)
    else:
        name = "DOAS "+name

    doas = hvac.add_subelement(bldg,"AirSys")
    hvac.add_subelement(doas,"Name",text=name)
    hvac.add_subelement(doas,"Type",text="DOASVAV")
    hvac.add_subelement(doas,"CtrlSysType",text="DDCToZone")
    hvac.add_subelement(doas,"AirFlowPerSqFt",text="1.0")
    hvac.add_subelement(doas,"ClgCtrl",text="FixedDualSetpoint")
    hvac.add_subelement(doas,"ClgFixedSupTemp",text="75")
    hvac.add_subelement(doas,"HtgFixedSupTemp",text="55")
    hvac.add_AirSeg(doas,name,type="Supply")
    hvac.add_AirSeg(doas,name,type="Return",airsystem="DOAS")
    hvac.add_OACtrl(doas,name)

    for zone in tz:
        zn_name = str(zone[0].text)
        hvac.add_TermUnit(doas, name=zn_name)

        if len(zone.findall("PriAirCondgSysRef")) == 0:
            pri_ac = ET.SubElement(zone,"PriAirCondgSysRef",attrib={"index":"0"})
            pri_ac.text = name
        if len(zone.findall("VentSysRef")) == 0:
            vsr = ET.SubElement(zone,"VentSysRef")
            vsr.text = name

doas_count = input("Enter number of DOAS units you wish to create: ")
if doas_count.isdigit():
    doas_count = int(doas_count)
    if doas_count == 0:
        exit("0 DOAS created. Bye bye.")
else:
    exit("Enter a number.")
print()

tz_list = dict()
for tz in root.findall(".//ThrmlZn"):
    if tz[1].text == "Conditioned":
        tz_list[tz[0].text] = tz
print("List of conditioned thermal zones in file:")
print(tz_list.keys())
print()

for num, dc in enumerate(range(doas_count)):
    print("For DOAS #",str(num+1))
    to_add = input(r"  Enter list of thermal zones to add, SEPARATED BY A COMMA (ex. 'Zone1', 'Zone2', 'Zone3'): ")

    # Some string manipulation to account for user error when entering / pasting from thermal zone list
    to_add = to_add.replace("'","")
    to_add = to_add.replace("\"","")
    to_add = re.split(r",\s*", to_add)

    # For the zones entered by user, check if it's in the list of thermal zones and get the reference in the ElementTree. If it's not not, don't add.
    for count, add_zn in enumerate(to_add):
        if add_zn in tz_list:
            to_add[count] = tz_list[add_zn]
        else:
            print("\tZone ",add_zn," not in thermal zone list. Not adding.")
            to_add.remove(add_zn)
    if len(to_add) != 0:
        DOAS(to_add)


# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)
