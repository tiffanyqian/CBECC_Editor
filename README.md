# **CBECC_Editor**
Helper package intended to help optimize repetitive steps in the T24 workflow when converting from IES to CBECC.

Only outside dependency is pandas in "results_compiler.py", otherwise works with just Python Standard Library.

*Currently only supports edits/conversions with CBECC 2022 (tested on 2022.3.1). Conversion was tested from both IES 2019 and IES 2023.*

> ## **!!! BEFORE RUNNING ANYTHING !!!**
> For **all files**, _Non-Residential_ AND _Residential_ files, open in CBECC and save as a .cibd22x file to have CBECC default some values. This also means if working file type is .xml, open it in CBECC and save it as a .cibd22x file to make any edits.

Main files
* **ies-to-cbecc.py** - Converts files from IES (of type .xml, .cibd22x) to CBECC acceptable files
    * Adds a list of CBECC-Com default materials and construction as defined in IES. This can be replaced.
    * Ability to set specific Fenestration values such as U-Value, SHGC, Construction Type if desired
    * Removes hole doors due to it causing CBECC errors 
* **combine_nonres_res.py** - For multi-family workflow, will combine the 2019 IES Non-Residential version of a model with the 2023 Residential version of a model, based on user specified split.
    * Redundancies in zones accounted for
    * File will prompt user with further details
* **hvac_components.py** - Contains methods to create components necessary for Mechanical Systems
    * Currently contains methods for creating CoilCooling, CoilHeating, Fan, OutsideAirControl, TerminalUnit, AirSegment
    * *WARNING: needs more fine-tuning and commenting: currently only tested for SZHP and DOAS additions* 
* **base_doas_generator.py** - Generates a number of DOAS AirSystems for specified thermal zones
    * Depends on hvac_components.py
    * File will prompt user with number of DOAS systems to create and the available zones given the input file. Error handling will discard errors in user input.
* **base_szhp_generator.py** - Generates SZHP AirSystems for specified thermal zones
    * Depends on hvac_components.py
    * File will prompt user with SZHP creation for all thermal zones or to manually determine SZHP creation per zone.

Helper Files
* **CBECC-Com Default Materials and Constructions.xml** - Default CBECC materials and constructions in an .xml file
    * NOTE: keep this in the same folder as **ies-to-cbecc.py**
* **results_compiler** - Takes in a folder location and returns tabled result of all CBECC log files inside
    * Can access all subdirectories as well
* **comparefiles.py** - Basic comparison python file to log differences between two files to "differences.txt"