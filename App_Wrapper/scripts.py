import xml.etree.ElementTree as ET
import re, glob
import pandas as pd

# ---------------------------------------------------------------------------------------------------------------------------
## *** ies_to_cbecc.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def ies_to_cbecc_run(input_f, output_f, f_uvalue, f_shgc, attic_check):
    ## ** USER INPUT ** -------------------
    # File Names:
    input_filename = str(input_f)
    if len(input_filename) == 0:
        exit("Enter an input file.")
    output_filename = str(output_f)
    if len(output_filename) == 0:
        output_filename = input_filename
    elif len(re.findall(r".cibd22x$",output_filename)) == 0:
        output_filename = output_filename + ".cibd22x"
    # Fenestration Inputs:
    SHGC = str(f_shgc)
    U_Factor = str(f_uvalue)
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
    # else:
    #     print("No Document Author / Responsible Designer tags found or removed. Did you open this file in CBECC-2022 before running the script?")

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
    if attic_check == False:
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
        <ConsAssm>\n<Name>Roof</Name>\n<CompatibleSurfType>Roof</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<FieldAppliedCoating>0</FieldAppliedCoating>\n<CRRCInitialRefl>0.9</CRRCInitialRefl>\n<CRRCAgedRefl>0.85</CRRCAgedRefl><CRRCInitialEmit>0.85</CRRCInitialEmit>\n<CRRCAgedEmit>0.85</CRRCAgedEmit>\n<MatRef index=\"0\">Ctns Ins R-26</MatRef>\n<MatRef index=\"1\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"2\">Cavity</MatRef>\n<MatRef index=\"3\">Ceiling Tile</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<RoofDens>0</RoofDens>\n<BuiltUpRoof>0</BuiltUpRoof>\n<BallastedRoof>0</BallastedRoof>\n</ConsAssm>\n\
        <ConsAssm>\n<Name>Internal Ceiling/Floor</Name>\n<CompatibleSurfType>InteriorFloor</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Metal Deck - 1/16in.</MatRef>\n<MatRef index=\"1\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"2\">Carpet</MatRef>\n<MatRef index=\"3\">- none -</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<MatRef index=\"5\">- none -</MatRef>\n</ConsAssm>\n\
        <ConsAssm>\n<Name>External Wall</Name>\n<CompatibleSurfType>ExteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Metal Rain Screen</MatRef>\n<MatRef index=\"1\">Ctns Ins R-2</MatRef>\n<MatRef index=\"2\">Composite 16in OC R-21</MatRef>\n<MatRef index=\"3\">- none -</MatRef>\n<MatRef index=\"4\">- none -</MatRef>\n<MatRef index=\"5\">- none -</MatRef>\n</ConsAssm>\n\
        <ConsAssm>\n<Name>Internal Partition</Name>\n<CompatibleSurfType>InteriorWall</CompatibleSurfType>\n<SpecMthd>Layers</SpecMthd>\n<MatRef index=\"0\">Gypsum 5/8 in.</MatRef>\n<MatRef index=\"1\">Air Metal Wall Framing 16 or 24in.</MatRef>\n<MatRef index=\"2\">Gypsum 5/8 in.</MatRef>\n</ConsAssm>\n\
        <ConsAssm>\n<Name>Exposed Floor</Name>\n<CompatibleSurfType>ExteriorFloor</CompatibleSurfType>\n<MatRef index=\"0\">Concrete 140lb 10in</MatRef>\n<MatRef index=\"1\">Carpet</MatRef>\n</ConsAssm>\n\
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

# ---------------------------------------------------------------------------------------------------------------------------
## *** combine_nonres_res.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

global nr_tree, nr_bldg, nr_root
global r_tree, r_proj, r_bldg, r_root
global combined_storeys

def nr_r_precheck(nr_input, r_input):
    global nr_tree, nr_bldg, nr_root
    global r_tree, r_proj, r_bldg, r_root
    global combined_storeys

    ## ** USER INPUT ** -------------------
    # File Names:
    # File Names:
    nr_filename = nr_input
    if len(nr_filename) == 0:
        exit("Enter a NR input file.")
    r_filename = r_input
    if len(r_filename) == 0:
        exit("Enter a R input file.")
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
    
    return combined_storeys

def nr_r_run(f_output, split_ind):
    global nr_tree, nr_bldg, nr_root
    global r_tree, r_proj, r_bldg, r_root
    global combined_storeys

    output_filename = f_output
    if len(output_filename) == 0:
        exit("Enter an output filename.")

    story_split_ind = str(split_ind)
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

# ---------------------------------------------------------------------------------------------------------------------------
## *** base_szhp_generator.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

def SZHP(bldg, tz):
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

def szhp_tz_loader(input_filename):
    # This creates an ElementTree out of the input file to make easier edits
    tree = ET.parse(input_filename)
    root = tree.getroot()

    szhp_list = []

    for tz in root.findall(".//ThrmlZn"):
        if tz[1].text == "Conditioned":
            szhp_list.append(tz[0].text)

    return szhp_list

def szhp_generator_run(input_f, szhp_list, output_f):
    input_filename = input_f
    output_filename = output_f

    # This creates an ElementTree out of the input file to make easier edits
    tree = ET.parse(input_filename)
    root = tree.getroot()
    bldg = root.findall("./Proj/Bldg")[0]
    
    # Adding SZHP to all Conditioned NonRes Thermal Zones
    for tz in root.findall(".//ThrmlZn"):
        if tz[1].text == "Conditioned":
            if tz[0].text in szhp_list:
                SZHP(bldg, tz)

    # This writes the changes made to the output file
    ET.indent(tree)
    tree.write(output_filename)

# ---------------------------------------------------------------------------------------------------------------------------
## *** base_doas_generator.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

global doas_tree

def doas_tz_loader(input_filename):
    global doas_tree

    # This creates an ElementTree out of the input file to make easier edits
    doas_tree = ET.parse(input_filename)
    doas_root = doas_tree.getroot()

    doas_list = []

    for tz in doas_root.findall(".//ThrmlZn"):
        if tz[1].text == "Conditioned":
            doas_list.append(tz[0].text)

    return doas_list

def doas_generator_run(doas_tz, doas_count):
    global doas_tree

    doas_root = doas_tree.getroot()
    bldg = doas_root.findall("./Proj/Bldg")[0]

    name = "DOAS "+str(doas_count)

    doas = add_subelement(bldg,"AirSys")
    add_subelement(doas,"Name",text=name)
    add_subelement(doas,"Type",text="DOASVAV")
    add_subelement(doas,"CtrlSysType",text="DDCToZone")
    add_subelement(doas,"AirFlowPerSqFt",text="1.0")
    add_subelement(doas,"ClgCtrl",text="FixedDualSetpoint")
    add_subelement(doas,"ClgFixedSupTemp",text="75")
    add_subelement(doas,"HtgFixedSupTemp",text="55")
    add_AirSeg(doas,name,type="Supply")
    add_AirSeg(doas,name,type="Return",airsystem="DOAS")
    add_OACtrl(doas,name)

    for tz in doas_root.findall(".//ThrmlZn"):
        if tz[0].text in doas_tz:
            zn_name = str(tz[0].text)
            add_TermUnit(doas, name=zn_name)

            if len(tz.findall("PriAirCondgSysRef")) == 0:
                pri_ac = ET.SubElement(tz,"PriAirCondgSysRef",attrib={"index":"0"})
                pri_ac.text = name
            if len(tz.findall("VentSysRef")) == 0:
                vsr = ET.SubElement(tz,"VentSysRef")
                vsr.text = name
    
def doas_save(output_filename):
    global doas_tree
    # This writes the changes made to the output file
    ET.indent(doas_tree)
    doas_tree.write(output_filename)


# ---------------------------------------------------------------------------------------------------------------------------
## *** results_compiiler.py *** ##
# ---------------------------------------------------------------------------------------------------------------------------

global files

def found_log_count(logs_path):
  global files
  # This searches the entered log path and any subdirectories for log CSV files.
  files = glob.glob('**/*log.csv',root_dir=logs_path,recursive=True)
  return str(len(files))

def logs_compile_run(logs_path):
  global files
  # Base creation for the Annual TDV standard/proposed table
  header = ["Case Name", "Conditioned Floor Area (SF)", "HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT","PROC. MTRS",\
                "PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT",\
                  "PROC. MTRS","PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS",\
                      "OTH LGHT","PROC. MTRS","PV","BATTERY"]
  output_df = pd.DataFrame()

  # Stepping through every log file found to pull the correct numbers / perform math and get annual values.
  for filename in files:
    # This will save the start date and filename for each run to be appended with data 
    fpath = logs_path + "\\" + filename
    df = pd.read_csv(fpath,index_col=False,skiprows=2)

    # In case multiple runs within one log file, this will step through each run and append.
    # NOTE: this may result in keeping unwanted results. Read the output log file carefully.
    for i in range(len(df.index)):
      dt = df.iloc[i,0]
      casename = df.iloc[i,1]
      area = df.iloc[i,5]
      arr = df.to_numpy()
      li = arr.tolist()

      b_l1 = arr[i][86:93]+29.3*arr[i][101:108]+0.293*arr[i][114:121]/1000
      b_l2 = arr[i][94:98]+29.3*arr[i][108:112]+0.293*arr[i][122:126]/1000
      p_l1 = arr[i][14:21]+29.3*arr[i][29:36]+0.293*arr[i][42:49]/1000
      p_l2 = arr[i][22:26]+29.3*arr[i][37:41]+0.293*arr[i][50:54]/1000

      standard = [casename, area]+li[i][127:134]+li[i][135:141]+li[i][262:269]+li[i][270:276]+b_l1.tolist()+b_l2.tolist()+li[i][98:100]
      proposed = [casename, area]+li[i][55:62]+li[i][64:70]+li[i][247:254]+li[i][255:261]+p_l1.tolist()+p_l2.tolist()+li[i][26:28]

      # This appends the calculated run information to the output dataframe
      if output_df.empty:
        output_df = pd.DataFrame([standard,proposed],index=[dt+" Standard",dt+" Proposed"],columns=header)
      else:
        output_df = pd.concat([output_df,pd.DataFrame([standard,proposed],index=[dt+" Standard",dt+" Proposed"],columns=header)])

  # This saves all the annual TDV calculations for each run into the original log path with the given output file name "output_fname"
  output_df.to_csv(logs_path+"\\Logs.csv")


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
