import requests
import json
import wikipedia
import re
import sys

if len(sys.argv) >= 2:
    if sys.argv[1] == "log":  # If log parameter is present, enable logging

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

    if 'v.' in word: # for court cases
       num_sentences+=1 # definitions often contain lots of periods which mistakenly cut it short, so get an extra "sentence"

    if len(word.split()) < 3:
        try: # only try Google dictionarty first for terms with fewer than 3 words
            response = requests.get("https://api.dictionaryapi.dev/api/v2/entries/en/"+word) # get response from (unofficial) Google Dictionary API (as JSON)
            response.raise_for_status()  # returns an HTTPError object if an error has occurred
            jsonResponse = response.json() if response and response.status_code == 200 else None # access JSON content
            definition = jsonResponse[0]["meanings"][0]["definitions"][0]["definition"] # get the first definition
            definition = definition[0].lower() + definition[1:] # lowercase the first letter
            print(f"The definition of {word} is: "+definition)
        except Exception as err: # if there's an error (can't find the word on Google Dictionary)
            # print(f"   An error occurred getting the definition from Google: {err}")
            print(f"   Definition not found on Google for '{word}'. Checking Wikipedia instead...")
            try:
                definition = wikipedia.summary(word, sentences=num_sentences, auto_suggest=True, redirect=True) # try to find the word on Wikipedia
                if len(definition.split()) < 8:  # if the definition contains fewer than 8 words
                    print(f"   The definition of {word} was too short, getting definiton with {str(num_sentences+1)} sentences instead.")
                    definition = wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence
            except Exception as err: # if a page isn't immedietly available (disambiguation, etc)
                # print(err)
                try:
                    print(f"   Couldn't find a Wikipedia article called '{word}'. Searching Wikipedia for relevant articles...")
                    word = wikipedia.search(word)[0]  # suggest the result
                    print(f"   Wikipedia returned '{word}' as the best article. Getting summary of '{word}'...")
                    definition = wikipedia.summary(word, sentences=num_sentences, auto_suggest=False, redirect=True) # get a summary of that article
                    if len(definition.split()) < 6:  # if the definition contains fewer than 8 words
                        print(f"   The definition of {word} was too short, getting definiton with {str(num_sentences+1)} sentences instead.")
                        definition = wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence
                except Exception as err:
                    # print(err)
                    definition = "No definition found."

            print("According to Wikipedia: "+definition)

            if ' is ' in definition or ' was ' in definition or ' are ' in definition or ' were ' in definition: # if the Wikipedia definition contains one of these words
                print("   Isolating the definition...")
                definition = re.split(" is | was | are | were", definition, maxsplit=1)[1] # split the definition once and assign the second part ([1]) to definition

    else:
        print("   Since this item has more than 2 words, I won't bother checking Google Dictionary for it.")
        try:
            definition = wikipedia.summary(word, sentences=num_sentences, auto_suggest=True, redirect=True) # try to find the word on Wikipedia
            if len(definition.split()) < 6:  # if the definition contains fewer than 8 words
                print(f"   The definition of {word} was too short, getting definiton with {str(num_sentences+1)} sentences instead.")
                definition = wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence
        except Exception as err: # if a page isn't immedietly available (disambiguation, etc)
            # print(err)
            try:
                print(f"   Couldn't find a Wikipedia article called '{word}'. Searching Wikipedia for relevant articles...")
                word = wikipedia.search(word)[0]  # suggest the result
                print(f"   Wikipedia returned '{word}' as the best article. Getting summary of '{word}'...")
                definition = wikipedia.summary(word, sentences=num_sentences, auto_suggest=False, redirect=True) # get a summary of that article
                if len(definition.split()) < 8:  # if the definition contains fewer than 8 words
                    print(f"   The definition of {word} was too short, getting definiton with {str(num_sentences+1)} sentences instead.")
                    definition = wikipedia.summary(word, sentences=num_sentences+1, auto_suggest=True, redirect=True) # get the definition with one extra sentence
            except Exception as err:
                # print(err)
                definition = "No definition found."

        print("According to Wikipedia: "+definition)

        if ' is ' in definition or ' was ' in definition or ' are ' in definition or ' were ' in definition: # if the Wikipedia definition contains one of these words
            print("   Isolating the definition...")
            definition = re.split(" is | was | are | were", definition, maxsplit=1)[1] # split the definition once and assign the second part ([1]) to definition

    if '==' in definition:  # if the definition contains dividers
        print("   Detected new heading divider. Isolating preceding text...")
        definition = definition.split('==')[0] # split the definition and assign the first part to definition
        print("Extracted: "+definition)

    print("   Cleaning up definition to remove excess characters, end periods, and line breaks...")
    definition = definition.strip()  # strip any unnecessary start or end spaces
    definition = definition.replace('\n', ' ')
    if definition.endswith('.'):  # if the last character is a period
        definition = definition[:-1]  # remove end period
    return definition  # return the definition of the word

def main():  # main method

    try:
        file = open('words.txt', encoding='utf8')  # open the words file
    except: # if you can't open it (meaning it probably doesn't exist)...
        print("Creating words.txt file...")
        file = open('words.txt', 'w', encoding='utf8')  # create the words file
        file.write("Paste words or phrases here, one term per line.\nMake sure to save changes to this file (Ctrl+S)."
                   + "\nPlease delete this message before proceeding.")
        input("Please enter your words into the words.txt file and run the program again. Press Enter to continue.")
    else: # if you can open it
        print("Opening words file...")

    words = [line for line in file.readlines() if line.strip()] # append each non-empty line of text in the file to the words list
    file.close()

    words = [word.strip() for word in words] # strip each line to remove unessecary characters

    print("\nThere are the terms I read:") # print the words list
    print(words)

    print() # add a blank line to the console

    while True:
        try:
            print("Enter number of sentences to get from Wikipedia definitions:", end=" ")
            num_sentences = int(input())  # get number of sentences from user
        except Exception: # if it is not an integer,
            print("Number must be an integer.", end=" ") # inform the user and...
            continue # return to the start of the loop
        else: # if it is an integer,
            break # break the loop

    # indicate the number of sentences getting from Wikipedia
    if num_sentences != 1:
        print(f"\nI will get definitions from Wikipedia that are {str(num_sentences)} sentences long.\n") 
    else:
        print("\nI will get definitions from Wikipedia that are 1 sentence long.\n")

    definitions = []  # declare an empty definitions list

    for word in words:
        print(f"Getting definition of '{word}' to add to dictionary...")
        definitions.append(lookup(word, num_sentences)) # look up each word (with num_sentences sentences), append it to the dictionary list

    errors = []  # declare an empty list of errors

    for i in range(len(definitions)):  # for each definition in the list
        if definitions[i] == "No definition found":  # find each term without a definition
            errors.append(words[i]) # add each term without a definition to the list

    successful_words = len(words)-len(errors) # calculate the number of successfully defined terms

    definitions_file = open('words_defined.txt', 'w', encoding='utf8')  # open the destination file for writing
    for i in range(len(words)):  # for each element in the words list
        definitions_file.writelines(words[i]+" - "+definitions[i]+"\n") # write each 'word - definition' line
    print(f"\nSuccessfully wrote {str(successful_words)} out of {str(len(words))} terms and definitions to wordsDefined.txt.")
    if len(errors) == 1:  # if there were errors, print them
        print("There was 1 term I could not define: '"+str(errors[0])+"'")
    elif len(errors) > 0:
        print(f"There were {str(len(errors))} terms I could not define: "+str(errors))

    definitions_file.close()

main()
input("\nPress Enter to continue.")