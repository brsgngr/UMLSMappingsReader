UMLSMappingReader README

Introduction
-------------------
This python script can be used to examine a list of ICD-10-GM, LOINC or OPS codes for mappings in UMLS. First, the concept ID (CUI) stored in UMLS for the code is identified and second, all mappings based on the CUI are listed.


Explanation of the files
-------------------
Before running UMLSMappingReader, following files can be find in the progamm folder:
- README.txt: 	Contains all important information to run the script.
- umlsMappingsReader.py: Main python file for execution. Contains all necessary functions.
- config.py: 	Config file, which contains the UMLS-API-Key.
- input_icd.txt:Contains all ICD-10-GM codes to be examined by the UMLSMappingReader.
- input_loinc.txt:Contains all LOINC codes to be examined by the UMLSMappingReader.
- input_ops.txt:Contains all OPS codes to be examined by the UMLSMappingReader.
- OPS-SNOMED_map.csv: Contains a list of OPS-SNOMED-CT-Mappings. Can be downloaded here https://open.trinetx.com/download/

After running UMLSMappingReader, following files will be created:
- input_icd_all_atoms.txt: Contains all found atoms (mappings) from UMLS for all ICD-10-GM codes.
- input_icd_mapping_frequency.txt: Contains all mapping frequencies for each terminology based on the file input_icd_all_atoms.txt.
- input_loinc_all_atoms.txt: Contains all found atoms (mappings) from UMLS for all LOINC codes.
- input_loinc_mapping_frequency.txt: Contains all mapping frequencies for each terminology based on the file input_loinc_all_atoms.txt.
- input_ops_all_atoms.txt: Contains all found atoms (mappings) from UMLS for all OPS codes.
- input_ops_mapping_frequency.txt: Contains all mapping frequencies for each terminology based on the file input_ops_all_atoms.txt.
- OPS_SNOMED_map.txt: This file is created when running the UMLSMappingReaderfor OPS codes. This file commits the OPS-SNOMED-CT-Mappings from OPS-SNOMED_map.csv to another format and is only used for internal execution. 


Preparation
-------------------
Make sure of the following points before running the script:
1. Python packages are installed: lxml, prettytable, requests
2. Insert API-KEY from UMLS into config.py. Get your API key from your UTS profile.You can find the API key in the UTS ‘My Profile’ area after signing in (https://uts.nlm.nih.gov/).
3. Do not rename the config.py file. All other files can be renamed.
4. Insert your ICD-10-GM, LOINC an OPS Codes into the respective input files. Each code must be on a new line. There are some random sample codes in the input files, which can be used for test purposes. 
5. In case of OPS, make sure you have downloaded the OPS-SNOMED-CT-Mappings file. For this purpose, this file can be downloaded https://open.trinetx.com/download/.
 

Execution
-------------------
The command line could look like this:

python .\umlsMappingsReader.py -i input_icd.txt -l input_loinc.txt -o input_ops.txt OPS-SNOMED_map.csv 

-i : expectes name of the input file with the ICD-10-GM codes
-l : expectes name of the input file with the LOINC codes
-o : expectes name of the input files with the OPS codes AND name of the csv-File with OPS-SNOMED-Mappings.

The commands can be executed in any combination.


Outcomes
-------------------
Two output files are always created per terminology. 
..._all_atoms.txt contains all found atoms (mappings) from UMLS for the respective terminology.
..._mapping_frequency.txt contains all mapping frequencies based on the file ..._all_atoms.txt.

These text files can be integrated into any visualization tool. E.g. Excel can be used for this purpose.


Limitations & Terms of use
-------------------
UMLS API limitations: https://documentation.uts.nlm.nih.gov/terms-of-service.html
TriNetX terms of use: https://trinetx.com/terms-of-use/

