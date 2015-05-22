from __future__ import absolute_import
import pygame
import time
import sys
import logging

from asec.rom import Loader


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s\t%(levelname)-10s\t"
           "%(name)-20s\t%(process)-5d\t%(message)s"
)


logger = logging.getLogger(__name__)

white = (255, 255, 255)

last_redraw = time.time()


def main():
    global last_redraw
    pygame.init()
    window = None

    def redraw(screen):
        global last_redraw
        _fps = 1000/(time.time()-last_redraw)
        last_redraw = time.time()

        image = screen.toImage()
        mode = image.mode
        size = image.size
        data = image.tostring()

        last_screen = pygame.image.fromstring(data, size, mode)
        window.blit(last_screen, (0, 0))

        myfont = pygame.font.SysFont("monospace", 15)
        label = myfont.render("FPS: %d" % _fps, 1, (255,255,0))
        window.blit(label, (20, 20))

        pygame.display.flip()

    if len(sys.argv) == 2:
        loader = Loader(sys.argv[1])
        loader.read()
        emulator = loader.loader.emulator()
        pygame.display.set_caption(loader.name)
        window = pygame.display.set_mode(
            (emulator.GPU.screen.width, emulator.GPU.screen.height),
            pygame.OPENGL | pygame.OPENGLBLIT | pygame.RESIZABLE
        )
        emulator.GPU.renderScreen.connect(redraw)
    else:
        logger.error('Please pass as the first argument path to ROM')
        pygame.quit()
        sys.exit()

    while (True):

        # check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        emulator.frame()


if __name__ == '__main__':
    main()
