#!/usr/bin/env python
'''
This application needs to be run three times, once each with Fulltext, Facttext, and Nonfacttext.
The file names need to be changed in the block below before the 2nd and 3rd runs.

'''
from __future__ import division

#Set up run-time variables for files and directories.
run_root = "/Users/brianlarson/Dropbox/Terminal/140209Data/"
nltkcorpus_dir = run_root + "NLTKCorporaUncatUntag/Nonfacttext/"
pickle_dir = run_root + "NLTKCorporaUncatUntag/Pickles/"
featurepickle = pickle_dir + "NonfacttextFeaturesPrefixes.pickle"
relation = "gender-nonfacttext" #This is what appears in Weka with dataset.
arff_out = run_root + "NonfacttextFeatures.ARFF"

import os
import shutil
import sys
import pickle
import nltk
import numpy, re, pprint, matplotlib, pylab #re is for regular expressions
import csv

features = pickle.load( open ( featurepickle, "rb"))

stdout = sys.stdout
sys.stdout = open(arff_out, 'w')

#. Write the ARFF file header information.
print '%TITLE: ARFF output for features of' + nltkcorpus_dir
print
print '@relation  ' + relation
print

keys = sorted(features[0].keys()) #We'll use this variablfe twice; so it's not declared in the following for-loop.
for i in keys:
    i = i.strip() #The next few lines reformat the strings to make them (a) acceptable and (b) easier to read.
    i = i.replace(" ", "-")
    if i.startswith("$"):
        i = "d" + i
    i = i.replace('``', 'OQuote')
    i = i.replace("''", "CQuote")
    if i == "d$$gender":
        print '@attribute \"' + i + '\" { 0, 1 }'
    else:
        print '@attribute \"' + i + '\" numeric'

print
print '@data'

for i in features:              #We take one paper at a time.
    s = ''                      #Declar the string variable we'll write out.
    for j in keys:              #We take one key at a time.
        s += str(i[j]) + ","    #Write the value for the key, add a comma, and move on.
    s = s[:-1]                  #Removes the last comma.
    print s                  #Write it to the file
sys.stdout = stdout
