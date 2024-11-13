import pygame as pg
import random
import os
import math
import copy
import numpy as np

#PERRIN: How to make an exe:
#1. Install pyinstaller
#1.5. If you haven't yet, run pyinstaller HD2RoguelikeGen/RoguelikeGen.py to create the necessary files
#2. Run the command: pyinstaller --onefile --noconsole --icon=icon.ico HD2RoguelikeGen/RoguelikeGen.py

# GEAR LISTS
PRIMARIES = [
    "Liberator", 
    "Liberator Penatrator", 
    "Liberator Concussive", 
    "Liberator Carbine",
    "Tenderizer",
    "Adjudicator",
    "Cookout",
    "Purifier",
    "Torcher",
    "Knight", 
    "Defender", 
    "Pummeler", 
    "Punisher", 
    "Slugger", 
    "Breaker", 
    "Breaker Incendiary", 
    "Breaker Spray & Pray", 
    "Diligence", 
    "Diligence Counter Sniper", 
    "Scythe", 
    "Sickle", 
    "Scorcher", 
    "Punisher Plasma", 
    "Blitzer", 
    "Dominator", 
    "Erupter",
    "Exploding Crossbow",
    "Reprimand",
    "Constitution",
    "Halt",
    ]

SECONDARIES = [
    "Crisper",
    "Dagger",
    "Peacemaker",
    "Redeemer", 
    "Grenade Pistol", 
    "Verdict",
    "Senator", 
    "Stim Pistol", 
    "Bushwhacker",
    "Loyalist",
    ]

GRENADES = [
    "Gas Grenade",
    "Throwing Knife",
    "High Explosive Grenade", 
    "Frag Grenade", 
    "Impact Grenade", 
    "Smoke Grenade", 
    "Incendiary Grenade", 
    "Stun Grenade", 
    "Thermite Grenade", 
    "Incendiary Impact"
    ]

STRATEGEMS = [
    "Eagle Strafing Run",
    "Eagle Airstrike",
    "Eagle Cluster Bomb",
    "Eagle Napalm Strike",
    "Eagle Smoke Strike",
    "Eagle 110MM Rocket Pods",
    "Eagle 500kg Bomb",
    "Orbital Precision Strike",
    "Orbital Airburst Strike",
    "Orbital 120MM HE Barrage",
    "Orbital 380MM HE Barrage",
    "Orbital Walking Barrage",
    "Orbital Laser",
    "Orbital Railcannon Strike",
    "Orbital Gatling Barrage",
    "Orbital Gas Strike",
    "Orbital EMS Strike",
    "Orbital Smoke Strike",
    "Orbital Napalm Strike",
    "Airburst Rocket Launcher",
    "Autocannon",
    "Expendable Anti-Tank",
    "Flamethrower",
    "Laser Cannon",
    "Stalwart",
    "Machine Gun",
    "Arc Thrower",
    "Grenade Launcher",
    "Anti-Material Rifle",
    "Railgun",
    "Recoilless Rifle",
    "Spear",
    "Sterilizer",
    "Quasar Cannon",
    "Heavy Machine Gun",
    "MLS-4X Commando",
    "Guard Dog Dog Breath",
    "Guard Dog Rover",
    "Guard Dog",
    "Jump Pack",
    "Supply Pack",
    "Shield Generator Pack",
    "Ballistic Shield Backpack",
    "Tesla Tower",
    "Mortar Sentry",
    "EMS Mortar Sentry",
    "Machine Gun Sentry",
    "Gatling Sentry",
    "Anti-Personnel Minefield",
    "Anti-Tank Mines",
    "Incendiary Mines",
    "Shield Generator Relay",
    "HMG Emplacement",
    "Autocannon Sentry",
    "Rocket Sentry",
    "Patriot Exosuit",
    "Emancipator Exosuit",
    ]

Build = [
    None, # Primary
    None, # Secondary
    None, # Grenade

    None, # Stratagem 1
    None, # Stratagem 2
    None, # Stratagem 3
    None, # Stratagem 4
]

SAVEGAME = pg.USEREVENT + 1
ENDGAME = pg.USEREVENT + 2

def main():
    # Generate chance lists, so that we can weight the random selection to favor items that aren't being selected as often
    imageBasePath = "HD2RoguelikeGen/HD2 Icons/"
    primaries = []
    primaryImages = []
    for i in range(len(PRIMARIES)):
        primaries.append(1)
        try:
            primaryImages.append(pg.image.load(imageBasePath + PRIMARIES[i] + ".png"))
        except:
            primaryImages.append(None)
    secondaries = []
    secondaryImages = []
    for i in range(len(SECONDARIES)):
        secondaries.append(1)
        try:
            secondaryImages.append(pg.image.load(imageBasePath + SECONDARIES[i] + ".png"))
        except:
            secondaryImages.append(None)
    grenades = []
    grenadeImages = []
    for i in range(len(GRENADES)):
        grenades.append(1)
        try:
            grenadeImages.append(pg.image.load(imageBasePath + GRENADES[i] + ".png"))
        except:
            grenadeImages.append(None)
    strategems = []
    strategemImages = []
    for i in range(len(STRATEGEMS)):
        strategems.append(1)
        try:
            strategemImages.append(pg.image.load(imageBasePath + STRATEGEMS[i] + ".png"))
        except:
            strategemImages.append(None)

    class Button:
        #To use the function args, you must pass a list of the arguments you want to pass to the function
        def __init__(self, image, pos, function = None, functions = [], FunctionArgs = [], heldFunctions = [], heldFunctionArgs = [], heldTimeLimit = 1):
            self.image = image
            if self.image != None and type(self.image) == str:
                self.image = pg.image.load(self.image)
                self.BASEIMAGE = self.image
                self.rect = self.image.get_rect()
                self.rect.topleft = pos
            elif self.image != None:
                self.BASEIMAGE = self.image
                self.rect = self.image.get_rect()
                self.rect.topleft = pos
            else:
                self.rect = pg.Rect(pos, (80, 80))

            self.hidden = False
            self.font = pg.font.Font(None, 36)
            self.functions = []
            if function != None:
                self.functions.append(function)
            self.destroyed = False
            for i in range(len(functions)):
                self.functions.append(functions[i])
            self.FunctionArgs = []
            for i in range(len(FunctionArgs)):
                self.FunctionArgs.append(FunctionArgs[i])

            self.held = False
            self.heldTime = 0
            self.heldTimeLimit = 60 * heldTimeLimit

            self.heldFunctions = []
            for i in range(len(heldFunctions)):
                self.heldFunctions.append(heldFunctions[i])
            self.heldFunctionArgs = []
            for i in range(len(heldFunctionArgs)):
                self.heldFunctionArgs.append(heldFunctionArgs[i])

            self.rotation = 0
            self.StoredRotation = 0
            self.scale = 1
            self.children = []
            self.toDestroy = []


        def destroy(self):
            failedToDestroy = False
            for child in self.children:
                if not child.destroy():
                    failedToDestroy = True
                    self.toDestroy.append(child)
                self.children.remove(child)
            for child in self.toDestroy:
                if not child.destroy():
                    failedToDestroy = True
                else:
                    self.toDestroy.remove(child)
            if failedToDestroy:
                self.destroyed = True
                return False
            self.destroyed = True
            return True

        def setImage(self, image):
            oldCenter = self.rect.center
            if image != None and type(image) == str:
                self.image = pg.image.load(image)
                self.BASEIMAGE = self.image
                self.rect = self.image.get_rect()
                self.rect.center = oldCenter
            elif image != None:
                self.image = image
                self.BASEIMAGE = image
                self.rect = self.image.get_rect()
                self.rect.center = oldCenter
            else:
                self.image = None
                self.BASEIMAGE = None
                self.rect = pg.Rect((0, 0), (80, 80))
                self.rect.center = oldCenter


        def addChild(self, child):
            child.parent = self
            self.children.append(child)
            



        def draw(self, screen):
            if not self.hidden and not self.destroyed: #if the object is destroyed, don't draw it, only draw its children, because we assume we're trying to clean them up
                if self.image == None:
                    pg.draw.rect(screen, (255, 255, 255), self.rect)
                    #Handle the rotation
                    if self.StoredRotation != self.rotation:
                        #Assume we rotate around the center of the image
                        oldCenter = self.rect.center
                        originalImage = self.BASEIMAGE
                        self.image = originalImage
                        self.image = pg.transform.rotate(self.image, self.rotation)
                        self.rect = self.image.get_rect()
                        self.rect.center = oldCenter
                        self.StoredRotation = self.rotation
                    if self.scale != 1:
                        oldCenter = self.rect.center
                        originalImage = self.BASEIMAGE
                        self.image = originalImage
                        self.image = pg.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
                        if self.StoredRotation != 0:
                            self.image = pg.transform.rotate(self.image, self.StoredRotation)
                        self.rect = self.image.get_rect()
                        self.rect.center = oldCenter
                else:
                    screen.blit(self.image, self.rect)
                    #Handle the rotation
                    if self.StoredRotation != self.rotation:
                        oldCenter = self.rect.center
                        originalImage = self.BASEIMAGE
                        self.image = originalImage
                        self.image = pg.transform.rotate(self.image, self.rotation)
                        self.rect = self.image.get_rect()
                        self.rect.center = oldCenter
                        self.StoredRotation = self.rotation
                    if self.scale != 1:
                        oldCenter = self.rect.center
                        originalImage = self.BASEIMAGE
                        self.image = originalImage
                        self.image = pg.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
                        if self.StoredRotation != 0:
                            self.image = pg.transform.rotate(self.image, self.StoredRotation)
                        self.rect = self.image.get_rect()
                        self.rect.center = oldCenter

            if self.children != []:
                for child in self.children:
                    child.draw(screen)
                for child in self.toDestroy:
                    if child.destroy():
                        self.toDestroy.remove(child)
                    else:
                        child.draw(screen)
				#TODO: Remove the above code, shouldn't be nessisary with the below code.
            
            if self.toDestroy != []:
                for child in self.toDestroy:
                    if child.destroy():
                        self.toDestroy.remove(child)
                    else:
                        child.draw(screen)

        def update(self):
            if not self.destroyed: #if not destroyed, update the button, else, try and clean up the children
                if self.held:
                    self.heldTime += 1
                if self.heldTime >= self.heldTimeLimit and self.held:
                    self.heldTime = 0
                    self.held = False
                    self.onClickAndHold()
            if self.children != []:
                for child in self.children:
                    if child.destroyed:
                        self.toDestroy.append(child)
                        self.children.remove(child)
                        continue
                    child.update()
            if self.toDestroy != []:
                for child in self.toDestroy:
                    if child.destroy():
                        self.toDestroy.remove(child)
                    else:
                        child.update() #Assume the child is trying to clean up its children or something


        def positionByTopMiddle(self, pos):
            self.rect.top = pos[1]
            self.rect.centerx = pos[0]

        def getTopMiddle(self):
            return (self.rect.centerx, self.rect.top)
        
        def positionByBottomMiddle(self, pos):
            self.rect.bottom = pos[1]
            self.rect.centerx = pos[0]

        def getBottomMiddle(self):
            return (self.rect.centerx, self.rect.bottom)
        
        def positionByCenter(self, pos):
            self.rect.center = pos

        def getCenter(self):
            return self.rect.center
        

        def handleInput(self, event):
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = pg.mouse.get_pos()
                    if self.isClicked(pos):
                        self.held = True
            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    pos = pg.mouse.get_pos()
                    if self.isClicked(pos) and self.heldTime < self.heldTimeLimit and self.held:
                        self.onClick()
                    elif self.isClicked(pos) and self.heldTime >= self.heldTimeLimit and self.held:
                        self.onClickAndHold()
                    self.held = False
                    self.heldTime = 0
            elif event.type == pg.MOUSEMOTION:
                pos = pg.mouse.get_pos()
                if self.held:
                    if not self.isClicked(pos):
                        self.held = False
                        self.heldTime = 0
                if self.isClicked(pos):
                    self.onHover()

        def isClicked(self, pos):
            if not self.hidden:
                return self.rect.collidepoint(pos)
            
        def onClickAndHold(self):
            for i in range(len(self.heldFunctions)):
                if self.heldFunctions[i] != None:
                    #Maybe this works, maybe it doesn't. I'm not sure if this will work with multiple functions
                    if len(self.heldFunctionArgs) > i:
                        #We know there is a list of parameters for this function in the list of function args
                        arguments = []
                        for j in range(len(self.heldFunctionArgs[i])):
                            arguments.append(self.heldFunctionArgs[i][j])
                        self.heldFunctions[i](*arguments)
                    else:
                        self.heldFunctions[i]()
            
        def onClick(self):
            for i in range(len(self.functions)):
                if self.functions[i] != None:
                    #Maybe this works, maybe it doesn't. I'm not sure if this will work with multiple functions
                    if len(self.FunctionArgs) > i:
                        #We know there is a list of parameters for this function in the list of function args
                        arguments = []
                        for j in range(len(self.FunctionArgs[i])):
                            arguments.append(self.FunctionArgs[i][j])
                        self.functions[i](*arguments)
                    else:
                        self.functions[i]()

        def getWidth(self):
            return self.rect.width
        
        def getHeight(self):
            return self.rect.height
        
        def hide(self):
            self.hidden = True

        def show(self):
            self.hidden = False

        def onHover(self):
            pass
            # self.image = self.font.render(self.text, True, (255, 0, 0))


    

    class Player():
        def __init__(self, playerName, playerNameImage, font):
            self.playerName = playerName
            self.loadout = [None, None, None, None, None, None, None]
            self.rolls = 0
            self.nameImage = playerNameImage #So I can position everything based on the name image
            self.gearNameImages = []
            self.font = font
            self.maxRolls = 12
            self.selectionButtons = []
            self.rollButton = None
            self.pendingChoice = False
            self.childObjects = []
            self.ToDestroy = [] #Objects we're trying to clean up

            self.rollButton = Button(None, (0, 0), function=self.roll)
            position = self.nameImage.getBottomMiddle()
            position = (position[0] - self.rollButton.getWidth(), position[1] + self.rollButton.getHeight() * 3)
            self.rollButton.positionByTopMiddle(position)
            self.rollButton.hide()
            self.rollButton.setImage(self.font.render("Roll", True, (255, 0, 0)))

            self.lockInButton = Button(None, (0, 0))
            position = self.rollButton.getCenter()
            position = (position[0] + self.rollButton.getWidth() * 2, position[1])
            self.lockInButton.positionByCenter(position)
            self.lockInButton.hide()
            self.lockInButton.setImage(self.font.render("Lock In", True, (255, 0, 0)))


            self.rollsTextImage = gameTextImage("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls), (0, 0), self.font)
            x = self.nameImage.getCenter()[0]
            y = self.rollButton.getTopMiddle()[1]
            position = (x, y)
            self.rollsTextImage.positionByBottomMiddle(position)

            #loadout Images
            self.loadoutImages = []
            for i in range(7):
                button = Button(None, (0, 0), heldFunctions=[self.TransitionToWildCard])
                button.heldFunctionArgs.append([button])
                self.loadoutImages.append(button)


            nameBottomMiddle = playerNameImage.getBottomMiddle()
            imageWidth = self.loadoutImages[0].getWidth()
            startingX = (nameBottomMiddle[0] - imageWidth * 4) + int(imageWidth) 
            y = nameBottomMiddle[1] + 10
            j = 0
            for i in range(7): #we skip one to give seperation between the weapons and strategems
                self.loadoutImages[j].positionByTopMiddle((startingX + imageWidth * i, y))
                j += 1

            for image in self.loadoutImages:
                image.hide()
        
        def replaceWithWildCard(self, button):
            buttonSlotIndex = self.loadoutImages.index(button)
            newButton = Button(None, (0, 0), function=self.replaceSlot, FunctionArgs=[self.loadoutImages.index(button), "Wild"])
            newButton.setImage(self.font.render("Wild", True, (255, 255, 0)))
            newButton.positionByCenter(button.getCenter())
            self.loadoutImages[self.loadoutImages.index(button)] = newButton
            self.childObjects.append(newButton)

            if not button.destroy():
                self.ToDestroy.append(button)

            self.loadout[buttonSlotIndex] = "Wild"
            pg.event.post(pg.event.Event(SAVEGAME))

        def setPrimary(self, primary):
            self.loadout[0] = primary
            self.loadoutImages[0].setImage(primaryImages[PRIMARIES.index(primary)])
            pg.event.post(pg.event.Event(SAVEGAME))

        def TransitionToWildCard(self, button):
            #We'll attach a partical effect to the 4 corners of the button, and have them follow the corners
            #We'll also have the button spin and shrink, and then disappear
            #Testing the theory with a single gen
            animManager = Animator(button)
            animManager.slerpRotationsTo(-50, 600)
            animManagerTwo = Animator(button)
            animManagerTwo.lerpScaleTo(0.01, 240)
            animManagerTwo.setOnAnimationEnd(self.replaceWithWildCard, [button])
            button.addChild(animManager) 
            button.addChild(animManagerTwo)

            particalArgs = [[0, 0], (255, 0, 0, 255), 3, [0, 0], 10, [1, 1], 60, True, 0.1, 30, 0.01]
            particalGen = particalGenerator([0, 0], BasicParticle, particalCountPerFrame=5, particalConstructorArgs=particalArgs)
            particalGen2 = particalGenerator([0, 0], BasicParticle, particalCountPerFrame=5, particalConstructorArgs=particalArgs)
            particalGen3 = particalGenerator([0, 0], BasicParticle, particalCountPerFrame=5, particalConstructorArgs=particalArgs)
            particalGen4 = particalGenerator([0, 0], BasicParticle, particalCountPerFrame=5, particalConstructorArgs=particalArgs)
            
            particalGen.pos[1] = button.getTopMiddle()[1]
            particalGen.pos[0] = button.getTopMiddle()[0]
            particalGen.pos[0] -= button.getWidth() / 2

            particalGen2.pos[1] = button.getBottomMiddle()[1]
            particalGen2.pos[0] = button.getBottomMiddle()[0]
            particalGen2.pos[0] -= button.getWidth() / 2

            particalGen3.pos[1] = button.getTopMiddle()[1]
            particalGen3.pos[0] = button.getTopMiddle()[0]
            particalGen3.pos[0] += button.getWidth() / 2

            particalGen4.pos[1] = button.getBottomMiddle()[1]
            particalGen4.pos[0] = button.getBottomMiddle()[0]
            particalGen4.pos[0] += button.getWidth() / 2

            particalGen.SetParent(button)
            particalGen2.SetParent(button)
            particalGen3.SetParent(button)
            particalGen4.SetParent(button)

            self.childObjects.append(particalGen)
            self.childObjects.append(particalGen2)
            self.childObjects.append(particalGen3)
            self.childObjects.append(particalGen4)


        def refresh(self):
            #needed for the loading, so we can refresh the images that we set manually
            for i in range(len(self.loadout)):
                if self.loadout[i] == "Wild":
                    self.loadoutImages[i].setImage(self.font.render("Wild", True, (255, 255, 0)))
                elif i == 0:
                    self.loadoutImages[i].setImage(primaryImages[PRIMARIES.index(self.loadout[i])])
                elif i == 1:
                    self.loadoutImages[i].setImage(secondaryImages[SECONDARIES.index(self.loadout[i])])
                elif i == 2:
                    self.loadoutImages[i].setImage(grenadeImages[GRENADES.index(self.loadout[i])])
                else:
                    self.loadoutImages[i].setImage(strategemImages[STRATEGEMS.index(self.loadout[i])])
            self.nameImage.image = self.font.render(self.playerName, True, (255, 255, 255))
            self.nameImage.show()
            self.rollsTextImage.image = self.font.render("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls), True, (255, 255, 255))


            
        def hide(self):
            for image in self.loadoutImages:
                image.hide()
            for image in self.gearNameImages:
                image.hide()
            for button in self.selectionButtons:
                button.hide()
            if self.rollButton != None:
                self.rollButton.hide()
            if self.lockInButton != None:
                self.lockInButton.hide()
            self.rollsTextImage.hide()

        def show(self):
            self.rollsTextImage.show()
            if self.loadout[0] is not None:
                for image in self.loadoutImages:
                    image.show()
                for image in self.gearNameImages:
                    image.show()
                for button in self.selectionButtons:
                    button.show()
                if self.rollButton != None and not self.pendingChoice:
                    self.rollButton.show()
                if self.lockInButton != None and not self.pendingChoice:
                    self.lockInButton.show()
            else:
                return


        def handleInput(self, event):
            for image in self.loadoutImages:
                image.handleInput(event)   
            for button in self.selectionButtons:
                button.handleInput(event)
            if self.rollButton != None:
                self.rollButton.handleInput(event)
            if self.lockInButton != None:
                self.lockInButton.handleInput(event)

        def update(self):
            for image in self.loadoutImages:
                image.update()
            for object in self.childObjects:
                object.update
            for object in self.ToDestroy:
                if object.destroy():
                    self.ToDestroy.remove(object)
                else:
                    object.update()

        def draw(self, screen):
            for image in self.loadoutImages:
                image.draw(screen)
            for image in self.gearNameImages:
                image.draw(screen)
            for button in self.selectionButtons:
                button.draw(screen)
            if self.rollButton != None:
                self.rollButton.draw(screen)
            self.rollsTextImage.draw(screen)
            if self.lockInButton != None:
                self.lockInButton.draw(screen)
            for object in self.childObjects:
                object.draw(screen)
            for object in self.ToDestroy:
                object.draw(screen)


        def onStart(self):
            for i in range(len(self.loadout)):
                if i == 0:
                    selection = random.choices(range(len(PRIMARIES)), primaries)[0]
                    #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                    primaries[selection] /= 1.5
                    for j in range(len(primaries)):
                        if j != selection:
                            primaries[j] *= 1.01
                            if primaries[j] > 10:
                                primaries[j] = 10
                    self.loadout[i] = PRIMARIES[selection]
                    self.loadoutImages[i].setImage(primaryImages[selection])
                elif i == 1:
                    selection = random.choices(range(len(SECONDARIES)), secondaries)[0]
                    #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                    secondaries[selection] /= 1.5
                    for j in range(len(secondaries)):
                        if j != selection:
                            secondaries[j] *= 1.1
                            if secondaries[j] > 10:
                                secondaries[j] = 10
                    self.loadout[i] = SECONDARIES[selection]
                    self.loadoutImages[i].setImage(secondaryImages[selection])
                elif i == 2:
                    selection = random.choices(range(len(GRENADES)), grenades)[0]
                    #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                    grenades[selection] /= 1.5
                    for j in range(len(grenades)):
                        if j != selection:
                            grenades[j] *= 1.01
                            if grenades[j] > 10:
                                grenades[j] = 10
                    self.loadout[i] = GRENADES[selection]
                    self.loadoutImages[i].setImage(grenadeImages[selection])
                else:
                    selection = random.choices(range(len(STRATEGEMS)), strategems)[0]
                    currentBuild = self.loadout[3:i]
                    while STRATEGEMS[selection] in currentBuild:
                        #if the strategem is already in the self.loadout, try again
                        selection = random.choices(range(len(STRATEGEMS)), strategems)[0]
                    #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                    strategems[selection] /= 1.5
                    for j in range(len(strategems)):
                        if j != selection:
                            strategems[j] *= 1.01
                            if strategems[j] > 10:
                                strategems[j] = 10
                    self.loadout[i] = STRATEGEMS[selection]
                    self.loadoutImages[i].setImage(strategemImages[selection])

            for image in self.loadoutImages:
                image.show()

            # #Create a roll Button
            # self.rollButton = Button(None, (0, 0), function=self.roll)
            # position = self.nameImage.getBottomMiddle()
            # position = (position[0], position[1] + self.rollButton.getHeight() * 3)
            # self.rollButton.positionByTopMiddle(position)
            self.rollButton.show()
            self.lockInButton.show()

            pg.event.post(pg.event.Event(SAVEGAME))


            # print("Player " + self.playerName + "'s Loadout:")
            # for i in range(len(self.loadout)):
            #     print(self.loadout[i])

        def replaceSlot(self, slot, item):
            if slot < 3:
                if item in PRIMARIES:
                    self.loadout[slot] = item
                    self.loadoutImages[slot].setImage(primaryImages[PRIMARIES.index(item)])
                elif item in SECONDARIES:
                    self.loadout[slot] = item
                    self.loadoutImages[slot].setImage(secondaryImages[SECONDARIES.index(item)])
                elif item in GRENADES:
                    self.loadout[slot] = item
                    self.loadoutImages[slot].setImage(grenadeImages[GRENADES.index(item)])
            else:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(strategemImages[STRATEGEMS.index(item)])


        def madeDecision(self):
            self.pendingChoice = False
            self.selectionButtons = []
            self.rollButton.show()
            self.lockInButton.show()

            if self.rolls == self.maxRolls:
                self.lockIn()
            else:
                pg.event.post(pg.event.Event(SAVEGAME))

        def roll(self):
            categoryChances = [1.3, 1.3, 1.3, 4] #Chance of getting a primary, secondary, grenade, or strategem. Strategems are weighted higher because theres 4 of them
            categorySelections = []
            for i in range(3):
                categorySelections.append(random.choices(range(4), categoryChances)[0])
                #If the category is a primary, secondary, or grenade, we can't have more than one of each
                if categorySelections[i] < 3:
                    while categorySelections[i] in categorySelections[:i]:
                        categorySelections[i] = random.choices(range(4), categoryChances)[0]
            #Roll the selections, store them in a list so the player can choose which one they want, or if they want all 3
            selections = []
            for i in range(3):
                if categorySelections[i] == 0:
                    selection = random.choices(range(len(PRIMARIES)), primaries)[0]
                    #ensure the selection isn't already in the build
                    while PRIMARIES[selection] in self.loadout:
                        selection = random.choices(range(len(PRIMARIES)), primaries)[0]
                    selections.append(PRIMARIES[selection])
                    #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                    primaries[selection] /= 1.5
                    for j in range(len(primaries)):
                        if j != selection:
                            primaries[j] *= 1.01
                            if primaries[j] > 10:
                                primaries[j] = 10
                elif categorySelections[i] == 1:
                    selection = random.choices(range(len(SECONDARIES)), secondaries)[0]
                    #ensure the selection isn't already in the build
                    while SECONDARIES[selection] in self.loadout:
                        selection = random.choices(range(len(SECONDARIES)), secondaries)[0]
                    selections.append(SECONDARIES[selection])
                    #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                    secondaries[selection] /= 1.5
                    for j in range(len(secondaries)):
                        if j != selection:
                            secondaries[j] *= 1.01
                            if secondaries[j] > 10:
                                secondaries[j] = 10
                elif categorySelections[i] == 2:
                    selection = random.choices(range(len(GRENADES)), grenades)[0]
                    #ensure the selection isn't already in the build
                    while GRENADES[selection] in self.loadout:
                        selection = random.choices(range(len(GRENADES)), grenades)[0]
                    selections.append(GRENADES[selection])
                    #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                    grenades[selection] /= 1.5
                    for j in range(len(grenades)):
                        if j != selection:
                            grenades[j] *= 1.01
                            if grenades[j] > 10:
                                grenades[j] = 10
                else:
                    selection = random.choices(range(len(STRATEGEMS)), strategems)[0]
                    #ensure the selection isn't already in the build
                    while STRATEGEMS[selection] in self.loadout or STRATEGEMS[selection] in selections:
                        selection = random.choices(range(len(STRATEGEMS)), strategems)[0]
                    selections.append(STRATEGEMS[selection])
                    #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                    strategems[selection] /= 1.5
                    for j in range(len(strategems)):
                        if j != selection:
                            strategems[j] *= 1.01
                            if strategems[j] > 10:
                                strategems[j] = 10
            #For each Stratagem, select a random slot to replace. The entry in the list is the index of the selection
            strategemSlots = [0, 0, 0, 0]
            #find out how many strategems where selected
            strategemCount = 0
            for i in range(3):
                if categorySelections[i] == 3:
                    strategemCount += 1
            #roll a random slot for each strategem
            for i in range(strategemCount):
                slot = random.randint(0, 3)
                #ensure the slot isn't already taken
                while strategemSlots[slot] != 0:
                    slot = random.randint(0, 3)
                #find the index in the selections list of the strategem to put in the slot
                selectionIndex = 0
                skips = i
                for j in range(len(selections)):
                    if selections[j] in STRATEGEMS:
                        if skips == 0:
                            selectionIndex = j
                            break
                        skips -= 1
                #put the selection in the slot
                strategemSlots[slot] = selectionIndex + 1 #So its not 0 indexed
            

            #We'll Create buttons under each of the slots we've chosen, so the player can select which one they want
            #We'll also create a button that lets them select all of them

            #Show the selections to the player, and let them choose which ones they want
            for i in range(len(selections)):
                slotNum = 0
                if i + 1 in strategemSlots:
                    slotNum = 3 + strategemSlots.index(i+1)
                else:
                    slotNum = categorySelections[i]
                button = Button(None, (0, 0), functions=[self.replaceSlot, self.madeDecision], FunctionArgs=[[slotNum, selections[i]]])
                if i + 1 in strategemSlots: #The index is in the strategems
                    x = self.loadoutImages[3 + strategemSlots.index(i+1)].getCenter()[0]
                    y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                    button.positionByTopMiddle((x, y))
                    button.image = strategemImages[STRATEGEMS.index(selections[i])]
                else:
                    x = self.loadoutImages[categorySelections[i]].getCenter()[0]
                    y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                    button.positionByTopMiddle((x, y))
                    if selections[i] in PRIMARIES:
                        button.image = primaryImages[PRIMARIES.index(selections[i])]
                    elif selections[i] in SECONDARIES:
                        button.image = secondaryImages[SECONDARIES.index(selections[i])]
                    elif selections[i] in GRENADES:
                        button.image = grenadeImages[GRENADES.index(selections[i])]
                button.show()
                self.selectionButtons.append(button)

            #Create a button that lets the player select all of the options
            slotNums = [0, 0, 0]
            for i in range(3):
                if i + 1 in strategemSlots:
                    slotNums[i] = 3 + strategemSlots.index(i+1)
                else:
                    slotNums[i] = categorySelections[i]
            button = Button(None, (0, 0), functions=[self.replaceSlot, self.replaceSlot, self.replaceSlot, self.madeDecision], FunctionArgs=[[slotNums[0], selections[0]], [slotNums[1], selections[1]], [slotNums[2], selections[2]]])
            middleOfSlot3 = self.loadoutImages[2].getBottomMiddle()
            middleOfSlot3 = (middleOfSlot3[0] + button.getWidth(), middleOfSlot3[1])
            button.positionByTopMiddle(middleOfSlot3)
            button.setImage(self.font.render("All", True, (255, 0, 0)))
            button.show()
            self.selectionButtons.append(button)

            self.rolls += 1
            self.rollsTextImage.updateText("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls))
            self.rollsTextImage.show()

            self.rollButton.hide()
            self.lockInButton.hide()

        def lockIn(self):
            self.lockInButton = None
            self.rollButton = None
            pg.event.post(pg.event.Event(SAVEGAME))

    class TextBox():
        def __init__(self, x, y, width, height, text, color, textColor, font):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
            self.color = color
            self.textColor = textColor
            self.font = font
            self.focused = True
            self.hidden = False
            self.exitFunction = None
            self.exitFunctionArgs = []
            self.destroyed = False
            self.timer = 0
            self.timeToHoldKey = 45
            self.keyHeld = False
            self.keyCurrentlyHeld = None
            self.hasBeenEdited = False
            self.cursorBlinkTime = 60
            self.cursorBlinkTimer = 0
            self.cursorVisible = True
            self.cursor = "|"
            self.text += self.cursor


        def destroy(self):
            self.destroyed = True
        
        def draw(self, screen):
            pg.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            #We have to render the test as though the cursor is always there, to stop it from moving back and forth
            #text = self.font.render(self.text, True, self.textColor)
            text = self.font.render(self.text, True, self.textColor)
            cursor = self.font.render(self.cursor, True, self.textColor)
            textRect = text.get_rect()
            cursorRect = cursor.get_rect()
            
            #if the cursor is hidden, we add the width of the cursor to the text rect
            if not self.cursorVisible:
                textRect.width += cursorRect.width
            textRect.center = (self.x + self.width / 2, self.y + self.height / 2)
            screen.blit(text, textRect)

        def isClicked(self, pos):
            return pos[0] >= self.x and pos[0] <= self.x + self.width and pos[1] >= self.y and pos[1] <= self.y + self.height
        
        def onClick(self):
            self.focused = True

        def update(self):
            if self.keyHeld:
                self.timer += 1
                self.cursorBlinkTimer = 0
                self.cursorVisible = True
                if self.timer >= self.timeToHoldKey:
                    if self.keyCurrentlyHeld == pg.K_BACKSPACE:
                        self.text = self.text[:-1] #Remove the cursor
                        self.text = self.text[:-1] #Remove the last character
                        self.text += "|" #Add the cursor
                    else: #holding a letter key
                        self.text = self.text[:-1] #Remove the cursor
                        self.text += self.keyCurrentlyHeld
                        self.text += "|" #Add the cursor

            self.cursorBlinkTimer += 1
            if self.cursorBlinkTimer >= self.cursorBlinkTime:
                self.cursorBlinkTimer = 0
                self.cursorVisible = not self.cursorVisible
                if self.cursorVisible:
                    self.text += "|" #Add the cursor
                else:
                    self.text = self.text[:-1]

        def RemoveCursor(self):
            self.cursorVisible = False



        def handleInput(self, event):
            if event.type == pg.KEYDOWN:
                #if the cursor is visible, remove it
                if self.cursorVisible:
                    self.text = self.text[:-1]

                #handle the key press
                if event.key == pg.K_BACKSPACE:
                    if not self.hasBeenEdited:
                        self.hasBeenEdited = True
                        self.text = ""
                    self.keyCurrentlyHeld = pg.K_BACKSPACE
                    self.timer = 0
                    self.keyHeld = True
                    self.text = self.text[:-1]
                elif event.key == pg.K_RETURN or event.key == pg.K_DELETE:
                    if self.exitFunction != None:
                        if self.exitFunctionArgs != []:
                            self.exitFunction(*self.exitFunctionArgs)
                        else:
                            self.exitFunction()
                else:
                    if not self.hasBeenEdited:
                        self.hasBeenEdited = True
                        self.text = "" 
                    self.text += event.unicode
                    self.keyCurrentlyHeld = event.unicode
                    self.timer = 0
                    self.keyHeld = True

                #Reset the cursor blink timer
                self.cursorBlinkTimer = 0
                self.cursorVisible = True
                self.text += "|"

            elif event.type == pg.KEYUP: #If the key is released, stop holding it
                self.keyHeld = False
                self.keyCurrentlyHeld = None

                #if the mouse is clicked outside the text box, call the exit function
            #Is causing issues
            # elif event.type == pg.MOUSEBUTTONDOWN:
            #     if not self.isClicked(pg.mouse.get_pos()):
            #         if self.exitFunction != None:
            #             self.exitFunction()

        #A function to call when the player presses enter or escape, or clicks outside the text box
        def SetExitFunction(self, function, exitFuncitonArgs = []):
            self.exitFunction = function
            self.exitFunctionArgs = exitFuncitonArgs

        def hide(self):
            self.hidden = True

        def show(self):
            self.hidden = False

    class Animator():
        #For very low level animations, like lerping to a position
        def __init__(self, parent):
            self.parent = parent
            self.animations = []
            #Tuples, first value is the time remaining, second value is the total time
            self.times = []
            self.destroyed = False
            #Fairly certain this wont work for multiple animations, but I'm not sure
            self.index = 0
            self.done = True
            self.onAnimationEnd = None
            self.animationEndArgs = []

        def destroy(self):
            self.destroyed = True
            return True

        def lerpScaleTo(self, scale, time):
            self.animations.append([self.lerpScale, [scale, self.index]])
            self.times.append((time, time))

        def lerpScale(self, scale, timeIndex):
            start = self.parent.scale
            diff = scale - start
            step = diff / self.times[timeIndex][0]
            start += step
            self.parent.scale = start
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1

        def lerpToSize(self, size, time):
            self.animations.append([self.lerpSize, [size, self.index]])
            self.times.append((time, time))

        def lerpSize(self, size, timeIndex):
            start = self.parent.rect.size
            x = start[0]
            y = start[1]
            xDiff = size[0] - x
            yDiff = size[1] - y
            xStep = xDiff / self.times[timeIndex][0]
            yStep = yDiff / self.times[timeIndex][0]
            x += xStep
            y += yStep
            self.parent.rect.size = (x, y)
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1

        def slerpRotateTo(self, angle, time):
            self.animations.append([self.slerpRotate, [angle, self.index]])
            self.times.append((time, time))

        def slerpRotate(self, angle, timeIndex):
            startingRot = 0

            # Get the current rotation of the object
            currentRot = self.parent.rotation

            # Calculate the total distance to rotate
            startRot = currentRot
            distance = angle - startRot

            # Get the remaining frames for this movement from the times list
            frames_remaining = self.times[timeIndex][0]

            # Get the total frames (initially set when the movement starts)
            total_frames = self.times[timeIndex][1]

            # Calculate the fraction of frames remaining (from 1 to 0 as time passes)
            time_fraction = 1 - (frames_remaining / total_frames) if total_frames > 0 else 1
            # Clamp the time fraction to be within [0, 1]
            time_fraction = max(0, min(time_fraction, 1))

            eased_fraction = time_fraction ** 4

            # Use a sine wave to modulate the movement
            # The sine wave will range from 0 to 1, so adjust it to make smooth movement
            progress = np.sin(eased_fraction * np.pi / 2)   # np.pi ensures smooth transition (0 -> 1 and back to 0)

            # Distance with progress applied
            distance = distance * progress

            # Calculate the new rotation
            newRot = startRot + distance

            # Set the new rotation of the object
            self.parent.rotation = newRot
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1


        #Rotates the parent x times over the course of time
        def slerpRotationsTo(self, rotations, time):
            self.animations.append([self.slerpRotate, [rotations * 360, self.index]])
            self.times.append((time, time))

        def slerpRotations(self, rotations, timeIndex):
            startingRot = 0 #assume a default rotation of 0
            
            #Rotates the parent x times over the course of time
            #Rotations is the number of rotations to make
            #time is the time to make the rotations

            # Get the current rotation of the object
            currentRot = self.parent.rotation

            # Calculate the total distance to rotate
            startRot = currentRot
            distance = rotations * 360

            # Get the remaining frames for this movement from the times list
            frames_remaining = self.times[timeIndex][0]

            # Get the total frames (initially set when the movement starts)
            total_frames = self.times[timeIndex][1]

            # Calculate the fraction of frames remaining (from 1 to 0 as time passes)
            time_fraction = 1 - (frames_remaining / total_frames) if total_frames > 0 else 1
            # Clamp the time fraction to be within [0, 1]
            time_fraction = max(0, min(time_fraction, 1))

            eased_fraction = time_fraction ** 1

            # Use a sine wave to modulate the movement
            # The sine wave will range from 0 to 1, so adjust it to make smooth movement
            progress = np.sin(eased_fraction * np.pi / 2)   # np.pi ensures smooth transition (0 -> 1 and back to 0)

            # Distance with progress applied
            distance = distance * progress

            # Calculate the new rotation
            newRot = startRot + distance

            # Set the new rotation of the object
            self.parent.rotation = newRot
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1



        def lerpTo(self, pos, time):
            self.animations.append([self.lerp, [pos, self.index]])
            self.times.append((time, time))

        def lerp(self, pos, timeIndex):
            start = self.parent.getCenter()
            x = start[0]
            y = start[1]
            xDiff = pos[0] - x
            yDiff = pos[1] - y
            xStep = xDiff / self.times[timeIndex][0]
            yStep = yDiff / self.times[timeIndex][0]
            x += xStep
            y += yStep
            self.parent.positionByCenter((x, y))
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1

        def sinTo(self, pos, time):
            self.animations.append([self.sin, [pos, self.index]])
            self.times.append((time, time))

        def sin(self, pos, timeIndex):
            # Get the current position of the object
            current_pos = self.parent.getCenter()

            # Calculate the total distance to move
            start_pos = current_pos
            distance = (pos[0] - start_pos[0], pos[1] - start_pos[1])

             # Get the remaining frames for this movement from the times list
            frames_remaining = self.times[timeIndex][0]

            # Get the total frames (initially set when the movement starts)
            total_frames = self.times[timeIndex][1]

            # Calculate the fraction of frames remaining (from 1 to 0 as time passes)
            time_fraction = 1 - (frames_remaining / total_frames) if total_frames > 0 else 1
            # Clamp the time fraction to be within [0, 1]
            time_fraction = max(0, min(time_fraction, 1))

            eased_fraction = time_fraction ** 4
            # Use a sine wave to modulate the movement
            # The sine wave will range from 0 to 1, so adjust it to make smooth movement
            progress = np.sin(eased_fraction * np.pi / 2)   # np.pi ensures smooth transition (0 -> 1 and back to 0)

            # Distance with progress applied
            distance = (distance[0] * progress, distance[1] * progress)

            # Calculate the new position
            new_pos = (start_pos[0] + distance[0], start_pos[1] + distance[1])

            # Set the new position of the object
            self.parent.positionByCenter(new_pos)
            self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
            if self.times[timeIndex][0] <= 0:
                self.animations.remove(self.animations[timeIndex])
                self.times.remove(self.times[timeIndex])
                self.index -= 1

        def update(self):
            for animation in self.animations:
                animation[0](*animation[1])

            if len(self.animations) == 0:
                if self.onAnimationEnd != None:
                    self.onAnimationEnd(*self.animationEndArgs)
                else:
                    self.destroyed = True



        def setOnAnimationEnd(self, function, args = []):
            self.onAnimationEnd = function
            self.animationEndArgs = args

        def draw(self, screen):
            pass

        def handleInput(self, event):
            pass




    class particalGenerator():
        def __init__(self, pos, particalClass, particalCountPerFrame = 10, particalConstructorArgs = []):
            self.pos = pos
            self.partical = particalClass
            self.particalCountPerFrame = particalCountPerFrame
            self.particalConstructorArgs = particalConstructorArgs
            self.particals = []
            self.destroyed = False
            self.parent = None
            self.parentPos = [0, 0]
            self.parentOffset = [0, 0] #The offset from the parent's center, so we can position the partical generator relative to the parent
            self.parentRotation = 0 #The rotation of the parent, so we can rotate the partical generator with the parent
            self.parentScale = 1 #The scale of the parent, so we can scale the partical generator with the parent

        def update(self):
            if not self.destroyed:
                for i in range(self.particalCountPerFrame):
                    if random.random() < 0.75:
                        continue
                    size = random.randint(int(self.particalConstructorArgs[2] / 1.5), int(self.particalConstructorArgs[2] * 1.5))
                    color = [random.randint(200, 255), random.randint(0, 200), 0, random.randint(100, 255)]
                    maxSpeed = self.particalConstructorArgs[4] / size
                    speed = [random.uniform(-maxSpeed / 2, maxSpeed / 2), random.uniform(-maxSpeed / 2, maxSpeed / 2)]
                    #pos, color, size, speed, maxSpeed, direction, life, hasGravity = False, gravity = 0.1, fadeOutTime = 0, drag = 0.1
                    self.particals.append(self.partical([self.pos[0], self.pos[1]], color, size, speed, maxSpeed, self.particalConstructorArgs[5], self.particalConstructorArgs[6], self.particalConstructorArgs[7], self.particalConstructorArgs[8], self.particalConstructorArgs[9], self.particalConstructorArgs[10]))


            for partical in self.particals:
                partical.update()
                if partical.destroyed:
                    self.particals.remove(partical)

            if self.parent != None:
                #Update the position based on the parent's position, rotation, and scale
                self.pos = [self.parentPos[0] + self.parentOffset[0], self.parentPos[1] + self.parentOffset[1]]
                self.parentRotation = self.parent.rotation
                self.parentScale = self.parent.scale
                self.pos = self.rotatePoint(self.pos, self.parentPos, self.parentRotation)
                self.pos = self.scalePoint(self.pos, self.parentPos, self.parentScale)

        def SetParent(self, parent):
            self.parent = parent
            if self.parent != None:
                self.parentPos = parent.getCenter()
                self.parentOffset = [self.pos[0] - self.parentPos[0], self.pos[1] - self.parentPos[1]]
                self.parentRotation = parent.rotation
                self.parentScale = parent.scale
                self.parent.children.append(self)


        def rotatePoint(self, point, center, angle):
            angle = math.radians(-angle)
            x = point[0] - center[0]
            y = point[1] - center[1]
            x1 = x * math.cos(angle) - y * math.sin(angle)
            y1 = x * math.sin(angle) + y * math.cos(angle)
            return [x1 + center[0], y1 + center[1]]
        
        #Adjusts the point based on the center of the parent and the new scale
        def scalePoint(self, point, center, scale):
            x = point[0] - center[0]
            y = point[1] - center[1]
            x1 = x * scale
            y1 = y * scale
            return [x1 + center[0], y1 + center[1]]

        def draw(self, screen):
            for partical in self.particals:
                partical.draw(screen)

        def handleInput(self, event):
            for partical in self.particals:
                partical.handleInput(event)

        def getCenter(self):
            return self.pos
        
        def destroy(self):
            self.destroyed = True
            if self.particals != []:
                return False
            return True

        def positionByCenter(self, pos):
            self.pos = pos



    #A particle will have an image, and will be a random transparency and size
    class BasicParticle():
        def __init__(self, pos, color, size, speed, maxSpeed, direction, life, hasGravity = False, gravity = 0.1, fadeOutTime = 0, drag = 0.1):
            self.pos = pos
            self.color = color
            self.size = size
            self.speed = speed
            self.maxSpeed = maxSpeed
            self.direction = direction
            self.life = life
            self.destroyed = False
            self.hasGravity = hasGravity
            self.gravity = gravity
            self.fadeOutTime = fadeOutTime
            self.drag = drag
            self.momentum = [self.speed[0], self.speed[1]]
            self.acceleration = 30 #acceleration

        def destroy(self):
            self.destroyed = True

        def fadeOut(self):
            fadeOutRate = 255 / self.fadeOutTime
            self.color = (self.color[0], self.color[1], self.color[2], self.color[3] - fadeOutRate)
            self.fadeOutTime -= 1
            if self.color[3] <= 0:
                self.color = (self.color[0], self.color[1], self.color[2], 0)

        def update(self):
            if self.destroyed:
                return
            self.life -= 1
            if self.life <= 0 and self.fadeOutTime == 0:
                self.destroy()
            else:
                if self.life <= 0 and self.fadeOutTime > 0:
                    self.fadeOut()
                if self.hasGravity:
                    self.momentum[1] += self.gravity

                #cap the speed
                momentumMagnitude = math.sqrt(self.momentum[0] ** 2 + self.momentum[1] ** 2)
                if momentumMagnitude > self.maxSpeed:
                    self.momentum[0] = self.momentum[0] / momentumMagnitude * self.maxSpeed
                    self.momentum[1] = self.momentum[1] / momentumMagnitude * self.maxSpeed

                #apply drag
                self.momentum[0] -= self.momentum[0] * self.drag
                self.momentum[1] -= self.momentum[1] * self.drag

                #move the enemy
                self.pos[0] += self.momentum[0]
                self.pos[1] += self.momentum[1]

                


        def draw(self, screen):
            if self.destroyed:
                return
            #transparency
            s = pg.Surface((self.size * 2, self.size * 2), pg.SRCALPHA)
            pg.draw.circle(s, (self.color[0], self.color[1], self.color[2], self.color[3]), (self.size, self.size), self.size)
            screen.blit(s, (int(self.pos[0] - self.size), int(self.pos[1] - self.size)))

        def handleInput(self, event):
            pass

    class gameTextImage():
        def __init__(self, text, pos, font, width = 0, height = 0):
            self.text = text
            self.font = font
            self.image = self.font.render(self.text, True, (255, 255, 255))
            if width == 0 and height == 0:
                self.rect = self.image.get_rect()
            else:
                if height == 0:
                    aspectRatio = self.image.get_width() / self.image.get_height()
                    self.rect = pg.Rect(pos, (width, int(width / aspectRatio)))

                else:
                    self.rect = pg.Rect(pos, (width, height))
            #Resize the image to fit the rect
            self.image = pg.transform.scale(self.image, (self.rect.width, self.rect.height))
            
            self.rect.topleft = pos
            self.hidden = False
            self.destroyed = False


        def destroy(self):
            self.destroyed = True

        def positionByTopMiddle(self, pos):
            self.rect.top = pos[1]
            self.rect.centerx = pos[0]

        def getTopMiddle(self):
            return (self.rect.centerx, self.rect.top)
        
        def positionByBottomMiddle(self, pos):
            self.rect.bottom = pos[1]
            self.rect.centerx = pos[0]

        def getBottomMiddle(self):
            return (self.rect.centerx, self.rect.bottom)
        
        def positionByCenter(self, pos):
            self.rect.center = pos

        def getCenter(self):
            return self.rect.center
        
        def getHeight(self):
            return self.rect.height
        
        def getWidth(self):
            return self.rect.width
        
        def draw(self, screen):
            if not self.hidden:
                screen.blit(self.image, self.rect)

        def updateText(self, text):
            self.text = text
            self.image = self.font.render(self.text, True, (255, 255, 255))
            self.image = pg.transform.scale(self.image, (self.rect.width, self.rect.height))

        def update(self):
            pass

        def handleInput(self, event):
            pass

        def hide(self):
            self.hidden = True

        def show(self):
            self.hidden = False
    
    class Game:
        def __init__(self):
            self.running = True
            self.clock = pg.time.Clock()
            self.font = pg.font.Font("Hacked-KerX.ttf", 36)
            self.screen = pg.display.set_mode((1280, 720))
            pg.display.set_caption("Helldivers Gear Generator")
            self.MaxRolls = 15
            self.numRolls = 0
            self.gameObjects = []
            self.addPlayerButtons = [] #So we can remove them when we're done
            self.numPlayers = 0
            self.players = []
            self.autoSave = True
            #self.startGame()

        def loadGame(self):
            try:
                file = open("save.dat", "r")
            except:
                self.startGame()
                self.run()
                return
            data = file.read()
            file.close()
            lines = data.split("\n")
            lineNum = 0
            numPlayers = 0
            while lineNum < len(lines):
                playerName = lines[lineNum]
                if playerName == "!None#" or playerName == "" or playerName == "\n":
                    lineNum = 999
                    continue
                numPlayers += 1
                playerNameImage = Button(self.font.render(playerName, True, (255, 255, 255)), (0, 0), functions=[self.changeName], FunctionArgs=[[numPlayers]])
                self.gameObjects.append(playerNameImage)
                if lineNum == 0:
                    playerNameImage.positionByTopMiddle((320, 0))
                if lineNum == 11:
                    playerNameImage.positionByTopMiddle((960, 0))
                if lineNum == 22:
                    playerNameImage.positionByTopMiddle((320, 360))
                if lineNum == 33:
                    playerNameImage.positionByTopMiddle((960, 360))
                player = Player(playerName, playerNameImage, self.font)
                player.loadoutImages[0].functions = [self.viewPrimaries]
                player.loadoutImages[0].FunctionArgs = [[numPlayers]]
                player.loadout = [lines[lineNum + 1], lines[lineNum + 2], lines[lineNum + 3], lines[lineNum + 4], lines[lineNum + 5], lines[lineNum + 6], lines[lineNum + 7]]
                player.rolls = int(lines[lineNum + 8])
                #player has locked in
                if lines[lineNum + 9] == "True":
                    player.rollButton = None
                    player.lockInButton = None
                else:
                    player.lockInButton.functions = [self.openConfirmBox]
                    player.lockInButton.FunctionArgs = [[numPlayers]]

                player.show()
                player.refresh()
                self.players.append(player)
                lineNum += 11 #Skip a blank line
            self.numPlayers = numPlayers

            if numPlayers < 1:
                self.startGame()
                self.run()
                return
            if numPlayers < 2:
                addPlayerButton2 = Button(None, (960, 180), functions=[self.addPlayer])
                addPlayerButton2.positionByTopMiddle((960, 180))
                addPlayerButton2.setImage(self.font.render("Add Player", True, (255, 0, 0)))
                self.gameObjects.append(addPlayerButton2)
                self.addPlayerButtons.append(addPlayerButton2)
            if numPlayers < 3:
                addPlayerButton3 = Button(None, (320, 540), functions=[self.addPlayer])
                addPlayerButton3.positionByTopMiddle((320, 540))
                addPlayerButton3.setImage(self.font.render("Add Player", True, (255, 0, 0)))
                self.gameObjects.append(addPlayerButton3)
                self.addPlayerButtons.append(addPlayerButton3)
            if numPlayers < 4:
                addPlayerButton4 = Button(None, (960, 540), functions=[self.addPlayer])
                addPlayerButton4.positionByTopMiddle((960, 540))
                addPlayerButton4.setImage(self.font.render("Add Player", True, (255, 0, 0)))
                self.gameObjects.append(addPlayerButton4)
                self.addPlayerButtons.append(addPlayerButton4)
            self.run()
        
        def saveGame(self):
            file = open("save.dat", "w")
            for player in self.players:
                if player.loadout[0] == None:
                    continue
                file.write(player.playerName + "\n")
                for i in range(len(player.loadout)):
                    file.write(player.loadout[i] + "\n")
                file.write(str(player.rolls) + "\n")
                if player.lockInButton == None:
                    file.write("True\n")
                else:
                    file.write("False\n")
                file.write("\n") #Blank line to seperate players, for readability
            for i in range(4 - len(self.players)):
                file.write("!None#\n")
            file.close()

        def run(self):
            while self.running:
                self.events()
                self.update()
                self.draw()

        def events(self):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == SAVEGAME:
                    self.saveGame()
                for object in self.gameObjects:
                    object.handleInput(event)
                for player in self.players:
                    player.handleInput(event)

        def update(self):

            for object in self.gameObjects:
                if object.destroyed:
                    self.gameObjects.remove(object)
                object.update()
            for player in self.players:
                player.update()
                       
        def startGame(self):
            #split the screen into 4 equal parts, and have 1 button in each part
            addPlayerButton1 = Button(None, (320, 180), functions=[self.addPlayer])
            addPlayerButton2 = Button(None, (960, 180), functions=[self.addPlayer])
            addPlayerButton3 = Button(None, (320, 540), functions=[self.addPlayer])
            addPlayerButton4 = Button(None, (960, 540), functions=[self.addPlayer])

            addPlayerButton1.positionByTopMiddle((320, 180))
            addPlayerButton2.positionByTopMiddle((960, 180))
            addPlayerButton3.positionByTopMiddle((320, 540))
            addPlayerButton4.positionByTopMiddle((960, 540))

            addPlayerButton1.setImage(self.font.render("Add Player", True, (255, 0, 0)))
            addPlayerButton2.setImage(self.font.render("Add Player", True, (255, 0, 0)))
            addPlayerButton3.setImage(self.font.render("Add Player", True, (255, 0, 0)))
            addPlayerButton4.setImage(self.font.render("Add Player", True, (255, 0, 0)))

            self.gameObjects.append(addPlayerButton1)
            self.gameObjects.append(addPlayerButton2)
            self.gameObjects.append(addPlayerButton3)
            self.gameObjects.append(addPlayerButton4)

            

            for i in range(4):
                self.addPlayerButtons.append(self.gameObjects[i])

        def addPlayer(self):
            #hide everything
            for object in self.gameObjects:
                object.hide()
            for player in self.players:
                player.hide()
            #Add a text box for the player to enter their name
            center = (640, 360)
            boxSize = (400, 200)
            self.gameObjects.append(TextBox(int(center[0] - boxSize[0] * 0.5), int(center[1] - boxSize[1] * 0.5), 400, 200, "Enter your name", (255, 255, 255), (0, 0, 0), self.font))
            self.gameObjects[-1].SetExitFunction(self.returnFromTextBox)

        def changeName(self, playerNum):
            #opens a text box for the player to change their name
            #hide everything
            for object in self.gameObjects:
                object.hide()
            for player in self.players:
                player.hide()
            #Add a text box for the player to enter their name
            center = (640, 360)
            boxSize = (400, 200)
            self.gameObjects.append(TextBox(int(center[0] - boxSize[0] * 0.5), int(center[1] - boxSize[1] * 0.5), 400, 200, self.players[playerNum - 1].playerName, (255, 255, 255), (0, 0, 0), self.font))
            self.gameObjects[-1].SetExitFunction(self.returnFromNameChange, [playerNum])


        def checkForEndGame(self):
            for player in self.players:
                if player.lockInButton != None:
                    return
            
            #Create an end game button
            endGameButton = Button(None, (0, 0), functions=[self.endGame])
            endGameButton.positionByTopMiddle((640, 360))
            endGameButton.setImage(self.font.render("End Game", True, (255, 0, 0)))
            self.gameObjects.append(endGameButton)

        def endGame(self):
            #delete the save file
            os.remove("save.dat")
            pg.event.post(pg.event.Event(pg.QUIT))
        
        def openConfirmBox(self, playerNum):
            #Confirms if the player wants to lock in
            #hide everything
            for object in self.gameObjects:
                object.hide()
            for player in self.players:
                player.hide()

            #ARE YOU SURE YOU WANT TO LOCK IN? text
            textImage = gameTextImage("Are you sure you want to lock in?", (640, 180), self.font)
            textImage.positionByTopMiddle((640, 180))
            self.gameObjects.append(textImage)
            self.gameObjects[-1].show()

            #Yes button
            yesButton = Button(None, (0, 0), functions=[self.players[playerNum - 1].lockIn, self.showAll, self.checkForEndGame])
            position = textImage.getBottomMiddle()
            position = (position[0] - yesButton.getWidth(), position[1] + 10)
            yesButton.positionByTopMiddle(position)
            self.gameObjects.append(yesButton)
            self.gameObjects[-1].show()

            #No button
            noButton = Button(None, (0, 0), functions=[self.showAll])
            position = textImage.getBottomMiddle()
            position = (position[0] + noButton.getWidth(), position[1] + 10)
            noButton.positionByTopMiddle(position)
            self.gameObjects.append(noButton)
            self.gameObjects[-1].show()

            yesButton.image = self.font.render("Yes", True, (255, 255, 255))
            noButton.image = self.font.render("No", True, (255, 255, 255))

            yesButton.functions.append(yesButton.destroy)
            yesButton.functions.append(noButton.destroy)
            yesButton.functions.append(textImage.destroy)

            noButton.functions.append(noButton.destroy)
            noButton.functions.append(yesButton.destroy)
            noButton.functions.append(textImage.destroy)

        def showAll(self):
            for object in self.gameObjects:
                object.show()
            for player in self.players:
                player.show()

        def hideAll(self):
            for object in self.gameObjects:
                object.hide()
            for player in self.players:
                player.hide()

        def returnFromNameChange(self, playerNum):
            #remove the text box
            textBox = self.gameObjects.pop() #it'll always be the last object
            
            #show everything
            for object in self.gameObjects:
                object.show()
            for player in self.players:
                player.show()
            if textBox.text == "":
                return
            self.players[playerNum - 1].playerName = textBox.text
            self.players[playerNum - 1].nameImage.setImage(self.font.render(textBox.text, True, (255, 255, 255)))
        
        def viewPrimaries(self, playerNum):
            #hide everything
            for object in self.gameObjects:
                object.hide()
            for player in self.players:
                player.hide()
            #we'll make buttons for each primary weapon, and a wild card, rows of 15
            #we'll also have a button to go back
            weaponNum, i, j = 0, 0, 0
            while weaponNum < len(PRIMARIES):
                for i in range(15):
                    if weaponNum < len(PRIMARIES):
                        weapon = Button(primaryImages[weaponNum], (0, 0), functions=[self.returnFromPrimarySelection, self.players[playerNum - 1].setPrimary], FunctionArgs=[[], [PRIMARIES[weaponNum]]])
                        weapon.positionByTopMiddle((80 + i * 80, 100 + j * 80))
                        #weapon.setImage(self.font.render(PRIMARIES[weaponNum + i], True, (255, 0, 0)))
                        self.gameObjects.append(weapon)
                        weaponNum += 1
                j += 1

            backButton = Button(None, (0, 0), functions=[self.returnFromPrimarySelection])
            backButton.positionByTopMiddle((640, 540))
            backButton.setImage(self.font.render("Back", True, (255, 0, 0)))
            self.gameObjects.append(backButton)

        def returnFromPrimarySelection(self):
            self.gameObjects = self.gameObjects[:len(self.gameObjects) - (len(PRIMARIES) + 1)] #remove all the buttons that will be at the end of the list
            self.showAll()
            

        def returnFromTextBox(self):
            #remove the text box
            textBox = self.gameObjects.pop() #it'll always be the last object
            #show everything
            for object in self.gameObjects:
                object.show()
            for player in self.players:
                player.show()
            #remove the first button
            self.gameObjects.remove(self.addPlayerButtons.pop(0))
            self.numPlayers += 1

            #For testing purposes
            # particalArgs = [[0, 0], (255, 0, 0, 255), 3, [0, 0], 10, [1, 1], 60, True, 0.1, 30, 0.01]
            # particalGen = particalGenerator([600, 400], BasicParticle, particalCountPerFrame=10, particalConstructorArgs=particalArgs)
            # self.gameObjects.append(particalGen)

            # animator = Animator(particalGen)
            # animator.lerpTo([1000, 400], 60)
            # self.gameObjects.append(animator)
            


            if self.numPlayers == 1:
                #position a name at top middle of quadrant 1
                textImage = Button(self.font.render(textBox.text, True, (255, 255, 255)), (320, 0), functions=[self.changeName], FunctionArgs=[[1]])
                textImage.positionByTopMiddle((320, 0))
                self.gameObjects.append(textImage)
                
                self.players.append(Player(textBox.text, textImage, self.font))

                #Add a button to start under the player name
                startButton = Button(None, textImage.getBottomMiddle(), functions=[self.players[0].onStart])
                startButton.image = self.font.render("Start", True, (255, 255, 255))
                startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
                startButton.positionByTopMiddle(textImage.getBottomMiddle())
                self.gameObjects.append(startButton)

                self.players[0].lockInButton.functions.append(self.openConfirmBox)
                self.players[0].lockInButton.FunctionArgs.append([1])
                self.players[0].loadoutImages[0].functions = [self.viewPrimaries]
                self.players[0].loadoutImages[0].FunctionArgs = [1]
            elif self.numPlayers == 2:
                #position a name at top middle of quadrant 2
                textImage = Button(self.font.render(textBox.text, True, (255, 255, 255)), (960, 0), functions=[self.changeName], FunctionArgs=[[2]])
                textImage.positionByTopMiddle((960, 0))
                self.gameObjects.append(textImage)

                self.players.append(Player(textBox.text, textImage, self.font))

                #Add a button to start under the player name
                startButton = Button(None, textImage.getBottomMiddle(), functions=[self.players[1].onStart])
                startButton.image = self.font.render("Start", True, (255, 255, 255))
                startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
                startButton.positionByTopMiddle(textImage.getBottomMiddle())
                self.gameObjects.append(startButton)

                self.players[1].lockInButton.functions.append(self.openConfirmBox)
                self.players[1].lockInButton.FunctionArgs.append([2])
                self.players[1].loadoutImages[0].functions = [self.viewPrimaries]
                self.players[1].loadoutImages[0].FunctionArgs = [2]
            elif self.numPlayers == 3:
                #position a name at top middle of quadrant 3
                textImage = Button(self.font.render(textBox.text, True, (255, 255, 255)), (320, 360), functions=[self.changeName], FunctionArgs=[[3]])
                textImage.positionByTopMiddle((320, 360))
                self.gameObjects.append(textImage)

                self.players.append(Player(textBox.text, textImage, self.font))

                #Add a button to start under the player name
                startButton = Button(None, textImage.getBottomMiddle(), functions=[self.players[2].onStart])
                startButton.image = self.font.render("Start", True, (255, 255, 255))
                startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
                startButton.positionByTopMiddle(textImage.getBottomMiddle())
                self.gameObjects.append(startButton)

                self.players[2].lockInButton.functions.append(self.openConfirmBox)
                self.players[2].lockInButton.FunctionArgs.append([3])
                self.players[2].loadoutImages[0].functions = [self.viewPrimaries]
                self.players[2].loadoutImages[0].FunctionArgs = [3]
            elif self.numPlayers == 4:
                #position a name at top middle of quadrant 4

                textImage = Button(self.font.render(textBox.text, True, (255, 255, 255)), (960, 360), functions=[self.changeName], FunctionArgs=[[4]])
                #textImage.image = self.font.render(textBox.text, True, (255, 255, 255))
                textImage.positionByTopMiddle((960, 360))
                self.gameObjects.append(textImage)

                self.players.append(Player(textBox.text, textImage, self.font))

                #Add a button to start under the player name
                startButton = Button(None, textImage.getBottomMiddle(), functions=[self.players[3].onStart])
                startButton.image = self.font.render("Start", True, (255, 255, 255))
                startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
                startButton.positionByTopMiddle(textImage.getBottomMiddle())
                self.gameObjects.append(startButton)

                self.players[3].lockInButton.functions.append(self.openConfirmBox)
                self.players[3].lockInButton.FunctionArgs.append([4])
                self.players[3].loadoutImages[0].functions = [self.viewPrimaries]
                self.players[3].loadoutImages[0].FunctionArgs = [4]

        def draw(self):
            self.screen.fill((0, 0, 0))
            for object in self.gameObjects:
                object.draw(self.screen)
            for player in self.players:
                player.draw(self.screen)
            pg.display.flip()
            self.clock.tick(60)
        
    pg.init()
    pg.font.init()
    game = Game()
    game.loadGame()


if __name__ == "__main__":
    main()
