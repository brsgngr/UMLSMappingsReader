UMLSMappingReader
=========

Introduction
-------------------
This python script queries the [UMLS API](https://documentation.uts.nlm.nih.gov/) in order to identify UMLS mappings for a list of ICD-10-GM, LOINC or OPS codes. For each input code, the corresponding concept ID (CUI) is searched in UMLS, and then mappings associated with the identified CUI are listed.


Explanation of files
-------------------
This repository includes the following files:
- `README.md`: 	This explanation.
- `umlsMappingsReader.py`: Executable python file; contains necessary functions.
- `config.py`: 	Config file, which contains the UMLS-API-Key (see below).
- `input_icd.txt`: Contains all ICD-10-GM codes to be examined by the UMLSMappingReader.
- `input_loinc.txt`: Contains all LOINC codes to be examined by the UMLSMappingReader.
- `input_ops.txt`: Contains all OPS codes to be examined by the UMLSMappingReader.
- `OPS-SNOMED_map.csv`: Contains a list of OPS-SNOMED-CT-Mappings. Can be downloaded here https://open.trinetx.com/download/

A successful run of UMLSMappingReader will create the following files:
- `input_icd_all_atoms.txt`: Contains all found atoms (mappings) from UMLS for all ICD-10-GM codes.
- `input_icd_mapping_frequency.txt`: Contains all mapping frequencies for each terminology based on the file input_icd_all_atoms.txt.
- `input_loinc_all_atoms.txt`: Contains all found atoms (mappings) from UMLS for all LOINC codes.
- `input_loinc_mapping_frequency.txt`: Contains all mapping frequencies for each terminology based on the file input_loinc_all_atoms.txt.
- `input_ops_all_atoms.txt`: Contains all found atoms (mappings) from UMLS for all OPS codes.
- `input_ops_mapping_frequency.txt`: Contains all mapping frequencies for each terminology based on the file input_ops_all_atoms.txt.
- `OPS_SNOMED_map.txt`: This file is created when running the UMLSMappingReaderfor OPS codes. This file commits the OPS-SNOMED-CT-Mappings from OPS-SNOMED_map.csv to another format and is only used for internal execution. 


Requirements and configuration
-------------------
Before running the script, ensure the following requirements:
1. Python packages are installed: `lxml`, `prettytable`, `requests`
2. Insert your API-KEY from UMLS into config.py. Get your API key from your UTS profile. You can find the API key in the UTS ‘My Profile’ area after signing in (https://uts.nlm.nih.gov/).
3. Do not rename the config.py file. All other files can be renamed.
4. Insert your ICD-10-GM, LOINC an OPS Codes into the respective input files. Each code must be on a new line. There are some random sample codes in the input files, which can be used for test purposes. 
5. In case of OPS, make sure you have downloaded the OPS-SNOMED-CT-Mappings file. For this purpose, this file can be downloaded https://open.trinetx.com/download/.
 

Execution
-------------------
Command line invocations may look like this:

```
umlsMappingsReader.py -i input_icd.txt -l input_loinc.txt -o input_ops.txt OPS-SNOMED_map.csv 

-i : expects the name of an input file with ICD-10-GM codes
-l : expects the name of an input file with LOINC codes
-o : expects the name of an input files with OPS codes AND the name of another csv-File with OPS-SNOMED-mappings.

```
These commands can be executed in any combination.

Outputs
-------------------
Two output files are always created per terminology. 
 * `..._all_atoms.txt` contains all found atoms (mappings) from UMLS for the respective terminology.
 * `..._mapping_frequency.txt` contains all mapping frequencies based on the file `..._all_atoms.txt`.

These text files can be integrated into any visualization tool. E.g. Excel can be used for this purpose.


Limitations & Terms of use
-------------------
 * UMLS API limitations: https://documentation.uts.nlm.nih.gov/terms-of-service.html
* TriNetX terms of use: https://trinetx.com/terms-of-use/

