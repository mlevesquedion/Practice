import os
import pygame
import shelve
import sys
from copy import copy
from pygame.locals import *
import time as TIME
from tkinter import Tk

pygame.init()
pygame.mouse.set_visible(False)

dimensions_window = Tk()
SCREENWIDTH = dimensions_window.winfo_screenwidth()
SCREENHEIGHT = dimensions_window.winfo_screenheight()
dimensions_window.destroy()

HALFSCREENWIDTH = SCREENWIDTH // 2
HALFSCREENHEIGHT = SCREENHEIGHT // 2
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.FULLSCREEN)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (200, 40, 40)
GREEN = (40, 200, 40)

taskTime = 60
maxHighScores = 5

def flash_screen(color, waitTime=50):
    SCREEN.fill(color)
    pygame.display.update()
    pygame.time.delay(waitTime)

def calculate_maxWidth_and_totalHeight(surfaceRects, padding):
    maxWidth = max(surface.get_width() for surface, _ in surfaceRects)
    totalHeight = sum(surface.get_height() for surface, _ in surfaceRects)
    maxWidth += 2 * padding
    totalHeight += 2 * padding
    return maxWidth, totalHeight

def make_surfaceRects(font, fontSize, textLines, header=None):
    textSurfaceRects = []
    if header is not None:
        headerFont = pygame.font.SysFont(font, fontSize, True)
        headerSurface = headerFont.render(header, True, BLACK, WHITE)
        headerRect = headerSurface.get_rect()
        textSurfaceRects.append((headerSurface, headerRect))
        textLines = [''] + textLines
    normalFont = pygame.font.SysFont(font, fontSize)
    for line in textLines:
        lineSurface = normalFont.render(line, True, BLACK, WHITE)
        lineRect = lineSurface.get_rect()
        textSurfaceRects.append((lineSurface, lineRect))
    return textSurfaceRects

def display_multiline_text(text=None, header=None, *, font='calibri', fontSize=50, horizontalAlignment='CENTER', verticalAlignment='CENTER', exitKey=None, waitTime=None):
    """Displays multiple lines of text to the SCREEN at once. Text is simply a string with 0 or more lines."""

    if text is None:
        return

    if exitKey is None and waitTime is None:
        exitKey = 'SPACE'

    if exitKey is not None:
        # Add a line to explain what key to press to exit
        keyInText = {'ESCAPE': 'touche "Échap"',
                     'SPACE': 'barre d\'espacement',
                     'ENTER': 'touche "Enter"'}[exitKey]
        keyText = 'Appuyez sur la {} pour continuer.'.format(keyInText)
        text += '\n\n' + keyText

        exitKey = {'SPACE': K_SPACE,
                   'ESCAPE': K_ESCAPE,
                   'ENTER': K_RETURN}[exitKey]

    minimumPadding = fontSize // 2
    textLines = text.splitlines()
    textSurfaceRects = make_surfaceRects(font, fontSize, textLines, header)

    # Adjust text size if it is too big
    maxWidth, totalHeight = calculate_maxWidth_and_totalHeight(textSurfaceRects, minimumPadding)
    while maxWidth > SCREENWIDTH or totalHeight > SCREENHEIGHT:
        fontSize -= 1
        textSurfaceRects = make_surfaceRects(font, fontSize, textLines, header)
        maxWidth, totalHeight = calculate_maxWidth_and_totalHeight(textSurfaceRects, minimumPadding)

    yPos = {verticalAlignment == 'CENTER': (SCREENHEIGHT - totalHeight) // 2 + minimumPadding,
              verticalAlignment == 'TOP': minimumPadding,
              verticalAlignment == 'BOTTOM': SCREENHEIGHT - totalHeight - minimumPadding}[True]

    for surface, rect in textSurfaceRects:
        width, height = surface.get_width(), surface.get_height()
        xPos = {horizontalAlignment == 'CENTER': (SCREENWIDTH - width) // 2,
                horizontalAlignment == 'LEFT': minimumPadding,
                horizontalAlignment == 'RIGHT': SCREENWIDTH - width - minimumPadding}[True]
        rect.topleft = (xPos, yPos)
        yPos += height

    if waitTime:
        pygame.time.set_timer(QUIT, waitTime)

    Quit = False
    while not Quit:

        SCREEN.fill(WHITE)
        for surface, rect in textSurfaceRects:
            SCREEN.blit(surface, rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT:
                Quit = True
            if event.type == KEYDOWN:
                if event.key == exitKey:
                    Quit = True

    if waitTime:
        pygame.time.set_timer(QUIT, 0)

class HighScoreTable:

    def __init__(self):
        self.scoreDates = []
        self.maxSize = maxHighScores

    def update(self, newScore):
        timestamp = TIME.strftime('%Y/%m/%d %H:%M')
        self.scoreDates.append((newScore, timestamp))
        self.scoreDates.sort(key = lambda x: x[0], reverse = True)
        if len(self.scoreDates) > self.maxSize:
            self.scoreDates.pop()
        if newScore in [score for score, date in self.scoreDates]:
            return True

    def show(self):
        print('MEILLEURS SCORES :')
        for (score, date) in self.scoreDates:
            print('Score : {}, Date : {}'.format(score, date))

class Trial:

    def __init__(self, prompt, correctAnswer, font):
        self.prompt = prompt
        self.correct = correctAnswer
        self.font = font

    def __call__(self):
        questionStartTime = TIME.time()
        answer = self.display_prompt_get_answer()
        questionEndTime = TIME.time()
        answerTime = questionEndTime - questionStartTime
        points = {0 < answerTime <= 1: 3,
                  1 < answerTime <= 5: 1,
                  5 < answerTime: 0}[True]

        showTime = 2000
        if answer.lower() == self.correct:
            flash_screen(GREEN)
            validity = 'juste'
            feedback = ''
        else:
            flash_screen(RED)
            validity = 'raté'
            feedback = 'La réponse était {}.\n\n'.format(self.correct)
            showTime += 1000
            points = 0

        summary = 'C\'est {} !'.format(validity)
        plural = '' if points == 1 else 's'
        feedback +=  'Vous avez répondu en {:.2f} s et gagné {} point{}.'.format(answerTime, points, plural)
        # Feedback is turned off to allow more practice cycles
        # display_multiline_text(feedback, summary, waitTime=showTime)

        return points

    def display_prompt_get_answer(self):
        offset = 40
        answerLineSize = 2
        answerLineOffset = 27
        answerLineWidth = 100

        promptSurface = self.font.render(self.prompt, True, BLACK, WHITE)
        promptRect = promptSurface.get_rect()
        promptRect.center = (HALFSCREENWIDTH, HALFSCREENHEIGHT - offset)

        answerLineStart = [HALFSCREENWIDTH - answerLineWidth // 2, HALFSCREENHEIGHT + offset + answerLineOffset]
        answerLineEnd = [HALFSCREENWIDTH + answerLineWidth // 2, HALFSCREENHEIGHT + offset + answerLineOffset]

        answerText = ''
        while True:
            SCREEN.fill(WHITE)
            SCREEN.blit(promptSurface, promptRect)

            answerSurface = self.font.render(answerText, True, BLACK, WHITE)
            answerRect = answerSurface.get_rect()
            answerRect.center = (HALFSCREENWIDTH, HALFSCREENHEIGHT + offset)

            pygame.draw.line(SCREEN, BLACK, answerLineStart, answerLineEnd, answerLineSize)

            SCREEN.blit(answerSurface, answerRect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        return answerText
                    elif event.key == K_BACKSPACE:
                        answerText = answerText[:-1]
                    else:
                        answerText += event.unicode

class Practice:

    def __init__(self, taskName, trialDataGenerator, instructions, trialPrompt):
        self.taskName = taskName
        self.trialDataGenerator = trialDataGenerator
        self.instructions = instructions
        self.trialPrompt = trialPrompt
        self.font = pygame.font.SysFont('calibri', 50)
        self.shelf = shelve.open('Pratique_' + taskName)
        try:
            self.highScoreTable = self.shelf['table']
        except (KeyError, EOFError):
            self.highScoreTable = HighScoreTable()

        self.points = 0
        self.trials = 0

    def __call__(self):
        self.display_welcome()

        startTime = TIME.time()
        for trialData, correctAnswer in self.trialDataGenerator():
            self.trials += 1

            prompt = self.trialPrompt.format(*trialData)
            trialPoints = Trial(prompt, correctAnswer, self.font)()
            self.points += trialPoints

            currentTime = TIME.time()
            if (currentTime - startTime) > taskTime:
                break

        self.display_recap()
        self.display_highscores()
        if self.ask_play_again():
            self()
        else:
            display_multiline_text('Au revoir !', waitTime = 500)
            self.shelf.close()
            pygame.quit()
            sys.exit()

    def display_welcome(self):
        greeting = 'Bienvenue dans la pratique "{}" !'.format(self.taskName)
        timePlural = '' if taskTime == 1 else 's'
        timeText = 'Vous avez {} seconde{} pour faire autant d\'essais que possible.'.format(taskTime, timePlural)
        taskInformation = '\n'.join([self.instructions, timeText])
        display_multiline_text(taskInformation, greeting, exitKey='ENTER')

    def display_recap(self):
        endMessage = 'La pratique est terminée !'
        trialPlural = '' if self.trials == 1 else 's'
        pointPlural = '' if self.points == 1 else 's'
        recapText = 'Votre score total sur {} essai{} est de {} point{}.'.format(self.trials, trialPlural, self.points, pointPlural)
        if self.highScoreTable.update(self.points):
            recapText += '\nVous avez fait un nouveau record !'
            self.shelf['table'] = self.highScoreTable
        display_multiline_text(recapText, endMessage)

    def display_highscores(self):
        highScoreStrings = ['Score : {}, Date: {}'.format(score, date)
                            for score, date in self.highScoreTable.scoreDates]
        highScoreText = '\n'.join(highScoreStrings)
        display_multiline_text(highScoreText, 'MEILLEURS SCORES')

    def ask_play_again(self):

        pygame.mouse.set_visible(True)

        offset = 50
        buttonDistance = offset * 2
        buttonBorderSize = 1
        fontOffset = -3

        questionText = 'Voulez-vous réessayer ?'
        questionSurface = self.font.render(questionText, True, BLACK, WHITE)
        questionRect = questionSurface.get_rect()
        questionRect.center = (HALFSCREENWIDTH, HALFSCREENHEIGHT - offset)

        yesButtonSurface = self.font.render('OUI', True, BLACK)
        yesButtonRect = yesButtonSurface.get_rect()
        yesButtonRect.center = (HALFSCREENWIDTH - buttonDistance, HALFSCREENHEIGHT + offset)
        yesButtonOutlineRect = copy(yesButtonRect)
        yesButtonOutlineRect.top += fontOffset

        noButtonSurface = self.font.render('NON', True, BLACK)
        noButtonRect = noButtonSurface.get_rect()
        noButtonRect.center = (HALFSCREENWIDTH + buttonDistance, HALFSCREENHEIGHT + offset)
        noButtonOutlineRect = copy(noButtonRect)
        noButtonOutlineRect.top += fontOffset

        while True:
            SCREEN.fill(WHITE)

            mouseX, mouseY = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    if yesButtonRect.collidepoint(mouseX, mouseY):
                        self.trials = 0
                        self.points = 0
                        pygame.mouse.set_visible(False)
                        return True
                    if noButtonRect.collidepoint(mouseX, mouseY):
                        return False

            if yesButtonRect.collidepoint(mouseX, mouseY):
                pygame.draw.rect(SCREEN, GRAY, yesButtonOutlineRect)
            if noButtonRect.collidepoint(mouseX, mouseY):
                pygame.draw.rect(SCREEN, GRAY, noButtonOutlineRect)

            pygame.draw.rect(SCREEN, BLACK, yesButtonOutlineRect, buttonBorderSize)
            pygame.draw.rect(SCREEN, BLACK, noButtonOutlineRect, buttonBorderSize)

            SCREEN.blit(questionSurface, questionRect)
            SCREEN.blit(yesButtonSurface, yesButtonRect)
            SCREEN.blit(noButtonSurface, noButtonRect)

            pygame.display.update()

        pygame.mouse.set_visible(False)

if __name__ == '__main__':
    pygame.quit()
    sys.exit()
