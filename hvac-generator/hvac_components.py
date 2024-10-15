import xml.etree.ElementTree as ET

print("NOTE: Currently only checked for SZHP & DOAS generation.")

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
