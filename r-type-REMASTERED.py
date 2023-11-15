#!/usr/bin/python3

import pygame , random, os

CWD = os.getcwd()

GAME_FPS    = 30
GAME_WIDTH  = 800
GAME_HEIGHT = 400

OBJ_PLAYER     = -2
OBJ_BACKGROUND = -1
OBJ_FIRE       = +1
OBJ_MONSTER    = +2
OBJ_BLAST      = +3
OBJ_BOSS       = +4
OBJ_BOSS_FIRE  = +5

PLAYER_SPEED     = 10
BACKGROUND_SPEED = 4
MONSTER_COUNT    = 3
MONSTER_SPEED    = 7 
MONSTER_SCORE    = 1
FIRE_SPEED       = 9
x = 1

# Load images
def load_bmp(filename:str):
    player = pygame.image.load(filename).convert()
    player.set_colorkey((255,0,255))
    return player

# Load Background
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

# Load Sprites
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
        pygame.mixer.Sound.play(g['fire_sound'])
    if t == OBJ_MONSTER:
    	g["objects"].append({"t":t,"img":g['img/monster'],"coord" : [x,y]})

    if t == OBJ_BLAST:
        g["objects"].append({"t":t,"img":g['img/blast'],"coord" : [x-32,y-32],"sprites" : 0})

    if t == OBJ_BOSS:
        g["objects"].append({"t":t,"img":g['img/boss'],"coord" : [x,y]})
        pygame.mixer.stop()
        pygame.mixer.Sound.play(g['boss'],-1)

    if t == OBJ_BOSS_FIRE :
        g["objects"].append({"t":t,"img":g['img/boss_fire'],"coord" : [x,y]})
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
    if t == OBJ_BOSS_FIRE:
        for element in g["objects"]:
            if element["t"] == t:
                last.append(element)
        n = len(last)
        if n == 0:
            return 0
        i = 0
        while i < n:
            j = 0
            while j < n-i-1:
                if last[j]["coord"] < last[j+1]["coord"]:
                    last[j]["coord"], last[j+1]["coord"] = last[j+1]["coord"], last[j]["coord"]
                j += 1
            i+=1
        return last[0]["coord"][0]
    else:
        for element in g["objects"]:
            if element["t"] == t:
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
        else :
        	window.blit(element["img"],element["coord"],g['sprites'][element['sprites']])

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

        if element['t'] == OBJ_BOSS:
            if  element["coord"][1] < 30 :
                g['boss_move'] = True
            elif element["coord"][1] + element["img"].get_height() > GAME_HEIGHT - 30:
                g['boss_move'] = False
            if g['boss_move']:
                element["coord"][1] += 5
            else:
                element["coord"][1] -= 5
            randspawn = random.randint(0,100)
            randfire = random.randint(0,1)
            if randspawn < 50 and objects_last(g,OBJ_BOSS_FIRE) < GAME_WIDTH - element["img"].get_width() - 50:
                y = element["coord"][1]+3 
                y2 = element["coord"][1]+57
                if randfire:
                    objects_append(g,OBJ_BOSS_FIRE,element["coord"][0]+14,y2)
                else:
                    objects_append(g,OBJ_BOSS_FIRE,element["coord"][0]+14,y)

        if element['t'] == OBJ_BOSS_FIRE:
            if element["coord"][0] < -10:
                g["objects"].remove(element)
            element["coord"][0] -= FIRE_SPEED

# Handle keys (arrows, q, space).
def process_keys(g, keys):
    if(g['play']):
        if keys[pygame.K_UP] and g["objects"][0]["coord"][1]>PLAYER_SPEED:
            g["objects"][0]["coord"][1] -= PLAYER_SPEED
        elif keys[pygame.K_UP]:
            g["objects"][0]["coord"][1] = 0
            
        if keys[pygame.K_DOWN] and GAME_HEIGHT - g["objects"][0]["coord"][1]-g['img/player'].get_height()>PLAYER_SPEED:
            g["objects"][0]["coord"][1]+=PLAYER_SPEED
        elif keys[pygame.K_DOWN]:
            g["objects"][0]["coord"][1] = GAME_HEIGHT - g['img/player'].get_height()
            
        if keys[pygame.K_LEFT] and g["objects"][0]["coord"][0]>PLAYER_SPEED:
            g["objects"][0]["coord"][0] -= PLAYER_SPEED
        elif keys[pygame.K_LEFT]:
            g["objects"][0]["coord"][0] = 0
            
        if keys[pygame.K_RIGHT] and GAME_WIDTH - g["objects"][0]["coord"][0]- g['img/player'].get_width()>PLAYER_SPEED:
            g["objects"][0]["coord"][0] += PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            g["objects"][0]["coord"][0] = GAME_WIDTH - g['img/player'].get_width()

        if keys[pygame.K_SPACE] and objects_last(g,OBJ_FIRE)-g["objects"][0]["coord"][0]>35:
            objects_append(g, OBJ_FIRE, g["objects"][0]["coord"][0], g["objects"][0]["coord"][1])

# Ensure there is MONSTER_COUNT monsters on the window.    
def make_monsters(g):
    randspawn = random.randint(0,255)
    if randspawn > 200:
        if MONSTER_COUNT > objects_count(g,OBJ_MONSTER):
            y = random.randint(0,GAME_HEIGHT-g['img/monster'].get_height())
            objects_append(g, OBJ_MONSTER,GAME_WIDTH,y)
        elif (g['actualMenu'] != 0 or g['gameover']) and 35 > objects_count(g,OBJ_MONSTER):
            y = random.randint(0,GAME_HEIGHT-g['img/monster'].get_height())
            objects_append(g, OBJ_MONSTER,GAME_WIDTH,y)

# Check collisions between fires, monsters and player.
def check_collisions(g):
    fires = []
    monsters = []
    players = []
    bosses = []
    for element in g['objects']:
        if element["t"] == OBJ_FIRE:
            fires.append(element)
        if element["t"] == OBJ_MONSTER:
            monsters.append(element)
        if element["t"] == OBJ_PLAYER:
            players.append(element)
        if element["t"] == OBJ_BOSS:
            bosses.append(element)
    for fire in fires:
        for monster in monsters:   
            if (fire['coord'][0] + fire["img"].get_width() > monster['coord'][0] and fire['coord'][0] + fire["img"].get_width()  < monster['coord'][0] + monster["img"].get_width()):
                    if fire['coord'][1] + fire["img"].get_height() > monster['coord'][1] and fire['coord'][1]  < monster['coord'][1] + monster["img"].get_height():
                        objects_append(g, OBJ_BLAST,monster['coord'][0],monster['coord'][1])
                        g['objects'].remove(fire)
                        fires.remove(fire)
                        g['objects'].remove(monster)
                        monsters.remove(monster)
                        g['score'] += 1 
        for boss in bosses:
            if (fire['coord'][0] + fire["img"].get_width() > boss['coord'][0] and fire['coord'][0] + fire["img"].get_width()  < boss['coord'][0] + boss["img"].get_width()):
                    if fire['coord'][1] + fire["img"].get_height() > boss['coord'][1] and fire['coord'][1]  < boss['coord'][1] + boss["img"].get_height():
                        objects_append(g, OBJ_BLAST,fire['coord'][0],fire['coord'][1])
                        g['HP'] -= 3
                        g['objects'].remove(fire)
                        fires.remove(fire)
                        if g['HP'] == 0:
                            bosses.remove(boss)
                            g['score'] += 1 
                            g['objects'].remove(boss)
                            g['jukebox'] += 1
                            x = g['jukebox']
                            level_up(g)
                            pygame.mixer.stop()
                            pygame.mixer.Sound.play(g['level'][x],-1)
    
    for monster in monsters:
        for player in players:
            if (player['coord'][0] + player["img"].get_width()> monster['coord'][0] and player['coord'][0] + player["img"].get_width() < monster['coord'][0] + monster["img"].get_width()) \
            or (player['coord'][0] > monster['coord'][0] and player['coord'][0] < monster['coord'][0] + monster["img"].get_width()):
            
                if (player['coord'][1] + player["img"].get_height()> monster['coord'][1] and player['coord'][1]  < monster['coord'][1] + monster["img"].get_height()) \
                or (player['coord'][1] > monster['coord'][1] and player['coord'][1]  < monster['coord'][1] + monster["img"].get_height()):

                    objects_append(g, OBJ_BLAST,monster['coord'][0],monster['coord'][1])
                    g['objects'].remove(monster)
                    monsters.remove(monster)
                    g['objects'].remove(player)
                    players.remove(player)
                    g["gameover"] = True
                    g['play'] = False
                    pygame.mixer.stop()
                    pygame.mixer.Sound.play(g['ending'],-1)

# Check if monsters arrived on the left of the window.
def check_monsters_have_won(g):
    for element in g['objects']:
        if element['t'] == OBJ_MONSTER:
            if element['coord'][0] < 0: 
                g['objects'].remove(element)
                if g['play']:
                    g['play'] = False
                    g["gameover"] = True
                    pygame.mixer.stop()
                    pygame.mixer.Sound.play(g['ending'],-1)

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

#def rescale(g, window):
    #window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    #g['background'] = load_background('assets/level_1.bmp')
    #g['img/player'] = pygame.transform.scale(load_bmp('assets/player_1.bmp'),(32*(GAME_WIDTH%800), 12*(GAME_HEIGHT%400)))
    #g['img/fire'] = pygame.transform.scale(load_bmp('assets/fire.bmp'),(23*(GAME_WIDTH%800), 6*(GAME_HEIGHT%400)))
    #g['img/monster'] = pygame.transform.scale(load_bmp('assets/monster_1.bmp'),(22*(GAME_WIDTH%800), 24*(GAME_HEIGHT%400)))
    #g['img/blast'] = pygame.transform.scale(load_bmp('assets/blast.bmp'),(512*(GAME_WIDTH%800), 64*(GAME_HEIGHT%400)))
    #g['sprites'] = get_sprites(g['img/blast'],8)

# Display the score.
def score_draw(g, window):
    text = g['font'].render("Score :{0}".format(g['score']), True ,(100,100,100))
    window.blit(text, (16,16))
    pass

# Manage the selector of menus
def selector(g, window, keys, lastkeys):
    if keys[pygame.K_UP] and not lastkeys[pygame.K_UP] and g['select'] > 0:
        g['select'] -= 1
    if keys[pygame.K_DOWN] and not lastkeys[pygame.K_DOWN]:
        if g['select'] < 3:
            g['select'] += 1
    if keys[pygame.K_SPACE] and not lastkeys[pygame.K_SPACE]:
        # Main Menu
        if g['actualMenu'] == 1 and g['select'] == 0:
            g['actualMenu'] = 0
            g['play'] = True
            g['objects'] = []
            objects_append(g, OBJ_PLAYER, g['img/player'].get_width(), GAME_HEIGHT / 2)
            g['gameover'] = False
            pygame.mixer.stop()
            pygame.mixer.Sound.play(g['level'][0],-1)
        elif g['actualMenu'] == 1 and g['select'] == 1:
            g['actualMenu'] = 2
            g['select'] = 0
        elif g['actualMenu'] == 1 and g['select'] == 2:
            g['actualMenu'] = 3
            g['select'] = 0
        elif g['actualMenu'] == 1 and g['select'] == 3:
            g['quit'] = True

        # Settings Menu
        elif g['actualMenu'] == 2 and g['select'] == 0:
            g['iRel'] += 1
            if g['iRel'] > 5:
                g['iRel'] = 0
            iRel = g['iRel']
            #GAME_WIDTH = g['Resolution'][iRel][0]
            #GAME_HEIGHT = g['Resolution'][iRel][1]
            #rescale(g,window)
            
        elif g['actualMenu'] == 2 and g['select'] == 1:
            g['sound'] = not g['sound']
        elif g['actualMenu'] == 2 and g['select'] == 2:
            g['Difficulty'] += 1
            if g['Difficulty'] > 3:
                g['Difficulty'] = 1
        elif g['actualMenu'] == 2 and g['select'] == 3:
            g['actualMenu'] = 1
            g['select'] = 0     

        # About Menu
        elif g['actualMenu'] == 3 :
            g['actualMenu'] = 1
            g['select'] = 0

# Change the Difficulty Level
def level(g):
    global BACKGROUND_SPEED
    global MONSTER_COUNT
    global MONSTER_SPEED
    if g['score'] == 10 and objects_count(g,4) == 0:
        MONSTER_COUNT  = -1
        objects_append(g, OBJ_BOSS, GAME_WIDTH - g['img/boss'].get_width(), GAME_HEIGHT / 2)
        
    if g['Difficulty'] == 1 and MONSTER_COUNT  != -1:
        BACKGROUND_SPEED = 4
        MONSTER_COUNT    = 3
        MONSTER_SPEED    = 7

    
    elif g['Difficulty'] == 2 and MONSTER_COUNT  != -1:
        BACKGROUND_SPEED = 7
        MONSTER_COUNT    = 6
        MONSTER_SPEED    = 8

    elif g['Difficulty'] == 3 and MONSTER_COUNT  != -1:
        BACKGROUND_SPEED = 4
        MONSTER_COUNT    = 10
        MONSTER_SPEED    = 9

#Life bar of the boss
def Boss_life(g,window):
    HP_bar = pygame.Rect(1,1,g['HP'],20)
    HP_bar1 = pygame.Rect(0,0,150,20)
    Surf = pygame.Surface((152,22))
    pygame.draw.rect(Surf,(0,255,0),HP_bar,0)
    pygame.draw.rect(Surf,(255,255,255),HP_bar1,2)
    window.blit(Surf,(GAME_WIDTH-200,10))

def level_up(g):
    global MONSTER_COUNT
    g['Difficulty'] += 1
    MONSTER_COUNT = 0

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    random.seed(9)
    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    game   = {}     # Game data.
    #*****************#
    #    Variables    #
    #*****************#
    game['quit']   = False
    game['gameover'] = False
    game['score'] = 0
    game['WR'] = 0
    game['sound'] = True
    game['iRel'] = 0
    game['Difficulty'] = 1
    game['Resolution'] = [(800,400),(1200,600),(1400,700),(1600,800),(2000,1000),(2500,1250)]
    WR = False
    game['select'] = 0
    game['actualMenu'] = 1
    game['play'] = False
    game['boss_move'] = True
    game['noMonster'] = False
    game['HP'] = 150
    game['jukebox'] = 0
    #*****************#
    #      Fonts      #
    #*****************#
    game['font'] = pygame.font.Font(CWD + '\\assets\\Beware.ttf', 32)
    game['mess_font'] = pygame.font.Font(CWD + '\\assets\\Pixeled.ttf', 15)
    #*****************#
    #     Bitmaps     #
    #*****************#
    game['img/player'] = load_bmp(CWD + '\\assets\\player_1.bmp')
    game['img/fire'] = load_bmp(CWD + '\\assets\\fire.bmp')
    game['img/monster'] = load_bmp(CWD + '\\assets\\monster_1.bmp')
    game['img/blast'] = load_bmp(CWD + '\\assets\\blast.bmp')
    game['sprites'] = get_sprites(game['img/blast'],8)
    game['img/boss'] = pygame.transform.rotate(load_bmp(CWD + '\\assets\\boss.bmp'), 90)
    game['img/boss_fire'] = load_bmp(CWD + '\\assets\\fire_boss.bmp')
    #*****************#
    #      Sounds     #
    #*****************#
    game['fire_sound'] = pygame.mixer.Sound(CWD + '\\assets\\fire.ogg')
    game["title_screen"] = pygame.mixer.Sound(CWD + '\\assets\\Title Screen.wav')
    game["level"] = [pygame.mixer.Sound(CWD + '\\assets\\Level 1.wav'),pygame.mixer.Sound(CWD + '\\assets\\Level 2.wav'),pygame.mixer.Sound(CWD + '\\assets\\Level 3.wav')]
    game["boss"] = pygame.mixer.Sound(CWD + '\\assets\\Boss Battle.wav')
    game["ending"] = pygame.mixer.Sound(CWD + '\\assets\\Ending.wav')
    #*****************#
    #    Background   #
    #*****************#
    game['background'] = load_background(CWD + '\\assets\\level_1.bmp')
    game['background/x1'] = 0
    game['background/x2'] = GAME_WIDTH
    keys = pygame.key.get_pressed()
    #*******************************#
    #    List of displayed object   #
    #*******************************#
    game['objects'] = []
    objects_append(game, OBJ_PLAYER, game['img/player'].get_width(), GAME_HEIGHT / 2)

    pygame.mixer.Sound.play(game['title_screen'],-1)
    # Infinite Loop of the Game
    while not game['quit']:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game['quit'] = True

        # Update of the pressed keys
        lastkeys = keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            game['quit'] = True

        # Animation Game + Menu
        selector(game, window, keys, lastkeys)
        process_keys(game, keys)
        background_draw(game, window)
        make_monsters(game)
        objects_animate(game)
        check_monsters_have_won(game)
        objects_draw(game, window)

        # Main Menu
        if game['actualMenu'] == 1:
            
            Surf = pygame.Surface((150,300))

            Title = game['mess_font'].render("R-Type", True ,(255,255,255))
            WR = game['mess_font'].render("Record : {0}".format(game['WR']), True ,(255,255,255))

            Start = game['mess_font'].render("Start", True ,(255,255,255))
            if game['select'] == 0:
                pygame.draw.rect(Surf, (255,255,255),(15,130,85,30),2)

            Settings = game['mess_font'].render("Settings", True ,(255,255,255))
            if game['select'] == 1:
                pygame.draw.rect(Surf, (255,255,255),(15,160,120,30),2)

            About = game['mess_font'].render("About", True ,(255,255,255))
            if game['select'] == 2:
                pygame.draw.rect(Surf, (255,255,255),(15,190,85,30),2)

            Exit = game['mess_font'].render("Exit", True ,(255,255,255))
            if game['select'] == 3:
                pygame.draw.rect(Surf, (255,255,255),(15,220,65,30),2)

            Surf.blit(Title,(30,20))
            Surf.blit(WR,(20,70))
            Surf.blit(Start,(20,120))
            Surf.blit(Settings,(20,150))
            Surf.blit(About,(20,180))
            Surf.blit(Exit,(20,210))

            rendu = pygame.Surface((200,300))
            rendu.blit(Surf,(rendu.get_width()//2 - Surf.get_width() //2 ,rendu.get_height()//2 - Surf.get_height() //2))
            pygame.draw.rect(rendu, (255,255,255),rendu.get_rect(),2)
            window.blit(rendu,(GAME_WIDTH//2 - rendu.get_width() //2 ,GAME_HEIGHT//2 - rendu.get_height() //2)) 

        # Settings Menu
        elif game['actualMenu'] == 2:
            Surf = pygame.Surface((300,300))

            Title = game['mess_font'].render("Settings", True ,(255,255,255))
            Resolution = game['mess_font'].render("Resolution : {0}x{1}".format(GAME_WIDTH,GAME_HEIGHT), True ,(255,255,255))
            if game['select'] == 0:
                pygame.draw.rect(Surf, (255,255,255),(15,130,270,30),2)

            if game['sound']:
                sound = "ON"
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                    game['fire_sound'] = pygame.mixer.Sound(CWD + '\\assets\\fire.ogg')
                    game["title_screen"] = pygame.mixer.Sound(CWD + '\\assets\\Title Screen.wav')
                    game["level1"] = pygame.mixer.Sound(CWD + '\\assets\\Level 1.wav')
                    game["ending"] = pygame.mixer.Sound(CWD + '\\assets\\Ending.wav')
                    pygame.mixer.Sound.play(game['title_screen'],-1)
            else :
                sound = "OFF"
                pygame.mixer.quit()

            Sound = game['mess_font'].render("Sound : {0}".format(sound), True ,(255,255,255))
            if game['select'] == 1:
                pygame.draw.rect(Surf, (255,255,255),(80,160,150,30),2)

            Difficulty = game['mess_font'].render("Difficulty : {0}".format(game['Difficulty']), True ,(255,255,255))
            if game['select'] == 2:
                pygame.draw.rect(Surf, (255,255,255),(40,190,215,30),2)

            Return = game['mess_font'].render("Return", True ,(255,255,255))
            if game['select'] == 3:
                pygame.draw.rect(Surf, (255,255,255),(90,220,110,30),2)

            Surf.blit(Title,(100,20))
            Surf.blit(Resolution,(20,120))
            Surf.blit(Sound,(90,150))
            Surf.blit(Difficulty,(80,180))
            Surf.blit(Return,(100,210))

            rendu = pygame.Surface((500,300))
            rendu.blit(Surf,(rendu.get_width()//2 - Surf.get_width() //2 ,rendu.get_height()//2 - Surf.get_height() //2))
            pygame.draw.rect(rendu, (255,255,255),rendu.get_rect(),2)
            window.blit(rendu,(GAME_WIDTH//2 - rendu.get_width() //2 ,GAME_HEIGHT//2 - rendu.get_height() //2)) 

        # About Menu
        elif game['actualMenu'] == 3:
            Surf = pygame.Surface((600,300))

            Title = game['mess_font'].render("About this game", True ,(255,255,255))
            Text0 = game['mess_font'].render("This little copy of the game R-Type", True ,(255,255,255))
            Text1 = game['mess_font'].render("has been created in 2020 by Clement Cardot", True ,(255,255,255))
            Text2 = game['mess_font'].render("at the ESEO, a french school of engineering", True ,(255,255,255))
            Return = game['mess_font'].render("Return", True ,(255,255,255))

            pygame.draw.rect(Surf, (255,255,255),(240,220,110,30),2)

            Surf.blit(Title,(180,20))
            Surf.blit(Text0,(50,70))
            Surf.blit(Text1,(30,100))
            Surf.blit(Text2,(30,130))
            Surf.blit(Return,(250,210))

            rendu = pygame.Surface((600,300))
            rendu.blit(Surf,(rendu.get_width()//2 - Surf.get_width() //2 ,rendu.get_height()//2 - Surf.get_height() //2))
            pygame.draw.rect(rendu, (255,255,255),rendu.get_rect(),2)
            window.blit(rendu,(GAME_WIDTH//2 - rendu.get_width() //2 ,GAME_HEIGHT//2 - rendu.get_height() //2)) 
            
        # Alert Gameover
        elif game['gameover']:
            
            if game["score"] > game["WR"]:
                game['WR'] = game["score"]
                WR = True
            
            if WR:
                text0 = game['mess_font'].render(("NEW RECORD !"), True ,(255,255,255))
                Surf0 = pygame.Surface((200,40))
                Surf0.blit(text0, (25,-5))
                pygame.draw.rect(Surf0, (255,0,0),Surf0.get_rect(),2)
                window.blit(Surf0, (GAME_WIDTH//2 - Surf0.get_width() //2 ,40))

            Score = game['mess_font'].render("Your score : {0}".format(game['score']), True ,(255,255,255))
            Retry = game['mess_font'].render("Want to retry ? Press the R key !", True ,(255,255,255))
            Menu = game['mess_font'].render("To go back to Menu, Press the Esc key !", True ,(255,255,255))

            f_rect = pygame.Rect(0,0, 525, 130)
            Surf = pygame.Surface((f_rect.width,f_rect.height))
            Surf.blit(Score, (150,8))
            Surf.blit(Retry, (40,40))
            Surf.blit(Menu, (20,70))
            pygame.draw.rect(Surf, (255,255,255),Surf.get_rect(),2)
            window.blit(Surf, (GAME_WIDTH//2 - Surf.get_width() //2 ,GAME_HEIGHT//2 - Surf.get_height() //2))

            if keys[pygame.K_r]:
                game['gameover'] = False
                game['play'] = True
                game['objects'] = []
                game['score'] = 0
                WR = False
                objects_append(game, OBJ_PLAYER, game['img\player'].get_width(), GAME_HEIGHT / 2)
                pygame.mixer.stop()
                pygame.mixer.Sound.play(game['level'][0],-1)

            if keys[pygame.K_ESCAPE]:
                game['gameover'] = False
                game['actualMenu'] = 1
                game['score'] = 0
                pygame.mixer.stop()
                pygame.mixer.Sound.play(game['title_screen'],-1)

        # Game Fonctions
        if game['play']:
            level(game)
            check_collisions(game)
            score_draw(game, window)
            if MONSTER_COUNT == -1:
                Boss_life(game, window)
        pygame.display.flip()
        pygame.time.wait(1000 // GAME_FPS)

        print('{0} objects displayed'.format(len(game['objects'])))
    pygame.mixer.quit()
    pygame.quit()