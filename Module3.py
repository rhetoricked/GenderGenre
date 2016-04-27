'''
GenderGenreMod3
Copyright 2016 Brian N. Larson and licensors

GENDER/GENRE PROJECT CODE: Module 3
This code is the third of four segments used to generate the data for the article
"Gender/Genre: The lack of gendered stylistic differences in texts requiring
genre knowledge," published in Volume ___, Issue ___ of the journal _Written
Communication_ (the "Article").

For each of three corpora ("Nonfacttext", "Facttext", "Fulltext"), this code
identifies all the POS bigrams and trigrams in it and determines the 100 most
common bigrams and 500 most common trigrams. It saves those as pickles to be
used in Module4.

'''

######
#TOOLS AND OPERATING SYSTEM stuff
######

from __future__ import division
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
#nltk.download()
import numpy, re, pprint, matplotlib, pylab #re is for regular expressions

#Sentence tokenizer (sentence splitter using sent_tokenize default, which is?)
from nltk.tokenize import sent_tokenize
#Word tokenizer Version using TreebankWorkTokenizer
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()

######
#DIRECTORY AND FILE VARIABLES
######
#These set some of the working directories and files. They are set manually,
#and users should be sure that the directories exist and are empty before running
#the code.

#Following line is name selected for directory with corpora out from Module 2.
existingNLTK_dir = "NLTKCorporaUncatUntag/"

print ("\n \n \nYou must enter a directory path for a directory that contains ")
print ("a folder called " + existingNLTK_dir + " with corpor files from Module 2.")
print ("Be sure to include the / at the end of the path! \n \n")
home_dir = input("Enter the path for the data working directory root:")

#Next line sets directory where the corpora files are. This code could be
#more efficient.
working_root = home_dir + existingNLTK_dir
#Next line sets the location of the pickles that are the outputs of this module.
#Note that this directory is a sister of the existingNLTK_dir. The line after
#makes this directory if it does not already.
pickle_dir = home_dir + "Pickles/"
os.makedirs(pickle_dir, exist_ok=True)

#####
#DEBUGGING CODE
#####
#The following lines relate to options for debugging the code.

#The following line sets up debugging, which allows the recording of notices
#regarding the progress of the module to be printed to the screen or recorded
#in a log file.
logging_file = home_dir + 'Module3' + " " + str(now + ".log")
logging.basicConfig(filename=logging_file, filemode='w', level=logging.DEBUG)
#To log to a file, add these parameters to previous basicConfig:
# filename=logging_file, filemode='w',
#To log to the console, delete the parameters in the previous line.

#This code records some basic run information
logging.debug(" Gender/genre Module 3: Run " + str(now))
logging.debug(" Run on data in " + home_dir)
logging.debug(" Source of corpora files out from Module 2: " + existingNLTK_dir)
logging.debug(" Output from this module in: " + pickle_dir)

#For testing, it may be desirable to pull just a few papers. The next variable works
#with code below to select only those files from the start_wd directory that
#begin with these characters. Note that these are strings and should be only
#four characters long.
sought_papers = ["1007", "1055", "2021"]

######
#FUNCTIONS SEGMENT
# sets up functions that will be used below.
######

#FUNCTION process
# This function has the main payload of this module. The main code below runs
# this function once for each "section" of each text, fulltext, facttext, and
# nonfacttext. The section processed is the only parameter passed to this function.
def process(section) :
    #The next lines set directories and pickle names.
    nltkcorpus_dir = working_root + section +"/"
    trigrampickle = pickle_dir + section +"trigram.pickle"
    bigrampickle = pickle_dir + section + "bigram.pickle"

    #The next lines initialize set variables to keep a running tally of bigrams
    #and trigrams over all the papers.
    aggregate_bigrams = [ ]
    aggregate_trigrams = [ ]

    #Begin loop over papers
    logging.debug("Reached")
    count = 0
    for file_name in os.listdir(nltkcorpus_dir):
        count = count + 1;
        paper_num = file_name[0:4] #Note: this makes paper_num a str
        ###ONE OF THE TWO FOLLOWING IF-STATEMENT ALTERNATIVES MUST BE COMMENTED OUT
        #ALTERNATIVE 1:
        #If-statement on the next line is one of two options. This one
        #screens out Mac oS hidden files names of which start '.'
        if (not file_name.startswith('.') )  :
        #ALTERNATIVE 2:
        #If-statement on the next line is one of two options. This one does
        #the same as the preceding line, but it also limits the run just to
        #those papers specified in the sought_papers variable above.
#        if ((not file_name.startswith('.')) and (paper_num in sought_papers) ) :

            filepath = nltkcorpus_dir + file_name
            logging.debug("\n***********")
            logging.debug("Paper #: " + paper_num)
            logging.debug("At: " + filepath)
            #opens the subject file , reads its contents, and closes it.
            f = open(filepath, 'r', encoding = 'utf-8')
            infile = f.read()
            f.close()

            #Tokenize infile into sentences. The result is a list of sentences.
            sentences = sent_tokenize(infile)

            #Begin loop over sentences in paper.
            for i in sentences: #For each sentence in the paper...
                #Word-tokenize it.
                tokenized = tokenizer.tokenize(i)
                #Result is a list of word-tokens.

                #POS Tag it
                postagged = nltk.pos_tag(tokenized)
                #Result is a list of tuples, with word-token and pos-token.

                #Find trigrams in this sentence.
                trigrams = nltk.trigrams(postagged)
                #Result is a list of lists of lists.

                for i in trigrams: #For each trigram in the sentence...
                    aggregate_trigrams.append(i)
                    #Append that trigram to the global aggregate_trigram.

                #Next three lines repeat the previous steps, except with
                #bigrams in stead of trigrams.
                #Find bigrams in this sentence.

                bigrams = nltk.bigrams(postagged)
                #Result is a list of lists of lists.

                for i in bigrams:
                    aggregate_bigrams.append(i)

            #end loop over files

    #Here begins the number crunching, looking for the most common bigrams
    #and trigrams.

    #We do the same things for bigrams and trigrams:
        #1. ID each instance of a bigram, create a text label for it,
            #and add it to the list agg_posbigrams.append(v)
        #2. Do a frequency distribution of the bigram and create a list
            #of its items.
        #3. Pickle that list (for use later)
    logging.debug("\n**************************")
    logging.debug("TOP BIGRAMS")
    logging.debug("\n**************************")
    agg_posbigrams = [ ]
    for l in aggregate_bigrams:
        v = "Bi_"
        for m in l:
            v += m[1]
            v += "_"
        v = v[:-1]
        agg_posbigrams.append(v)

    fdistbigram = nltk.FreqDist(agg_posbigrams)
    bigramlist = list(fdistbigram.items())
    logging.debug(bigramlist[:50])
    pickle.dump(bigramlist, open (bigrampickle, "w+b"))

    logging.debug("\n**************************")
    logging.debug("TOP TRIGRAMS")
    logging.debug("\n**************************")
    agg_postrigrams = [ ]
    for l in aggregate_trigrams:
        v = "Tri_"
        for m in l:
            v += m[1]
            v += "_"
        v = v[:-1]
        agg_postrigrams.append(v)

    fdisttrigram = nltk.FreqDist(agg_postrigrams)
    trigramlist = list(fdisttrigram.items())
    logging.debug(trigramlist[:50])
    pickle.dump(trigramlist, open (trigrampickle, "w+b"))
    logging.debug("Good job")

#####
#MAIN PROGRAM CODE
#####
# This merely processes the different sections with the same method and saves
# them in different output folders

process("Nonfacttext")
process("Facttext")
process("Fulltext")
