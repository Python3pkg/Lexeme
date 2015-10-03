import dataset
import random
import sys
import re
from tabulate import tabulate

from IOHelper import parseDic, parseList

db = dataset.connect('sqlite:///words.db')
phonemes = {}
allophones = {}
vowels = []
consonants = []

# Declension information
declensions = {}

# Transcribe from orthographic representation to phonetic representation
def transcribePhonemes(word):
        
        for current, new in phonemes.items():
                word = re.sub(current, new, word)

        word = "/" + word + "/"

        return word


def transcribeAllophones(word):
        word = word[1:-1]
        
        for current, new in allophones.items():
            word = re.sub(current, new, word)

        return word


def outputWord(word, t):
        meaning = word['english']
        conlang = word['word']
        phonetic = transcribePhonemes(conlang)
        allophonetic = transcribeAllophones(phonetic)
        form = word['form']

        if t == "english":
                print(tabulate([[meaning, conlang, form],
                                ["", phonetic, ""],
                                ["", allophonetic, ""]],
                               headers=['English', 'Conlang', 'Features']))

        elif t == "onlyconlang":
                print(tabulate([[conlang], [phonetic], [allophonetic]],
                      headers=["Conlang"]))

        else:
                print(tabulate([[conlang, meaning, form],
                                [phonetic, "",  ""],
                                [allophonetic, "", ""]],
                               headers=['Conlang', 'English', 'Features']))


def query():
        print("Word database contains " + str(len(db['words'])) + " words.")


def search():
        term = input("Enter search term: ")
        print("Results:")
        print("")
        result = db['words'].find(english=term)
        if result is not None:
                for word in result:
                        outputWord(word, "english")
                        print("")

        result = db['words'].find(word=term)
        if result is not None:
                for word in result:
                        outputWord(word, "onlyconlang")
                        print("")


def generateWord(meaning, form):
        word = ""

        for syllable in range(random.randint(2, 5)):
            word += random.choice(consonants) + random.choice(vowels)

        return {'english': meaning, 'word': word, 'form': form}


def generate(meaning=None):
        form = input("Enter word type (noun/verb/other): ")
        while form not in ["noun", "verb", "other"]:
                print("Not a valid type!")
                form = input("Enter word type (noun/verb/other): ")

        if meaning is None:
                meaning = input("Enter word meaning: ")

        result = db['words'].find_one(english=meaning)

        if result is not None:
                print("Word already exists!")
                outputWord(result, "english")
                return 0

        # generate and display words until acceptance
        accepted = "n"
        while accepted != "y":

                # generate words until there are no matches in database
                word = generateWord(meaning, form)
                while db['words'].find_one(word=word['word']) is not None:
                        word = generateWord(meaning, form)

                print(outputWord(word, "english"))
                accepted = input("Accept word? (y/n): ")

        db['words'].insert(dict(english=word['english'], word=word['word'], form=word['form']))

        print("Word saved in database!")


def quit():
        sys.exit(0)


def decline():
        conlang = input("Enter verb (in conlang) to conjugate: ")
        word = db['words'].find_one(word=conlang)
        
        if word is None:
                print("Word does not exist!")
                conlang = input("Enter verb (in conlang) to conjugate: ")
                word = db['words'].find_one(word=conlang)
        
        decmessage = "Available declensions: "
        
        for dec in declensions:
            decmessage = decmessage + dec + " "
        
        print(decmessage)

        d = input("Enter declension: ")
        while d not in declensions.keys():
                print("Invalid input. Ensure you are using the shortened code.")
                atense = input("Enter declension: ")

        dec = declensions[d].split("->")
        
        word['word'] = re.sub(dec[0], dec[1], word['word'])

        outputWord(word, "onlyconlang")


def list():
        t = input('Enter list type (all/form): ')
        outList = []

        if t == "all":
                for word in db['words']:
                        outList.append([word['english'], word['word'],  word['form']])
        elif t == "form":
                f = input("Enter desired form (verb/noun/other): ")
                if f == "noun":
                        for word in db.query('SELECT * FROM words WHERE form LIKE "noun"'):
                                outList.append([word['english'], word['word'], word['form']])
                elif f == "verb":
                        for word in db.query('SELECT * FROM words WHERE form LIKE "verb"'):
                                outList.append([word['english'], word['word'], word['form']])
                elif f == "other":
                        for word in db.query('SELECT * FROM words WHERE form LIKE "other"'):
                                outList.append([word['english'], word['word'], word['form']])

        print(tabulate(outList, headers=["English", "Conlang", "Form"]))

''' Takes three strings for meaning, word in conlang, and part of speech and
adds word to database '''
def addWord(meaning, word, form):
        db['words'].insert(dict(english=meaning, word=word, form=form))
        return 0

# Loads all language-specific information from file
def loadData():
    global phonemes
    phonemes = parseDic("phonemes.txt")
    
    global allophones
    allophones = parseDic("allophones.txt")

    global vowels
    vowels = parseList("vowels.txt")

    global consonants
    consonants = parseList("consonants.txt")

    global declensions
    declensions = parseDic("declensions.txt")

def main():
        commands = {"add": add,
                    "list": list,
                    "decline": decline,
                    "query": query,
                    "search": search,
                    "generate": generate,
                    "quit": quit}
        commandList = ""

        for key, value in commands.items():
                commandList = commandList + value.__name__ + ", "

        commandList = commandList[:-2] + "."
        print("Available commands: " + commandList)

        loadData()

        command = input("Please enter a command: ")
        while command != "quit":
                commands[command]()
                command = input("Please enter a command: ")

if __name__ == '__main__':
        main()
