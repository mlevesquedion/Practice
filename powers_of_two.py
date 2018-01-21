import random
from practice import Practice

lowerBound = 0
upperBound = 20

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((x, ), str(2 ** x))

taskName = 'Puissances de 2'
instructions = 'Calculez mentalement la puissance de 2 demandée.'
trialPrompt = '2 ^ {} = '

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
