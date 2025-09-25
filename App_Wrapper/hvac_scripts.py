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
    proj = kwargs.get("proj_root", None)

    cc = add_subelement(parent,"CoilClg")
    add_subelement(cc,"Name",text=name+" CoilCooling")
    add_subelement(cc,"Type",text=type)
    
    if proj is not None:
        fluid_Connect(proj, cc, type)

def add_CH(parent, name, **kwargs):
    type = kwargs.get("type","HeatPump")
    proj = kwargs.get("proj_root", None)

    ch = add_subelement(parent,"CoilHtg")
    add_subelement(ch,"Name",text=name+" CoilHeating")
    add_subelement(ch,"Type",text=type)
        
    if proj is not None:
        fluid_Connect(proj, ch, type)

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
    proj = kwargs.get("proj_root", None)

    if type is not None:
        name = name + " " + type
    
    airseg = add_subelement(parent,"AirSeg")
    add_subelement(airseg,"Name",text=name+" AirSegment")
    add_subelement(airseg,"Type",text=type)
    if path is not None:
        add_subelement(airseg,"Path",text=path)

    if type == "Supply":
        if proj is None:
            add_CC(airseg,name,type=cc)
            add_CH(airseg,name,type=ch)
        else:
            add_CC(airseg,name,type=cc,proj_root=proj)
            add_CH(airseg,name,type=ch,proj_root=proj)
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

def SZ_HP_AC_VAV(proj, tz, **kwargs):
    sz_as_type = kwargs.get("sz_as_type","SZHP")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    outsideac = kwargs.get("oac","DifferentialDryBulb")
    supp_fan = kwargs.get("fan_in","VariableSpeedDrive")
    return_fan = kwargs.get("fan_out","VariableSpeedDrive")
    bldg = proj.findall(".//Bldg")[0]
    
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

    if (coilheat == "HotWater") or (coilcool == "ChilledWater"):
        add_AirSeg(szhp_as, name=tz_name, type="Supply", cc=coilcool, ch=coilheat, fan_in=supp_fan, proj_root=proj)
    else:
        add_AirSeg(szhp_as, name=tz_name, type="Supply", cc=coilcool, ch=coilheat, fan_in=supp_fan)
    add_AirSeg(szhp_as, name=tz_name, type="Return", fan_out=return_fan)
    add_OACtrl(szhp_as, name=tz_name, type=outsideac)
    add_TermUnit(szhp_as, name=tz_name)

def AS_Exhaust(proj, tz, **kwargs):
    exh_fan = kwargs.get("fan_out","VariableSpeedDrive")
    exh_ctrl = kwargs.get("exh_ctrl","-- DEFAULT --")
    bldg = proj.findall(".//Bldg")[0]

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

def mz_VAV(proj, mz_name, yes_rh_tz, no_rh_tz, **kwargs):
    mz_as_type = kwargs.get("mz_as_type","PVAV")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    outsideac = kwargs.get("oac","DifferentialDryBulb")
    supp_fan = kwargs.get("fan_in","VariableSpeedDrive")
    return_fan = kwargs.get("fan_out","VariableSpeedDrive")
    reheat_ch = kwargs.get("rh_ch_type","Resistance")
    bldg = proj.findall(".//Bldg")[0]

    mz_as = add_subelement(bldg,"AirSys")
    add_subelement(mz_as,"Name",text=mz_name)
    add_subelement(mz_as,"Type",text=mz_as_type)
    add_subelement(mz_as,"CtrlSysType",text="DDCToZone")
    add_subelement(mz_as,"AirFlowPerSqFt",text="1.0")
    add_subelement(mz_as,"ClgCtrl",text="FixedDualSetpoint")
    add_subelement(mz_as,"ClgFixedSupTemp",text="75")
    add_subelement(mz_as,"HtgFixedSupTemp",text="55")
    if (coilheat == "HotWater") or (coilcool == "ChilledWater"):
        add_AirSeg(mz_as,mz_name,type="Supply",cc=coilcool,ch=coilheat,fan_in=supp_fan,proj_root=proj)
    else:
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

def ZS_Sys(proj, tz, **kwargs):
    sz_zs_type = kwargs.get("sz_zs_type","SZHP")
    coilcool = kwargs.get("cc","DirectExpansion")
    coilheat = kwargs.get("ch","HeatPump")
    fan = kwargs.get("fan","VariableSpeedDrive")
    bldg = proj.findall(".//Bldg")[0]
    
    tz_name = tz[0].text
    if len(tz.findall("PriAirCondgSysRef")) != 0 and len(tz.findall("VentSysRef")) != 0:
        print("TZ: ",tz_name," already references another Ventilation System. ZoneSys created and linked only to HVAC system. See more in CBECC file.")
        
        hvac_ref = tz.findall("./PriAirCondgSysRef")
        if len(hvac_ref) > 0:
            hvac_ref[0].text = tz_name + " " + sz_zs_type
        hvac_prior = tz.findall("./PriAirCondgSysPriority")
        if len(hvac_prior) > 0:
            hvac_prior[0].text = "1"
        else:
            hvac_prior = ET.SubElement(tz,"PriAirCondgSysPriority",attrib={"index":"0"})
            hvac_prior.text = "1"

        vent_prior = tz.findall("./VentSysPriority")
        if len(vent_prior) > 0:
            vent_prior[0].text = "2"
        else:
            vent_prior = ET.SubElement(tz,"VentSysPriority")
            vent_prior.text = "2"
    else:
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

    sz_zs = add_subelement(proj,"ZnSys")
    add_subelement(sz_zs,"Name",text=tz_name + " " + sz_zs_type)
    add_subelement(sz_zs,"Type",text=sz_zs_type)

    if sz_zs_type == "VRF":
        add_subelement(sz_zs,"VRFSysRef")
    if sz_zs_type == "FPFC":
        add_subelement(sz_zs,"FanCtrl",text="Cycling")
        add_subelement(sz_zs,"Cnt",text="1")
        add_subelement(sz_zs,"DuctLctn",text="Conditioned")

    if coilcool == "ChilledWater":
        dd_CC(sz_zs,tz_name,type=coilcool, proj_root=proj)
    else:
        add_CC(sz_zs,tz_name,type=coilcool)
    if coilheat == "HotWater":
        add_CH(sz_zs,tz_name,type=coilheat, proj_root=proj)
    else:
        add_CH(sz_zs,tz_name,type=coilheat)
    add_Fan(sz_zs,tz_name,type=fan)

def ZS_Exhaust(proj, tz, **kwargs):
    exh_fan = kwargs.get("fan_out","VariableSpeedDrive")
    exh_ctrl = kwargs.get("exh_ctrl","-- DEFAULT --")
    bldg = proj.findall(".//Bldg")[0]

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

# ---------------------------------------------------------------------------------------------------------------------------
## *** FLUID SYSTEMS *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def FluidSys(proj, fs_type, ctrl_type, temp_ctrl):
    fs_name = ""
    repeat = 0
    # Check to see if FluidSystem type already exists, if so, append number
    for ex_fs in proj.findall(".//FluidSys"):
        if ex_fs[1].text == fs_type:
            repeat = repeat + 1
            fs_name = " "+str(repeat)

    # Naming based on FluidSys Type
    if fs_type == "ChilledWater":
        fs_name = "CHW"+fs_name
    elif fs_type == "CondenserWater":
        fs_name = "CCW"+fs_name
    elif fs_type == "HotWater":
        fs_name = "HHW"+fs_name

    # Creating the tags for the FluidSystem
    fs = add_subelement(proj,"FluidSys")
    add_subelement(fs,"Name",text=fs_name)
    add_subelement(fs,"Type",text=fs_type)
    add_subelement(fs,"CtrlType",text=ctrl_type)
    add_subelement(fs,"TempCtrl",text=temp_ctrl)

    fs_sup = add_subelement(fs,"FluidSeg")
    add_subelement(fs_sup,"Name",text=fs_name+" Supply")
    add_subelement(fs_sup,"Type",text="PrimarySupply")

    fs_ret = add_subelement(fs,"FluidSeg")
    add_subelement(fs_ret,"Name",text=fs_name+" Return")
    add_subelement(fs_ret,"Type",text="PrimaryReturn")

    return fs_name

def FS_Chiller(fs, **kwargs):
    create_num = kwargs.get("create_num",0)
    ch_type = kwargs.get("ch_type","Screw")
    ch_cond_type = kwargs.get("cond_type","Air")
    pump_spd_ctrl = kwargs.get("pump_spd_ctrl","VariableSpeed")

    ch_name = "Chiller"
    # Check to see if any Chillers already exist, if so, append number
    repeat = len(fs.findall(".//Chlr"))
    if repeat > 0:
        ch_name = "Chiller " + str(repeat)

    # Finding FluidSeg In/Out References
    fs_in = 0
    fs_out = 0
    for seg in fs.findall(".//FluidSeg"):
        if seg[1].text == "PrimarySupply":
            fs_in = seg[0].text
        if seg[1].text == "PrimaryReturn":
            fs_out = seg[0].text
    if (fs_in == 0) or (fs_out == 0):
        exit("ERROR: No Fluid Segment on FluidSystem. Check CBECC file or create new FluidSystem.")

    for x in range(create_num):
        if x > 0:
            ch_name = "Chiller " + str(repeat+x)

        ch = add_subelement(fs,"Chlr")
        add_subelement(ch,"Name",text=ch_name)
        add_subelement(ch,"Type",text=ch_type)
        add_subelement(ch,"CndsrType",text=ch_cond_type)
        add_subelement(ch,"EvapFluidSegInRef",text=fs_in)
        add_subelement(ch,"EvapFluidSegOutRef",text=fs_out)
        ch_pump = add_subelement(ch,"Pump")
        add_subelement(ch_pump,"Name",text=ch_name+" Pump")
        add_subelement(ch_pump,"SpdCtrl",text=pump_spd_ctrl)

def FS_Boiler(fs, **kwargs):
    create_num = kwargs.get("create_num",0)
    bl_type = kwargs.get("bl_type","HotWater")
    bl_fuel = kwargs.get("fuel_src","Electric")
    pump_spd_ctrl = kwargs.get("pump_spd_ctrl","VariableSpeed")

    bl_name = "Boiler"
    # Check to see if any Boilers already exist, if so, append number
    repeat = len(fs.findall(".//Blr"))
    if repeat > 0:
        bl_name = "Boiler " + str(repeat)
    
    # Finding FluidSeg In/Out References
    fs_in = 0
    fs_out = 0
    for seg in fs.findall(".//FluidSeg"):
        if seg[1].text == "PrimarySupply":
            fs_in = seg[0].text
        if seg[1].text == "PrimaryReturn":
            fs_out = seg[0].text
    if (fs_in == 0) or (fs_out == 0):
        exit("ERROR: No Fluid Segment on FluidSystem. Check CBECC file or create new FluidSystem.")

    for x in range(create_num):
        if x > 0:
            bl_name = "Boiler " + str(repeat+x)

        bl = add_subelement(fs,"Blr")
        add_subelement(bl,"Name",text=bl_name)
        add_subelement(bl,"Type",text=bl_type)
        add_subelement(bl,"FuelSrc",text=bl_fuel)
        add_subelement(bl,"FluidSegInRef",text=fs_in)
        add_subelement(bl,"FluidSegOutRef",text=fs_out)
        bl_pump = add_subelement(bl,"Pump")
        add_subelement(bl_pump,"Name",text=bl_name+" Pump")
        add_subelement(bl_pump,"SpdCtrl",text=pump_spd_ctrl)

def FS_WaterHeater(fs, **kwargs):
    create_num = kwargs.get("create_num",0)
    wh_type = kwargs.get("wh_type","HeatPumpPackaged")
    wh_subtype = kwargs.get("wh_subtype","R410a_MultiPass")
    pump_spd_ctrl = kwargs.get("pump_spd_ctrl","VariableSpeed")

    wh_name = "WaterHeater"
    # Check to see if any WaterHeaters already exist, if so, append number
    repeat = len(fs.findall(".//WtrHtr"))
    if repeat > 0:
        wh_name = "WaterHeater " + str(repeat)

    # Finding FluidSeg In/Out References
    fs_in = 0
    fs_out = 0
    for seg in fs.findall(".//FluidSeg"):
        if seg[1].text == "PrimarySupply":
            fs_in = seg[0].text
        if seg[1].text == "PrimaryReturn":
            fs_out = seg[0].text
    if (fs_in == 0) or (fs_out == 0):
        exit("ERROR: No Fluid Segment on FluidSystem. Check CBECC file or create new FluidSystem.")

    for x in range(create_num):
        if x > 0:
            wh_name = "WaterHeater " + str(repeat+x)

        wh = add_subelement(fs,"WtrHtr")
        add_subelement(wh,"Name",text=wh_name)
        add_subelement(wh,"Type",text=wh_type)
        add_subelement(wh,"FluidSegOutRef",text=fs_in)
        add_subelement(wh,"FluidSegInRef",text=fs_out)
        # add_subelement(wh,"COP",text=cop)
        add_subelement(wh,"HtPumpSubType",text=wh_subtype)
        add_subelement(wh,"StorLoc",text="1")
        # add_subelement(wh,"CapRtd",text=cap_rat)
        wh_pump = add_subelement(wh,"Pump")
        add_subelement(wh_pump,"Name",text=wh_name+" Pump")
        add_subelement(wh_pump,"SpdCtrl",text=pump_spd_ctrl)

def fluid_Connect(proj, coil, c_type):
    if c_type == "HotWater":
        fs_sup = 0
        fs_ret = 0
        for fs in proj.findall(".//FluidSys"):
            if fs[1].text == "HotWater":
                for seg in fs.findall(".//FluidSeg"):
                    if seg[1].text == "PrimarySupply": 
                        fs_sup = seg[0].text
                    if seg[1].text == "PrimaryReturn": 
                        fs_ret = seg[0].text
                break

        if fs_sup == 0 or fs_ret == 0:
            add_subelement(coil,"FluidSegInRef",text=fs_sup)
            add_subelement(coil,"FluidSegOutRef",text=fs_ret)
        else:
            print("No complete HotWater FluidSystems found. Heating Coil with HotWater created but not connected, see CBECC file.")
    elif c_type == "ChilledWater":
        fs_sup = 0
        fs_ret = 0
        for fs in proj.findall(".//FluidSys"):
            if fs[1].text == "ChilledWater":
                for seg in fs.findall(".//FluidSeg"):
                    if seg[1].text == "PrimarySupply": 
                        fs_sup = seg[0].text
                    if seg[1].text == "PrimaryReturn": 
                        fs_ret = seg[0].text
                break

        if fs_sup == 0 or fs_ret == 0:
            add_subelement(coil,"FluidSegInRef",text=fs_sup)
            add_subelement(coil,"FluidSegOutRef",text=fs_ret)
        else:
            print("No complete ChilledWater FluidSystems found. Cooling Coil with ChilledWater created but not connected, see CBECC file.")
