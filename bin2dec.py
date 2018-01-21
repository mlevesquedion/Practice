import random
from practice import Practice

lowerBound = 0
upperBound = 15

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((bin(x)[2:].zfill(len(bin(upperBound)) - 2),), str(x))

taskName = 'Binaire à Décimal'
instructions = 'Convertissez mentalement le chiffre binaire en chiffre décimal.'
trialPrompt = '{} en base 10 = '

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
