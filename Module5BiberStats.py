'''
This app needs to be run only for Fulltext.

'''
#!/usr/bin/env python
from __future__ import division

#Set up run-time variables for files and directories.


import os
import shutil
import sys
import pickle
import logging
import datetime
now = datetime.datetime.now().strftime("%y-%m-%d %H.%M.%S")
from io import StringIO #"For strings StringIO can be used like a file opened in
                        #text mode." See https://docs.python.org/3/library/io.html
import nltk
import numpy, re, pprint, matplotlib, pylab #re is for regular expressions
import scipy.stats as stats
import csv
from numpy import std, mean, sqrt


######
#DIRECTORY AND FILE VARIABLES
######
#These set some of the working directories and files. They are set manually,
#and users should be sure that the directories exist and are empty before running
#the code.

#Following line is name selected for directory with corpora out from Module 2.
existingNLTK_dir = "NLTKCorporaUncatUntag/"

#Use next five lines only if you want to solicit end-user input regarding
#directorly
#print ("\n \n \nYou must enter a directory path for a directory that contains ")
#print ("a folder called " + existingNLTK_dir + " with corpora files from Module 2.")
#print ("And THAT folder has to have a Pickles/ directory in it.")
#print ("Be sure to include the / at the end of the path! \n \n")
#home_dir = input("Enter the path for the data working directory root:")

home_dir = "/Users/brianlarson/ProjectsLocal/160728BNLTestBiberModule/"

run_root = home_dir

xml_dir = run_root + "XMLOutfromPython/"
pickle_dir = run_root + "NLTKCorporaUncatUntag/Pickles/"

#####
#DEBUGGING CODE
#####
#The following lines relate to options for debugging the code.

#The following line sets up debugging, which allows the recording of notices
#regarding the progress of the module to be printed to the screen or recorded
#in a log file.
logging_file = home_dir + 'Module5BiberStats' + " " + str(now + ".log")
logging.basicConfig(filename=logging_file, filemode='w', level=logging.DEBUG)
#To log to a file, add these parameters to previous basicConfig:
# filename=logging_file, filemode='w',
#To log to the console, delete the parameters in the previous line.

#This code records some basic run information
logging.debug(" Gender/genre Module 4BiberStats: Run " + str(now))
logging.debug(" Run on data in " + home_dir)
logging.debug(" Source of pickle file out from Module 4Biber: " + pickle_dir)
logging.debug(" Output from this module in: " + run_root)

#Check for Gaussian distribution in the values
logging.debug("Checking for Gaussian distribution.")

def cohen_d(x,y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return ((mean(x) - mean(y)) / sqrt(((nx-1)*std(x, ddof=1) ** 2 +
        (ny-1)*std(y, ddof=1) ** 2) / dof))

def mannw(x,y):
    #using the method described at http://www.real-statistics.com/non-parametric-tests/mann-whitney-test/
    n1 = len(x)
    n2 = len(y)
    if ((sum(x) == 0) or (sum(y) == 0)):
        mwU_p = ["n/a", 1, "n/a", "n/a"]
        return mwU_p
    else:
        mwU_p = list(stats.mannwhitneyu(x, y))
        U = mwU_p[0]
        meanU = n1 * n2 / 2
        varU = meanU * (n1 + n2 +1 )/6
        stdvU = sqrt(varU)
        zscore = abs(U - meanU)/stdvU
        rscore = zscore / sqrt(n1 + n2)
        mwU_p.append(zscore)
        mwU_p.append(rscore)
        return mwU_p

def process(section):
    valsPickle = pickle_dir + section + "Features.pickle"
    print(valsPickle)
    logging.debug("Loading: " + valsPickle)
    with open(valsPickle, "rb") as p:
        papers = pickle.load(p)

    csv_out_file = run_root + "BiberStatsOutput " + section + " " + str(now) + ".csv"

    statskeys = ["A_tokens", "A_sents", "A_words", "02PrivateVerbs",
            "03ThatDeletion", "04Contractions", "05PresVerbs", "06SecPersPrn",
            "07DOproverb", "08AnalyticNeg", "9DemoPron", "10GenEmphatics",
            "11FirstPersPrn", "12It", "13BeMain", "14CauseSub", "15DiscPart",
            "16IndefPro", "17GenHedges", "18Amplifiers", "19SentRelatives",
            "20WhQuestion", "21PossModals", "23WhClauses",
            "24FinalPreps", "25Adverbs", "26Nouns", "27WordLength", "28Preps",
            "29TTRatio", "30AttribAdj"]

    gArray = []
    gIndex = 0
    for key in statskeys:
        g0Values = []
        g1Values = []
        gValues = []
        for p in papers:
            if p["01Gender"] == "0":
                g0Values.append(p[key])
            if p["01Gender"] == "1":
                g1Values.append(p[key])
        gValues = g0Values + g1Values
        # print("gValues")
        # print(gValues)
        # print("g0Values")
        # print(g0Values)
        # print("g1Values")
        # print(g1Values)
        #
        gTest = list(stats.normaltest(gValues))
        g1mean = numpy.mean(g1Values)
        g1stdev = numpy.std(g1Values)
        g0mean = numpy.mean(g0Values)
        g0stdev = numpy.std(g0Values)
        g0size = len(g0Values)
        g1size = len(g1Values)
        if g1mean > g0mean:
            prevalence = "F"
        else:
            if g0mean > g1mean:
                prevalence = "M"
        if gTest[1] < 0.05:
            gDesignator = "Not Gaussian"
            #Next line implements rank biserial correlation to test effect size.
            #effectSize = (1 - (2*sigTest[0])) / (g0size * g1size)
        else:
            gDesignator = "Gaussian"
            #sigTest = stats.ttest_ind(g0Values, g1Values)
            #Next line implements Cohen's d to test effect size.
            #effectSize = cohen_d(g1Values, g0Values)
        sigTest = mannw(g0Values, g1Values)
        if sigTest[1] < 0.05:
            sDesignator = "*"
        else:
            sDesignator = ""
        #Struture of the gArrayRow (which follows): key name, gender 0 mean, gender 0
        #   standard dev, gender 1 mean, gender 1 st dev, prevalent gender, Gaussian
        #   test statistic, Gaussian p value, Gaussian indicator, significance test
        #   statistic (U if non-Gaussian, t stat if Gaussian), significance p value,
        #   significance indicator, effect size
        gArrayRow = [key, g0mean, g0stdev, g1mean, g1stdev, prevalence, sigTest[0],
            sigTest[1], sDesignator, sigTest[3], gTest[0],
                gTest[1], gDesignator, sigTest[2]]
        print(gArrayRow)
        gArray.append(gArrayRow)
        logging.debug(gArrayRow)
        gIndex += 1

    with open(csv_out_file, "w") as csv_out:
        headers = ["Feature", "M mean", "M stdev", "F mean", "F stdev", "prevalence",
        "MW U", "MW p", "Signif", "rscore", "Gaussian test", "Gaussian p", "Gaussian",
        "zscore"]
        csvwriter = csv.writer(csv_out)
        csvwriter.writerow(headers)
        csvwriter.writerows(gArray)

process("Nonfacttext")
process("Facttext")
process("Fulltext")
