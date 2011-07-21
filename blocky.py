#!/usr/bin/env python
#------------------------------------------------------
# Blocky
#
# Created by Matt Titterington
# License: GPL
#
#------------------------------------------------------


try:
    """Attempt to import required modules"""
    import pygame
    import math
    import os
    import random
    from pygame.locals import K_w, K_a, K_s, K_d, K_ESCAPE, KEYDOWN, KEYUP
except ImportError:
    print 'Please ensure pygame is installed and try again'
    raise SystemExit

#functions used to load sounds and images (if any)
def load_image(name, colorkey=None):
    """Loads an image into memory"""
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    """Loads a sound file (.wav) in memory"""
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', fullname
        raise SystemExit, message
    return sound

class KeyTracker:
    """Keeps track of which keys are down and which aren't
    
    Functions:
    isDown(key): returns True if the specified key is down
    addKey(key, state=False): adds a new record to tell whether key is down or now
    setKey(key,state): sets the specified key to the specified state"""
    
    def __init__(self):
        self.keys = {}
        
        self.keys['w'] = False
        self.keys['a'] = False
        self.keys['s'] = False
        self.keys['d'] = False
    
    def isDown(self, key):
        if key in self.keys:
            return self.keys[key]
        else:
            return False
    
    def addKey(self,key,state=False):
        self.keys[key] = state
    
    def setKey(self,key,state):
        self.keys[key] = state
   
class DepthMeter:
    def __init__(self,background,screen,size,maxHeight=1000):
        self.screen = screen
        self.image = pygame.Surface([40,400])
        self.maxHeight = maxHeight

        
    def update(self,background,height=0,):
        self.image.fill(background)
        meter = pygame.Surface([10,400])
        marker = pygame.Surface([20,5])
        meter.fill([220,220,220])
        marker.fill([255,0,0])
        
        self.image.blit(meter,[15,0])
        relHeight = 398-((height/self.maxHeight)*398)
        self.image.blit(marker,[10,relHeight])
        
        self.screen.blit(self.image,[660,280])

class Player(pygame.sprite.Sprite):
    """A sprite for our player"""
    def __init__(self,colour,size,screen):
        pygame.sprite.Sprite.__init__(self)
        
        self.size = size
        self.screen = screen
        self.maxVelocity = 8
        
        self.image = pygame.Surface([50,50])
        self.image.fill(colour)
                
        self.rect = self.image.get_rect()
        self.rect.center = [size[0]/2,size[1]/2]
                
        ############Movement variables##########
        self.velocity = [0,0]
        self.acceleration = 0.5
        self.resistance = 0.5
        self.position = [-200,-200]
                
    def update(self,directions):
        #If a button is pressed, do not apply resistances
        if not directions == [0,0]:
            self.velocity[1] += (self.acceleration*directions[1])
            self.velocity[0] += (self.acceleration*directions[0])
            
            #Makes sure we cannot exceed the maximum velocity
            for i in xrange(2):
                if self.velocity[i]>self.maxVelocity:
                    self.velocity[i] = self.maxVelocity
                if self.velocity[i]<(self.maxVelocity*-1):
                    self.velocity[i] = (-1*self.maxVelocity)
        
        #Applies resistances
        if directions[0]==0:
            self._applyHorizontalRes()
        if directions[1]==0:
            self._applyVerticalRes()
            
        #Updates the position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.screen.blit(self.image,self.rect)
        
    def _applyHorizontalRes(self):
        """Applies the resistance variable on the horizontal plane"""
        if math.fabs(self.velocity[0]-self.resistance)<self.resistance:
                self.velocity[0]=0
        if self.velocity[0]>0:
                self.velocity[0] -= self.resistance
        elif self.velocity[0]<0:
                self.velocity[0] += self.resistance
        
    
    def _applyVerticalRes(self):
        """Applies the resistance variable on the vertical plane"""
        if math.fabs(self.velocity[1]-self.resistance)<self.resistance:
                self.velocity[1]=0
 
        if self.velocity[1]>0:
            self.velocity[1] -= self.resistance
        elif self.velocity[1]<0:
            self.velocity[1] += self.resistance
        
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self,actualPlayerPos,playerPos,spawnRadius):
        pygame.sprite.Sprite.__init__(self)
        
        self.actualPlayerPos = actualPlayerPos
        self.spawnRadius = spawnRadius
        
        #Set the basic sprite attributes
        self.image = pygame.Surface([20,20])
        self.image.fill([0,255,0])
        self.rect = self.image.get_rect()
        
        #Randomly finds the initial position
        self.position = self._findInitialPos(playerPos)
        #Moves image to that position
        self.rect.center = self.getScreenPos(playerPos)
        #Randomly sets the initial velocity
        self.velocity = [random.uniform(-1,1),random.uniform(-1,1)]
  
    def update(self,playerPos):
        self.position[0]+=self.velocity[0]
        self.position[1]+=self.velocity[1]
        
        self.rect.center = self.getScreenPos(playerPos)
        
        if self.distanceToObject(self.position,playerPos)>self.spawnRadius:
            self.kill()
   
    def getScreenPos(self,playerPos):
        screenPos = [0,0]
        relativePos = [0,0]
        
        for i in xrange(2):
            relativePos[i]=self.position[i]-playerPos[i]
        
        
        screenPos[0] = self.actualPlayerPos[0]+relativePos[0]
        screenPos[1] = self.actualPlayerPos[1]-relativePos[1]
        
        return screenPos
    
    def distanceToObject(self,selfPos,objectPos=[0,0]):
        squarex = math.pow(math.fabs(objectPos[0]-selfPos[0]),2)
        squarey = math.pow(math.fabs(objectPos[1]-selfPos[1]),2)
        distance = math.sqrt(squarex+squarey)
        return distance
    
    def _findInitialPos(self,playerPos):
        while True:
            initialPosX = random.uniform(playerPos[0]-self.spawnRadius,playerPos[0]+self.spawnRadius)
            initialPosY = random.uniform(playerPos[1]-self.spawnRadius,playerPos[1]+self.spawnRadius)
            initialPos = [initialPosX,initialPosY]
            if self._isValidSpawnPosition(initialPos,playerPos):
                return initialPos
    
    def _isValidSpawnPosition(self,selfPos,playerPos):
        minDist = math.sqrt((self.actualPlayerPos[0]*self.actualPlayerPos[0])+(self.actualPlayerPos[1]*self.actualPlayerPos[1]))
        if self.distanceToObject(selfPos,playerPos)>minDist:
            if self.distanceToObject(selfPos,playerPos)<self.spawnRadius:
                return True
        return False

def main():
    clock = pygame.time.Clock()
    pygame.init()
    #create and set basic variables
    size = [700,700]
    maxHeight = 100000
    backgroundColour = [135,206,250]
    actualPlayerPos = [size[0]/2,size[1]/2]
    numberOfEnemies = 200
    spawnRadius = 2*size[0] #Maximum distance the sprite can be from player
    
    
    #create and set the screen
    screen = pygame.display.set_mode(size)
    background = pygame.Surface(size)
    background.fill(backgroundColour)
    screen.blit(background,[0,0])
    
    
    
    
    #create the non-sprite objects
    depthMeter = DepthMeter(background,screen,size,maxHeight)
    player = Player([255,255,0],size,screen)
    keyTracker = KeyTracker()
    
    #create the enemies
    enemyGroup = pygame.sprite.RenderUpdates()
    for i in xrange(numberOfEnemies):
        enemyGroup.add(Enemy(actualPlayerPos,player.position,spawnRadius))

    
    
    while True:
        clock.tick(60)
            
        #########HANDLING KEY EVENTS##############    
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key==K_w:
                    keyTracker.setKey('w',True)
                if event.key==K_a:
                    keyTracker.setKey('a',True)
                if event.key == K_d:
                    keyTracker.setKey('d',True)
                if event.key == K_s:
                    keyTracker.setKey('s',True)
                if event.key == K_ESCAPE:
                    raise SystemExit
            if event.type == KEYUP:
                if event.key==K_w:
                    keyTracker.setKey('w',False)
                if event.key==K_a:
                    keyTracker.setKey('a',False)
                if event.key == K_d:
                    keyTracker.setKey('d',False)
                if event.key == K_s:
                    keyTracker.setKey('s',False)
        
        #######Sending the keypresses to the sprite#######
        directions = [0,0]
        if keyTracker.isDown('s'):
            directions[1] -= 1
        if keyTracker.isDown('w'):
            directions[1] += 1
        if keyTracker.isDown('d'):
            directions[0] += 1
        if keyTracker.isDown('a'):
            directions[0] -= 1
        
        
        #Update sprite objects
        enemyGroup.clear(screen,background)
        enemyGroup.update(player.position)
        enemylist = enemyGroup.draw(screen)
        #pygame.display.update(enemylist)
        
        #Update non-sprite objects
        depthMeter.update(backgroundColour,player.position[1])
        player.update(directions)    
        
        
        
        #Repopulate the dead sprites
        if len(enemyGroup)<numberOfEnemies:
            for i in xrange(numberOfEnemies-len(enemyGroup)):
                enemyGroup.add(Enemy(actualPlayerPos,player.position,spawnRadius))
        
        pygame.display.flip()

def titleScreen():
    """the start-up screen that asks you which difficulty to play"""
    
    pygame.init()
    running = 1
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 60)
    font2 = pygame.font.Font(None, 40)
    yellow = 255,255,0
    hum = 2, 81, 76


    screen = pygame.display.set_mode((700,700))
    screen.fill([135,206,250])

    ren = font.render("Welcome to Blocky!", 1, yellow)
    screen.blit(ren, (160,120))

    ren = font2.render("v0.0.1", 1, hum)
    screen.blit(ren, (300, 200))
    ren = font2.render("Press any key to continue.", 1, hum)
    screen.blit(ren, (140, 400))

    while running:
        clock.tick(55)
        pygame.display.flip()
        pygame.event.pump()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    raise SystemExit()
                else:
                    main()
                
                
if __name__=='__main__':
    titleScreen()

