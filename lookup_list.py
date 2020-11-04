import requests
import json
import wikipedia
import re
import os
import sys

if len(sys.argv) >= 2:
    if sys.argv[1]=="log": # If log parameter is present, enable logging

        class Logger(object):
            def __init__(self):
                self.terminal = sys.stdout
                self.log = open("logfile.log", "w")

            def write(self, message):
                self.terminal.write(message)
                self.log.write(message)  

            def flush(self):
                pass    

        sys.stdout = Logger()

        print("Logging is enabled, creating logfile.log...\n")

def lookup(word, num_sentences):
        
    try: # try Google dictionarty first
        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word) # get response from (unofficial) Google Dictionary API (as JSON)
        response.raise_for_status() # returns an HTTPError object if an error has occurred
        # access JSON content
        jsonResponse = response.json() if response and response.status_code == 200 else None
        definition = jsonResponse[0]["meanings"][0]["definitions"][0]["definition"] # this is how you get the first definition
        definition = definition[0].lower() + definition[1:]  # lowercase the first letter
        print("The definition of "+word+" is: "+definition)

    except Exception as err: # if there's an error (can't find the word on Google Dictionary)
        # print(f'   HTTP error occurred: {http_err}') # might need this for diagnosing HTTP errors # (requires 'from requests.exceptions import HTTPError')
        print(f'   An error occurred getting the definition from Google: {err}')
        print("   Definition not found on Google for '"+word+"'. Checking Wikipedia instead...")
        try:
            definition=wikipedia.summary(word, sentences=num_sentences, auto_suggest=True, redirect=True) # try to find the word on Wikipedia
            if len(definition.split()) < 8: # if the definition contains fewer than 8 words
                print("   The definition of "+word+" was too short, getting definiton with "+str(num_sentences+1)+" sentences instead.")
                definition=wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence

        except Exception as err: # if a page isn't immedietly available (disambiguation, etc)
            print(err)
            try:
                print("   Couldn't find a Wikipedia article called '"+word+"'. Searching Wikipedia for relevant articles...")
                word=wikipedia.search(word)[0] # suggest the result
                print("   Wikipedia returned '"+word+"' as the best article. Getting summary of '"+word+"'...")
                definition=wikipedia.summary(word, sentences = num_sentences, auto_suggest=False, redirect=True) # get a summary of that article
                if len(definition.split()) < 8: # if the definition contains fewer than 8 words
                    print("   The definition of "+word+" was too short, getting definiton with "+str(num_sentences+1)+" sentences instead.")
                    definition=wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence
            except Exception as err:
                print(err)
                definition="No definition found."

        # print("According to Wikipedia, the extended definition is: "+definition)

        # experimental U.S. detection...
        # US_list = definition.split()
        # num_US=US_list.count("U.S.")
        # print("U.S. occured "+str(num_US)+" times in the string")
        # sentence_split=''
        # sentence_split.join(definition.split("U.S.", num_US)[:num_US])

        # sentence_split=definition.split('.')[0] # isolate the part before the first period
        # if len(sentence_split.split()) > 5: # if this first "sentence" contains more than 5 words
        #     definition=sentence_split # assign it to the definition

        # *******************
        # when there is a v. in the definition, it gets split. Solution, if word.contains("v."), get one extra sentence and split manually

        print("According to Wikipedia: "+definition)

        if ' is ' in definition or ' was ' in definition or ' are ' in definition or ' were ' in definition: # if the Wikipedia definition contains one of these words
            print("   Isolating the definition...")
            definition = re.split(" is | was | are | were", definition, maxsplit=1)[1] # split the definition once and assign the second part ([1]) to definition

    if '==' in definition: # if the definition contains dividers
        print("   Detected new heading divider. Isolating preceding text...")
        definition = definition.split('==')[0] # split the definition and assign the first part to definition
        print("Extracted: "+definition)

    print("   Cleaning up definition to remove excess characters, end periods, and line breaks...")
    definition = definition.strip() # strip any unnecessary start or end spaces
    definition = definition.replace('\n', ' ')
    if definition.endswith('.'): # if the last character is a period
        definition = definition[:-1] # remove end period
    return definition # return the definition of the word

def main(num_sentences): # main method
    try: 
        print("Opening words file...")
        file=open('words.txt', encoding='utf8') # open the words file
    except Exception:
        print("File not found.")
        print("Currently working in "+str(os.getcwd())) # print info about local directory and files to help diagnose missing words.txt
        print("Only files in this directory are: "+str(os.listdir()))
        input("\nPlease ensure words.txt is in the root directory (same folder where this program is located). Press Enter to continue.")

    words = [line for line in file.readlines() if line.strip()] # append each non-empty line of text in the file to the words list
    file.close() # close the file

    words = [word.strip() for word in words] # strip each line to remove unessecary characters

    print("\nThere are the terms I read:") # print the words list
    print(words)
    if num_sentences!=1:
        print("\nI will get definitions from Wikipedia with "+str(num_sentences)+" sentences.\n") # indicate the number of sentences getting from Wikipedia
    else:
        print("\nI will get definitions from Wikipedia with 1 sentence.\n") # indicate the number of sentences getting from Wikipedia
    
    definitions=[] # declare an empty definitions list

    bad_chars = ['“', '”'] # characters to remove before looking up

    for word in words:
        if '“' in word or '”' in word: # if any word contains quotes
            print("   "+word+" has a bad character. Fixing it...")
            for i in bad_chars: # check each bad character
                 word = word.replace(i, '') # replace the quote characters (from bad_chars) with nothing
            print("   It is now: "+word)
        print("Getting definition of '"+word+"' to add to dictionary...")
        definitions.append(lookup(word, num_sentences)) # look up the word (using num_sentences sentences) and append it to the dictionary list

    errors = [] # declare an empty list of errors

    for i in range(len(definitions)): # for each definition in the list
        if definitions[i] == "No definition found": # find each term without a definition
            errors.append(words[i]) # add each term without a definition to the list

    successful_words = len(words)-len(errors) # calculate the number of successfully defined terms

    definitions_file = open('wordsDefined.txt', 'w', encoding='utf8') # open the destination file for writing
    for i in range(len(words)): # for each element in the words list
        definitions_file.writelines(words[i]+" - "+definitions[i]+"\n") # write each 'word - definition' line
    print("\nSuccessfully wrote "+str(successful_words)+" out of "+str(len(words))+" terms and definitions to wordsDefined.txt.")
    if len(errors) == 1: # if there were errors, print them
        print("There was 1 term I could not define: '"+str(errors[0])+"'")
    elif len(errors) > 0:
        print("There were "+str(len(errors))+" terms I could not define: "+str(errors))

    definitions_file.close() # close the file

while True:
    try:
        print("Enter number of sentences to get from Wikipedia: ")
        num_sentences = int(input()) # get number of sentences from user
    except Exception: # if it is not an integer,
        print("Number must be an integer.") # inform the user and..
        continue # return to the start of the loop
    else: # if it is an integer,
        break # break the loop

main(num_sentences) # call the main function (parameter is number of sentences to get from Wikipedia)

input("\nPress Enter to continue.")