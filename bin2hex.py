import random
from practice import Practice

lowerBound = 0
upperBound = 15

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((bin(x)[2:].zfill(4), ), hex(x)[2:])

taskName = 'Binaire à hexadécimal'
instructions = 'Convertissez mentalement le chiffre binaire en chiffre hexadécimal.'
trialPrompt = '{}'

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
