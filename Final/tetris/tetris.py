import pygame
import random
import math
import copy
from pygame.locals import *
from timeit import default_timer as timer

I = [['0000', '1111', '0000', '0000'], ['0100', '0100', '0100', '0100'],
     ['0000', '0000', '1111', '0000'], ['0010', '0010', '0010', '0010']]
L = [['002', '222', '000'], ['020', '020', '022'],
     ['000', '222', '200'], ['220', '020', '020']]
J = [['300', '333', '000'], ['033', '030', '030'],
     ['000', '333', '003'], ['030', '030', '330']]
O = [['044', '044', '000'], ['044', '044', '000'],
     ['044', '044', '000'], ['044', '044', '000']]
S = [['055', '550', '000'], ['050', '055', '005'],
     ['000', '055', '550'], ['500', '550', '050']]
Z = [['660', '066', '000'], ['006', '066', '060'],
     ['000', '660', '066'], ['060', '660', '600']]
T = [['070', '777', '000'], ['070', '077', '070'],
     ['000', '777', '070'], ['070', '770', '070']]


class blocks():
    length = 20

    def __init__(self, shape):
        global leftup, width
        self.piece = {'shape': shape, 'x': width/2-2 *
                      self.length, 'y': leftup[1]-2*self.length, 'r': 0}
        self.draw(1)
        return

    def draw(self, x, y=0):
        color = [(0, 255, 255), (255, 153, 0), (0, 0, 255),
                 (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255)]
        s, t = self.piece['x']+2, self.piece['y']+2
        for col in self.piece['shape'][self.piece['r']]:
            for i in col:
                if int(i) and t >= 200:
                    if x:
                        if y:
                            rec = pygame.draw.rect(background, color[int(
                                i)-1], (s, t, self.length-4, self.length-4))
                            rec = pygame.draw.rect(
                                background, (0, 0, 0), (s+2, t+2, self.length-8, self.length-8))
                        else:
                            rec = pygame.draw.rect(background, color[int(
                                i)-1], (s, t, self.length-5, self.length-5))
                    else:
                        rec = pygame.draw.rect(
                            background, (0, 0, 0), (s, t, self.length-3, self.length-3))
                s += self.length
            s = self.piece['x']+2
            t += self.length
        return

    def freefall(self):
        self.draw(0)
        self.piece['y'] += self.length
        if not self.isvalid():
            self.piece['y'] -= self.length
            self.draw(1)
            return False
        return True

    def move(self, key):
        if key == pygame.K_DOWN:
            self.draw(0)
            self.piece['y'] += self.length
            if self.isvalid():
                pygame.time.delay(100)
            else:
                self.piece['y'] -= self.length
                self.draw(1)
                return False

        elif key == pygame.K_LEFT:
            self.draw(0)
            self.piece['x'] -= self.length
            if self.isvalid():
                pygame.time.delay(100)
            else:
                self.piece['x'] += self.length

        elif key == pygame.K_RIGHT:
            self.draw(0)
            self.piece['x'] += self.length
            if self.isvalid():
                pygame.time.delay(100)
            else:
                self.piece['x'] -= self.length

        elif key == pygame.K_UP:
            self.draw(0)
            if self.can_rotate():
                pygame.time.delay(10)

        elif key == pygame.K_SPACE:
            self.draw(0)
            while self.isvalid():
                self.piece['y'] += self.length
            self.piece['y'] -= self.length
            self.draw(1)
            return False

        return True

    def isvalid(self):
        global back_d
        x = self.piece['x']
        y = self.piece['y']
        t = self.piece['r']
        for i in range(len(self.piece['shape'][t])):
            for j in range(len(self.piece['shape'][t])):
                if back_d[(int(x+self.length*j), int(y+self.length*i))] and int(self.piece['shape'][t][i][j]):
                    return False
        return True

    def can_rotate(self):
        r = self.piece['r']
        x = self.piece['x']
        y = self.piece['y']
        self.piece['r'] = (self.piece['r']+1) % 4
        l = len(self.piece['shape'][self.piece['r']])
        for t in range(2):
            if any(back_d[(self.piece['x'], self.piece['y']+j*self.length)] and int(self.piece['shape'][self.piece['r']][j][0]) for j in range(l)):
                self.piece['x'] += self.length
            if any(back_d[(self.piece['x']+(l-1)*self.length, self.piece['y']+j*self.length)] and int(self.piece['shape'][self.piece['r']][j][l-1]) for j in range(l)):
                self.piece['x'] -= self.length
            if any(back_d[(self.piece['x']+i*self.length, self.piece['y']+(l-1)*self.length)] and int(self.piece['shape'][self.piece['r']][l-1][i]) for i in range(l)):
                self.piece['y'] -= self.length
        if self.isvalid():
            return True
        self.piece['x'] = x
        self.piece['y'] = y
        self.piece['r'] = r
        return False

    def touchdown(self, shape):
        global back_d
        x = self.piece['x']
        y = self.piece['y']
        for i in range(len(self.piece['shape'][self.piece['r']])):
            for j in range(len(self.piece['shape'][self.piece['r']])):
                back_d[(int(x+self.length*j), int(y+self.length*i))
                       ] += int(self.piece['shape'][self.piece['r']][i][j])
        return blocks(shape)

    def shadow(self):
        while self.isvalid():
            self.piece['y'] += self.length
        self.piece['y'] -= self.length
        self.draw(1, 1)
        return


class blockly():
    def __init__(self, player=0):  # player 0 = self, 1 = others
        self.block = [I, L, J, O, S, Z, T]
        random.shuffle(self.block)
        self.count = 0
        self.cur = self.block[self.count]
        self.next = self.block[self.count]
        self.hold = False
        if player == 0:
            self.inil = 500
            self.init = 200
        else:
            self.inil = 1100
            self.init = 200

    def new(self):
        t = self.next
        self.cur = self.next
        self.count = (self.count+1) % 7
        if not self.count:
            random.shuffle(self.block)
        self.next = self.block[self.count]
        self.draw()
        return t

    def shift(self):
        if not self.hold:
            self.hold = self.cur
            self.cur = self.next
            self.count = (self.count+1) % 7
            if not self.count:
                random.shuffle(self.block)
            self.next = self.block[self.count]
            self.draw()
            return self.cur
        self.hold, self.cur = self.cur, self.hold
        return self.cur

    def draw(self):
        pygame.draw.rect(background, (0, 0, 0),
                         (self.inil+20+5, self.init+10, 90, 90))
        s, t = self.inil+30, self.init+15
        color = [(0, 255, 255), (255, 153, 0), (0, 0, 255),
                 (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255)]
        for col in self.next[0]:
            for i in col:
                if int(i):
                    rec = pygame.draw.rect(
                        background, color[int(i)-1], (s, t, 20-5, 20-5))
                s += 20
            s = self.inil+30
            t += 20
        return


class Point():
    def __init__(self):
        self.point = 0
        self.combo = 0

    def score(self, flag):
        if flag == 0:
            self.combo = 0
            return self.point, self.combo

        if self.combo >= 1:
            self.point += math.ceil(self.combo/2)
            # print('ceil.',math.ceil(self.combo/2))
            if flag >= 2:
                self.point += 2**(flag-2)
            self.combo += 1
        if self.combo == 0:
            if flag == 1:
                self.combo += 1
            if flag >= 2:
                self.point += 2**(flag-2)
                self.combo += 1
        return self.point, self.combo


def text_objects(text, font):
    textSurface = font.render(text, True, (255, 255, 255))
    return textSurface, textSurface.get_rect()


def score(s, c, ll, tt):
    pygame.draw.rect(background, (0, 0, 0), (ll-100, tt+200, 90, 100))
    pygame.draw.rect(background, (0, 0, 0), (ll-250, tt+260, 240, 100))

    smallText = pygame.font.SysFont('comicsansms', 20)

    textSurf1, textRect1 = text_objects('Score : ', smallText)
    textRect1.center = (ll-150, tt+250)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects(s, smallText)
    textRect2.center = (ll-50, tt+250)
    background.blit(textSurf2, textRect2)
    if int(c) >= 2:
        textSurf3, textRect3 = text_objects('Combo : ', smallText)
        textRect3.center = (ll-50, tt+300)
        background.blit(textSurf3, textRect3)
        textSurf4, textRect4 = text_objects(c, smallText)
        textRect4.center = (ll+50, tt+300)
        background.blit(textSurf4, textRect4)
    pygame.display.update()


def draw_boundary(ll, tt):
    color = 100, 255, 200
    pygame.draw.rect(background, color, (ll-5, tt-5, 200+10, 400+10))
    pygame.draw.rect(background, (0, 0, 0), (ll, tt, 200, 400))
    for i in range(ll-1, ll+200, 20):
        pygame.draw.line(background, (100, 100, 100), (i, tt), (i, tt+400), 1)
    for i in range(tt-1, 600, 20):
        pygame.draw.line(background, (100, 100, 100), (ll, i), (ll+200, i), 1)

    pygame.draw.rect(background, color, (ll-120, tt+5, 100, 100))
    pygame.draw.rect(background, (0, 0, 0), (ll-120+5, tt+10, 90, 90))
    for i in range(3):
        pygame.draw.rect(background, color, (ll+200+20, tt+5+i*120, 100, 100))
        pygame.draw.rect(background, (0, 0, 0),
                         (ll+200+20+5, tt+10+i*120, 90, 90))

    smallText = pygame.font.SysFont('comicsansms', 30)
    textSurf1, textRect1 = text_objects('Hold', smallText)
    textRect1.center = (ll-70, tt-20)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Next', smallText)
    textRect2.center = (ll+270, 180)
    background.blit(textSurf2, textRect2)
    textSurf3, textRect3 = text_objects('?', smallText)
    textRect3.center = (ll+270, 370)
    background.blit(textSurf3, textRect3)
    textSurf4, textRect4 = text_objects('?', smallText)
    textRect4.center = (ll+270, 490)
    background.blit(textSurf4, textRect4)
    score('0', '0', ll, tt)
    pygame.display.update()


def start():
    BTStart = (340, 320, 120, 60)
    BTQuit = (340, 500, 120, 60)
    pygame.draw.rect(background, (0, 150, 0), BTStart)
    pygame.draw.rect(background, (200, 0, 0), BTQuit)

    smallText = pygame.font.SysFont('comicsansms', 30)
    smallText_t = pygame.font.SysFont('comicsansms', 100)
    textSurf_t, textRect_t = text_objects('Tetris', smallText_t)
    textRect_t.center = (400, 150)
    background.blit(textSurf_t, textRect_t)

    textSurf1, textRect1 = text_objects('Start', smallText)
    textRect1.center = (400, 350)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Quit', smallText)
    textRect2.center = (400, 530)
    background.blit(textSurf2, textRect2)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 340+120 > mouse[0] > 340 and 320 + 60 > mouse[1] > 320:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return
                if 340 + 120 > mouse[0] > 340 and 500 + 60 > mouse[1] > 500:
                    pygame.quit()


def clear():
    global back_d
    flag = 0
    for j in range(200, 600, 20):
        if all(back_d[(i, j)] for i in range(300, 500, 20)):
            flag += 1
            for t in range(j, 180, -20):
                for s in range(300, 500, 20):
                    back_d[(s, t)] = back_d[(s, t-20)]
    if flag:
        color = [(0, 255, 255), (255, 153, 0), (0, 0, 255),
                 (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255)]
        for i in range(300, 500, 20):
            for j in range(200, 600, 20):
                pygame.draw.rect(background, (0, 0, 0), (i+2, j+2, 15, 15))
                if back_d[(i, j)]:
                    pygame.draw.rect(
                        background, color[back_d[(i, j)]-1], (i+2, j+2, 15, 15))
    return flag


def game_loop(level, ll=200, tt=200):
    start = timer()
    crashed = False
    blist = blockly(0)  # player 0
    a = blocks(blist.new())
    shift = 0
    point = Point()
    while not crashed:
        a1 = copy.deepcopy(a)
        a1.shadow()
        # lose
        for i in range(ll, ll+200, 20):
            if back_d[(i, ll-20)]:
                crashed = True
        # get key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == KEYDOWN:
                # if event.key == K_p:
                #     pygame.time.delay(10000) // no need
                a1.draw(0)
                if not a.move(event.key):
                    a1.draw(0)
                    a.draw(1)
                    a = a.touchdown(blist.new())
                    shift = 0
                    # flag = clear()
                    # s, c = point.score(flag)
    #                 sc(str(s), str(c))
    #             if event.key == K_LSHIFT and not shift:
    #                 a.draw(0)
    #                 pygame.draw.rect(background, (0, 0, 0),
    #                                  (300-120+5, 200+10, 90, 90))
    #                 a.piece['x'], a.piece['y'] = 190, 215
    #                 a.draw(1)
    #                 a = blocks(blist.shift())
    #                 shift = 1
    #             a1 = copy.deepcopy(a)
    #             a1.shadow()

    #     # freefall
    #     if timer()-start > level:
    #         if not a.freefall():
    #             a1.draw(0)
    #             a.draw(1)
    #             a = a.touchdown(blist.new())
    #             shift = 0
    #             flag = clear()
    #             s, c = point.score(flag)
    #             sc(str(s), str(c))
    #         start = timer()

    #     a.draw(1)
    #     pygame.display.update()
    #     clock.tick(60)
    # return s


while True:
    file = open('Tetris_Record.txt', 'a+')
    pygame.init()
    width, height = 1200, 650
    background = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()

    gamewidth, gameheight = 300, 600
    leftup = (300, 200)

    back_d = {}
    for i in range(0, 800, 20):
        for j in range(0, 800, 20):
            back_d[(i, j)] = 1
    for i in range(300, 500, 20):
        for j in range(160, 600, 20):
            back_d[(i, j)] = 0
    start()
    l = (1.0, 'easy')
    draw_boundary(200, 200)
    draw_boundary(800, 200)
    score = game_loop(l[0])
    while True:
        pass
