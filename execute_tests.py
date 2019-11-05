#!/usr/bin/env python3
import argparse
import csv
import os
from io import StringIO
import sys
import subprocess


#====================================================DEFINE FUNCTIONS====================================================
#Reads arguments from command line
def get_args():
    parser = argparse.ArgumentParser(description='Test Plan parameters')
    parser.add_argument('-p', '--plan', type=str, help='Run specific test plan identified by name',required=False)
    parser.add_argument('-T', '--Test', type=str, help='Run specific test identified by name', required=False)
    parser.add_argument('-t', '--tag', type=str, help='Run all tests that are tagged with tag', required=False)
    parser.add_argument('-l', '--list', type=str, help='List all tags, test plans or tests available', required=False)

    args = parser.parse_args()

    plan = args.plan
    test = args.Test
    tag = args.tag
    list = args.list
    return plan, test, tag, list

#function to read test plan csv file
def readTestPlan(filename):
    with open(filename) as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            fileNames.append(row[0])
            tags.append(row[1])
        #Remove titles from CSV file
        fileNames.pop(0)
        tags.pop(0)

#function to check test output - importing the file rather than using exec for consistency
def runTest(testFile, reportName):
    #Store standard output to reset to later
    old_stdout = sys.stdout

    print('Testing file: %s...' % testFile)

    #Runs the rest file as a subprocess, and store that output ready to be checked
    output = subprocess.check_output("python -c 'from %s import *'" % testFile, shell=True)

    #The subprocess captures 'binary' output, it needs to be converted to ascii
    outputStripped = output.decode('ascii')

    #Start capturing standard output
    result = StringIO()
    sys.stdout = result
    print(outputStripped)
    sys.stdout = old_stdout
    #Stop capturing standard output

    #Grab the value stored in standard output and removing trailing whitespace
    passed = result.getvalue().rstrip()

    return passed



#====================================================END OF FUNCTIONS====================================================

#Get parameter values
plan, test, tag, list = get_args()

#Exit out if a list is requested
if list != None:
    #Reads list parameter
    if list == "tag":
        print ("Possible tags are: short, long, endurance, performance or must_pass")
    elif list == "plan":
        os.system("ls | grep .csv")
    elif list == "test":
        os.system("ls | grep .py | grep -v 'execute_tests.py'")
    else:
        print('Unknown option: %s\nPotential options are: tag, plan or test' % list)
    raise SystemExit


#Init global arrays
fileNames = []
tags = []
newList = []

#Report extension
ext = '.log'

#Check if -T is supplied to only run one test file then replace list
if test != None:
    fileNames.append(test)
    reportName = str(test)
else:
    try:
        #Read testplan csv file - this will store it to fileNames and tags (needs -p)
        readTestPlan(plan)
        reportName = str(plan)
    except:
        if tag != None:
            print('Supply plan file with -p')
        else:
            print('Failed to load test plan file. Ensure the name is correct')

#Check if -t is supplied in specify which tags to run
if tag != None:
    try:
        #Find index of supplied tag
        indecies = [i for i, x in enumerate(tags) if x == tag]
        #Temp list to replce fileName
        for index in indecies:
            newList.append(fileNames[index])

        #Replace previous list in order ot keep code a little cleaner
        fileNames = newList
        reportName = str(tag)
    except:
        print('ERROR: ', sys.exc_info()[0])
        print('Please make sure you have selected a tag that exists\nUse -l to list all possible tags ')
        raise SystemExit

#Removes extension of reportname if present
reportName = os.path.splitext(reportName)[0] + ext
#Set output for log file
output = ''

#Reading each value from currently stored array
for testFile in fileNames:
    passed = runTest(testFile, reportName)

    indexOfTestFile = fileNames.index(testFile)

    print(tags[fileNames.index(testFile)])
    #Write output to report file (and terminal)
    if passed == '1':
        output += testFile + ' file has passed testing. '
    else:
        output += testFile + ' file has failed testing. '
        if tags[indexOfTestFile] == 'must_pass':
            output += 'This test is marked as must_pass. Exiting...'
            break
    output += 'Result = ' + passed + ' Test is tagged as: ' + tags[indexOfTestFile] + '\n'

print(output)
#Write output to reportfile
with open(reportName, 'w') as f:
    print(output, file=f)

#Delete compiled bytecode files that are generated on import
os.system("rm -rf *.pyc")
