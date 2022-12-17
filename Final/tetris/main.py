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


class blockly():
    def __init__(self):
        self.block = [I, L, J, O, S, Z, T]
        random.shuffle(self.block)
        self.count = 0
        self.cur = self.block[self.count]
        self.next = self.block[self.count]
        self.hold = False

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
        pygame.draw.rect(background, (0, 0, 0), (500+20+5, 200+10, 90, 90))
        s, t = 530, 215
        color = [(0, 255, 255), (255, 153, 0), (0, 0, 255),
                 (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255)]
        for col in self.next[0]:
            for i in col:
                if int(i):
                    rec = pygame.draw.rect(
                        background, color[int(i)-1], (s, t, 20-5, 20-5))
                s += 20
            s = 530
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
        # print('point,',self.point)
        # print('combo,',self.combo)
        return self.point, self.combo


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


def start():
    pygame.draw.rect(background, (0, 150, 0), (340, 370, 120, 60))
    pygame.draw.rect(background, (200, 0, 0), (340, 570, 120, 60))

    smallText = pygame.font.SysFont('comicsansms', 30)
    smallText_t = pygame.font.SysFont('comicsansms', 100)
    textSurf_t, textRect_t = text_objects('Tetris', smallText_t)
    textRect_t.center = (400, 150)
    background.blit(textSurf_t, textRect_t)

    textSurf1, textRect1 = text_objects('Start', smallText)
    textRect1.center = (400, 400)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Quit', smallText)
    textRect2.center = (400, 600)
    background.blit(textSurf2, textRect2)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 340+120 > mouse[0] > 340 and 370 + 60 > mouse[1] > 370:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return
                if 340 + 120 > mouse[0] > 340 and 570 + 60 > mouse[1] > 570:
                    pygame.quit()


def text_objects(text, font):
    textSurface = font.render(text, True, (255, 255, 255))
    return textSurface, textSurface.get_rect()


def final():
    alphabet = {K_a: 'a', K_b: 'b', K_c: 'c', K_d: 'd', K_e: 'e', K_f: 'f', K_g: 'g', K_h: 'h', K_i: 'i', K_j: 'j', K_k: 'k', K_l: 'l', K_m: 'm', K_n: 'n', K_o: 'o',
                K_p: 'p', K_q: 'q', K_r: 'r', K_s: 's', K_t: 't', K_u: 'u', K_v: 'v', K_w: 'w', K_x: 'x', K_y: 'y', K_z: 'z', K_0: '0', K_1: '1', K_2: '2', K_3: '3',
                K_4: '4', K_5: '5', K_6: '6', K_7: '7', K_8: '8', K_9: '9', K_0: '0', K_SPACE: ' '}
    pygame.draw.rect(background, (0, 0, 0), (300, 250, 200, 200))
    smallText = pygame.font.SysFont('comicsansms', 30)
    smallText2 = pygame.font.SysFont('comicsansms', 30)
    textSurf2, textRect2 = text_objects('Your Name : ', smallText2)
    textRect2.center = (400, 280)
    background.blit(textSurf2, textRect2)
    pygame.display.update()
    name = []
    count = -1
    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if count <= 9:
                    if event.key in alphabet:
                        count += 1
                        name.append(alphabet[event.key])
                        textSurf, textRect = text_objects(
                            alphabet[event.key], smallText)
                        textRect.center = (320+count*17, 340)
                        background.blit(textSurf, textRect)
                        pygame.display.update()
                if event.key == K_BACKSPACE:
                    if count < 0:
                        continue
                    pygame.draw.rect(background, (0, 0, 0),
                                     (312.5+count*17, 330, 17, 35))
                    count -= 1
                    if len(name) > 0:
                        name = name[:-1]
                    pygame.display.update()
                if event.key == K_RETURN:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return ''.join(name)


def gameover(score):
    pygame.draw.rect(background, (0, 0, 0), (300, 250, 200, 200))
    pygame.draw.rect(background, (0, 0, 255), (350, 400, 100, 40))

    smallText1 = pygame.font.SysFont('comicsansms', 80)
    smallText2 = pygame.font.SysFont('comicsansms', 30)
    smallText3 = pygame.font.SysFont('comicsansms', 20)

    textSurf1, textRect1 = text_objects('Game Over', smallText1)
    textRect1.center = (400, 80)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Your Score : ', smallText2)
    textRect2.center = (400, 280)
    background.blit(textSurf2, textRect2)
    textSurf3, textRect3 = text_objects('Continue', smallText3)
    textRect3.center = (400, 420)
    background.blit(textSurf3, textRect3)
    textSurf4, textRect4 = text_objects(str(score), smallText2)
    textRect4.center = (400, 340)
    background.blit(textSurf4, textRect4)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 350+100 > mouse[0] > 350 and 400 + 40 > mouse[1] > 400:
                    return


def level():
    pygame.draw.rect(background, (0, 0, 255), (350, 400, 100, 40))
    pygame.draw.rect(background, (0, 0, 255), (350, 500, 100, 40))
    pygame.draw.rect(background, (0, 0, 255), (350, 600, 100, 40))

    smallText_t = pygame.font.SysFont('comicsansms', 100)
    textSurf_t, textRect_t = text_objects('Tetris', smallText_t)
    textRect_t.center = (400, 150)
    background.blit(textSurf_t, textRect_t)

    smallText0 = pygame.font.SysFont('comicsansms', 30)
    textSurf0, textRect0 = text_objects('Please Select Level', smallText0)
    textRect0.center = (400, 300)
    background.blit(textSurf0, textRect0)
    smallText = pygame.font.SysFont('comicsansms', 20)
    textSurf1, textRect1 = text_objects('Easy', smallText)
    textRect1.center = (400, 420)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Normal', smallText)
    textRect2.center = (400, 520)
    background.blit(textSurf2, textRect2)
    textSurf3, textRect3 = text_objects('Hard', smallText)
    textRect3.center = (400, 620)
    background.blit(textSurf3, textRect3)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 350+100 > mouse[0] > 350 and 400 + 40 > mouse[1] > 400:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return 1.0, 'easy'
                if 350+100 > mouse[0] > 350 and 500 + 40 > mouse[1] > 500:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return 0.5, 'normal'
                if 350+100 > mouse[0] > 350 and 600 + 40 > mouse[1] > 600:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return 0.1, 'hard'


def sc(s, c):
    pygame.draw.rect(background, (0, 0, 0), (200, 400, 90, 100))
    pygame.draw.rect(background, (0, 0, 0), (50, 460, 240, 100))

    smallText = pygame.font.SysFont('comicsansms', 30)

    textSurf1, textRect1 = text_objects('Score : ', smallText)
    textRect1.center = (150, 450)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects(s, smallText)
    textRect2.center = (250, 450)
    background.blit(textSurf2, textRect2)
    if int(c) >= 2:
        textSurf3, textRect3 = text_objects('Combo : ', smallText)
        textRect3.center = (150, 500)
        background.blit(textSurf3, textRect3)
        textSurf4, textRect4 = text_objects(c, smallText)
        textRect4.center = (250, 500)
        background.blit(textSurf4, textRect4)
    pygame.display.update()


def leader(l, listt, name):
    smallText = pygame.font.SysFont('comicsansms', 30)
    smallText1 = pygame.font.SysFont('comicsansms', 20)

    textSurf, textRect = text_objects('Leaderboard ', smallText)
    textRect.center = (400, 100)
    background.blit(textSurf, textRect)
    textSurf1, textRect1 = text_objects('Level : ' + l[1], smallText)
    textRect1.center = (400, 200)
    background.blit(textSurf1, textRect1)
    for i in range(len(listt)):
        if ''.join(name) == str(listt[i][1]):
            textSurf4 = smallText.render(str(listt[i][1]), True, (200, 200, 0))
            textRect4 = textSurf4.get_rect()
            textRect4.center = (200+len(listt[i][1])*15/2, 300+40*i)
            background.blit(textSurf4, textRect4)
            textSurf5 = smallText.render(str(listt[i][0]), True, (200, 200, 0))
            textRect5 = textSurf5.get_rect()
            textRect5.center = (500-len(listt[i][0])*15/2, 300+40*i)
            background.blit(textSurf5, textRect5)

        else:
            textSurf2, textRect2 = text_objects(str(listt[i][1]), smallText)
            textRect2.center = (200+len(listt[i][1])*15/2, 300+40*i)
            background.blit(textSurf2, textRect2)
            textSurf3, textRect3 = text_objects(str(listt[i][0]), smallText)
            textRect3.center = (500-len(listt[i][0])*15/2, 300+40*i)
            background.blit(textSurf3, textRect3)

    pygame.draw.rect(background, (0, 0, 255), (350, 600, 100, 40))
    textSurf5, textRect5 = text_objects('Continue', smallText1)
    textRect5.center = (400, 620)
    background.blit(textSurf5, textRect5)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 350+100 > mouse[0] > 350 and 600 + 40 > mouse[1] > 600:
                    return


def draw_boundary():
    color = 100, 255, 200
    pygame.draw.rect(background, color, (300-5, 200-5, 200+10, 400+10))
    pygame.draw.rect(background, (0, 0, 0), (300, 200, 200, 400))
    for i in range(319, 500, 20):
        pygame.draw.line(background, (100, 100, 100), (i, 200), (i, 600), 1)
    for i in range(219, 600, 20):
        pygame.draw.line(background, (100, 100, 100), (300, i), (500, i), 1)

    pygame.draw.rect(background, color, (300-120, 200+5, 100, 100))
    pygame.draw.rect(background, (0, 0, 0), (300-120+5, 200+10, 90, 90))
    for i in range(3):
        pygame.draw.rect(background, color, (500+20, 200+5+i*120, 100, 100))
        pygame.draw.rect(background, (0, 0, 0),
                         (500+20+5, 200+10+i*120, 90, 90))

    smallText = pygame.font.SysFont('comicsansms', 30)
    textSurf1, textRect1 = text_objects('Hold', smallText)
    textRect1.center = (230, 180)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Next', smallText)
    textRect2.center = (570, 180)
    background.blit(textSurf2, textRect2)
    textSurf3, textRect3 = text_objects('?', smallText)
    textRect3.center = (570, 370)
    background.blit(textSurf3, textRect3)
    textSurf4, textRect4 = text_objects('?', smallText)
    textRect4.center = (570, 490)
    background.blit(textSurf4, textRect4)
    sc('0', '0')

    pygame.display.update()


def game_loop(level):
    start = timer()
    crashed = False
    blist = blockly()
    a = blocks(blist.new())
    shift = 0
    point = Point()
    while not crashed:
        a1 = copy.deepcopy(a)
        a1.shadow()
        # 突破天際
        for i in range(300, 500, 20):
            if back_d[(i, 180)]:
                crashed = True
        # get key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == KEYDOWN:
                if event.key == K_p:
                    pygame.time.delay(10000)
                a1.draw(0)
                if not a.move(event.key):
                    a1.draw(0)
                    a.draw(1)
                    a = a.touchdown(blist.new())
                    shift = 0
                    flag = clear()
                    s, c = point.score(flag)
                    sc(str(s), str(c))
                if event.key == K_LSHIFT and not shift:
                    a.draw(0)
                    pygame.draw.rect(background, (0, 0, 0),
                                     (300-120+5, 200+10, 90, 90))
                    a.piece['x'], a.piece['y'] = 190, 215
                    a.draw(1)
                    a = blocks(blist.shift())
                    shift = 1
                a1 = copy.deepcopy(a)
                a1.shadow()

        # freefall
        if timer()-start > level:
            if not a.freefall():
                a1.draw(0)
                a.draw(1)
                a = a.touchdown(blist.new())
                shift = 0
                flag = clear()
                s, c = point.score(flag)
                sc(str(s), str(c))
            start = timer()

        a.draw(1)
        pygame.display.update()
        clock.tick(60)
    return s


while True:
    file = open('Tetris_Record.txt', 'a+')
    pygame.init()
    width, height = 800, 800
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
    # start()
    # l=level()
    l = (1.0, 'easy')
    draw_boundary()
    score = game_loop(l[0])
    gameover(score)
    name = final()
    info = [l[1], str(score), str(name)]
    message = ','.join(info)
    file.write(message)
    file.write('\n')
    file.close()
    file = open('Tetris_Record.txt', 'r')
    listt = []
    s = file.readline()
    while s != '':
        s = s.split(',')
        if s[0] == l[1]:
            listt.append((s[1], s[2].strip('\n')))
        s = file.readline()
    listt = sorted(listt, key=lambda s: int(s[0]), reverse=True)
    listt = listt[:5]
    leader(l, listt, name)

    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
    pygame.display.update()

    print('level: ', l[1])
    print(listt[:5])
    file.close()
