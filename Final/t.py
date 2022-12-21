import pygame
import random
import math
import copy
import os
import io
import time
from ctypes import *
from pygame.locals import *
from timeit import default_timer as timer
from threading import Thread
import queue
from n import Network

os.environ["SDL_VIDEODRIVER"] = "dummy"

q = queue.Queue()

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

LE = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
LI = [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]]
LL = [[0, 0, 0, 2], [0, 2, 2, 2], [0, 0, 0, 0], [0, 0, 0, 0]]
LJ = [[0, 3, 0, 0], [0, 3, 3, 3], [0, 0, 0, 0], [0, 0, 0, 0]]
LO = [[0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
LS = [[0, 0, 5, 5], [0, 5, 5, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
LZ = [[0, 6, 6, 0], [0, 0, 6, 6], [0, 0, 0, 0], [0, 0, 0, 0]]
LT = [[0, 0, 7, 0], [0, 7, 7, 7], [0, 0, 0, 0], [0, 0, 0, 0]]

mapping = {0: LE, 1: LI, 2: LL, 3: LJ, 4: LO, 5: LS, 6: LZ, 7: LT}


class Info(Structure):
    _fields_ = [('player0_main', c_int*20*10),
                ('player0_shift', c_int*4*4),
                ('player0_next', c_int*4*4),
                ('player0_pts', c_int),
                ('player0_cbs', c_int),
                ('player1_main', c_int*20*10),
                ('player1_shift', c_int*4*4),
                ('player1_next', c_int*4*4),
                ('player1_pts', c_int),
                ('player1_cbs', c_int)]


class blocks():
    length = 20

    def __init__(self, shape, player=0):
        global leftup, width
        self.piece = {'shape': shape, 'x': width/4-2 *
                      self.length, 'y': leftup[1]-2*self.length, 'r': 0}
        self.draw(1)
        self.player = player
        return

    def draw(self, x, y=0):
        # color = [(0, 255, 255), (255, 153, 0), (0, 0, 255),
        #          (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255)]
        # s, t = self.piece['x']+2, self.piece['y']+2
        # for col in self.piece['shape'][self.piece['r']]:
        #     for i in col:
        #         if int(i) and t >= 200:
        #             if x:
        #                 if y:  # for shawdow
        #                     rec = pygame.draw.rect(background, color[int(
        #                         i)-1], (s, t, self.length-4, self.length-4))
        #                     rec = pygame.draw.rect(
        #                         background, (0, 0, 0), (s+2, t+2, self.length-8, self.length-8))
        #                 else:  # for normal block
        #                     rec = pygame.draw.rect(background, color[int(
        #                         i)-1], (s, t, self.length-5, self.length-5))
        #             else:  # for black
        #                 rec = pygame.draw.rect(
        #                     background, (0, 0, 0), (s, t, self.length-3, self.length-3))
        #         s += self.length
        #     s = self.piece['x']+2
        #     t += self.length
        return

    def freefall(self):
        self.draw(0)
        self.piece['y'] += self.length
        if not self.isvalid():
            self.piece['y'] -= self.length
            self.draw(1)
            return False
        update_status(self.piece['x'], self.piece['y']-self.length,
                      self.piece['shape'][self.piece['r']], self.length, 0, self.player)
        update_status(self.piece['x'], self.piece['y'],
                      self.piece['shape'][self.piece['r']], self.length, 1, self.player)
        return True

    def move(self, key):
        # if key == 'd':
        # print(back_d)
        if key == "d":
            # if key == pygame.K_DOWN:
            self.draw(0)
            self.piece['y'] += self.length
            if self.isvalid():
                update_status(self.piece['x'], self.piece['y']-self.length,
                              self.piece['shape'][self.piece['r']], self.length, 0, self.player)
                update_status(self.piece['x'], self.piece['y'],
                              self.piece['shape'][self.piece['r']], self.length, 1, self.player)
                pygame.time.delay(100)
            else:
                self.piece['y'] -= self.length
                self.draw(1)
                return False

        elif key == 'l':
            # elif key == pygame.K_LEFT:
            self.draw(0)
            self.piece['x'] -= self.length
            if self.isvalid():
                update_status(self.piece['x']+self.length, self.piece['y'],
                              self.piece['shape'][self.piece['r']], self.length, 0, self.player, 1)
                update_status(self.piece['x'], self.piece['y'],
                              self.piece['shape'][self.piece['r']], self.length, 1, self.player, 1)
                pygame.time.delay(100)
            else:
                self.piece['x'] += self.length

        elif key == 'r':
            # elif key == pygame.K_RIGHT:
            self.draw(0)
            self.piece['x'] += self.length
            if self.isvalid():
                update_status(self.piece['x']-self.length, self.piece['y'],
                              self.piece['shape'][self.piece['r']], self.length, 0, self.player, 1)
                update_status(self.piece['x'], self.piece['y'],
                              self.piece['shape'][self.piece['r']], self.length, 1, self.player, 1)
                pygame.time.delay(100)
            else:
                self.piece['x'] -= self.length

        elif key == 'u':
            # elif key == pygame.K_UP:
            self.draw(0)
            if self.can_rotate():
                pygame.time.delay(10)

        elif key == ' ':
            # elif key == pygame.K_SPACE:
            self.draw(0)
            oldy = self.piece['y']
            while self.isvalid():
                self.piece['y'] += self.length
            self.piece['y'] -= self.length
            self.draw(1)
            update_status(self.piece['x'], oldy,
                          self.piece['shape'][self.piece['r']], self.length, 0, self.player)
            update_status(self.piece['x'], self.piece['y'],
                          self.piece['shape'][self.piece['r']], self.length, 1, self.player)
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
            update_status(x, y, self.piece['shape']
                          [r], self.length, 0, self.player, 1)
            update_status(self.piece['x'], self.piece['y'],
                          self.piece['shape'][self.piece['r']], self.length, 1, self.player, 1)
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
        return blocks(shape, self.player)

    def shadow(self):
        while self.isvalid():
            self.piece['y'] += self.length
        self.piece['y'] -= self.length

        update_status(self.piece['x'], self.piece['y'],
                      self.piece['shape'][self.piece['r']], self.length, 2, self.player, 1)

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
            self.inil = 400
            self.init = 200
        else:
            self.inil = 1000
            self.init = 200

    def new(self):
        t = self.next
        self.cur = self.next
        self.count = (self.count+1) % 7
        if not self.count:
            random.shuffle(self.block)
        self.next = self.block[self.count]
        status["next0"] = mapping[int(str(int(max(self.next[2])))[0])]
        return t

    def shift(self):
        if not self.hold:
            self.hold = self.cur
            self.cur = self.next
            self.count = (self.count+1) % 7
            if not self.count:
                random.shuffle(self.block)
            self.next = self.block[self.count]
            status["next0"] = mapping[int(str(int(max(self.next[2])))[0])]
            return self.cur
        self.hold, self.cur = self.cur, self.hold
        return self.cur

    def draw(self):
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


def sc(s, c):
    status["score0"] = int(s)
    status["combo0"] = int(c)
    ll = 200
    tt = 200
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
        textRect3.center = (ll-150, tt+300)
        background.blit(textSurf3, textRect3)
        textSurf4, textRect4 = text_objects(c, smallText)
        textRect4.center = (ll-50, tt+300)
        background.blit(textSurf4, textRect4)
    pygame.display.update()

    ll = 800
    tt = 200

    pygame.draw.rect(background, (0, 0, 0), (ll-100, tt+200, 90, 100))
    pygame.draw.rect(background, (0, 0, 0), (ll-250, tt+260, 240, 100))

    smallText = pygame.font.SysFont('comicsansms', 20)

    textSurf1, textRect1 = text_objects('Score : ', smallText)
    textRect1.center = (ll-150, tt+250)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects(str(status["score1"]), smallText)
    textRect2.center = (ll-50, tt+250)
    background.blit(textSurf2, textRect2)
    if status["combo1"] >= 2:
        textSurf3, textRect3 = text_objects('Combo : ', smallText)
        textRect3.center = (ll-150, tt+300)
        background.blit(textSurf3, textRect3)
        textSurf4, textRect4 = text_objects(str(status["combo1"]), smallText)
        textRect4.center = (ll-50, tt+300)
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
    sc('0', '0')
    pygame.display.update()


def start():
    BTStart = (540, 320, 120, 60)
    BTQuit = (540, 500, 120, 60)
    pygame.draw.rect(background, (0, 150, 0), BTStart)
    pygame.draw.rect(background, (200, 0, 0), BTQuit)

    smallText = pygame.font.SysFont('comicsansms', 30)
    smallText_t = pygame.font.SysFont('comicsansms', 100)
    textSurf_t, textRect_t = text_objects('Tetris', smallText_t)
    textRect_t.center = (600, 150)
    background.blit(textSurf_t, textRect_t)

    textSurf1, textRect1 = text_objects('Start', smallText)
    textRect1.center = (600, 350)
    background.blit(textSurf1, textRect1)
    textSurf2, textRect2 = text_objects('Quit', smallText)
    textRect2.center = (600, 530)
    background.blit(textSurf2, textRect2)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                if 540+120 > mouse[0] > 540 and 320 + 60 > mouse[1] > 320:
                    pygame.draw.rect(background, (0, 0, 0), (0, 0, 800, 800))
                    pygame.display.update()
                    return
                if 540 + 120 > mouse[0] > 540 and 500 + 60 > mouse[1] > 500:
                    pygame.quit()


def clear():
    global back_d
    flag = 0
    for j in range(200, 600, 20):
        if all(back_d[(i, j)] for i in range(200, 400, 20)):
            flag += 1
            for t in range(j, 180, -20):
                for s in range(200, 400, 20):
                    back_d[(s, t)] = back_d[(s, t-20)]
                    status[(s, t)] = status[(s, t-20)]
    if flag:
        draw_status()
        send_status()
    return flag


# x = self.piece['x']
# y = self.piece['y']
# l = self.piece['shape'][self.piece['r']]
# length = self.length
# mode 0 = erase
def update_status(x, y, l, length, mode,  player=0,  cleanShadow=0):
    if cleanShadow:
        for key in status:
            if status[key] == 8:
                status[key] = 0
    for i in range(len(l)):
        for j in range(len(l)):
            m = int(x+length*j) + player * 600
            n = int(y+length*i)
            if ((m, n) not in status) or int(l[i][j]) == 0:
                continue
            if mode == 1:
                status[(m, n)] = int(l[i][j])
            elif mode == 2:
                if status[(m, n)] == 0:
                    status[(m, n)] = 8  # shadow
            else:
                status[(m, n)] = 0
    draw_status()
    if mode == 1:
        send_status()


def send_status():
    package = {}
    for i in range(200, 400, 20):
        for j in range(160, 600, 20):
            package[(i, j)] = status[(i, j)]
    package["score0"] = status["score0"]
    package["combo0"] = status["combo0"]
    package["shift0"] = status["shift0"]
    package["next0"] = status["next0"]
    status.update(n.send(package))
    # print("T received!", n.send(package))

# todo: shadow


def draw_status(shadow=0):
    color = [(0, 0, 0), (0, 255, 255), (255, 153, 0), (0, 0, 255),
             (255, 255, 0), (0, 255, 0), (255, 0, 0), (102, 0, 255), (128, 128, 128)]
    for key in status:
        if key in specialKey:
            continue
        s, t = key[0] + 2, key[1] + 2
        if t < 200:
            continue
        if status[key] != 8:
            pygame.draw.rect(background, color[status[key]], (s, t, 15, 15))
        else:
            pygame.draw.rect(background, color[8], (s, t, 15, 15))
            pygame.draw.rect(background, (0, 0, 0), (s+2, t+2, 11, 11))
    sc(str(status["score0"]), str(status["combo0"]))

    s, t = 90, 225
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(
                background, color[status["shift0"][i][j]], (s, t, 15, 15))
            s += 20
        s = 90
        t += 20

    s, t = 690, 225
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(
                background, color[status["shift1"][i][j]], (s, t, 15, 15))
            s += 20
        s = 690
        t += 20

    s, t = 430, 225
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(
                background, color[status["next0"][i][j]], (s, t, 15, 15))
            s += 20
        s = 430
        t += 20

    s, t = 1030, 225
    for i in range(4):
        for j in range(4):
            pygame.draw.rect(
                background, color[status["next1"][i][j]], (s, t, 15, 15))
            s += 20
        s = 1030
        t += 20

    # print(status)
    t = Info()

    for i in range(200, 400, 20):
        for j in range(200, 600, 20):
            x = int((i - 200) / 20)
            y = int((j - 200) / 20)
            t.player0_main[x][y] = status[(i, j)]
            t.player1_main[x][y] = status[(i+600, j)]

    for i in range(4):
        for j in range(4):
            t.player0_shift[i][j] = status["shift0"][i][j]
            t.player1_shift[i][j] = status["shift1"][i][j]
            t.player0_next[i][j] = status["next0"][i][j]
            t.player1_shift[i][j] = status["next1"][i][j]

    t.player0_pts = status["score0"]
    t.player1_pts = status["score1"]
    t.player0_cbs = status["combo0"]
    t.player1_cbs = status["combo1"]

    f.write(t)


def game_loop(level, player=0):
    ll = 200
    tt = 200
    start = timer()
    crashed = False
    blist = blockly()
    print("init player", player)
    a = blocks(blist.new(), player)
    shift = 0
    point = Point()
    while not crashed:
        a1 = copy.deepcopy(a)
        a1.shadow()
        # 突破天際
        for i in range(200, 400, 20):
            if back_d[(i, 180)]:
                print("crashed!")
                crashed = True

        # get key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
        if not q.empty():
            # if event.type == KEYDOWN:
            # if event.key == K_p:
            #     pygame.time.delay(10000)
            a1.draw(0)
            order = q.get()
            if not a.move(order):
                a1.draw(0)
                a.draw(1)
                a = a.touchdown(blist.new())
                shift = 0
                flag = clear()
                s, c = point.score(flag)
                sc(str(s), str(c))
            if order == "s" and not shift:
                # a.draw(0)
                update_status(a.piece['x'], a.piece['y'],
                              a.piece['shape'][a.piece['r']], a.length, 0, a.player, 1)
                status["shift0"] = mapping[int(
                    str(int(max(a.piece['shape'][a.piece['r']])))[0])]
                # pygame.draw.rect(background, (0, 0, 0),
                #                  (ll-120+5, tt+10, 90, 90))
                # a.piece['x'], a.piece['y'] = 90, 215
                # a.draw(1)
                a = blocks(blist.shift(), player)
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
        draw_status()
        send_status()
    return s


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


def main(player=0):
    global n
    global f
    file_name = 'panel.fifo'
    if not os.path.exists(file_name):
        os.mkfifo(file_name)

    fd = os.open(file_name, os.O_RDWR)
    f = io.FileIO(fd, 'wb')

    n = Network()
    global status

    pygame.init()
    global background
    background = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Tetris')

    # start()
    l = (1, 'easy')
    draw_boundary(200, 200)
    draw_boundary(800, 200)
    score = game_loop(l[0], player)


def signal():
    while True:
        data = input("Order:")
        q.put(data)


width, height = 1200, 650
clock = pygame.time.Clock()

gamewidth, gameheight = 300, 600
leftup = (200, 200)
back_d = {}
status = {"combo0": 0, "score0": 0, "combo1": 0, "score1": 0,
          "shift0": LE, "next0": LE, "shift1": LE, "next1": LE}

for i in range(0, 640, 20):
    for j in range(0, 640, 20):
        back_d[(i, j)] = 1

# for player 0
for i in range(200, 400, 20):
    for j in range(160, 600, 20):
        back_d[(i, j)] = 0
        status[(i, j)] = 0

# for player 1
for i in range(800, 1000, 20):
    for j in range(160, 600, 20):
        status[(i, j)] = 0

specialKey = ["score0", "score1", "combo0",
              "combo1", "shift0", "shift1", "next0", "next1"]

player0_thread = Thread(target=main, args=(0,))
signal_thread = Thread(target=signal)

player0_thread.start()
signal_thread.start()

player0_thread.join()
signal_thread.join()
