import random
from practice import Practice

lowerBound = 0
upperBound = 15

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((hex(x)[2:], ), bin(x)[2:].zfill(4))

taskName = 'Héxadécimal à Binaire'
instructions = 'Convertissez mentalement le chiffre hexadécimal en chiffre binaire.'
trialPrompt = '{}'

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
