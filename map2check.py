#!/usr/bin/env python
# -*- coding: latin1 -*-
# -------------------------------------------------
# Map2Check Tool v3
# by Herbert Rocha
#
# e-mail: map2check.tool@gmail.com
# -------------------------------------------------

from __future__ import print_function
from modules.traceoutput.graphml import write_graphml_output
from modules.points2leak import identify_points2leak

FRAMEWORK_VERSION = 'Map2Check_FORTES-v3'


import argparse
import sys
import os
import commands
import re
import csv
import ConfigParser
import shutil
from pipes import quote
from operator import itemgetter
import pwd
import linecache

from modules.utils import generate_data_funct


# -------------------------------------------------
# Global variables
# -------------------------------------------------
########## Check setup to run the program
#ABS_PATH_FORTES='/home/nhb/Documents/ON_DEV/MAP2CHECK_FORTES_ON_DEV/FORTES'
ABS_PATH_FORTES = os.path.dirname(os.path.abspath(__file__))


######### settings for auxliary scripts
COMPLETE_CHECK_SCRIPT = ABS_PATH_FORTES+"/modules/utils/complete_check.py"
# Hack GNU extensions
GNU_SKIP_SCRIPT = ABS_PATH_FORTES+"/modules/gnu_extension/hack_extensions.py"
# Tokenizer
TOKENIZER = ABS_PATH_FORTES+"/modules/tokenizer/tokenizer"




########## settings preprocessor and arch flag
get_arch=commands.getoutput("arch")
set_arch=0

if get_arch == "x86_64":
    set_arch="--64"
    check_status_esbmc_path = ABS_PATH_FORTES + "/modules/bmc_tool/esbmc_tool/64/bin/esbmc"
    #FIRST_PREPROCESSING=ABS_PATH_FORTES+"/modules/preprocessor/primary_preprocessing/arch_64/uncrustify"
else:
    set_arch="--32"
    check_status_esbmc_path = ABS_PATH_FORTES + "/modules/bmc_tool/esbmc_tool/32/bin/esbmc"
    #FIRST_PREPROCESSING=ABS_PATH_FORTES+"/modules/preprocessor/primary_preprocessing/arch_32/uncrustify"

# Checking if we have the uncrustify installed in the OS system


CONFIG_CFG=ABS_PATH_FORTES+"/modules/preprocessor/primary_preprocessing/ben.cfg"
AUX_PREPROCESSING=ABS_PATH_FORTES+"/modules/preprocessor/aux_preprocessing/aux_formatting.pl"

########## settings for get and set claims
ESBMC_PATH = check_status_esbmc_path

DIR_RESULT_CLAIMS = ABS_PATH_FORTES+"/result_claims"
if not os.path.exists(DIR_RESULT_CLAIMS):
    os.makedirs(DIR_RESULT_CLAIMS)
    #save the name of the user logged
    username = os.getlogin()
    saveusernameid = pwd.getpwnam(str(username)).pw_uid
    os.chown(DIR_RESULT_CLAIMS, saveusernameid, saveusernameid)

GET_DATA_CLAIMS = ABS_PATH_FORTES+"/modules/get_and_set_claims/abs_claims.pl"
CLAIM_TRANSLATOR = ABS_PATH_FORTES+"/modules/claim_translator/parse_2_claims_v16_09.py"
WRITE_NEW_INSTANCE = ABS_PATH_FORTES+"/modules/get_and_set_claims/write_new_instance.py"
FLAG_IS_CLAIM = False

DIR_RESULT_END_CODE = ABS_PATH_FORTES+"/new_code"
#map2check
MAP_2_CHECK_MAP = ABS_PATH_FORTES+"/modules/map2check/generate_map/main_map.py"

# Utils
#GET_DATA_LOC_FUNC = ABS_PATH_FORTES+"/modules/utils/get_data_func_location.pl"
LIBRAY_HEADER_MAP = ABS_PATH_FORTES+"/modules/map2check/library/check_safety_memory_FORTES.h"


# List the has the tmp file generated by the method execution
list_tmp_path = []


# Global args options
TRACK_ALL = "0"
GENERATE_GRAPHML = False
WRITE_GRAPHMLOUT = write_graphml_output.WriteGraphMLOutput()
# -------------------------------------------------


# -------------------------------------------------
# Utils function of the program
# -------------------------------------------------

def code_preprocessor(cFile):
    # Return the tmp location of the code
    
    # get the name of the analyzed program
    name_program=commands.getoutput('echo '+cFile+' | grep -o "[^/]*$"')
    rec_file="pre_"+name_program
    rec_path=commands.getoutput('echo '+cFile+' | sed "s/'+name_program+'/'+rec_file+'/g"')

    #os.system('uncrustify -q -l C -c '+CONFIG_CFG+' -f '+cFile)
    #sys.exit()
    os.system('uncrustify -q -l C -c '+CONFIG_CFG+' -f '+cFile+' > '+rec_path)
    
    return rec_path
    
    
def isolate_claim_by_func(listClaim,funcName):
    flagAddList = True
    listTextCl = []
    tmpBlocCl = []
    i = 0
    while i < len(listClaim):
        matNTCl = re.search(r'Claim.*', listClaim[i])
        if matNTCl: 
            # get blocks
            while (listClaim[i] and listClaim[i].strip()):
                tmpBlocCl.append(listClaim[i])
                i += 1
            
            matchNamF = re.search(r'function '+funcName, tmpBlocCl[1])
            if matchNamF:
                tmpBlocCl.append("\n")            
                for tmp in tmpBlocCl:
                    listTextCl.append(tmp)
        else:
            listTextCl.append(listClaim[i])
        
        i += 1
        tmpBlocCl = []
    
    textCl = ' \n'.join(listTextCl)    
    #return listTextCl
    return textCl



def get_esbmc_claims(cFile, enClaimByFunc):
    
    global FLAG_IS_CLAIM
    
    # Get the claims from cFile and return the path the file with the claims    
    if enClaimByFunc:        
        #print("Options: ", cFile, enClaimByFunc)
        tmp_cl=commands.getoutput('echo '+cFile+' | grep -o "[^/]*$" | grep -o "^[^.]*"')
        rec_name=tmp_cl+".cl"
        rec_name=rec_name+"_func_"+enClaimByFunc+".cl"
        #Running the ESBMC to get the claims by functions               
        list_claims=commands.getoutput(ESBMC_PATH+' '+set_arch+' --no-library --function '+enClaimByFunc+' --show-claims '+cFile)

        #os.system(ESBMC_PATH+' '+set_arch+' --no-library --function '+enClaimByFunc+' --show-claims '+cFile)
        #sys.exit()

        check_command_exec(list_claims, 0, "Generating esbmc claims",1)   
        
        ressulTextCL=isolate_claim_by_func(list_claims.rsplit('\n'),enClaimByFunc)                        
        os.system('echo '+quote(ressulTextCL)+' > '+DIR_RESULT_CLAIMS+'/'+rec_name)        
        
    else:
        #print("Options: ", cFile)
        tmp_cl=commands.getoutput('echo '+cFile+' | grep -o "[^/]*$" | grep -o "^[^.]*"')
        rec_name=tmp_cl+".cl"
        #Running the ESBMC to get the claims        
        #os.system(ESBMC_PATH+' '+set_arch+' --no-library --show-claims '+cFile)
        #sys.exit()
        result=commands.getoutput(ESBMC_PATH+' '+set_arch+' --no-library --show-claims '+cFile+' > '+DIR_RESULT_CLAIMS+'/'+rec_name)

        #os.system(ESBMC_PATH+' '+set_arch+' --no-library --show-claims '+cFile)
        #sys.exit()

        file_result = DIR_RESULT_CLAIMS+'/'+rec_name
        check_command_exec(result, file_result, "Generating esbmc claims",0)   
        
    pathCl = DIR_RESULT_CLAIMS+'/'+rec_name    
    #list_tmp_path.append(rec_name)
    # Check if the program has at least one claim if not the process is aborted
    ckResult = commands.getoutput('cat '+pathCl+' | grep -c "Claim .*"')
    if int(ckResult):
        FLAG_IS_CLAIM = True
        return pathCl
    else:
        FLAG_IS_CLAIM = False
        #print("There are not claims for this functions!")
        #sys.exit()



def call_abs_claims(cFile,textCl):
    # generating a data csv   
    
    pathFile=commands.getoutput('echo '+cFile+' | grep -o "[^/]*$" | grep -o "^[^.]*"')
    csvName=pathFile+".1st" 
               
    result = commands.getoutput(GET_DATA_CLAIMS+" "+textCl+" > "+DIR_RESULT_CLAIMS+"/"+csvName)
    pathCsvName = DIR_RESULT_CLAIMS+"/"+csvName
    
    #os.system("cat "+DIR_RESULT_CLAIMS+"/"+csvName)
    #sys.exit()
    check_command_exec(result, pathCsvName, "Generating data from esbmc claims",0)   
    return pathCsvName


def get_and_set_claims(cFile, dataLocFunction, mapFile , absClaimFile, has_claims):
    # Get data claim and add claim in the new instace program, and finally
    # return the path of the new instance
    path2NewInstFile = cFile.replace("pre_","new_")  
    
    #print(WRITE_NEW_INSTANCE+" "+cFile+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims))
    #os.system(WRITE_NEW_INSTANCE+" "+cFile+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims))
    #os.system("cat "+absClaimFile)
    #os.system("cat "+mapFile)
    #sys.exit

    # 3nd HackCode
    # Apply hacking to handle with GNU extensions
    # HackGNUext: Generate a copy the analyzed program to a tmp file
    tmpFileGnuSkip_end = "/tmp/tmp_hack_gnu_end.c"
    commands.getoutput(GNU_SKIP_SCRIPT + " " + cFile + " 2>&1 > " + tmpFileGnuSkip_end)
    list_tmp_path.append(tmpFileGnuSkip_end)


    
    #result = commands.getoutput(WRITE_NEW_INSTANCE+" "+cFile+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims)+" > "+path2NewInstFile)
    #print(WRITE_NEW_INSTANCE+" "+cFile+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims))
    #os.system(WRITE_NEW_INSTANCE+" "+cFile+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims))
    #sys.exit()

    result = commands.getoutput(WRITE_NEW_INSTANCE+" "+tmpFileGnuSkip_end+" "+dataLocFunction+" "+mapFile+" "+absClaimFile+" "+str(has_claims)+" > "+path2NewInstFile)
    check_command_exec(result, path2NewInstFile, "Writing a new instance of the analyzed code",0) 
    
    return path2NewInstFile
    


def call_map2check(cFile, enReWriteResult):
    
    #if not enReWriteResult:
    #    
    mapAstParse = ParseAstPy()
    mapAstParse.load2Parse(cFile)

    # Gathering data about all typedef
    mapAstParse.searchTypedef()

    # Global mapping OKAY
    mapAstParse.mapGlobalVars()

    # Function  mapping OKAY
    mapAstParse.mapEachFunction()

    # Sorting data mapped by the line of the program
    mapAstParse.sortListMapByNumLine()
    mapAstParse.printMapResult(1)

    # Generate Overview results and print if True arg
    test.createOverviewResult(False)
    
    
def sortClaimsFile(csvFileClaims):
    claims_csv_file = open(csvFileClaims)
    claims_lines_csv = claims_csv_file.readlines()
    claims_csv_file.close()
    
    eachLine = []
    
    numColumns = 0
    for lines in claims_lines_csv:
        eachLine.append(lines.rsplit(";"))
        numColumns = len(lines.rsplit(";"))
        #print(lines.rsplit(";"))
    
    for i,d in enumerate(eachLine):
        num = int(d[numColumns-1])
        d[numColumns-1] = num
    
    eachLine.sort(key=itemgetter(numColumns-1))
    
    
    file = open(csvFileClaims, "w")
    
    # Re-write the file
    for line in eachLine:
        count = 0        
        mountLine = ''        
        
        for data in line:
            if count < (len(line)-1):                
                #print(data," ; ",end="") 
                mountLine += str(data)+" ; "
            else:
                #print(data) 
                mountLine += str(data)+" \n"
            count += 1
            
        file.write(mountLine)
            
    
    file.close()
        
    #return 
    #os.system("cat "+csvFileClaims)        
    #sys.exit()
    
    


def add_new_num_lines2csv(fileMapPath, listNumLinesMap, opName):
    
    if opName:
        # Mapping file
        name_new_file_map = fileMapPath.replace('.1st','.map')
    else:
        # Claims file        
        name_new_file_map = fileMapPath.replace('.csv','.ncl')         
    
    with open(fileMapPath,'r') as csvinput:
        with open(name_new_file_map, 'w') as csvoutput:
            
            writer = csv.writer(csvoutput, delimiter=';')
            
            count_row = 0
            index_list = 0
            for row in csv.reader(csvinput, delimiter=';', quotechar='"'):
                if opName:
                    if count_row == 0:                                        
                        writer.writerow(row+["After_Pre_LOC"])
                        count_row += 1
                    else:
                        if index_list < len(listNumLinesMap):                            
                            writer.writerow(row+[str(listNumLinesMap[index_list])])
                            index_list += 1
                else:
                    if index_list < len(listNumLinesMap):                                                                                 
                            writer.writerow(row+[str(listNumLinesMap[index_list])])
                            index_list += 1
                    
                #if row[0] == "Name":
                #    writer.writerow(row+["Berry"])
                
            #os.remove(fileMapPath)
    
    if not opName:
        sortClaimsFile(name_new_file_map)
            
    return name_new_file_map
    


def apply_claim_translator(cFile, csvClaimFile, dataFunctionFile, csvMappedFromCode):
    # Apply claim translator and return the path of the csv file
    name_new_csv_file = csvClaimFile.replace('.1st','.csv')  
    file_from_map_2_cl = DIR_RESULT_CLAIMS+"/aux_file_map_2_translator.csv"
    list_tmp_path.append(file_from_map_2_cl)

    # print(CLAIM_TRANSLATOR+" -i "+csvClaimFile+" -c "+cFile+" -f "+dataFunctionFile
    #           +" -m "+file_from_map_2_cl+" -p" + csvMappedFromCode + " -d 0")
    # sys.exit()
    #os.system(CLAIM_TRANSLATOR+" -i "+csvClaimFile+" -c "+cFile+" -f "+dataFunctionFile
    #          +" -m "+file_from_map_2_cl+" -p" + csvMappedFromCode + " -d 0")

    #os.system("cat "+csvClaimFile)
    #sys.exit()
    result = commands.getoutput(CLAIM_TRANSLATOR + " -i " + csvClaimFile + " -c " + cFile
                                + " -f " + dataFunctionFile + " -m " + file_from_map_2_cl
                                + " -p " + csvMappedFromCode + " > " + name_new_csv_file)
    check_command_exec(result, name_new_csv_file, "Translating esbmc claims",0)   
    return name_new_csv_file
    
    
def get_data_functions(cFile):
    file_loc_fun = DIR_RESULT_CLAIMS+"/tmp_data_function.loc"
    getdataf = generate_data_funct.GetDataFuncts()
    getdataf.generate_ast(cFile)
    getdataf.overview_data_functs(cFile, file_loc_fun)

    #result = commands.getoutput(GET_DATA_LOC_FUNC+" "+cFile+" > "+file_loc_fun)
    #check_command_exec(result, file_loc_fun, "Generating data function",0)

    return file_loc_fun



def remove_tmp_files(list_path):
    uniclist = list(set(list_path))
    for path in uniclist:
        os.remove(path)
        #print(path)
        
        
        
def check_command_exec(result, file2Analyzed, note, flagNoReturn):
    # >>> Check if each step was executed correctly, otherwise print "Error"
    # Checking result command
    if result:
        if not flagNoReturn:
            print("Error. "+note)
            sys.exit()
        
        matchNumLine = re.search(r'ERROR', result)
        if matchNumLine:
            print("Error. "+note)
            sys.exit()
        
    # Checking file generated
    elif file2Analyzed != 0:
        if not os.path.isfile(file2Analyzed): 
            print('Error: unable to open the file (%s) \n' % file2Analyzed)            
            print('Note : '+note+'\n')
            sys.exit()
        

def handle_func_verifier_error(_cfile):
    file = open(_cfile, 'r')
    lines = file.readlines()
    file.close()

    file = open('/tmp/tmp_hd_funcve.c','w')
    for index, line in enumerate(lines):

        if line.startswith('extern'):
            if '__VERIFIER_error()'  in line.split():
                line = line.replace( '__VERIFIER_error()', '__VERIFIER_error(int linenumber)' )

        if '__VERIFIER_error();' in line.split():
            line = line.replace('__VERIFIER_error();', '__VERIFIER_error(' + str(index+1) + ');')
        file.write(line)

    file.close()
    return '/tmp/tmp_hd_funcve.c'


def removeunncesstokens(_listtokens, _linestartpointtoken):
    #print(_listtokens)
    listindex = []
    resulttokenanalyis =[]

    # checking if we have an array
    isanarray = False
    for index, token in enumerate(_listtokens):
        if token == "[":
            isanarray = True
            break

    if not isanarray:
        for index, token in enumerate(_listtokens):
            if token in ["(",")","{","}","=","*","+","-","/","||","%",";",",",""]:
                #print(token)
                listindex.append(index)

        # identify index tokens removed
        # this tmp list is generated based on start point of the token lines
        numtokens = range(_linestartpointtoken,(_linestartpointtoken+len(_listtokens)))

        indexes = sorted(list(listindex), reverse=True)
        for index in indexes:
            del numtokens[index]

        #
        resulttokenanalyis = [numtokens, _listtokens]

    else:
        numtokens = range(_linestartpointtoken,(_linestartpointtoken+len(_listtokens)))

        # Get only the array type
        indexes = sorted(list([0]), reverse=True)
        for index in indexes:
            del numtokens[index]

        #
        resulttokenanalyis = [numtokens, _listtokens]


    return resulttokenanalyis



def create_map_tokenizer(_cFile,):

    #print("Doing....")
    #print(_cFile)

    filec = open(_cFile,'r')
    linescfile = filec.readlines()
    filec.close()

    lastqdttoken = 0
    nextmaplineresult = 1 # Cuz the tokens number start in 1
    actualmapline = 0

    resulttokensnanalysis = []

    for index, line in enumerate(linescfile):
        filefortoken = open("/tmp/tmp_tokens.tmp",'w')
        # print(line)
        filefortoken.write(line)
        filefortoken.close()

        resulttokens = commands.getoutput(TOKENIZER+" "+"/tmp/tmp_tokens.tmp")
        #TODO: testing
        #print(resulttokens,end="")
        if index > 0:

            #print(str(index+1) + " ; " + str(nextmaplineresult) + " ; " + line, end="")

            lastqdttoken = resulttokens.count("\n")

            #if lastqdttoken == 0:
            #    nextmaplineresult -= 1

            #print("Print ount0: "+str(nextmaplineresult))

            token2print = removeunncesstokens(resulttokens.split("\n"), nextmaplineresult)

            resulttokensnanalysis.append([index+1,token2print])

            nextmaplineresult = lastqdttoken+nextmaplineresult

            # print("Last count0: "+str(lastqdttoken))
            # print("Next l map0: "+str(nextmaplineresult))


        else:

            #print(str(index+1) + " ; " + str(index+1) + " ; " +line, end="")
            lastqdttoken = resulttokens.count("\n")
            token2print = removeunncesstokens(resulttokens.split("\n"), nextmaplineresult)

            resulttokensnanalysis.append([index+1,token2print])

            nextmaplineresult = 1
            nextmaplineresult = lastqdttoken+nextmaplineresult

            # print("Last count: "+str(lastqdttoken))
            # print("Next l map: "+str(nextmaplineresult))

    #for debug
    # for item in resulttokensnanalysis:
    #    print(item)
    # sys.exit()
    os.remove("/tmp/tmp_tokens.tmp")
    return resulttokensnanalysis


def generate_data_tokens(_cfile):
    global WRITE_GRAPHMLOUT
    # >> generating a normalized dictionary for graphml
    # Create a method to generate the dictionary with data about the tokenizer
    result_tokens = create_map_tokenizer(_cfile)
    WRITE_GRAPHMLOUT.listdatatokens = result_tokens




def start_generation_cassert(cFile, enSetFunc):
    
    global FLAG_IS_CLAIM
    global WRITE_GRAPHMLOUT
    global GENERATE_GRAPHML
        
    # >>> First map to save the original line number    
    tmp_file_map = DIR_RESULT_CLAIMS+"/tmp_file_map.1st"

    # Apply hacking to handle with GNU extensions
    # HackGNUext: Generate a copy the analyzed program to a tmp file
    tmpFileGnuSkip = "/tmp/tmp_hack_gnu.c"
    commands.getoutput(GNU_SKIP_SCRIPT + " " + cFile + " 2>&1 > " + tmpFileGnuSkip)
    list_tmp_path.append(tmpFileGnuSkip)


    # Generating possible leaks points in the program
    # the result is save in /tmp/tmp_leakpoints.map2check
    runind = identify_points2leak.IdentifyLeakPoints(tmpFileGnuSkip)
    runind.identify_points()
    list_tmp_path.append("/tmp/tmp_leakpoints.map2check")
    #os.system("cat /tmp/tmp_leakpoints.map2check")
    #sys.exit()
    
    # Comment this and execute test
    # Checkout solution to support GNU extensions
    #os.system(MAP_2_CHECK_MAP+" "+tmpFileGnuSkip+" 1 "+TRACK_ALL)
    #sys.exit()

    # HackCode
    #result = commands.getoutput(MAP_2_CHECK_MAP+" "+cFile+" 1"+" > "+tmp_file_map)
    result = commands.getoutput(MAP_2_CHECK_MAP+" "+tmpFileGnuSkip+" 1 " + TRACK_ALL + " > "+tmp_file_map)
    check_command_exec(result, tmp_file_map, "Generating code map in original code",0)
    list_tmp_path.append(tmp_file_map)
       

    # OriCode
    # >>> First get claims to save the original line number
    getFisrtTextFileCl = get_esbmc_claims(cFile, enSetFunc) 
    #print(getFisrtTextFileCl)   
    #sys.exit()
    if FLAG_IS_CLAIM:
        # First call the function that running the abstraction method to get data from claims
        getFisrtCsvDataCl = call_abs_claims(cFile, getFisrtTextFileCl)
        list_tmp_path.append(getFisrtTextFileCl)
        list_tmp_path.append(getFisrtCsvDataCl)
        

    # Modify the analyzed code to handle the function __VERIFIER_error()
    #     replace __VERIFIER_error() by __VERIFIER_error(Number of the actual line)
    # HIP: Create a simple python script to read the file, count the lines, and then replace the string.
    #      Finally save this modifed txt code in a tmp file and then pass this tmp file to the next steps.
    m_cfile = handle_func_verifier_error(cFile)
    list_tmp_path.append(m_cfile)

    # OriCode
    # >>> Preprocessing source code
    getPreCFile = code_preprocessor(m_cfile)
    #os.system("cat "+getPreCFile)
    #sys.exit()


    # 2nd HackCode
    # Apply hacking to handle with GNU extensions
    # HackGNUext: Generate a copy the analyzed program to a tmp file
    tmpFileGnuSkip_afterpre = "/tmp/tmp_hack_gnu_ap.c"
    #os.system(GNU_SKIP_SCRIPT + " " + getPreCFile)
    #sys.exit()
    commands.getoutput(GNU_SKIP_SCRIPT + " " + getPreCFile + " 2>&1 > " + tmpFileGnuSkip_afterpre)
    list_tmp_path.append(tmpFileGnuSkip_afterpre)


    # TODO: Checkout if this not have a coloteral efect
    # OriCode
    # >>> Gather the data about functions location in the program
    #getDataFunction = get_data_functions(getPreCFile)
    getDataFunction = get_data_functions(tmpFileGnuSkip_afterpre)



    # HackCode
    # >>> Call map2check again to get data line number after preprocessing
    #get_2st_map = commands.getoutput(MAP_2_CHECK_MAP+" "+getPreCFile+" 2")
    get_2st_map = commands.getoutput(MAP_2_CHECK_MAP+" "+tmpFileGnuSkip_afterpre+" 2 " + TRACK_ALL)
    check_command_exec(get_2st_map, 0, "Generating code map after preprocessing",1)   
    list_lines_map = get_2st_map.split("\n")
    # Adding the result of 2st map in the tmp_file_map.map
    getFinalFileMap = add_new_num_lines2csv(tmp_file_map, list_lines_map, 1)        
    check_command_exec(0, tmp_file_map, "Generating code map after preprocessing",0)

    # [NEW] fix bug in the error function
    getPreCFile = tmpFileGnuSkip_afterpre
    
    # >>> Get the text claims again (second time) for the program    
    if FLAG_IS_CLAIM:
        # Get the text claims
        get_2st_path_fileCl = get_esbmc_claims(getPreCFile, enSetFunc)            
        
        #os.system("cat "+get_2st_path_fileCl)
        #sys.exit()
        
        # Call the function that running the abstraction method to get data from claims	    
        get_2st_CsvDataCl = call_abs_claims(getPreCFile, get_2st_path_fileCl)    
        
        #   
        
        list_tmp_path.append(get_2st_path_fileCl)
        list_tmp_path.append(get_2st_CsvDataCl)
        
        # >>> Call translate to claims
        getTranslatedCsvClaim = apply_claim_translator(getPreCFile, get_2st_CsvDataCl, getDataFunction, getFinalFileMap)
        list_tmp_path.append(getTranslatedCsvClaim)
        
        # Reading the claim list to add the original number lines in this list                
        #get_2st_text_Cl = commands.getoutput("cat "+getTranslatedCsvClaim)            
        get_1st_text_Cl = commands.getoutput("cat "+getFisrtCsvDataCl)            
        
        # generating a list from output            
        lines_CL = get_1st_text_Cl.split("\n")
        list_lines_CL = []
        for line in lines_CL:
            splitted = line.split(";")
            list_lines_CL.append(splitted[0])
          
                
        # Adding the result of 2st get claims in the tmp_file_map.map    
        # TODO: falta verificar a quest�o do num diff claims 
        get_final_path_csv_file_CL = add_new_num_lines2csv(getTranslatedCsvClaim, list_lines_CL, 0)      
        
        #os.system("cat "+get_final_path_csv_file_CL)
        #sys.exit()

        list_tmp_path.append(get_final_path_csv_file_CL) 
        check_command_exec(0, get_final_path_csv_file_CL, "Gathering esbmc claims",0)
       
       
       
    # >>> Call get claims and add in the new instance of the program
    # SEE: assert == 0 | CUnit == 1    
    if FLAG_IS_CLAIM:
        getPath2NewInstCFile = get_and_set_claims(getPreCFile, getDataFunction, getFinalFileMap, get_final_path_csv_file_CL, 1)
    else:
        getPath2NewInstCFile = get_and_set_claims(getPreCFile, getDataFunction, getFinalFileMap, "None", 0)
    #list_tmp_path.append(getPreCFile)
    list_tmp_path.append(getDataFunction)
    #print(GENERATE_GRAPHML)
    if not GENERATE_GRAPHML:
        list_tmp_path.append(getFinalFileMap)

        
    # >>> Call the last preprocessing
    # Because the map2check library we need to do a temporary copy    
    #   of the .h to program location to apply the preprocessing
    #    
    shutil.copy2(LIBRAY_HEADER_MAP, os.path.dirname(getPath2NewInstCFile))
    #print(getPath2NewInstCFile)
    getFinalCFile = code_preprocessor(getPath2NewInstCFile)
    os.system("cat "+getFinalCFile)
    list_tmp_path.append(getPath2NewInstCFile)
    list_tmp_path.append(getFinalCFile)
    where_copied_head = os.path.dirname(getPath2NewInstCFile)+"/check_safety_memory_FORTES.h"
    
    list_tmp_path.append(where_copied_head)
    remove_tmp_files(list_tmp_path)
    sys.exit()   
    
    
    
    
    
    
def start_generation_cunit_assert(cFile,enSetFunc):
    print("CUnit assertion")
    if enSetFunc:
        print("Options: ", cFile, enSetFunc)
    else:
        print("Options: ", cFile)


# -------------------------------------------------



# -------------------------------------------------
# Main python program
# -------------------------------------------------

if __name__ == "__main__":    
    
    ############# Parse args options
    parser = argparse.ArgumentParser(description='Run Map2Check v3')
    parser.add_argument('-v','--version', action='version' , version="version 3")
    parser.add_argument(dest='inputCProgram', metavar='file.c', type=str,
                        help='the C program file to be analyzed')
    parser.add_argument('-m','--map2checkout-to-graphml', metavar='map2checkout.tmp', type=str, dest='setMapOut2Graph',
                        help='Generating a GraphML from Map2Check output')
    parser.add_argument('-f','--function', metavar='name', type=str , dest='setMainFunction',
                        help='set main function name')
    parser.add_argument('-c','--complete-check', metavar='nr', type=int, dest='setCompleteCheck',
                        default=3, help='set the complete verification based on number of the program execution')
    parser.add_argument('-t','--track-all', action="store_true" , dest='setTrackAll',
                       help='create a complete trace of the variables', default=False)
    parser.add_argument('-g','--graphml-output', action="store_true" , dest='setGraphOut',
                       help='generate the output of the tool in GraphML format (experimental)', default=False)
    parser.add_argument('-w','--witnesspath', metavar='witnessfile.graphml', type=str, dest='setWitnessPath',
                       help='dump the witness into the given file')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-u','--cunit', action="store_true" , dest='setCunitAssert',
                       help='create test cases based in assertions from CUnit', default=False)
    group.add_argument('-a','--only-assert', action="store_true" , dest='setOnlyAssert',
                       help='create test cases based only in assertions from C language', default=False)

    args = parser.parse_args()        
    
    ############# Check options in the args
    ### vars to save data option

    
    inputCFile=''
    enCAssert=False
    enCUnitAssert=False
    getStartFunction=''

    
    if args.inputCProgram:                 
        if not os.path.isfile(args.inputCProgram): 
            print('Error: unable to open input file (%s)' % args.inputCProgram)
            parser.parse_args(['-h'])
            sys.exit()
        else:
            inputCFile = os.path.abspath(args.inputCProgram)

    #-----------------------------------------------------
    if args.setMapOut2Graph:
        map2checkoutpath = os.path.abspath(args.setMapOut2Graph)
        #print(inputCFile,"\n",map2checkoutpath)

        generate_data_tokens(inputCFile)

        # This option NOT support enterFunction, sorry about that
        #WRITE_GRAPHMLOUT.enable_enterFunction_attr = False
        # only for experiments and test regression
        WRITE_GRAPHMLOUT.enable_enterFunction_attr = True
        WRITE_GRAPHMLOUT.preprocess_outmap(map2checkoutpath)
        name_file_result = commands.getoutput("mktemp")
        lastoutput = open(str(name_file_result), "w")
        lastoutput.write(WRITE_GRAPHMLOUT.generate_graphml())
        lastoutput.close()

        print("The Map2Check output in GraphML format is in < " + name_file_result + " >")

        if os.path.exists("/tmp/tmp_map_currentlog.tmp"):
            os.remove("/tmp/tmp_map_currentlog.tmp")
        if os.path.exists("/tmp/tmp_idfunct.map2check"):
            os.remove("/tmp/tmp_idfunct.map2check")
        if os.path.exists("/tmp/trace_of_program_exec_map2check.tmp"):
            os.remove("/tmp/trace_of_program_exec_map2check.tmp")


        sys.exit()
                
    #-----------------------------------------------------
    if args.setMainFunction:
        #check if the given function there is in the code
        runind = generate_data_funct.GetDataFuncts()
        runind.generate_ast(inputCFile)
        checkFunc = runind.hasfunction(str(args.setMainFunction))
        #checkFunc=commands.getoutput('ctags -x --c-kinds=f '+inputCFile+' | grep -c "'+args.setMainFunction+'\"')
        if checkFunc:
            getStartFunction = args.setMainFunction
        else:
            print('Error: function { '+args.setMainFunction+' } not found')
            sys.exit()

    if args.setOnlyAssert:

        if args.setTrackAll:
            TRACK_ALL = "1"
        if args.setGraphOut:
            # only to do not remove the final map file
            GENERATE_GRAPHML = True

        start_generation_cassert(inputCFile,getStartFunction)

    elif args.setCompleteCheck:
        # Identify if is to perform a complete trace of the variables
        writegraphout = False
        if args.setTrackAll:
            TRACK_ALL = "1"

            # Run auxiliary script
            # The return is as following:
            #   - Status: [VERIFICATION SUCCESSFUL | VERIFICATION FAILED | TIME OUT | UNKNOW]
            #   - If UNKNOW -> Output: message
            #   - If VERIFICATION FAILED -> Output: The trace log is in PATH
            #   - If TIME OUT -> Output: In {show de time definied}
            if args.setGraphOut:
                saveresult_check = commands.getoutput(COMPLETE_CHECK_SCRIPT +
                                                     " -t " +
                                                     " -g " +
                                                     " -n " + str(args.setCompleteCheck) +
                                                     " " + inputCFile)

                writegraphout = True
            else:
                saveresult_check = commands.getoutput(COMPLETE_CHECK_SCRIPT +
                                                     " -t " +
                                                     " -n " + str(args.setCompleteCheck) +
                                                     " " + inputCFile)
        else:
            # BUG no generate graphml
            if args.setGraphOut:
                saveresult_check = commands.getoutput(COMPLETE_CHECK_SCRIPT +
                                                     " -g " +
                                                     " -n " + str(args.setCompleteCheck) +
                                                     " " + inputCFile)
                writegraphout = True
            else:
                saveresult_check = commands.getoutput(COMPLETE_CHECK_SCRIPT +
                                                    " -n " + str(args.setCompleteCheck) +
                                                    " " + inputCFile)


        if writegraphout:
            # Fisrt of all checking if we have a counterexample
            matchoutputCE = re.match(r'Status: VERIFICATION FAILED', saveresult_check)
            if matchoutputCE:
                nameoutputmap = ''
                matchoutputfile = re.search(r'The trace log is in <(.*)>', saveresult_check)
                if matchoutputfile:
                    nameoutputmap = matchoutputfile.group(1).strip()

                generate_data_tokens(inputCFile)

                # Generating the graphml
                #print(WRITE_GRAPHMLOUT.listdatatokens)
                # WRITE_GRAPHMLOUT.preprocess_outmap(nameoutputmap)
                # print(WRITE_GRAPHMLOUT.generate_graphml())
                # sys.exit()

                WRITE_GRAPHMLOUT.preprocess_outmap(nameoutputmap)
                name_file_result = commands.getoutput("mktemp")

                if args.setWitnessPath:
                    pathfile_graphml = os.path.abspath(args.setWitnessPath)
                    lastoutput = open(str(pathfile_graphml), "w")
                    lastoutput.write(WRITE_GRAPHMLOUT.generate_graphml())
                    lastoutput.close()
                else:
                    lastoutput = open(str(name_file_result), "w")
                    lastoutput.write(WRITE_GRAPHMLOUT.generate_graphml())
                    lastoutput.close()

                # Save this output in a tmp file
                os.remove(nameoutputmap)
                print("Status: VERIFICATION FAILED")
                if not args.setWitnessPath:
                    print("The trace log is in < " + name_file_result + " >")

                if os.path.exists(DIR_RESULT_CLAIMS+"/tmp_file_map.map"):
                    os.remove(DIR_RESULT_CLAIMS+"/tmp_file_map.map")

            else:
                # Verification okay
                print(saveresult_check)

        else:
            print(saveresult_check) # TODO TEST

        #os.remove("/tmp/tmp_map_currentlog.tmp")
        if os.path.exists("/tmp/tmp_idfunct.map2check"):
            os.remove("/tmp/tmp_idfunct.map2check")

    elif args.setCunitAssert:
        start_generation_cunit_assert(inputCFile,getStartFunction)

        
    

# -------------------------------------------------

