import random
from practice import Practice

lowerBound = 10
upperBound = 15

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((x, ), hex(x)[2:])

taskName = 'Décimal Hexadécimal'
instructions = 'Convertissez mentalement le chiffre décimal en chiffre hexadécimal.'
trialPrompt = '{} en hexadécimal ='

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
