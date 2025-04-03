import xml.etree.ElementTree as ET
global E_Tree

def save_changes(etree, output_filename):
    # This writes the changes made to the output file
    ET.indent(etree)
    etree.write(output_filename)

# ---------------------------------------------------------------------------------------------------------------------------
## *** hvac_components.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

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
        if type == "ConstantVolume":
            add_subelement(fan,"CtrlMthd",text=type)
        elif type == "VariableSpeedDrive":
            add_subelement(fan,"CtrlMthd",text=type)

def add_OACtrl(parent, name, **kwargs):
    type = kwargs.get("type", None)

    oa = add_subelement(parent,"OACtrl")
    add_subelement(oa,"Name",text=name+" OutsideAirControl")

    if type is not None:
        add_subelement(oa,"EconoCtrlMthd",text=type)

def add_TermUnit(parent, name, **kwargs):
    type = kwargs.get("type","Uncontrolled")
    rh_type = kwargs.get("rh","Resistance")

    tu = add_subelement(parent,"TrmlUnit")
    add_subelement(tu,"Name",text=name+" TerminalUnit")
    add_subelement(tu,"Type",text=type)
    add_subelement(tu,"ZnServedRef",text=name)

    if type == "VAVReheatBox":
        add_CH(tu,name+" TU",type=rh_type)

def add_AirSeg(parent, name, **kwargs):
    type = kwargs.get("type",None)
    cc = kwargs.get("cc","DirectExpansion")
    ch = kwargs.get("ch","HeatPump")
    fan_in = kwargs.get("fan_in",0)
    fan_out = kwargs.get("fan_out",0)
    path = kwargs.get("path",None)

    if type is not None:
        name = name + " " + type
    
    airseg = add_subelement(parent,"AirSeg")
    add_subelement(airseg,"Name",text=name+" AirSegment")
    add_subelement(airseg,"Type",text=type)
    if path is not None:
        add_subelement(airseg,"Path",text=path)

    if type == "Supply":
        add_CC(airseg,name,type=cc)
        add_CH(airseg,name,type=ch)
        add_Fan(airseg,name,type=fan_in)
    elif type == "Relief":
        add_Fan(airseg,name,type=fan_out)
    elif type == "Return":
        add_Fan(airseg,name,type=fan_out)
    elif type == "Exhaust":
        add_Fan(airseg,name,type=fan_out)

# ---------------------------------------------------------------------------------------------------------------------------
## *** SINGLE ZONE AIR SYSTEMS *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def SZ_HP_AC_VAV(bldg, tz, **kwargs):
    sz_as_type = kwargs.get("sz_as_type","SZHP")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    outsideac = kwargs.get("oac","DifferentialDryBulb")
    supp_fan = kwargs.get("fan_in","VariableSpeedDrive")
    return_fan = kwargs.get("fan_out","VariableSpeedDrive")
    
    tz_name = tz[0].text
    if len(tz.findall("PriAirCondgSysRef")) == 0:
        pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
        pri_ac.text = tz_name + " " + sz_as_type
    if len(tz.findall("VentSysRef")) == 0:
        vsr = ET.SubElement(tz,"VentSysRef")
        vsr.text = tz_name + " " + sz_as_type
    
    szhp_as = add_subelement(bldg,"AirSys")
    add_subelement(szhp_as,"Name",text=tz_name + " " + sz_as_type)
    add_subelement(szhp_as,"Type",text=sz_as_type)
    add_subelement(szhp_as,"CtrlZnRef",text=tz_name)
    add_subelement(szhp_as,"OptStart",text="0")
    add_subelement(szhp_as,"AirFlowPerSqFt",text="0.15")

    add_AirSeg(szhp_as, name=tz_name, type="Supply", cc=coilcool, ch=coilheat, fan_in=supp_fan)
    add_AirSeg(szhp_as, name=tz_name, type="Return", fan_out=return_fan)
    add_OACtrl(szhp_as, name=tz_name, type=outsideac)
    add_TermUnit(szhp_as, name=tz_name)

def AS_Exhaust(bldg, tz, **kwargs):
    exh_fan = kwargs.get("fan_out","VariableSpeedDrive")
    exh_ctrl = kwargs.get("exh_ctrl","-- DEFAULT --")

    tz_name = tz[0].text
    if len(tz.findall("ExhSysRef")) == 0:
        esr = ET.SubElement(tz,"ExhSysRef")
        esr.text = tz_name + " Exhaust"
    else:
        tz.findall("ExhSysRef")[0].text = tz_name + " Exhaust"
    
    exh_as = add_subelement(bldg,"AirSys")
    add_subelement(exh_as,"Name",text=tz_name + " Exhaust")
    add_subelement(exh_as,"Type",text="Exhaust")
    if exh_ctrl != "-- DEFAULT --":
        add_subelement(exh_as,"ExhCtrlMthd",text=exh_ctrl)

    add_AirSeg(exh_as, name=tz_name, type="Exhaust", path="Direct", fan_out=exh_fan)
    
# ---------------------------------------------------------------------------------------------------------------------------
## *** MULTI ZONE AIR SYSTEMS *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def mz_VAV(bldg, mz_name, yes_rh_tz, no_rh_tz, **kwargs):
    mz_as_type = kwargs.get("mz_as_type","PVAV")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    outsideac = kwargs.get("oac","DifferentialDryBulb")
    supp_fan = kwargs.get("fan_in","VariableSpeedDrive")
    return_fan = kwargs.get("fan_out","VariableSpeedDrive")
    reheat_ch = kwargs.get("rh_ch_type","Resistance")

    mz_as = add_subelement(bldg,"AirSys")
    add_subelement(mz_as,"Name",text=mz_name)
    add_subelement(mz_as,"Type",text=mz_as_type)
    add_subelement(mz_as,"CtrlSysType",text="DDCToZone")
    add_subelement(mz_as,"AirFlowPerSqFt",text="1.0")
    add_subelement(mz_as,"ClgCtrl",text="FixedDualSetpoint")
    add_subelement(mz_as,"ClgFixedSupTemp",text="75")
    add_subelement(mz_as,"HtgFixedSupTemp",text="55")
    add_AirSeg(mz_as,mz_name,type="Supply",cc=coilcool,ch=coilheat,fan_in=supp_fan)
    add_AirSeg(mz_as,mz_name,type="Return",fan_out=return_fan)
    add_OACtrl(mz_as,mz_name,type=outsideac)

    for tz in bldg.findall(".//ThrmlZn"):
        if tz[0].text in yes_rh_tz:
            zn_name = str(tz[0].text)
            add_TermUnit(mz_as, name=zn_name, type="VAVReheatBox")

            if len(tz.findall("PriAirCondgSysRef")) == 0:
                pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
                pri_ac.text = mz_name
            if len(tz.findall("VentSysRef")) == 0:
                vsr = ET.SubElement(tz,"VentSysRef")
                vsr.text = mz_name
        elif tz[0].text in no_rh_tz:
            zn_name = str(tz[0].text)
            add_TermUnit(mz_as, name=zn_name, type="VAVNoReheatBox", rh=reheat_ch)

            if len(tz.findall("PriAirCondgSysRef")) == 0:
                pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
                pri_ac.text = mz_name
            if len(tz.findall("VentSysRef")) == 0:
                vsr = ET.SubElement(tz,"VentSysRef")
                vsr.text = mz_name

# ---------------------------------------------------------------------------------------------------------------------------
## *** SINGLE ZONE ZONE SYSTEMS *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def ZS_Sys(bldg, tz, **kwargs):
    sz_zs_type = kwargs.get("sz_zs_type","SZHP")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    fan = kwargs.get("fan","VariableSpeedDrive")
    
    tz_name = tz[0].text
    if len(tz.findall("PriAirCondgSysRef")) == 0:
        pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
        pri_ac.text = tz_name + " " + sz_zs_type
    else:
        print("TZ: ",tz_name," already references another HVAC System. ZoneSys created but not linked. See more in CBECC file.")
    if len(tz.findall("VentSysRef")) == 0:
        vsr = ET.SubElement(tz,"VentSysRef")
        vsr.text = tz_name + " " + sz_zs_type
    else:
        print("TZ: ",tz_name," already references another Ventilation System. ZoneSys created but not linked. See more in CBECC file.")

    sz_zs = add_subelement(bldg,"ZnSys")
    add_subelement(sz_zs,"Name",text=tz_name + " " + sz_zs_type)
    add_subelement(sz_zs,"Type",text=sz_zs_type)

    if sz_zs_type == "VRF":
        add_subelement(sz_zs,"VRFSysRef")
    if sz_zs_type == "FPFC":
        add_subelement(sz_zs,"FanCtrl",text="Cycling")
        add_subelement(sz_zs,"Cnt",text="1")
        add_subelement(sz_zs,"DuctLctn",text="Conditioned")

    add_CC(sz_zs,tz_name,type=coilcool)
    add_CH(sz_zs,tz_name,type=coilheat)
    add_Fan(sz_zs,tz_name,type=fan)

def ZS_Exhaust(bldg, tz, **kwargs):
    exh_fan = kwargs.get("fan_out","VariableSpeedDrive")
    exh_ctrl = kwargs.get("exh_ctrl","-- DEFAULT --")

    tz_name = tz[0].text
    if len(tz.findall("ExhSysRef")) == 0:
        esr = ET.SubElement(tz,"ExhSysRef")
        esr.text = tz_name + " Exhaust"
    else:
        print("TZ: ",tz_name," already references another Exhaust System. Overwrote with ZoneSystem Exhaust. If not intended, discard changes or edit in CBECC file.")
        tz.findall("ExhSysRef")[0].text = tz_name + " Exhaust"
    
    exh_zs = add_subelement(bldg,"ZnSys")
    add_subelement(exh_zs,"Name",text=tz_name + " Exhaust")
    add_subelement(exh_zs,"Type",text="Exhaust")
    if exh_ctrl != "-- DEFAULT --":
        add_subelement(exh_zs,"ExhCtrlMthd",text=exh_ctrl)

    add_Fan(exh_zs,tz_name,type=exh_fan)
