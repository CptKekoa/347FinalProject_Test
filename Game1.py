import pygame
import sys
import random
import math
from entities import PhysicsEntity, Player
from utils import load_image, load_images, Animation
from tilemap import Tilemap
from clouds import Clouds
from particle import Particle

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Ninja Game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320,240))                   # Creates a smaller display for the small player to make it look bigger

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {                                             # Dictionary of all the assets
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'lava' : load_images('tiles/lava'),
            'large_decor' : load_images('tiles/large_decor'),
            'stone' : load_images('tiles/Stone'),
            'player' : load_image('entities/Slime.png'),
            'background' : load_image('sewer.png'),
            #'clouds' : load_images('clouds'),
            'player/idle' : Animation(load_images('entities/player/slime'), img_dur = 6),
            'player/run' : Animation(load_images('entities/player/slime'), img_dur = 4),
            'player/jump' : Animation(load_images('entities/player/slime_jump')),
            #'player/slide' : Animation(load_images('entities/player/slide')),
            'player/wall_slide' : Animation(load_images('entities/player/slime')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur = 20, loop = False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur = 6, loop = False),
        }

        #self.clouds = Clouds(self.assets['clouds'], count = 16)            # Sets clouds

        self.player = Player(self, (50,50), (8,15))        # Loads the player

        self.tilemap = Tilemap(self, tile_size=16)                          # Sets tiles
        self.tilemap.load('map.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep = True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.particles = []

        self.scroll = [0,0]                                                 # Camera Position
        

    def run(self):

        while True:
            self.display.fill((0, 0, 0))

            self.display.blit(self.assets['background'], (0,0)) 

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30            # Centers the camera on to the player
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            for rect in self.leaf_spawners:                                                                  # Spawns leaf particles
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity = [-0.1, 0.3], frame = random.randint(0, 20)))

            #self.clouds.update()
            #self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset = render_scroll)                              

            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)

            for particle in self.particles.copy():                                         # Manages particles
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animations.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:    
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.player.jump()
                    #if event.key == pygame.K_x:
                        #self.player.dash()
                if event.type == pygame.KEYUP:    
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))       # makes the screen the size of the display so that it is zoomed in
            pygame.display.update()
            self.clock.tick(60)

Game().run()