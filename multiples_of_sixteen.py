import random
from practice import Practice

lowerBound = 0
upperBound = 16

def trialDataGenerator():
    while True:
        x = random.randint(lowerBound, upperBound)
        yield((x,), str(x * 16))

taskName = 'Multiples de 16'
instructions = 'Effectuez mentalement la multiplication par 16.\nPetit truc : 5 x 16 = 80'
trialPrompt = '{} * 16 = '

Practice(taskName, trialDataGenerator, instructions, trialPrompt)()
