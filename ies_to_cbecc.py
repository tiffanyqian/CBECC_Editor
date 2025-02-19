import xml.etree.ElementTree as ET
import re

## ** USER INPUT ** -------------------
# File Names:
input_filename = input(r"Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
output_filename = input(r"Enter Output File Name/Path (leave blank to overwrite input): ")
if len(output_filename) == 0:
    output_filename = input_filename
elif len(re.findall(r".cibd22x$",output_filename)) == 0:
    output_filename = output_filename + ".cibd22x"
# Fenestration Inputs: leave any of them 0 for default values or update to desired values
fen_inputs = input("  Enter Fenestration Inputs or leave as default? (Y for yes, anything else is no): ")
if fen_inputs == "Y":
    SHGC = input("\tSHGC (Default=0.3): ")
    U_Factor = input("\tU-Factor (Default=0.45): ")
    Fen_Product_Type = input("\tFenestration Product Type (Default=CurtainWall): ")
else:
    SHGC = str(0.3)
    U_Factor = str(0.45)
    Fen_Product_Type = "CurtainWall"
## ------------------------------------

# This creates an ElementTree out of the input file to make easier edits
tree = ET.parse(input_filename)
root = tree.getroot()
proj = root.findall("./Proj")[0]
bldg = root.findall("./Proj/Bldg")[0]

# Stores information about whether building is NonResidential (NR) or Residential (R)
b_type = "NR"
# This changes GeometryInpType to Detailed
if len(root.findall(".//ResZnGrp")) > 0:
    b_type = "R"
    for child in root.findall(".//GeometryInpType"):
        child.text = "Detailed"

# This finds the index range of tags (<tag>) associated with Document Author / Responsible Designer generation in reports in order to remove them to make them blank in the final report
# for later signing.
first_auth_ind = len(proj)
last_auth_ind = 0
for ind, child in enumerate(proj):
    if re.search(r"(Doc)|(RespDsgnr)",child.tag) is not None:
        if ind < first_auth_ind:
            first_auth_ind = ind
        if ind > last_auth_ind:
            last_auth_ind = ind
# This is error checking, only deleting tags if there were any tags found at all.
if first_auth_ind < last_auth_ind:
    for i in range(last_auth_ind, first_auth_ind-1, -1):
        proj.remove(proj[i])
else:
    print("No Document Author / Responsible Designer tags found or removed. Did you open this file in CBECC-2022 before running the script?")

# This removes any Hole Door constructions
for dr in root.findall(".//DrCons"):
    if dr[0].text == "HoleDoor":
        proj.remove(dr)
for spc in root.findall(".//Dr/.."):
    for child in spc.findall("./Dr"):
        if child.text == "HoleDoor":
            spc.remove(child)

# Sets what Construction Assembly / Story tags to search for depending on if the file is NR or R
consassm = ".//ConsAssm"
story = ".//Stoy"
if b_type == "R":
    consassm = ".//ResConsAssm"
    story = ".//ResZnGrp"

# This removes Attic constructions & Floors with Attics in them for both Residential and NonResidential
for rca in root.findall(consassm):
    for child in rca.findall("./Name"):
        if len(re.findall("(Attic)",child.text)) != 0:
            proj.remove(rca)
for parent in root.findall(story):
    for child in parent.findall("./Name"):
        if len(re.findall("(Attic)",child.text)) != 0:
            bldg.remove(parent)

# This makes ALL vent sources for spaces be Forced if not already done so
for vs in root.findall(".//VentSrc"):
    vs.text = "Forced"

# This section removes necessary sections based on tags
if len(bldg.findall("./TotStoryCnt")) != 0:
    bldg.remove(bldg.findall("./TotStoryCnt")[0])
if len(bldg.findall("./AboveGrdStoryCnt")) != 0:
    bldg.remove(bldg.findall("./AboveGrdStoryCnt")[0])
if len(bldg.findall("./HighRiseResLivingUnitCnt")) != 0:
    bldg.remove(bldg.findall("./HighRiseResLivingUnitCnt")[0])
if len(bldg.findall("./HotelMotelGuestRmCnt")) != 0:
    bldg.remove(bldg.findall("./HotelMotelGuestRmCnt")[0])
for tz in bldg.findall("./ThrmlZn"):
    if len(tz.findall("./VentSysRef")) != 0:
        tz.remove(tz.findall("./VentSysRef")[0])
for sp in bldg.findall(".//Spc"):
    if len(sp.findall("./SkyltReqExcpt")) != 0:
        sp.remove(sp.findall("./SkyltReqExcpt")[0])
    if len(sp.findall("./SkyltReqExcptFrac")) != 0:
        sp.remove(sp.findall("./SkyltReqExcptFrac")[0])
    if len(sp.findall("./RecptPwrDens")) != 0:
        sp.remove(sp.findall("./RecptPwrDens")[0])
    if len(sp.findall("./VentPerPerson")) != 0:
        sp.remove(sp.findall("./VentPerPerson")[0])
    if len(sp.findall("./VentPerArea")) != 0:
        sp.remove(sp.findall("./VentPerArea")[0])
    if len(sp.findall("./VentACH")) != 0:
        sp.remove(sp.findall("./VentACH")[0])
    if len(sp.findall("./VentPerSpc")) != 0:
        sp.remove(sp.findall("./VentPerSpc")[0])
    if len(sp.findall("./ExhPerArea")) != 0:
        sp.remove(sp.findall("./ExhPerArea")[0])
    if len(sp.findall("./ExhACH")) != 0:
        sp.remove(sp.findall("./ExhACH")[0])
    if len(sp.findall("./ExhPerSpc")) != 0:
        sp.remove(sp.findall("./ExhPerSpc")[0])
    if len(sp.findall("./IntLPDReg")) != 0:
        sp.remove(sp.findall("./IntLPDReg")[0])
    if len(sp.findall("./IntLtgRegHtGnSpcFrac")) != 0:
        sp.remove(sp.findall("./IntLtgRegHtGnSpcFrac")[0])
    if len(sp.findall("./IntLtgRegHtGnRadFrac")) != 0:
        sp.remove(sp.findall("./IntLtgRegHtGnRadFrac")[0])

# This updates Non-Residential Fenestration values SHGC, U Factor, Product Type, to default / user desired values
for child in root.findall(".//SHGC"):
    child.text = SHGC
for child in root.findall(".//UFactor"):
    child.text = U_Factor
for child in root.findall(".//FenProdType"):
    if Fen_Product_Type == "0":
        child.text = "CurtainWall"
    else:
        child.text = Fen_Product_Type

# Updates Residential Windows SHGC, U Factor to default / user desired values
for reswin in root.findall(".//ResWinType"):
    # Checks to see if "NFRC U-Factor" tag exists. If so, update to desired value, otherwise, create and set to desired value.
    if len(reswin.findall("NFRCUfactor")) == 0:
        r_ufactor = ET.SubElement(reswin, "NFRCUfactor")
        r_ufactor.text = U_Factor
    else:
        reswin.findall("NFRCUfactor")[0].text = str(0.45)
    
    # Checks to see if "NFRC SHGC" tag exists. If so, update to desired value, otherwise, create and set to desired value.
    if len(reswin.findall("NFRCSHGC")) == 0:
        r_shgc = ET.SubElement(reswin, "NFRCSHGC")
        r_shgc.text = SHGC
    else:
        reswin.findall("NFRCSHGC")[0].text = str(0.3)

if b_type == "NR":
    # Remove and replace default NR Materials & Construction Assemblies (keeps custom names)
    default_mat = ["Air Metal Wall Framing 16 or 24in.","Carpet","Cavity","Ceiling Tile","Composite 16in OC R-0","Composite 16in OC R-21",
                "Concrete - 140 lb/ft3 - 4 in","Concrete 140lb 8in","Concrete 140lb 10in","Ctns Ins R-0.01","Ctns Ins R-0.10","Ctns Ins R-0.50",
                "Ctns Ins R-1","Ctns Ins R-2","Ctns Ins R-5","Ctns Ins R-10","Ctns Ins R-15","Ctns Ins R-20","Ctns Ins R-25","Ctns Ins R-26",
                "Ctns Ins R-30","Gypsum 5/8 in.","Metal Rain Screen","Metal Deck - 1/16in."]
    for child in proj.findall("Mat"):
        if child[0].text in default_mat:
            proj.remove(child)
    default_ca = ["Ground contact wall: Depth = 12ft","Ground contact floor: Depth = 12ft","2013 Roof","2013 Internal Ceiling/Floor","2013 External Wall",
                    "2013 Internal Partition","2013 Exposed Floor","Int Partition Demising"]
    for child in proj.findall("ConsAssm"):
        if child[0].text in default_ca:
            proj.remove(child)

    # The following contains a string of default CBECC materials and constructions to be added
    add_mat_con_str = "<Proj>\
    <ConsAssm><Name>Ground contact wall: Depth = 12ft</Name><CompatibleSurfType>ExteriorWall</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Concrete 140lb 10in</MatRef><MatRef index=\"1\">- none -</MatRef><MatRef index=\"2\">- none -</MatRef></ConsAssm>\
    <ConsAssm><Name>Ground contact floor: Depth = 12ft</Name><CompatibleSurfType>ExteriorFloor</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Concrete 140lb 10in</MatRef><MatRef index=\"1\">- none -</MatRef><MatRef index=\"2\">- none -</MatRef><MatRef index=\"3\">- none -</MatRef></ConsAssm>\
    <ConsAssm><Name>Roof</Name><CompatibleSurfType>Roof</CompatibleSurfType><SpecMthd>Layers</SpecMthd><FieldAppliedCoating>0</FieldAppliedCoating><CRRCInitialRefl>0.9</CRRCInitialRefl><CRRCAgedRefl>0.85</CRRCAgedRefl><CRRCInitialEmit>0.85</CRRCInitialEmit><CRRCAgedEmit>0.85</CRRCAgedEmit><MatRef index=\"0\">Ctns Ins R-26</MatRef><MatRef index=\"1\">Concrete 140lb 10in</MatRef><MatRef index=\"2\">Cavity</MatRef><MatRef index=\"3\">Ceiling Tile</MatRef><MatRef index=\"4\">- none -</MatRef><RoofDens>0</RoofDens><BuiltUpRoof>0</BuiltUpRoof><BallastedRoof>0</BallastedRoof></ConsAssm>\
    <ConsAssm><Name>Internal Ceiling/Floor</Name><CompatibleSurfType>InteriorFloor</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Metal Deck - 1/16in.</MatRef><MatRef index=\"1\">Concrete 140lb 10in</MatRef><MatRef index=\"2\">Carpet</MatRef><MatRef index=\"3\">- none -</MatRef><MatRef index=\"4\">- none -</MatRef><MatRef index=\"5\">- none -</MatRef></ConsAssm>\
    <ConsAssm><Name>External Wall</Name><CompatibleSurfType>ExteriorWall</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Metal Rain Screen</MatRef><MatRef index=\"1\">Ctns Ins R-2</MatRef><MatRef index=\"2\">Composite 16in OC R-21</MatRef><MatRef index=\"3\">- none -</MatRef><MatRef index=\"4\">- none -</MatRef><MatRef index=\"5\">- none -</MatRef></ConsAssm>\
    <ConsAssm><Name>Internal Partition</Name><CompatibleSurfType>InteriorWall</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Gypsum 5/8 in.</MatRef><MatRef index=\"1\">Air Metal Wall Framing 16 or 24in.</MatRef><MatRef index=\"2\">Gypsum 5/8 in.</MatRef></ConsAssm>\
    <ConsAssm><Name>Exposed Floor</Name><CompatibleSurfType>ExteriorFloor</CompatibleSurfType><MatRef index=\"0\">Concrete 140lb 10in</MatRef><MatRef index=\"1\">Carpet</MatRef></ConsAssm>\
    <ConsAssm><Name>Int Partition Demising</Name><CompatibleSurfType>InteriorWall</CompatibleSurfType><SpecMthd>Layers</SpecMthd><MatRef index=\"0\">Ctns Ins R-2</MatRef><MatRef index=\"1\">Composite 16in OC R-21</MatRef><MatRef index=\"2\">- none -</MatRef></ConsAssm>\
    <Mat><Name>Air Metal Wall Framing 16 or 24in.</Name><CodeCat>Air</CodeCat><CodeItem>Air - Metal Wall Framing - 16 or 24 in. OC</CodeItem></Mat>\
    <Mat><Name>Carpet</Name><CodeCat>Finish Materials</CodeCat><CodeItem>Carpet - 3/4 in.</CodeItem></Mat>\
    <Mat><Name>Cavity</Name><CodeCat>Air</CodeCat><CodeItem>Air - Cavity - Wall Roof Ceiling - 4 in. or more</CodeItem></Mat>\
    <Mat><Name>Ceiling Tile</Name><CodeCat>Finish Materials</CodeCat><CodeItem>Acoustic Tile - 1/2 in.</CodeItem></Mat>\
    <Mat><Name>Composite 16in OC R-0</Name><CodeCat>Composite</CodeCat><CodeItem/><FrmMat>Metal</FrmMat><FrmConfig>Wall16inOC</FrmConfig><FrmDepth>3_5In</FrmDepth><CavityInsOpt>R-0</CavityInsOpt></Mat>\
    <Mat><Name>Composite 16in OC R-21</Name><CodeCat>Composite</CodeCat><CodeItem/><FrmMat>Metal</FrmMat><FrmConfig>Wall16inOC</FrmConfig><FrmDepth>5_5In</FrmDepth><CavityInsOpt>R-21</CavityInsOpt></Mat>\
    <Mat><Name>Concrete - 140 lb/ft3 - 4 in</Name><CodeCat>Concrete</CodeCat><CodeItem>Concrete - 140 lb/ft3 - 4 in.</CodeItem></Mat>\
    <Mat><Name>Concrete 140lb 8in</Name><CodeCat>Concrete</CodeCat><CodeItem>Concrete - 140 lb/ft3 - 8 in.</CodeItem></Mat>\
    <Mat><Name>Concrete 140lb 10in</Name><CodeCat>Concrete</CodeCat><CodeItem>Concrete - 140 lb/ft3 - 10 in.</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-0.01</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R0.01</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-0.10</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R0.10</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-0.50</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R0.10</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-1</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R1.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-2</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R2.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-5</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R5.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-10</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R10.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-15</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R15.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-20</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R20.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-25</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R25.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-26</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R26.00</CodeItem></Mat>\
    <Mat><Name>Ctns Ins R-30</Name><CodeCat>Insulation Board</CodeCat><CodeItem>Compliance Insulation R30.00</CodeItem></Mat>\
    <Mat><Name>Gypsum 5/8 in.</Name><CodeCat>Bldg Board and Siding</CodeCat><CodeItem>Gypsum Board - 5/8 in.</CodeItem></Mat>\
    <Mat><Name>Metal Rain Screen</Name><CodeCat>Bldg Board and Siding</CodeCat><CodeItem>Metal Siding - 1/16 in.</CodeItem></Mat>\
    <Mat><Name>Metal Deck - 1/16in.</Name><CodeCat>Bldg Board and Siding</CodeCat><CodeItem>Metal Deck - 1/16 in.</CodeItem></Mat>\
    </Proj>"
    # The following turns the above string into a workable element and adds it before the end of the <Proj> tag in the original file
    add_mat_con = ET.fromstring(add_mat_con_str)
    ET.indent(add_mat_con)
    for child in add_mat_con:
        proj.append(child)

if b_type == "R":
    # Remove all Residential Construct Assemblies
    for child in proj.findall("ResConsAssm"):
        proj.remove(child)
    
    # The following contains a string of default CBECC materials and constructions to be added
    add_res_cons = "<Proj>\
    <ResConsAssm><Name>Ext Wall Cons</Name><CanAssignTo>Exterior Walls</CanAssignTo><Type>Steel Framed Wall</Type><SheathInsul2Layer>R2 Sheathing</SheathInsul2Layer>\
    <CavityLayer>R  2</CavityLayer><FrameLayer>2x6 @ 16 in. O.C.</FrameLayer><SheathInsulLayer>R2 Sheathing</SheathInsulLayer>\
    <SheathInsulLayerRVal>4</SheathInsulLayerRVal><WallExtFinishLayer>All Other Siding</WallExtFinishLayer></ResConsAssm><ResConsAssm>\
    <Name>Interior Floor Cons</Name><CanAssignTo>Interior Floors</CanAssignTo><Type>Concrete / ICF / Brick</Type><MassLayer>Concrete</MassLayer>\
    <MassThickness>10 in.</MassThickness><FurringInsulLayer>R  2</FurringInsulLayer></ResConsAssm><ResConsAssm><Name>Interior Wall Cons</Name>\
    <CanAssignTo>Interior Walls</CanAssignTo><Type>Steel Framed Wall</Type><InsideFinishLayer>- select inside finish -</InsideFinishLayer>\
    <OtherSideFinishLayer>- select inside finish -</OtherSideFinishLayer></ResConsAssm><ResConsAssm><Name>Roof Cons</Name><CanAssignTo>Cathedral Ceilings</CanAssignTo>\
    <Type>Built-up Roof</Type><RoofingLayer>25 PSF (Very Heavy Ballast or Pavers)</RoofingLayer><CavityLayer>R 41</CavityLayer>\
    <FrameLayer>2x4 @ 24 in. O.C.</FrameLayer></ResConsAssm><ResConsAssm><Name>Undergrd Wall Cons</Name><CanAssignTo>Underground Walls</CanAssignTo>\
    </ResConsAssm></Proj>"

    # The following turns the above string into a workable element and adds it before the end of the <Proj> tag in the original file
    add_res_con = ET.fromstring(add_res_cons)
    ET.indent(add_res_con)
    for child in add_res_con:
        proj.append(child)

# This removes 2013 from the names of Construction Assembly and Fenestration Constructions for both Residential and NonResidential
list_cons_rem = [".//ConsAssm",".//ResConsAssm",".//FenCons"]
for ca in list_cons_rem:
    for rm2013 in root.findall(ca):
        for child in rm2013.findall("./Name"):
            name = re.findall(r"(^2013\s)(.*)",child.text)
            if len(name) > 0:
                child.text = str(name[0][1])
# This removes 2013 from the REFERENCES to the Construction Assembly / Fenestration Cons
list_cons_rem = [".//ConsAssmRef",".//FenConsRef"]
for ca in list_cons_rem:
    for rm2013 in root.findall(ca):
        name = re.findall(r"(^2013\s)(.*)",rm2013.text)
        if len(name) > 0:
            rm2013.text = str(name[0][1])

# Checks to see if the Ground Floor construction exists- if not, will add it at the bottom of <Proj>
if len(root.findall(".//GroundFloor")) == 0:
    # The following turns the above string into a workable element and adds it before the end of the <Proj> tag in the original file
    grndflr = ET.fromstring("<Proj><ConsAssm><Name>GroundFloor</Name><CompatibleSurfType>UndergroundFloor</CompatibleSurfType><SlabType>UnheatedSlabOnGrade</SlabType></ConsAssm></Proj>")
    ET.indent(grndflr)
    for child in grndflr:
        proj.append(child)
# Changes existing bottom/external floors to use the above Underground floor
for ef in root.findall(".//ExtFlr"):
    ef[2].text = "GroundFloor"
    ef.tag = "UndgrFlr"

# This writes the changes made to the output file
ET.indent(tree)
tree.write(output_filename)
