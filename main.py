import os
from sys import argv, exit

if len(argv) == 2:
    model_path = argv[1]\
        .strip()\
        .removeprefix('"')\
        .removeprefix("'")\
        .removesuffix('"')\
        .removesuffix("'")
    if not os.path.exists(model_path):
        raise FileNotFoundError("File: '{model_path}' does not exist")
elif len(argv) > 2:
    raise ValueError("Too many arguements passed")
else:
    raise ValueError("Not enough arguements passed")


import pygame
from constants import *
from parser import parse_obj
from models import KeyBoardControlledBox

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


font = pygame.font.SysFont("Cambria", 20)

model = KeyBoardControlledBox(screen, clock, parse_obj(model_path))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
    model.run(DisplayFlags.VERTEX.value | DisplayFlags.VERTEX_I.value | DisplayFlags.WIRE.value)
    
    
    screen.blit(font.render(str(int(clock.get_fps())), False, "White"), (10, 10))
    pygame.display.update()
    screen.fill("black")
    clock.tick(60)