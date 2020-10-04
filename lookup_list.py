import requests
import json
import wikipedia
import re
import os

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
            print("According to Wikipedia: "+definition)
        except Exception: # if a page isn't immedietly available (disambiguation, etc)
            try:
                print("   Couldn't find a Wikipedia article called '"+word+"'. Searching Wikipedia for relevant articles...")
                actual_article=wikipedia.search(word)[0] # suggest the result
                print("   Wikipedia returned '"+actual_article+"' as the best article. Getting summary of '"+actual_article+"'...")
                definition=wikipedia.summary(actual_article, sentences = num_sentences, auto_suggest=False, redirect=True) # get a summary of that article
            except Exception:
                definition="No definition found."
            print("According to Wikipedia: "+definition)

        if ' is ' in definition or ' was ' in definition or ' are ' in definition or ' were ' in definition: # if the Wikipedia definition contains one of these words
            print("   Isolating the definition...")
            definition = re.split(" is | was | are | were", definition, maxsplit=1)[1] # split the definition once and assign the second part ([1]) to definition

    if '==' in definition: # if the definition contains dividers
        print("   Detected new heading divider. Isolating preceding text...")
        definition = definition.split('==')[0] # split the definition once and assign the first part to definition
        print("Extracted: "+definition)

    print("   Cleaning up definition to remove excess characters, end periods, and line breaks...")
    definition = definition.strip() # strip any unnecessary start or end spaces
    definition = definition.replace('\n', ' ')
    definition = definition[:-1] # remove end period
    return definition # return the definition of the word

def main(num_sentences): # main method
    try: 
        print("Opening words file...")
        file=open('words.txt', encoding='utf8') # open the words file
    except Exception as err:
        print(err) # print errors
        print("File not found. Please ensure words.txt is in the root directory.")
        print("Currently working in "+str(os.getcwd())) # print info about local directory and files to help diagnose missing words.txt
        print("Only files in this directory are: "+str(os.listdir()))
        input("\nPress Enter to continue.")

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
    print("\nSuccessfully wrote "+str(successful_words)+" terms and definitions to wordsDefined.txt.")
    if len(errors) == 1: # if there were errors, print them
        print("There was 1 term I could not define: '"+str(errors[0])+"'")
    elif len(errors) > 0:
        print("There were "+str(len(errors))+" terms I could not define: "+str(errors))

    definitions_file.close() # close the file


while True:
    try:
        num_sentences = int(input("Enter number of sentences to get from Wikipedia: ")) # get number of sentences from user
    except Exception: # if it is not an integer,
        print("Number must be an integer.") # inform the user and..
        continue # return to the start of the loop
    else: # if it is an integer,
        break # break the loop

main(num_sentences) # call the main function (parameter is number of sentences to get from Wikipedia)

input("\nPress Enter to continue.")