import pygame
from windows import Work_zone

clock = pygame.time.Clock()
end_game = True
work_zone = Work_zone()
while end_game:
    clock.tick(30)
    work_zone.show(pygame.mouse.get_pos())
    pygame.display.update()
    for event in pygame.event.get():
        work_zone.press(event)
        if event.type == pygame.QUIT:
            end_game = False
pygame.quit()
