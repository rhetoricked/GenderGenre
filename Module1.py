'''
GenderGenreMod1
Copyright 2016 Brian N. Larson and licensors
License:

GENDER/GENRE PROJECT CODE: Module I
This code is the first of four segments used to generate the data for the article
"Gender/Genre: The lack of gendered stylistic differences in texts requiring
genre knowledge," published in Volume ___, Issue ___ of the journal _Written
Communication_ (the "Article").

The rest of this should be in the repository README, no?

Data collection and preparation, including human coding of key text spans, are
described in the Article and in Larson, B. (2015, May). Gender/Genre: Gender
difference in disciplinary communication (Ph.D. dissertation). University of
Minnesota, Minneapolis.

The original text artifacts for this study were Microsoft Word files (and one
PDF converted by the researcher to Word). Those files are available from...

The Article points to the following external
resources: (1) Online appendices available at GATech.edu at the specific address
identified in the Article; (2) The corpus of underlying texts (in MS Word format)
that are processed here, available from the Linguistic Data Consortium at the
specific address identified in the Article.

This code takes XML output from GATE (), enriches it with data from the
questionnaire that Larson administered to students, produces clean texts of
sections of the student documents after removing citations, etc.

NOTE: As ofr April 5, 2016, this code fails to perform on a small number (7)
of the 200 or so texts put through it. Performance/responses are explained in
Evernote note available to the project team. The console output for this
program makes it possible to see where the problems are, and they can be
corrected manually before the next phase.

'''

######
#TOOLS AND OPERATING SYSTEM stuff
######

from __future__ import division
import sys
sys.path.append('/users/Pranov/Documents/Research/2.7/')

#import numpy #BNL delete this line as Pranov did not need it?
import re #re is for regular expressions
import pprint #pretty print for formatting xml out to be more human-readable
import matplotlib
import pylab
import nltk
from lxml import etree
#import xml.etree.ElementTree as etree #BNL: Ask Pranov if we should delete.
import os
import csv
import shutil
import codecs
from io import StringIO #"For strings StringIO can be used like a file opened in
                        #text mode." See https://docs.python.org/3/library/io.html

# The following parser change for lxml results from this recommendation:
# http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
# That recommendation related to Python 2.7.
parser = etree.XMLParser(remove_blank_text=True, encoding='UTF-8')
#it affects subsequent etree.parse calls that use it as a second argument

######
#RUN TIME VARIABLES
######
#These set some of the working directories. They are set manually, and users
#should be sure that the directories exist and are empty before running
#the code

#sys.setdefaultencoding('utf8') #BNL ask Pranov about deleting. Looks like it doesn't work in Py3.x

#The next directory is the "root" for the work this code does.
home_dir = "/Users/brianlarson/ProjectsLocal/160405TestOfPython2OnMacBookAir/"
#The next directory is where the xml files from GATE are stored. This code does not
#alter the original files
start_wd = home_dir + "XMLoutfromGATE/"
#The next folder is for files from GATE that do not have human annotations in them.
#They are copied to this folder to allow inspection.
defective_xml_out = home_dir + "DefectiveXMLfromGATE/"
#The next folder is where the output of this code is placed.
xml_output_dir = home_dir + "XMLOutfromPython/"
#BNL ask Pranov if we can delete The next line.
end_wd = "/Users/brianlarson/ProjectsLocal/160405TestOfPython2OnMacBookAir/"
#The next line sets the file where the CSV data from the Excel export is. Obviously,
#the named file has to be in home_dir
csv_file = home_dir + 'MasterDataForXML.csv'

#For testing, it may be desirable to pull just a few papers. The next variable works
#with code below to select only those files from the start_wd directory that
#begin with these characters. Note that these are strings and should be only
#four characters long.
sought_papers = ["1007", "1055", "2021"]

#Large segments excluded from processing
#The files in GATE are manually annotated to delimit several large segment types.
#The next variable identifies the large segment types that are excluded from processing
lg_segments_out = ["Caption", "TOCTOA", "OtherFormal"]

#BNL ask Pranov about moving sm_segments_out here.

#The next two variables IDs the annotation sets that are possible based on who
#the annotators were. These are the initials of the human annotators who did
#annotations in GATE.
as1 = "SLL"
as2 = "BNL"

##FUNCTIONS SEGMENT
## sets up functions that will be used below.
def add_unq_subelement(parent, name): #Adds a unique subelement to parent.
    #print("add unique subelement") #Uncomment this line only for debugging.
    # parent is a tree element or subelement. name will be the name of a subelement under parent
    #First check to see if there is already an element with this name.
    name_present = False #This value is switched to True only if an element by this name is already present.
    for element in parent: #Test whether element by this name is already present.
        if element.tag == name:
            print( "Func add_unq_subelement: This parent already has a " + name + " subelement!")
            name_present = True
    #If this subelement does not already exist, create it.
    if name_present == False:
        return etree.SubElement(parent, name)

def add_unq_feature(parent, name, value): #Adds a unique feature under an element
    #print("Add unique  feature") #Uncomment this line only for debugging.
    # parent is a tree element or subelement. name and value will apply to the
    # newly created feature
    #First check to see if there is already a feature with this name.
    f_present = False   #This value is switched to True only if a Feature by this
                        #name is already present.
    for i in range(len(parent)):    #This iterates through the parent
                                    #looking for a Feature subelement with this
                                    #name.
        if parent[i].tag == "Feature" and parent[i].get("Name") == name:
            print( "Func add_unq_feature: This element's " + name + " feature is already set!")
            f_present = True
    #If a Feature by this name does not already exist, create it.
    if f_present == False:
        return etree.SubElement(parent, "Feature", Name = name, Value = value)

def get_csv_data(file_name, paper_num):     #This function returns the record
                                            #from the Micrsoft Excel worksheet
                                            #(file_name) with
                                            #information about the paper (paper_num).
    print("Get csv data")
    with open(file_name, 'rU') as csvfile:
        csv_in = csv.DictReader(csvfile, dialect = 'excel')
        for record in csv_in:
            if record['UniqueID'] == paper_num:
                return record #This is a dictionary object.
            #If there is no match, this function returns "FAIL"
            #for which the line of code that uses it below tests.

def add_xl_features(docroot, paper_num, record):    #Takes a Gate xml doc and adds
                                                    #GG elements and features.
    #"GG" here stands for Gender/Genre, the name of this project.
    #Add GG element under root and Questionnaire under GG
    print("add xl features") #Uncomment this line only for debugging.
    gg = add_unq_subelement(doc_root, "GG")
    add_unq_feature(gg, "PaperNum", paper_num)
    quest = add_unq_subelement(gg, "Questionnaire")
    for key in record.keys():   #This uses the excel data pulled with the
                                #get_csv_data function.
        add_unq_feature(quest, key, record[key])
    # print etree.tostring(gg, pretty_print = True) #Uncomment this line for debug only
    print( "XL features added to " + paper_num) #Uncomment this line only for debugging.

def verify_annotation(docroot, paper_name):     #Examines an XML file to make
                                                #sure an as1 or as2 annotation
                                                #set appears on it.
                                                #If there is none, this function
                                                #Copies the xml from GATE to
                                                #a "defective" folder, making it
                                                #easier for researcher to
                                                #locate and inspect them.
    print("Verify Annotation")
    names = [as1, as2]
    as_present = False  #This tracking variable is reset as true only if one
                        #of the approved annotator sets is present.
    for i in range(len(docroot)):   #Iterates over annotation sets and
                                    #checks for presence of one of the
                                    #approved annotator sets.
        if docroot[i].tag == "AnnotationSet" and docroot[i].get("Name") in names:
            as_present = True
    if as_present == False:
        #Copies file to "defective" folder.
        paper_path = os.path.join(start_wd, paper_name)
        print( "\n\n")
        print( "NO ANNOTATIONS IN " + paper_name + ": Copying " + paper_path + " to " + defective_xml_out)
        shutil.copy(paper_path, defective_xml_out)
        return False
    else:
        return True

def extract_original_text(gatefile): #extracts the original text TextWithNodes from the GATE output in string form.
    #Opening the original file in regular file mode lets us get at the text in it and do REgex operations without
        #freaking out the XML parser.
    #original alternative BNL: check with Pranov and delete this.
#    with open(gatefile) as f: #This reopens the original file, NOT as xml, and read-only.
#        original = f.read() #Creates a string from the original file.
#        original = unicode(original, errors='ignore')
#        re_s = re.compile(ur'<TextWithNodes>.*</TextWithNodes>', re.DOTALL) #Compiles regexpression. DOTALL allows .* to
                                                                                       #match line-ends.
#        return re_s.findall(original)[0] #Findal returns a LIST of segments from whole_doc that match re_s. Picking the first index
                                         #gives us the string at that point in the list. That should always be the one we want
                                         #because there should be only one!
    #end original alternative

    #Second alternative
    print("Extract Original Text")
    print(gatefile) #Uncomment this line only for debugging.
    gatefile = start_wd + gatefile
    print(gatefile) #Uncomment this line only for debugging.
    f = codecs.open(gatefile, encoding="utf-8")     #BNL ask Pranov whether we
                                                    #actually need this for Py3.x
    original = f.read()
    re_s = re.compile('<TextWithNodes>.*</TextWithNodes>', re.DOTALL)
    #In previous line, re.DOTALL option causes a '.' to match any character,
    #including a newline. Normally, '.' matches any character BUT a newline.

    result = re_s.findall(original)[0]
    f.close()
    return result
    #end second alternative #BNL delete this if you delete first alternative.

def get_annotation_set(root):   #Given an xml root, this returns the identifier
                                #for the annotation set that should be used.
                                #It prefers the as1 set where both are present.
    print("Get annotation root")
    as1_present = False
    as2_present = False
    for i in range(len(root)):
        if root[i].tag == "AnnotationSet" and root[i].get("Name") == as1:
            as1_present = True
        else:
            if root[i].tag == "AnnotationSet" and root[i].get("Name") == as2:
                as2_present = True
    if as1_present:
        print ("Annotator as1 (" + as1 + ") is present.")
        return as1
    else:
        if as2_present:
            print( "Annotator as2 (" + as2 + ") is present.")
            return as2
        else:
            return "ERROR: Neither annotator as1 nor as2 is present."

def extract_node_range(text,start,end):     #This function works on string, not
                                            #XML. It returns the node markers
                                            #and all text between
                                            #them indicated by the start and end
                                            #nodes.
    #print("Extract node range") #Uncomment this line only for debugging.
    re_string = r'<Node id=\"' + start + r'\"/>.*<Node id=\"' + end + r'\"/>'
    u = re.compile(re_string, re.DOTALL)
    v = u.findall(text)
    if not v:
        return "ERROR: Node range not matched in this document!"
    else:
        return v[0]

def delete_span_text(text,start,end):   #This function takes a string, not XML,
                                        #that has node markers and text in it
                                        #and removes all the text from between
                                        #the specified start and end node
                                        #markers, leaving the node markers.
    #print("delete span text") #Uncomment this line only for debugging.
    re_pattern = r'<Node id=\"' + start + r'\"/>.*<Node id=\"' + end + r'\"/>'
    re_repl = '<Node id=\"' + start + '\"/><Node id=\"' + end + '\"/>'
    text = re.sub(re_pattern, re_repl, text, flags=re.DOTALL)
    return text

def delete_segments(text, root, aset, lg_segs, sm_segs):
                                #This function iterates through XML annotations.
                                #Edits happen to a text string.
                                #Function IDs segements where there is text
                                #that should be deleted, sending
                                #their start and end nodes to delete_span_text.
    print("delete segments") #Uncomment this line for debugging only.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text in lg_segs:
                            text = delete_span_text(text,start_node,end_node)
                else:
                    if f.get("Type") in sm_segs:
                        start_node = f.get("StartNode")
                        end_node = f.get("EndNode")
                        text = delete_span_text(text,start_node,end_node)
    return text

def fact_delete(text, root, aset): #Iterates through XML features.
                                   #Identifies the start end end of the Fact
                                   #section using XML features, and removes that
                                   #text from the text string by sending to
                                   #delete_span_text.
    print("Fact delete") #Uncomment this line for debugging only.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text == "Facts":
                            text = delete_span_text(text,start_node,end_node)
    return text

def lg_seg_xtract(text, root, aset, lg_seg):    #Originally, this is just to permit
                                                #pulling the Facts section out,
                                                #but it would work with other
                                                #sections, too.
    print("Lg seg extract") #Uncomment this line for debugging only.
    for e in root.iter("AnnotationSet"):
        if e.get("Name") == aset:
            for f in e.iter("Annotation"):
                if f.get("Type") == "LargeSegment":
                    start_node = f.get("StartNode")
                    end_node = f.get("EndNode")
                    for g in f.iter("Value"):
                        if g.text == lg_seg:
                            re_string = r'<Node id=\"' + start_node + r'\"/>.*<Node id=\"' + end_node + r'\"/>'
                            u = re.compile(re_string, re.DOTALL)
                            try:
                                text = u.findall(text)[0]
                            except IndexError:
                                text = "Function error (lg_seg_xtract): Regex search function did not match any text."
                                print (text)
    return text

def nodes_out(text):    #This function texts a string (not XML) and removes
                        #all the node markers in it!
    #print("nodes out") #Uncomment this line for debugging only.
    re_pattern = r'<.*?>'
    re_repl = ''
    text = re.sub(re_pattern, re_repl, text, flags=re.DOTALL)
    return text

def cleanUTF8(doc) : #BNL: There is a tag in the header of the XML file that
                        #that comes from GATE. This function deletes that tag.
    utf = r'encoding=.UTF-8.'
    found = re.search(utf, doc)
    print('__________________________________________')
    print(found)
    print('__________________________________________')
    cleanDoc = doc[0:found.start()] + doc[found.end():]
    return cleanDoc


##MAIN LOOP This loop iterates over files in start_wd directory and does stuff to files.
os.chdir(start_wd)

#Had to set class path manually as it was pointing to an empty folder
#BNL let Pranov know I changed this to point to start_wd, which needs to be updated...
#when code is run from a different location.
name_path = start_wd

for orig_gate_doc_name in os.listdir(name_path):
    #print(os.getcwd())
        #If statement screens out Mac OS hidden files, names of which start '.' and
        #researcher-excluded files, which start xxxx;
    if (not orig_gate_doc_name.startswith('.') and not orig_gate_doc_name.startswith('xxxx') ):
        #If sought_papers is specified above and researcher wants to limit run
        #to them, add the following condition to previous if statement
        #and orig_gate_doc_name[0:4] in sought_papers.

        orig_doc = open(name_path + orig_gate_doc_name, "r", encoding = "UTF-8")
        orig_doc_content = orig_doc.read() #This creates a string object.
        print("Entered Loop")
        print(orig_gate_doc_name)
        #print(StringIO(orig_doc_content).getvalue())
        #print(orig_doc_content)

        #Next line removes the UTF8 tag from the XML file that came from GATE.
        orig_doc_content = cleanUTF8(orig_doc_content)
        #Next line parses file with defined parser creating ElementTree
        gate_doc = etree.parse(StringIO(orig_doc_content), parser)
        doc_root = gate_doc.getroot() #Get root Element of parsed file
        paper_num = orig_gate_doc_name[0:4] #NOTE: this makes paper_num a str

        #In next if statement, run verify_annotation as a condition of
        #processing the file further.
        #If verify_annotation is false, we move to next file.
        if verify_annotation(doc_root, orig_gate_doc_name):
            xl_rec_contents = get_csv_data(csv_file, paper_num) #Gets corresponding
                                                                #data from CSV file.
            if xl_rec_contents == "FAIL":
                #If there's no Excel/CSV data matching, we move to the next file.
                print( "Paper num: " + paper_num + " not appearing in CSV file!")
            ##Assuming we pass those two checks, we get to process the file.

            ###########
            ##THIS IS THE PAYLOAD, WHERE EVERYTHING HAPPENS
            ###########
            else:
                print('\n\n')
                print("************************")
                print("PAPER NUMBER: " + paper_num)
                print("************************")

                #Add features from the Excel file (survey, etc.) to the xml file.
                add_xl_features(doc_root, paper_num, xl_rec_contents)

                #Save the results to a new XML file (we don't edit the
                #original from GATE at all.)
                #Next line creates new name for the xml output of this program
                #(this version replaced by next line)
                rev_gate_doc_name = xml_output_dir + orig_gate_doc_name

                gate_doc.write(rev_gate_doc_name, pretty_print = True,
                                xml_declaration=True, encoding='UTF-8')
                    #xml_declaration and encoding necessary to open UTF later
                print( "Saved as " + rev_gate_doc_name)

                #Next line reads the new file in. Parses the new file into etree.
                xml_doc = etree.parse(rev_gate_doc_name, parser)
                #Next line creates a variable for referring to the root of
                #this xml doc.
                xml_root = xml_doc.getroot()

                #Next line gets the TextWithNodes from the original file
                orig_w_nodes = extract_original_text(orig_gate_doc_name)
                #NOTE: In the next few lines, we are operating on the string
                #pulled in from orig_gate_doc_name, not on the
                #XML file. This allows us to treat regard the XML nodes as
                #strings rather than having to use complicated
                #XML parsing to clean them out of the string before
                #it can be passed to NLP functions like splitter, tokenizer, etc.

                #print orig_w_nodes #Uncomment this line for debugging only

                ###
                #The following lines delete from orig_w_nodes the text components
                #from all segments that will not be analyzed.
                #They prefer the annotation set ascribed to as1, otherwise use as2.
                ###
                gate_ann_set = get_annotation_set(xml_root)
                sm_segments_out = ["Heading", "Footnote", "Cite", "Blockquote"] #List of small segments to be cleansed.
                #BNL Ask Pranov about moving previous line to run-time variables above. Why set for each paper?

                orig_w_nodes = delete_segments(orig_w_nodes, xml_root, gate_ann_set, lg_segments_out, sm_segments_out)

                #Next two lines create two new strings for the text that is
                #just the facts and text that is everything but facts.
                nonfact_w_nodes = fact_delete(orig_w_nodes, xml_root, gate_ann_set)
                facts_w_nodes = lg_seg_xtract(orig_w_nodes, xml_root, gate_ann_set, "Facts")
                #print facts_w_nodes #Uncomment this line for debugging only.

                #We now have three strings, each cleansed of segments we don't
                #want but each having the node markers, which we now no longer
                #need. We first create a place in our XML document to hold the
                #results...
                cleantext = add_unq_subelement(xml_root,"Cleantext")
                cleanfull = add_unq_subelement(cleantext, "CleanFull")
                cleannonfact = add_unq_subelement(cleantext, "CleanNonFact")
                cleanfact = add_unq_subelement(cleantext, "CleanFact")

                #...then we put the results in after running through the
                #nodes_out function.
                try:
                    cleanfull.text = nodes_out(orig_w_nodes)
                except ValueError:
                    print ("XML error thrown while writing cleanfull.text: ")
                try:
                    cleannonfact.text = nodes_out(nonfact_w_nodes)
                except ValueError:
                    print ("XML error thrown while writing cleannonfact.text: ")
                try:
                    cleanfact.text = nodes_out(facts_w_nodes)
                except ValueError:
                    print ("XML error thrown while writing cleanfact.text: ")

                #Finally, we write the revised XML file out.
                xml_doc.write(rev_gate_doc_name, pretty_print = True,
                                xml_declaration=True, encoding='UTF-8')

##POST-LOOP
os.chdir(end_wd)
