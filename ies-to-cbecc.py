import xml.etree.ElementTree as ET
import re

## ** USER INPUT ** -------------------
# File Names:
input_filename = input("Enter Input File Name/Path: ")
if len(input_filename) == 0:
    exit("Enter an input file.")
output_filename = input("Enter Output File Name/Path (leave blank to overwrite input): ")
if len(output_filename) == 0:
    output_filename = input_filename
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
for child in root.findall(".//GeometryInpType"):
    b_type = "R"
    child.text = "Detailed"

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
story = ".//Story"
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
    add_mat_con_str = "<Proj>\n\
    <ConsAssm>\n<Name>Ground contact wall: Depth = 12ft</Name>\n<CompatibleSurfType>ExteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"1\">- none -</MatRef>\n<MatRef index=\"2\">- none -</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>Ground contact floor: Depth = 12ft</Name>\n<CompatibleSurfType>ExteriorFloor</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"1\">- none -</MatRef>\n<MatRef index=\"2\">- none -</MatRef>\n<MatRef index=\"3\">- none -</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>2013 Roof</Name>\n<CompatibleSurfType>Roof</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<FieldAppliedCoating>0</FieldAppliedCoating>\n<CRRCInitialRefl>0.9</CRRCInitialRefl>\n<CRRCAgedRefl>0.85</CRRCAgedRefl><CRRCInitialEmit>0.85</CRRCInitialEmit>\n<CRRCAgedEmit>0.85</CRRCAgedEmit>\n<MatRef index=\"0\">Ctns Ins R-26</MatRef>\n<MatRef index=\"1\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"2\">Cavity</MatRef>\n<MatRef index=\"3\">Ceiling Tile</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<RoofDens>0</RoofDens>\n<BuiltUpRoof>0</BuiltUpRoof>\n<BallastedRoof>0</BallastedRoof>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>2013 Internal Ceiling/Floor</Name>\n<CompatibleSurfType>InteriorFloor</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Metal Deck - 1/16in.</MatRef>\n<MatRef index=\"1\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"2\">Carpet</MatRef>\n<MatRef index=\"3\">- none -</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<MatRef index=\"5\">- none -</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>2013 External Wall</Name>\n<CompatibleSurfType>ExteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Metal Rain Screen</MatRef>\n<MatRef index=\"1\">Ctns Ins R-2</MatRef>\n<MatRef index=\"2\">Composite 16in OC R-21</MatRef>\n<MatRef index=\"3\">- none -</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<MatRef index=\"5\">- none -</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>2013 Internal Partition</Name>\n<CompatibleSurfType>InteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Gypsum 5/8 in.</MatRef>\n<MatRef index=\"1\">Air Metal Wall Framing 16 or 24in.</MatRef>\n<MatRef index=\"2\">Gypsum 5/8 in.</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>2013 Exposed Floor</Name>\n<CompatibleSurfType>ExteriorFloor</CompatibleSurfType>\n<MatRef index=\"0\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"1\">Carpet</MatRef>\n</ConsAssm>\n\
    <ConsAssm>\n<Name>Int Partition Demising</Name>\n<CompatibleSurfType>InteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Ctns Ins R-2</MatRef>\n<MatRef index=\"1\">Composite 16in OC R-21</MatRef>\n<MatRef index=\"2\">- none -</MatRef>\n</ConsAssm>\n\
    <Mat>\n<Name>Air Metal Wall Framing 16 or 24in.</Name>\n<CodeCat>Air</CodeCat>\n<CodeItem>Air - Metal Wall Framing - 16 or 24 in. OC</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Carpet</Name>\n<CodeCat>Finish Materials</CodeCat>\n<CodeItem>Carpet - 3/4 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Cavity</Name>\n<CodeCat>Air</CodeCat>\n<CodeItem>Air - Cavity - Wall Roof Ceiling - 4 in. or more</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ceiling Tile</Name>\n<CodeCat>Finish Materials</CodeCat>\n<CodeItem>Acoustic Tile - 1/2 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Composite 16in OC R-0</Name>\n<CodeCat>Composite</CodeCat>\n<CodeItem/>\n<FrmMat>Metal</FrmMat>\n<FrmConfig>Wall16inOC</FrmConfig>\n<FrmDepth>3_5In</FrmDepth>\n<CavityInsOpt>R-0</CavityInsOpt>\n</Mat>\n\
    <Mat>\n<Name>Composite 16in OC R-21</Name>\n<CodeCat>Composite</CodeCat>\n<CodeItem/>\n<FrmMat>Metal</FrmMat>\n<FrmConfig>Wall16inOC</FrmConfig>\n<FrmDepth>5_5In</FrmDepth>\n<CavityInsOpt>R-21</CavityInsOpt>\n</Mat>\n\
    <Mat>\n<Name>Concrete - 140 lb/ft3 - 4 in</Name>\n<CodeCat>Concrete</CodeCat>\n<CodeItem>Concrete - 140 lb/ft3 - 4 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Concrete 140lb 8in</Name>\n<CodeCat>Concrete</CodeCat>\n<CodeItem>Concrete - 140 lb/ft3 - 8 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Concrete 140lb 10in</Name>\n<CodeCat>Concrete</CodeCat>\n<CodeItem>Concrete - 140 lb/ft3 - 10 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-0.01</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R0.01</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-0.10</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R0.10</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-0.50</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R0.10</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-1</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R1.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-2</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R2.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-5</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R5.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-10</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R10.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-15</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R15.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-20</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R20.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-25</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R25.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-26</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R26.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Ctns Ins R-30</Name>\n<CodeCat>Insulation Board</CodeCat>\n<CodeItem>Compliance Insulation R30.00</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Gypsum 5/8 in.</Name>\n<CodeCat>Bldg Board and Siding</CodeCat>\n<CodeItem>Gypsum Board - 5/8 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Metal Rain Screen</Name>\n<CodeCat>Bldg Board and Siding</CodeCat>\n<CodeItem>Metal Siding - 1/16 in.</CodeItem>\n</Mat>\n\
    <Mat>\n<Name>Metal Deck - 1/16in.</Name>\n<CodeCat>Bldg Board and Siding</CodeCat>\n<CodeItem>Metal Deck - 1/16 in.</CodeItem>\n</Mat>\n\
    </Proj>"
    # The following turns the above string into a workable element and adds it before the end of the <Proj> tag in the original file
    add_mat_con = ET.fromstring(add_mat_con_str)
    ET.indent(add_mat_con)
    for child in add_mat_con:
        proj.append(child)

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
