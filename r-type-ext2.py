#!/usr/bin/python3

import pygame
import random

GAME_FPS    = 30
GAME_WIDTH  = 800
GAME_HEIGHT = 400

OBJ_PLAYER     = -2
OBJ_BACKGROUND = -1
OBJ_FIRE       = +1
OBJ_MONSTER    = +2
OBJ_BLAST      = +3

PLAYER_SPEED     = 10
BACKGROUND_SPEED = 4
MONSTER_COUNT    = 3
MONSTER_SPEED    = 7
MONSTER_SCORE    = 1
FIRE_SPEED       = 9

def load_bmp(filename:str):
    player = pygame.image.load(filename).convert()
    player.set_colorkey((255,0,255))
    return player

def load_background(filename:str):
	img = pygame.image.load(filename).convert()
	h = img.get_height()
	w = img.get_width()
	background = pygame.Surface((GAME_WIDTH,GAME_HEIGHT))
	i = 0
	while i < GAME_HEIGHT%h:
		j = 0
		while j < GAME_WIDTH%w:
			background.blit(img,(j*w,i*h))
			j+=1
		i+=1
	return background

def get_sprites(image, count:int) -> list:
    width = image.get_width()
    heigth = image.get_height()
    size = pygame.Rect(0, 0, width, heigth)
    width_frame = width//count
    i = count
    sprites = []
    while i > 0:
            crop = pygame.Rect(i*width_frame,0,width_frame,heigth)
            frame = size.clip(crop)
            sprites.append(frame)
            i-=1
    return sprites

# Add displayable objects to the list.
def objects_append(g, t, x, y, **kwargs):
    if t == OBJ_PLAYER:
        g["objects"].append({"t":t,"img":g['img/player'],"coord" : [x,y]})

    if t == OBJ_FIRE:
        g["objects"].append({"t":t,"img":g['img/fire'],"coord" : [x,y]})

    if t == OBJ_MONSTER:
    	g["objects"].append({"t":t,"img":g['img/monster'],"coord" : [x,y]})

    if t == OBJ_BLAST:
        g["objects"].append({"t":t,"img":g['img/blast'],"coord" : [x-32,y-32],"sprites" : 0})
    pass

# Count objects by type.
def objects_count(g, t):
    i = 0
    for element in g['objects']:
        if t == element["t"]:
            i += 1
    return i

# Get last object by type.
def objects_last(g, t):
    last =[]
    for element in g["objects"]:
        if t == OBJ_FIRE and element["t"] == OBJ_FIRE:
            last.append(element)
    n = len(last)
    if n == 0:
        return GAME_WIDTH 
    i = 0
    while i < n:
        j = 0
        while j < n-i-1:
            if last[j]["coord"] > last[j+1]["coord"]:
                last[j]["coord"], last[j+1]["coord"] = last[j+1]["coord"], last[j]["coord"]
            j += 1
        i+=1
    return last[0]["coord"][0]

# Display objects on window.
def objects_draw(g, window):
    for element in g["objects"]:
        if element["t"] != OBJ_BLAST:
            window.blit(element["img"],element["coord"])
            # Hitboxes #
            ### pygame.draw.rect(window,(255,0,0),(element["coord"][0],element["coord"][1],element["img"].get_width(),element["img"].get_height()),2)
        else :
        	window.blit(element["img"],element["coord"],g['sprites'][element['sprites']])

    pass

# Moves objects (monsters, fires, animations, etc).
def objects_animate(g):
    for element in g["objects"]:
        if element["t"] == OBJ_FIRE:
            if element["coord"][0] > GAME_WIDTH:
                g["objects"].remove(element)
            element["coord"][0] += FIRE_SPEED
        
        if element["t"] == OBJ_MONSTER:
            element["coord"][0] -= MONSTER_SPEED

        if element["t"] == OBJ_BLAST:
        	element['sprites'] += 1
        	if element['sprites'] == 8:
        		g['objects'].remove(element)
    pass

# Handle keys (arrows, q, space).
def process_keys(g, keys):
    if keys[pygame.K_UP] and g["objects"][0]["coord"][1]>PLAYER_SPEED:
        g["objects"][0]["coord"][1]-=PLAYER_SPEED
    elif keys[pygame.K_UP]:
        g["objects"][0]["coord"][1] = 0
        
    if keys[pygame.K_DOWN] and GAME_HEIGHT - g["objects"][0]["coord"][1]-g['img/player'].get_height()>PLAYER_SPEED:
        g["objects"][0]["coord"][1]+=PLAYER_SPEED
    elif keys[pygame.K_DOWN]:
        g["objects"][0]["coord"][1] = GAME_HEIGHT - g['img/player'].get_height()
        
    if keys[pygame.K_LEFT] and g["objects"][0]["coord"][0]>PLAYER_SPEED:
        g["objects"][0]["coord"][0]-=PLAYER_SPEED
    elif keys[pygame.K_LEFT]:
        g["objects"][0]["coord"][0] = 0
        
    if keys[pygame.K_RIGHT] and GAME_WIDTH - g["objects"][0]["coord"][0]- g['img/player'].get_width()>PLAYER_SPEED:
        g["objects"][0]["coord"][0]+=PLAYER_SPEED
    elif keys[pygame.K_RIGHT]:
        g["objects"][0]["coord"][0] = GAME_WIDTH - g['img/player'].get_width()

    if keys[pygame.K_SPACE] and objects_last(g,OBJ_FIRE)-g["objects"][0]["coord"][0]>35:
        objects_append(g, OBJ_FIRE, g["objects"][0]["coord"][0], g["objects"][0]["coord"][1])
    pass

# Ensure there is MONSTER_COUNT monsters on the window.    
def make_monsters(g):
    if MONSTER_COUNT > objects_count(g,OBJ_MONSTER) :
        y = random.randint(0,GAME_HEIGHT-g['img/monster'].get_height())
        objects_append(g, OBJ_MONSTER,GAME_WIDTH,y)
    pass

# Check collisions between fires, monsters and player.
def check_collisions(g):
    fires = []
    monsters = []
    for element in g['objects']:
        if element["t"] == OBJ_FIRE:
            fires.append(element)
        if element["t"] == OBJ_MONSTER:
            monsters.append(element)
    for fire in fires:
        for monster in monsters:   
            if (fire['coord'][0] + fire["img"].get_width() > monster['coord'][0] and fire['coord'][0] + fire["img"].get_width()  < monster['coord'][0] + monster["img"].get_width()):
                    if fire['coord'][1] + fire["img"].get_height() > monster['coord'][1] and fire['coord'][1]  < monster['coord'][1] + monster["img"].get_height():
                        objects_append(g, OBJ_BLAST,monster['coord'][0],monster['coord'][1])
                        g['objects'].remove(fire)
                        fires.remove(fire)
                        g['objects'].remove(monster)
                        monsters.remove(monster)      
    pass

# Check if monsters arrived on the left of the window.
def check_monsters_have_won(g):
    for element in g['objects']:
        if element['t'] == OBJ_MONSTER:
            if element['coord'][0] < 0:
                g['objects'].remove(element)
    pass

# Display the background.
def background_draw(g, window):
    g['background/x1'] -= BACKGROUND_SPEED
    g['background/x2'] -= BACKGROUND_SPEED
    if g['background/x1'] < -GAME_WIDTH:
    	g['background/x1'] = GAME_WIDTH
    if g['background/x2'] < -GAME_WIDTH:
    	g['background/x2'] = GAME_WIDTH	
    window.blit(g['background'],(g['background/x1'],0))
    window.blit(g['background'],(g['background/x2'],0))
    pass

# Display the score.
def score_draw(g, window):
    pass

def main():
    pygame.init()
    random.seed(None,2)
    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    game   = {}     # Game data.
    quit   = False  # True when game is over.

    # Load bitmaps
    game['img/player'] = load_bmp('assets/player_1.bmp')
    game['img/fire'] = load_bmp('assets/fire.bmp')
    game['img/monster'] = load_bmp('assets/monster_1.bmp')
    game['img/blast'] = load_bmp('assets/blast.bmp')
    game['sprites'] = get_sprites(game['img/blast'],8)
    
    # Load background
    game['background'] = load_background('assets/level_1.bmp')
    game['background/x1'] = 0
    game['background/x2'] = GAME_WIDTH

    # Displayable objects list
    game['objects'] = []
    objects_append(game, OBJ_PLAYER, game['img/player'].get_width(), GAME_HEIGHT / 2)

    while not quit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            quit = True

        process_keys(game, keys)
        background_draw(game, window)
        make_monsters(game)
        objects_animate(game)
        check_collisions(game)
        check_monsters_have_won(game)
        objects_draw(game, window)
        score_draw(game, window)

        pygame.display.flip()
        pygame.time.wait(1000 // GAME_FPS)

        print('{0} objects displayed'.format(len(game['objects'])))

    pygame.quit()

main()