import xml.etree.ElementTree as ET

print("NOTE: Currently will only do SZHP generation for NR Thermal Zones as of right now.")
# File Names:
input_filename = input("Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
output_filename = input("Enter Output File Name/Path (leave blank to overwrite input): ")
if len(output_filename) == 0:
    output_filename = input_filename

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()
proj = root.findall("./Proj")[0]
bldg = root.findall("./Proj/Bldg")[0]

def add_subelement(parent,tag,**kwargs):
    text = kwargs.get("text",None)

    child = ET.SubElement(parent, tag)
    
    if text is not None:
        child.text = text
    
    return child

def add_CC(parent, name, **kwargs):
    type = kwargs.get("type","DirectExpansion")

    cc = add_subelement(parent,"CoilClg")
    add_subelement(cc,"Name",text=name+" CoilCooling")
    add_subelement(cc,"Type",text=type)

def add_CH(parent, name, **kwargs):
    type = kwargs.get("type","HeatPump")

    ch = add_subelement(parent,"CoilHtg")
    add_subelement(ch,"Name",text=name+" CoilHeating")
    add_subelement(ch,"Type",text=type)

def add_Fan(parent, name, **kwargs):
    type = kwargs.get("type",0)
    
    if type != 0:
        fan = add_subelement(parent,"Fan")
    add_subelement(fan,"Name",text=name+" Fan")

    if type == 1:
        type = "ConstantVolume"
        add_subelement(fan,"CtrlMthd",text=type)
    elif type == 2:
        type == "VariableSpeedDrive"
        add_subelement(fan,"CtrlMthd",text=type)

def add_OACtrl(parent, name, **kwargs):
    type = kwargs.get("type", None)

    oa = add_subelement(parent,"OACtrl")
    add_subelement(oa,"Name",text=name+" OutsideAirControl")

    if type is not None:
        add_subelement(oa,"Type",text=type)

def add_TermUnit(parent, name, **kwargs):
    type = kwargs.get("type","Uncontrolled")

    tu = add_subelement(parent,"TrmlUnit")
    add_subelement(tu,"Name",text=name+" TerminalUnit")
    add_subelement(tu,"Type",text=type)
    add_subelement(tu,"ZnServedRef",text=name)

def add_AirSeg(parent, name, **kwargs):
    type = kwargs.get("type",None)
    airsystem = kwargs.get("airsystem",None)

    if type is not None:
        name = name + " " + type
    
    airseg = add_subelement(parent,"AirSeg")
    add_subelement(airseg,"Name",text=name+" AirSegment")
    add_subelement(airseg,"Type",text=type)

    if type == "Supply":
        add_CC(airseg,name,type="DirectExpansion")
        add_CH(airseg,name,type="HeatPump")
        add_Fan(airseg,name,type=1)
    elif type == "Return":
        if airsystem != "DOAS":
            add_Fan(airseg,name,type=1)

def SZHP(tz):
    tz_name = tz[0].text
    if len(tz.findall("PriAirCondgSysRef")) == 0:
        pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
        pri_ac.text = tz_name + " SZHP"
    if len(tz.findall("VentSysRef")) == 0:
        vsr = ET.SubElement(tz,"VentSysRef")
        vsr.text = tz_name + " SZHP"
    
    szhp_as = add_subelement(bldg,"AirSys")
    add_subelement(szhp_as,"Name",text=tz_name + " SZHP")
    add_subelement(szhp_as,"Type",text="SZHP")
    add_subelement(szhp_as,"CtrlZnRef",text=tz_name)
    add_subelement(szhp_as,"OptStart",text="0")
    add_subelement(szhp_as,"AirFlowPerSqFt",text="0.15")

    add_AirSeg(szhp_as, name=tz_name, type="Supply")
    add_AirSeg(szhp_as, name=tz_name, type="Return")
    add_OACtrl(szhp_as, name=tz_name)
    add_TermUnit(szhp_as, name=tz_name)

# Adding SZHP to all Conditioned NonRes Thermal Zones
for tz in root.findall(".//ThrmlZn"):
    if tz[1].text == "Conditioned":
        print(tz[0].text)
        SZHP(tz)

# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)

