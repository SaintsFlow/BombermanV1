import threading

import pygame
from pygame.locals import *

import os
import settings
import sys
from bomb import Bomb
from box import Box
from grid import Grid
from hero import Hero
from map import Map


def check(x):
    return max(0, min(settings.WIDTH - settings.ICON, x))


def tableDraw():
    rect = pygame.Rect(settings.WIDTH + 2, 0, 220, settings.HEIGHT)
    surface.fill((0, 0, 0))
    textsurface = title.render("Hero", False, (255, 255, 255))
    surface.blit(textsurface, (680, 70))
    textsurface = myfont.render("Score: " + str(hero.score), False, (255, 255, 255))
    surface.blit(textsurface, (620, 140))
    textsurface = myfont.render("Bombs planted: " + str(hero.bombs) + "/" + str(hero.bomb_n), False, (255, 255, 255))
    surface.blit(textsurface, (620, 170))
    textsurface = myfont.render("Bomb radius: " + str(hero.bomb_r // settings.ICON) + " blocks", False, (255, 255, 255))
    surface.blit(textsurface, (620, 210))
    textsurface = title.render("Enemy", False, (255, 255, 255))
    surface.blit(textsurface, (670, 300))
    textsurface = myfont.render("Score: " + str(enemy.score), False, (255, 255, 255))
    surface.blit(textsurface, (620, 370))
    textsurface = myfont.render("Bombs planted: " + str(enemy.bombs) + "/" + str(enemy.bomb_n), False, (255, 255, 255))
    surface.blit(textsurface, (620, 400))
    textsurface = myfont.render("Bomb radius: " + str(enemy.bomb_r // settings.ICON) + " blocks", False,
                                (255, 255, 255))
    surface.blit(textsurface, (620, 440))

    textsurface = myfont.render(str(100 - step // 100), False, (255, 255, 255))
    surface.blit(textsurface, (700, 20))
    pygame.display.update(rect)


def Draw():
    surface.blit(settings.bgImg, (0, 0))
    grid.draw(surface)
    map.draw(surface, box, bombs, hero, enemy, explosion)
    pygame.display.update()
    tableDraw()


def KillThreads():
    for i in bombs:
        i.explode = True
        i.start = 7.0
    for i in explosion:
        i.start = 1.0
    for thread in threading.enumerate():
        if thread.isAlive():
            print()
            # try:
            #     thread._Thread__stop()
            # except:
            #     print(str(thread.getName()) + ' could not be terminated')


def Winner():
    if hero.alive:
        return "Hero is a Winner"
    if enemy.alive:
        return "Enemy is a Winner"
    if hero.score > enemy.score:
        return "Hero is a Winner"
    if hero.score < enemy.score:
        return "Enemy is a Winner"
    return "Draw"


pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 18)
title = pygame.font.SysFont('Comic Sans MS', 25)

gameOver = pygame.font.SysFont('Comic Sans MS', 30)

clock = pygame.time.Clock()
surface = pygame.display.set_mode((settings.WIDTH + 220, settings.HEIGHT))
pygame.mouse.set_visible(False)

grid = Grid()
hero = Hero(1)
enemy = Hero(2, settings.WIDTH - settings.ICON, settings.WIDTH - settings.ICON)
map = Map()
box = Box()
box.reset((hero.X // settings.ICON, hero.Y // settings.ICON), (enemy.X // settings.ICON, enemy.Y // settings.ICON))
bombs = []
explosion = []
running = True

lastKey = None
step = 0
gameState = True
while running:
    step += 1
    for event in pygame.event.get():
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
            KillThreads()
            break
        elif gameState == False and event.type == KEYDOWN and event.key == K_f:
            pygame.display.quit()
            pygame.quit()
            os.system(settings.PYTHON_EXECUTABLE + " main.py")
            sys.exit()
        elif gameState and event.type == KEYDOWN:
            if event.key == K_p:
                if enemy.bomb_n > enemy.bombs:
                    free = True
                    for i in bombs:
                        if i.X == enemy.X and i.Y == enemy.Y:
                            free = False
                            break
                    if free:
                        bombs.append(
                            Bomb(enemy.type, enemy.X, enemy.Y, map, box, bombs, hero, enemy, explosion, enemy.bomb_r))
                        enemy.bombs += 1
            if event.key == K_SPACE:
                if hero.bomb_n > hero.bombs:
                    free = True
                    for i in bombs:
                        if i.X == hero.X and i.Y == hero.Y:
                            free = False
                            break
                    if free:
                        bombs.append(
                            Bomb(hero.type, hero.X, hero.Y, map, box, bombs, hero, enemy, explosion, hero.bomb_r))
                        hero.bombs += 1
            else:
                key = event.key
                x = None
                y = None
                if key == K_w:
                    x, y = map.collission(hero.X, check(hero.Y - settings.SPEED), box, bombs, hero, enemy)
                elif key == K_s:
                    x, y = map.collission(hero.X, check(hero.Y + settings.SPEED), box, bombs, hero, enemy)
                elif key == K_a:
                    x, y = map.collission(check(hero.X - settings.SPEED), hero.Y, box, bombs, hero, enemy)
                elif key == K_d:
                    x, y = map.collission(check(hero.X + settings.SPEED), hero.Y, box, bombs, hero, enemy)
                if x != None:
                    hero.X, hero.Y = x, y
                x = None
                y = None
                if key == K_UP:
                    x, y = map.collission(enemy.X, check(enemy.Y - settings.SPEED), box, bombs, hero, enemy)
                elif key == K_DOWN:
                    x, y = map.collission(enemy.X, check(enemy.Y + settings.SPEED), box, bombs, hero, enemy)
                elif key == K_LEFT:
                    x, y = map.collission(check(enemy.X - settings.SPEED), enemy.Y, box, bombs, hero, enemy)
                elif key == K_RIGHT:
                    x, y = map.collission(check(enemy.X + settings.SPEED), enemy.Y, box, bombs, hero, enemy)
                if x != None:
                    enemy.X, enemy.Y = x, y
    if gameState:
        hero.takeLoot(box)
        enemy.takeLoot(box)
        for i in explosion:
            if i.explode:
                explosion.remove(i)
        Draw()
    # hero.smoothMove(grid, surface, clock, bombs)
    if gameState == True and (hero.alive == False or enemy.alive == False):
        if not hero.alive:
            hero.img = pygame.transform.rotate(hero.img, -90)
        if not enemy.alive:
            enemy.img = pygame.transform.rotate(enemy.img, -90)
        # KillThreads()
        Draw()
        text = gameOver.render(Winner(), False, (2, 180, 180))
        surface.blit(text, (230, 250))
        text = gameOver.render("To restart press F", False, (2, 180, 180))
        surface.blit(text, (230, 300))
        pygame.display.update()
        gameState = False
    if step > 10000:
        hero.alive = False
        enemy.alive = False
    clock.tick(60)
