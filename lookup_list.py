import requests
import json
from requests.exceptions import HTTPError
import wikipedia
import re

def lookup(word, num_sentences):
    try: # try Google dictionarty first
        response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word) # get response from (unofficial) Google Dictionary API (as JSON)
        response.raise_for_status() # returns an HTTPError object if an error has occurred
        # access JSON content
        jsonResponse = response.json() if response and response.status_code == 200 else None
        definition = jsonResponse[0]["meanings"][0]["definitions"][0]["definition"] # this is how you get the first definition
        definition = definition[0].lower() + definition[1:]  # lowercase the first letter
        print("The definition of "+word+" is: "+definition)

    except HTTPError: # if there's an error (can't find the word on Google Dictionary)
        # print(f'   HTTP error occurred: {http_err}') # might need this for diagnosing HTTP errors
        print("   Definition not found on Google for '"+word+"'. Checking Wikipedia instead...")
        try:
            definition=wikipedia.summary(word, sentences=num_sentences, auto_suggest=True, redirect=True) # try to find the word on Wikipedia
            print("According to Wikipedia: "+definition)
        except Exception: # if a page isn't immedietly available (disambiguation, etc)
            try:
                print("   Couldn't find a Wikipedia article for '"+word+"'. Searching Wikipedia for relevant articles...")
                actual_article=wikipedia.search(word)[0] # suggest the result
                print("   Wikipedia returned '"+actual_article+"' as the best article. Getting summary of "+actual_article+"...")
                definition=wikipedia.summary(actual_article, sentences = num_sentences, auto_suggest=False, redirect=True) # get a summary of that article
            except Exception:
                definition="No definition found."
            print("According to Wikipedia: "+definition)

        if ' is ' in definition or ' was ' in definition or ' are ' in definition or ' were ' in definition: # if the Wikipedia definition contains one of these words
            print("   Attempting to isolate the definition...")
            definition = re.split(" is | was | are | were", definition, maxsplit=1)[1] # split the definition once and assign the second part to definition
            print("   New Wikipedia summary: "+definition)

    except Exception as err: # print extraneous errors
        print(f'   Other error occurred: {err}')

    if '==' in definition: # if the definition contains dividers
        print("   Detected new heading divider. Isolating preceding text...")
        definition = definition.split('==')[0] # split the definition once and assign the first part to definition
        print("Extracted: "+definition)

    print("   Cleaning up definition to remove excess characters and end periods...")
    definition = definition.strip() # strip any unnecessary start or end spaces
    definition = definition[:-1] # remove end period
    return definition # return the definition of the word

def main(num_sentences): # main method
    try: 
        print("Opening words file...")
        file=open('words.txt', encoding='utf8') # open the words file
    except Exception:
        print("File not found. Please ensure words.txt is in the root directory.")
        input("\nPress Enter to continue.")

    # words = [] # declare an empty words list # might not need this idk yet

    words=file.readlines() # append each line of text in the file to the words list
    file.close() # close the file

    words = [word.strip() for word in words] # strip each line to remove unessecary characters

    print("There are the terms I read:") # print the words list
    print(words)
    if num_sentences!=1:
        print("I will get definitions from Wikipedia with "+str(num_sentences)+" sentences.") # indicate the number of sentences getting from Wikipedia
    else:
        print("I will get definitions from Wikipedia with 1 sentence.") # indicate the number of sentences getting from Wikipedia
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

    definitions_file = open('wordsDefined.txt', 'w') # open the destination file for writing
    for i in range(len(words)): # for each element in the words list
        definitions_file.writelines(words[i]+" - "+definitions[i]+"\n") # write each 'word - definition' line
    print("\nSuccessfully wrote "+str(len(words))+" terms and definitions to wordsDefined.txt.")
    definitions_file.close() # close the file

while True:
    try:
        num_sentences = int(input("Enter number of sentences to get from Wikipedia: ")) # get number of sentences from user
    except Exception: # if it is not an integer, return to the start of the loop
        print("Number must be an integer.")
        continue
    else: # if it is an integer, break the loop
        break

main(num_sentences) # call the main function (parameter is number of sentences to get from Wikipedia)

input("\nPress Enter to continue.")