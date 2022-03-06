#!/usr/bin/env python3
import requests
from lxml.html import fromstring
import argparse
import os
from prettytable import PrettyTable
import json
from json import JSONDecodeError
from config import apikey

########################################################################################################################
######################### Section 1: variables #########################################################################
########################################################################################################################
#delimeter
dm = "|"
tries = 20


########################################################################################################################
######################### Section 2: parser ############################################################################
########################################################################################################################

################################################################################################
# create parser
################################################################################################
parser = argparse.ArgumentParser(description = "umlsMapping parser")

################################################################################################
# defining arguments for parser object
################################################################################################
parser.add_argument("-i", "--icd10gm", type=str, nargs=1,
                    metavar="ICD10GM_input_file", default=None,
                    help="Reads the specified text file with ICD-10-GM codes.")

parser.add_argument("-l", "--loinc", type=str, nargs=1,
                    metavar="LOINC_input_file", default=None,
                    help="Reads the specified text file with LOINC codes.")

parser.add_argument("-o", "--ops", type=str, nargs=2,
                    metavar=('OPS_input_file', 'ops_snomed_ct_mapping_file'),
                    help="Reads the specified text file with OPS codes and maps them to SNOMED CT codes.")

################################################################################################
# parse the arguments from standard input
################################################################################################
args = parser.parse_args()

################################################################################################
# validate file name and path
################################################################################################
# error messages
INVALID_FILETYPE_MSG = "Error: Invalid file format. %s must be a .txt file."
INVALID_PATH_MSG = "Error: Invalid file path/name. Path %s does not exist."

def validate_file(file_name):
    if not valid_path(file_name):
        print(INVALID_PATH_MSG % (file_name))
        quit()
    elif not valid_filetype(file_name):
        print(INVALID_FILETYPE_MSG % (file_name))
        quit()
    return

def valid_filetype(file_name):
    # validate file type
    return file_name.endswith('.txt')

def valid_path(path):
    # validate file path
    return os.path.exists(path)

def validate_file_csv(file_name):
    if not valid_path(file_name):
        print(INVALID_PATH_MSG % (file_name))
        quit()
    elif not valid_filetype_csv(file_name):
        print(INVALID_FILETYPE_MSG % (file_name))
        quit()
    return

def valid_filetype_csv(file_name):
    # validate file type
    return file_name.endswith('.csv')


########################################################################################################################
######################### Section 3: functions #########################################################################
########################################################################################################################

################################################################################################
# returns false if umls_key is not inserted
################################################################################################
def checkapikey():
    if apikey == "":
        print("Please insert the UMLS api-key into the config.py file.")
        return False
    return True

################################################################################################
# prints error message for JSONDecodeError
################################################################################################
def printJSONDecodeError(tryCounter):
    print("JSONDecodeError: Server returns internal server error")
    print("try " + str(tryCounter) + ", programm will be interrupted")

################################################################################################
# get ticket granting ticket
################################################################################################
def gettgt():
    tryCounter = 1
    for tryCounter in range(tries):
        try:
            uriAuth = "https://utslogin.nlm.nih.gov/cas/v1/api-key"
            params = {'apikey': apikey}
            h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent": "python"}
            r = requests.post(uriAuth, data=params, headers=h)
            response = fromstring(r.text)
            return response.xpath('//form/@action')[0]

        except JSONDecodeError:
            if tryCounter < tries - 1:
                tryCounter = tryCounter + 1
                continue
            else:
                printJSONDecodeError(tryCounter)
                raise

################################################################################################
# get Service ticket
################################################################################################
def getst(tgt):
    tryCounter = 1
    for tryCounter in range(tries):
        try:
            # ticket granting ticket (tgt) is in form of https://utslogin.nlm.nih.gov/cas/v1/api-key/TGT-...-cas
            params = {'service': "http://umlsks.nlm.nih.gov"}
            h = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent": "python"}
            r = requests.post(tgt, data=params, headers=h)
            st = r.text
            #print(st)
            return st

        except JSONDecodeError:
            if tryCounter < tries - 1:
                tryCounter = tryCounter + 1
                continue
            else:
                printJSONDecodeError(tryCounter)
                raise



################################################################################################
# read input file and do function
################################################################################################
def readFileAndDoFunction(tgt, inputfile, function, outputFile, onlyrelevants, source, clearOutputfile, isOPS, OPSSNMmappingfileInput, OPSSNMmappingfileOutput):
    inputfile = open(inputfile, 'r')

    #one time
    if clearOutputfile and outputFile != "":
        out = open(outputFile, "w")
        out.write("")
        out.close()

    if function == "fromCodetoCUItoAllAtoms" and outputFile != "":
        out = open(outputFile, "a")
        out.write("inputSource" + dm + "inputCode")
        for field in getfields():
            out.write(dm + field)
        out.write("\n")
        out.close()

    opsmappings = {
        "OPS": "SNOMED"
    }
    if isOPS:
        opsfile = open(OPSSNMmappingfileInput, 'r')
        for line in opsfile:
            opsmappings[line.split(",")[0].strip()] = ''.join(c for c in line.split("|")[0].strip().split(",")[-1].strip() if c.isdigit())
        opsfile.close()
        opsSnmMapping = open(OPSSNMmappingfileOutput, 'w')
        for x in opsmappings:
            opsSnmMapping.write(x + dm + opsmappings[x] + "\n")
        opsSnmMapping.close()

    #for each line
    for line in inputfile:
        if line.strip() == "":
            continue

        if function == "fromCodetoCUItoAllAtoms":
            listSourceAs = source
            listCodeAs = line.strip()
            if isOPS:
                print(line.strip() + "[OPS] : " + str(opsmappings.get(line.strip())) + "[SNOMED_CT]")
                if opsmappings.get(line.strip()) == None:
                    if outputFile != "":
                        out = open(outputFile, "a")
                        out.write("OPS" + dm + line.strip())
                        for field in getfields():
                            out.write(dm)
                        out.write("\n")
                        out.close()
                    print("\n")
                    continue
                listSourceAs = "OPS"
                listCodeAs = line.strip()
                line = opsmappings.get(line.strip())
            fromCodetoCUItoAllAtoms(tgt, source, line.strip(), onlyrelevants, outputFile, getfields(), listSourceAs, listCodeAs)

    inputfile.close()


################################################################################################
# output fields for _all_atoms
################################################################################################
def getfields():
    #return ['concept', 'ui', 'rootSource', 'code', 'language', 'name']
    return ['concept', 'rootSource', 'code', 'language', 'name']


################################################################################################
# get cui and list all atoms
################################################################################################
def fromCodetoCUItoAllAtoms(tgt, source, code, onlyrelevant, outputFile, fields, listSourceAs, listCodeAs):
    code = makeCodeICD10apiConform(code)

    print("all atoms with " + source + " code " + makeCodeICD10readingConform(code) + ":")
    atomsfound = getAllAtoms(tgt, source, code, False, True, "", "", "", fields)
    if atomsfound == None:
        if outputFile != "":
            out = open(outputFile, "a")
            out.write(listSourceAs + dm + makeCodeICD10readingConform(listCodeAs))
            for field in fields:
                out.write(dm)
            out.write("\n")
            out.close()
        return None
    cui = getCUIFromCode(tgt, code, source)
    print("Concept CUI for " + makeCodeICD10readingConform(code) + " is " + cui)
    relevantText = ""
    if onlyrelevant: relevantText = " relevant"
    print("all" + relevantText + " atoms with concept CUI " + cui + ":")
    getAllAtoms(tgt, "CUI", cui, onlyrelevant, True, outputFile, listSourceAs, makeCodeICD10readingConform(listCodeAs), fields)
    print("\n")


################################################################################################
# ICD Code with point to unicode
################################################################################################
def makeCodeICD10apiConform(code):
    if len(code.split(".")) == 2:
        return code.replace(".", "%2E")
    elif len(code.split("%2E")) == 2:
        return code
    else:
        return code

def makeCodeICD10readingConform(code):
    if len(code.split(".")) == 2:
        return code
    elif len(code.split("%2E")) == 2:
        return code.replace("%2E", ".")
    else:
        return code

################################################################################################
# get all atoms of a concept
# onlyRelevants: Boolean
# returns number of atoms
# returns None if no results
################################################################################################
def getAllAtoms(tgt, source, code, onlyRelevants, printTrue, outputFile, printSourceAs, printCodeAs, fields):
    if source == "ICD10": code = makeCodeICD10apiConform(code)
    if source == "DMDICD10": code = makeCodeICD10apiConform(code)
    if source == "ICD10CM": code = makeCodeICD10apiConform(code)

    addWordSourceInURL = "source/"
    if source == "CUI" or source == "AUI":
        addWordSourceInURL = ""

    if printCodeAs == "": printCodeAs = source
    if printSourceAs == "": printSourceAs = code

    uriSearch = "https://uts-ws.nlm.nih.gov/rest/content/current/" + addWordSourceInURL + source + "/" + code + "/atoms"
    # + "/atoms/preferred"
    # + "/attributes"

    # "https://uts-ws.nlm.nih.gov/rest/content/current/source/ICD10/C76%2E1/atoms"
    # "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0155502/atoms"

    pageNumber = 0
    numberOfResults = 0
    #if printTrue: t = PrettyTable(['concept', 'ui', 'rootSource', 'code', 'language', 'name'])
    if printTrue: t = PrettyTable(fields)
    tryCounter = 1
    while True:
        try:
            serviceTicket = getst(tgt)
            pageNumber += 1
            query = {'ticket': serviceTicket, 'pageNumber': pageNumber}
            r = requests.get(uriSearch, params=query)
            r.encoding = 'utf-8'
            items = json.loads(r.text)
            if ('error' in items):
                if printTrue: print(items['error'] + "\n")
                return None

            jsonData = items["result"]
            for result in jsonData:
                #try:
                    if onlyRelevants == False or (
                            onlyRelevants and isrelevant(result["language"]) and isrelevant(result["rootSource"])):
                        if printTrue:
                            tlist = []
                            for field in fields:
                                if field == "code" or field == "concept":
                                    tlist.append(result[field].split("/")[-1])
                                else:
                                    tlist.append(result[field])
                            t.add_row(tlist)
                        if outputFile != "":
                            out = open(outputFile, "a")
                            out.write(printSourceAs + dm + printCodeAs)
                            for field in fields:
                                if field == "code" or field == "concept":
                                    out.write(dm + result[field].split("/")[-1].encode('ascii', errors="replace").decode('utf-8'))
                                else:
                                    out.write(dm + result[field].encode('ascii', errors="replace").decode('utf-8'))
                            out.write("\n")
                            out.close()
                        numberOfResults += 1
                #except:
                #    NameError

            if len(jsonData) == 0:
                break
        except JSONDecodeError:
            if tryCounter < tries - 1:
                tryCounter = tryCounter + 1
                pageNumber -= 1
                continue
            else:
                printJSONDecodeError(tryCounter)
            raise

    if printTrue: print(t)
    return numberOfResults

################################################################################################
# relevant sabs and languages
# returns true if value is relevant
# helps to filter atoms
################################################################################################
def isrelevant(value):
    # language = {"ENG", "GER"}
    #allSabsAndLanguage = {"RUS", "MDRRUS", "MSH", "MSHGER", "ICD10", "DMDICD10", "NCI", "UMD", "DMDUMD", "ICPC", "ICPCGER",
    #                      "WHO", "WHOGER", "SNOMED CT", "LNC", "LNC-DE-DE", "ATC"}
    allSabsAndLanguage = {"ENG", "GER", "MSH", "MSHGER", "ICD10", "DMDICD10", "NCI", "UMD", "DMDUMD", "ICPC", "ICPCGER",
                          "WHO", "WHOGER", "SNOMED CT", "LNC", "LNC-DE-DE", "ATC"}
    # sabsLevel1 = {"MSH", "MSHGER", "ICD10", "DMDICD10", "NCI", "UMD", "DMDUMD", "ICPC", "ICPCGER", "WHO", "WHOGER", "SNOMED CT", "LNC", "LNC-DE-DE", "ATC"}
    # sabsLevel2 = {"MSH", "MSHGER", "ICD10", "DMDICD10", "UMD", "DMDUMD", "ICPC", "ICPCGER", "LNC", "LNC-DE-DE", "ATC"}
    # sabsLevel2 = {"MSH", "MSHGER", "ICD10", "UMD", "ICPC", "ICPCGER", "LNC", "LNC-DE-DE", "ATC"}
    return value in allSabsAndLanguage


################################################################################################
# get concept CUI From ICD10 code ord DMDICD10 Code
# source can be ICD10 or DMDICD10
################################################################################################
def getCUIFromCode(tgt, code, source):
    if (source != "ICD10") and (source != "DMDICD10") and (source != "ICD10CM") and (source != "LNC") and (source != "SNOMEDCT_US"):
        print("getCUIFromCode: source can only be ICD10, DMDICD10, ICD10CM, LNC or SNOMEDCT_US")
        return None
    code = makeCodeICD10apiConform(code)

    tryCounter = 1
    while True:
        try:
            uriSearch = "https://uts-ws.nlm.nih.gov/rest/content/current/source/" + source + "/" + code + "/atoms"
            pageNumber = 1
            serviceTicket = getst(tgt)
            query = {'ticket': serviceTicket, 'pageNumber': pageNumber}
            r = requests.get(uriSearch, params=query)
            r.encoding = 'utf-8'
            items = json.loads(r.text)
            if ('error' in items):
                # print(items['error'])
                return None
            jsonData = items["result"]
            if (len(jsonData) == 0):
                return
            return jsonData[0]["concept"].split("/")[-1]

        except JSONDecodeError:
            if tryCounter < tries - 1:
                tryCounter = tryCounter + 1
                continue
            else:
                printJSONDecodeError(tryCounter)
            raise

################################################################################################
# get concept CUI From ICD10 code ord DMDICD10 Code
# source can be ICD10 or DMDICD10
################################################################################################
def createMappingFrequency(inputfile, fields, outputfile):
    #path = "C:/Users/Baris/Desktop/Projektarbeit/Python/EingabefuerPythonScript/"
    inputfile = open(inputfile, 'r')
    firstLine = True

    inputCodes = {""}
    inputSources = {""}
    sourceCodeConnections = {""}
    inputCodeNbr = 0
    rootSourceNbr = 0
    for line in inputfile:
        if firstLine:
            currfield = 0
            for field in line.split(dm):
                if field == "inputCode": inputCodeNbr = currfield
                if field == "rootSource": rootSourceNbr = currfield
                currfield = currfield + 1
            firstLine = False
            continue

        if firstLine == False:
            inputCodes.add(line.split(dm)[inputCodeNbr])
            inputSources.add(line.split(dm)[rootSourceNbr])
            sourceCodeConnections.add(line.split(dm)[rootSourceNbr] + dm + line.split(dm)[inputCodeNbr])
    inputfile.close()

    inputCodes.discard("")
    inputSources.discard("")
    sourceCodeConnections.discard("")
    inputCodesList = sorted(list(inputCodes))
    inputSourcesList = sorted(list(inputSources))

    dict = {}
    counter = 0
    out = open(outputfile, 'w')
    for s in inputSourcesList:
        for c in inputCodesList:
            if s + dm + c in sourceCodeConnections:
                counter += 1
        dict.update({s: [counter, counter/len(inputCodes)]})
        out.write(s + dm + str(counter) + dm + str(counter/len(inputCodes)) + "\n")
        counter = 0
    out.close()

    print("mapping frequency")
    t = PrettyTable(["rootSource", "number of mappings", "in percentage"])
    for x in dict:
        listt = [x, str(dict[x][0]), str(dict[x][1])]
        t.add_row(listt)
    print(t)




########################################################################################################################
######################### Section 4: main() function ####################################################
########################################################################################################################

if __name__=="__main__":
    print("umlsMapping started") # programm starts
    if checkapikey() == False: #read umls_key.txt file
        print("umlsMapping was terminated")
    else:
        tgt = gettgt() #create ticket granting ticket

        # calling functions depending on type of argument
        if args.icd10gm != None:
            filename_input = args.icd10gm[0]
            validate_file(filename_input)
            filename_all_atoms = filename_input[0:-4] + "_all_atoms.txt"
            filename_mapping_frequency = filename_input[0:-4] + "_mapping_frequency.txt"
            print("START ICD-10-GM")
            readFileAndDoFunction(tgt, filename_input, "fromCodetoCUItoAllAtoms", filename_all_atoms, False, "DMDICD10", True, False, "", "")
            createMappingFrequency(filename_all_atoms, ["inputSource", "inputCode"].append(getfields()), filename_mapping_frequency)
            print("END ICD-10-GM")

        if args.loinc != None:
            filename_input = args.loinc[0]
            validate_file(filename_input)
            filename_all_atoms = filename_input[0:-4] + "_all_atoms.txt"
            filename_mapping_frequency = filename_input[0:-4] + "_mapping_frequency.txt"
            print("START LOINC")
            readFileAndDoFunction(tgt, filename_input, "fromCodetoCUItoAllAtoms", filename_all_atoms, False, "LNC", True, False, "", "")
            createMappingFrequency(filename_all_atoms, ["inputSource", "inputCode"].append(getfields()), filename_mapping_frequency)
            print("END LOINC")

        if args.ops != None:
            filename_input = args.ops[0]
            filename_ops_snm_mapping = args.ops[1]
            validate_file(filename_input)
            validate_file_csv(filename_ops_snm_mapping)
            filename_all_atoms = filename_input[0:-4] + "_all_atoms.txt"
            filename_mapping_frequency = filename_input[0:-4] + "_mapping_frequency.txt"
            print("START OPS")
            readFileAndDoFunction(tgt, filename_input, "fromCodetoCUItoAllAtoms", filename_all_atoms, False, "SNOMEDCT_US", True, True, filename_ops_snm_mapping, "OPS_SNOMED_map.txt")
            createMappingFrequency(filename_all_atoms, ["inputSource", "inputCode"].append(getfields()), filename_mapping_frequency)
            print("END OPS")

        print("umlsMapping completed")