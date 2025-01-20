import pygame as pg
import random
import PyGameObjects as gameObjects
import Globals as g
import Modifiers as m
import copy

class Player:
    def __init__(self, playerName, playerNameImage, font, primaryImages, secondaryImages, grenadeImages, strategemImages, primaryChances, secondaryChances, grenadeChances, strategemChances, maxRolls = 12):
        self.playerName = playerName
        self.loadout = [None, None, None, None, None, None, None]
        self.rolls = 0
        self.nameImage = playerNameImage #So I can position everything based on the name image
        self.font = font
        self.fontRender = pg.font.Font(font, 36)
        self.maxRolls = maxRolls
        self.selectionButtons = []
        self.rollButton = None
        self.pendingChoice = False
        self.childObjects = []
        self.ToDestroy = [] #Objects we're trying to clean up
        self.lockedIn = False
        self.primaryImages = primaryImages
        self.secondaryImages = secondaryImages
        self.grenadeImages = grenadeImages
        self.strategemImages = strategemImages
        self.primaries = primaryChances
        self.secondaries = secondaryChances
        self.grenades = grenadeChances
        self.strategems = strategemChances
        self.modifiers = []
        self.addingModifier = False
        self.defaultRolls = maxRolls
        self.confirmBoxFunction = []
        self.confirmBoxArgs = []

        #Create the roll and lock in buttons
        for i in range(2):
            button = gameObjects.Button(None, (0, 0), toolTipEnabled=True, toolTip="Testing")
            position = self.nameImage.getBottomMiddle()
            position = (position[0] + ((i - 0.5) * 2) * (button.getWidth()), position[1] + button.getHeight() * 3)
            button.positionByTopMiddle(position)
            button.hide()
            if i == 0:
                button.setImage(self.fontRender.render("Roll", True, (255, 0, 0)))
                button.addOnClickFunction(self.roll)
                
                self.rollButton = button
            else:
                button.setImage(self.fontRender.render("Lock In", True, (255, 0, 0)))
                self.lockInButton = button

        #Display the amount of rolls the player has left
        self.rollsTextImage = gameObjects.gameTextImage("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls), (0, 0), self.font)
        x = self.nameImage.getCenter()[0]
        y = self.rollButton.getTopMiddle()[1]
        position = (x, y)
        self.rollsTextImage.positionByBottomMiddle(position)

        #loadout Images
        self.loadoutImages = []
        for i in range(7):
            button = gameObjects.Button(None, (0, 0), heldFunctions=[self.transitionToWildCard])
            button.heldFunctionArgs.append([button])
            self.loadoutImages.append(button)

        #Position the loadout images
        nameBottomMiddle = playerNameImage.getBottomMiddle()
        imageWidth = self.loadoutImages[0].getWidth()
        startingX = (nameBottomMiddle[0] - imageWidth * 4) + int(imageWidth) 
        y = nameBottomMiddle[1] + 10
        j = 0
        for i in range(7): 
            self.loadoutImages[j].positionByTopMiddle((startingX + imageWidth * i, y))
            j += 1

        for image in self.loadoutImages:
            image.hide()

    def rollModifier(self):
        attempts = 0
        mods = []
        firstRoll = False
        for mod in m.MODIFIERS:
            mods.append(mod())
        if len(self.modifiers) == 0:
            firstRoll = True
            tierOnes = []
            for mod in mods:
                if mod.tier == 1:
                    tierOnes.append(mod)

            if len(tierOnes) > 0:
                mod = random.choices(tierOnes)[0]
                self.modifiers.append(mod)
        
        
        def HasUpgrades():
            for mod in self.modifiers:
                if mod.upgrades != {}:
                    return True
            return False
        failed = False
        if not firstRoll:
            Upgrade = False
            if HasUpgrades():
                #If the player has upgrades, we'll roll to see if they get one
                if random.randint(1, 100) <= 20: #20% chance of getting an upgrade
                    Upgrade = True
            if Upgrade:
                upgradableMods = []
                for mod in self.modifiers:
                    if mod.upgrades != {}:
                        upgradableMods.append(mod)
                mod = random.choices(upgradableMods)[0]
                upgrade = random.choices(list(mod.upgrades.keys()), list(mod.upgrades.values()))[0]
                self.modifiers.remove(mod)
                mod = upgrade()
                self.modifiers.append(mod)
            
            tryagain = True
            while tryagain and not Upgrade:
                #Roll a random modifier
                tier = random.choices([1, 2, 3], [1.5, 1, 0.5])[0] #
                mods = []
                upgrades = []
                incompatible = []
                for mod in self.modifiers:
                    for upgrade in mod.upgrades:
                        upgrades.append(upgrade)
                    for incompatibleMod in mod.incompatibilities:
                        incompatible.append(incompatibleMod)
                    incompatible.append(mod.__class__)

                for modclass in m.MODIFIERS:
                    mod = modclass()
                    if mod.tier == tier and not any(isinstance(x, modclass) for x in self.modifiers) and modclass not in incompatible and modclass not in upgrades:
                        mods.append(mod)
                if len(mods) > 0:
                    mod = random.choices(mods)[0]
                    self.modifiers.append(mod)
                    tryagain = False
                else:
                    tier += 1
                    if tier > 3:
                        tier = 1
                    attempts += 1
                    if attempts > 2:
                        tryagain = False
                        failed = True
                    else:
                        tryagain = True

        if failed: #we have no available mods to roll, but upgrades happen in a round robin style
            upgradableMods = []
            for mod in self.modifiers:
                if mod.upgrades != {}:
                    upgradableMods.append(mod)
            mod = random.choices(upgradableMods)[0]
            upgrade = random.choices(list(mod.upgrades.keys()), list(mod.upgrades.values()))[0]
            self.modifiers.remove(mod)
            mod = upgrade()
            self.modifiers.append(mod)

        #Create a black box covering the whole screen, with 75% opacity
        blackBox = gameObjects.Button(None, (0, 0))
        blackBox.setImage(pg.Surface((g.SCREEN_SIZE[0], g.SCREEN_SIZE[1])))
        blackBox.image.fill((0, 0, 0))
        blackBox.setOpacity(191)
        blackBox.positionByCenter((g.SCREEN_SIZE[0] // 2, g.SCREEN_SIZE[1] // 2))
        self.childObjects.append(blackBox)

        pg.event.post(pg.event.Event(g.SAVEGAME))
        pg.event.post(pg.event.Event(g.LOCKCONTROLS))

        #Create a box for the modifier at 0% opacity
        modifierBox = gameObjects.Button(g.DEFAULT_MOD_ICON, (0, 0))
        modifierBox.scale = 5
        modifierBox.positionByCenter((g.SCREEN_SIZE[0] // 2, g.SCREEN_SIZE[1] // 2))
        modifierBox.setOpacity(0)
        self.childObjects.append(modifierBox)

        #animate the box to fade in
        animManager = gameObjects.Animator(modifierBox)
        animManager.lerpOpacityTo(250, 60)
        modifierBox.addChild(animManager)

        #animate the box to grow for a second
        animManager = gameObjects.Animator(modifierBox)
        animManager.lerpScaleTo(6, 60)
        animManager.setOnAnimationEnd(self.createModifierNameAndDescription, [mod, modifierBox])
        modifierBox.addChild(animManager)

        #animate a small bump in size
        animManager = gameObjects.Animator(modifierBox)
        animManager.setOnAnimationEnd(self.SpawnParticals, [[modifierBox.getTopMiddle()[0] - modifierBox.getWidth() * modifierBox.scale // 2, modifierBox.getTopMiddle()[1]]]) #Should spawn particals at the top left corner of the box
        animManager.addOnAnimationEnd(self.SpawnParticals, [[modifierBox.getTopMiddle()[0] + modifierBox.getWidth() * modifierBox.scale // 2, modifierBox.getTopMiddle()[1]]]) #Should spawn particals at the top right corner of the box
        animManager.addOnAnimationEnd(self.SpawnParticals, [[modifierBox.getBottomMiddle()[0] - modifierBox.getWidth() * modifierBox.scale // 2, modifierBox.getBottomMiddle()[1]]])
        animManager.addOnAnimationEnd(self.SpawnParticals, [[modifierBox.getBottomMiddle()[0] + modifierBox.getWidth() * modifierBox.scale // 2, modifierBox.getBottomMiddle()[1]]])
        animManager.lerpScaleTo(6.25, 65)
        modifierBox.addChild(animManager)

        #and we'll shrink it over 2 seconds, so itll look like it's growing and then shrinking
        animManager = gameObjects.Animator(modifierBox)
        animManager.setOnAnimationEnd(self.removeParticalGens)
        animManager.lerpScaleTo(6, 70)
        modifierBox.addChild(animManager)

        self.addingModifier = True

        pg.time.set_timer(g.CONTINUE, 2500, 1)
        pg.event.post(pg.event.Event(g.LOCKCONTROLS))

    def SpawnParticals(self, pos):
        particalGen = gameObjects.particalGenerator(pos, gameObjects.BasicParticle, particalCountPerFrame=60, particalConstructorArgs=[[0, 0], (255, 0, 0, 255), 3, [0, 0], 10, [1, 1], 60, True, 0.1, 30, 0.01])
        self.childObjects.append(particalGen)

    def removeParticalGens(self):
        for object in self.childObjects:
            if isinstance(object, gameObjects.particalGenerator):
                object.destroy()

    def createModifierNameAndDescription(self, modifier, modifierBox):
        #create a textImage for the modifier name
        modifierName = gameObjects.gameTextImage(modifier.name, (0, 0), self.font, fontSize = 36)
        modifierName.positionByTopMiddle((modifierBox.getTopMiddle()[0], modifierBox.getTopMiddle()[1] + 10))
        modifierName.setOpacity(255)
        modifierBox.addChild(modifierName)

        #create a textImage for the modifier description
        modifierDescription = gameObjects.gameTextImage(modifier.description, (0, 0), self.font, fontSize=16, centerText=True)
        modifierDescription.positionByTopMiddle((modifierBox.getTopMiddle()[0], modifierBox.getTopMiddle()[1] + 150))
        modifierDescription.setOpacity(255)
        modifierBox.addChild(modifierDescription)

        #we'll make certain mods take effect now, when the text appears
        if isinstance(modifier, m.MoreRollsMod):
            self.maxRolls = self.defaultRolls + 2
        if isinstance(modifier, m.LessRollsMod):
            self.maxRolls = self.defaultRolls - 6
        if isinstance(modifier, m.EvenLessRollsMod):
            self.maxRolls = self.defaultRolls - 9
        self.rollsTextImage.updateText("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls))

        if isinstance(modifier, m.CuratedBuildMod):
            self.loadout = random.choice(list(g.CURATED_BUILDS.values()))
            self.lockInButton.opacity = 155
            self.confirmBoxFunction = self.lockInButton.functions
            self.confirmBoxArgs = self.lockInButton.FunctionArgs
            self.lockInButton.functions = []
            self.lockInButton.FunctionArgs = []
            self.refresh()
            pg.event.post(pg.event.Event(g.SAVEGAME))
    
    def endModifierAnimation(self):
        #Add a button to the screen that will allow the player to continue
        button = gameObjects.Button(None, (0, 0), function=self.clearModifierScreenStuff)
        button.setImage(self.fontRender.render("Continue", True, (255, 0, 0)))
        button.positionByCenter((g.SCREEN_SIZE[0] // 2, (g.SCREEN_SIZE[1] // 4) * 3))
        self.childObjects.append(button)
        #Debuging

    def clearModifierScreenStuff(self):
        self.childObjects = self.childObjects[:-3]
        self.addingModifier = False
        pg.event.post(pg.event.Event(g.UNLOCKCONTROLS))
        
    #Replaces a loadout image with WILD text, if the user doesn't have access to the specific item
    def replaceWithWildCard(self, button):
        buttonSlotIndex = self.loadoutImages.index(button)
        newButton = gameObjects.Button(None, (0, 0))
        newButton.addOnHoldFunction(self.transitionToWildCard, [newButton])
        newButton.setImage(self.fontRender.render("Wild", True, (255, 255, 0)))
        newButton.positionByCenter(button.getCenter())
        self.loadoutImages[self.loadoutImages.index(button)] = newButton

        if not button.destroy():
            self.ToDestroy.append(button)

        self.loadout[buttonSlotIndex] = "Wild"
        pg.event.post(pg.event.Event(g.SAVEGAME))

    #Starts the effects of transitioning to a WILD card
    def transitionToWildCard(self, button):
        if self.lockedIn:
            return
        #We'll attach a partical effect to the 4 corners of the button, and have them follow the corners
        #We'll also have the button spin and shrink, and then disappear

        #Anim one will make the button spin
        animManager = gameObjects.Animator(button)
        animManager.slerpRotationsTo(-50, 600)
        #Anim two will make the button shrink
        animManagerTwo = gameObjects.Animator(button)
        animManagerTwo.lerpScaleTo(0.01, 240)
        #When the shrink animation is done, we'll replace the button with a WILD card
        animManagerTwo.setOnAnimationEnd(self.replaceWithWildCard, [button])
        button.addChild(animManager)
        button.addChild(animManagerTwo)
        button.functions = []
        button.FunctionArgs = []

        particalGens = []

        #TRhe arguments required to create a partical
        particalArgs = [[0, 0], (255, 0, 0, 255), 3, [0, 0], 10, [1, 1], 60, True, 0.1, 30, 0.01]
        for i in range(4):
            particalGen = gameObjects.particalGenerator([0, 0], gameObjects.BasicParticle, particalConstructorArgs= particalArgs)
            particalGens.append(particalGen)
        
        particalGens[0].pos[1] = button.getTopMiddle()[1] + button.getWidth()
        particalGens[0].pos[0] = button.getTopMiddle()[0] - button.getWidth()

        particalGens[1].pos[1] = button.getBottomMiddle()[1] - button.getWidth()
        particalGens[1].pos[0] = button.getBottomMiddle()[0] - button.getWidth()

        particalGens[2].pos[1] = button.getTopMiddle()[1] + button.getWidth()
        particalGens[2].pos[0] = button.getTopMiddle()[0] + button.getWidth()

        particalGens[3].pos[1] = button.getBottomMiddle()[1] - button.getWidth()
        particalGens[3].pos[0] = button.getBottomMiddle()[0] + button.getWidth()

        for particalGen in particalGens:
            particalGen.SetParent(button)

    #needed for the loading, so we can refresh the images that we set manually
    def refresh(self):
        for i in range(len(self.loadout)):
            if self.loadout[i] == "Wild":
                self.loadoutImages[i].setImage(self.fontRender.render("Wild", True, (255, 255, 0)))
            elif i == 0:
                self.loadoutImages[i].setImage(self.primaryImages[list(g.PRIMARIES.keys()).index(self.loadout[i])])
            elif i == 1:
                self.loadoutImages[i].setImage(self.secondaryImages[list(g.SECONDARIES.keys()).index(self.loadout[i])])
            elif i == 2:
                self.loadoutImages[i].setImage(self.grenadeImages[list(g.GRENADES.keys()).index(self.loadout[i])])
            else:
                self.loadoutImages[i].setImage(self.strategemImages[list(g.STRATEGEMS).index(self.loadout[i])])
                if "Backpack" in g.STRATEGEMS[self.loadout[i]] or "Weapon" in g.STRATEGEMS[self.loadout[i]]:
                    self.loadoutImages[i].functions.append(self.openReplacementMenu)
                    self.loadoutImages[i].FunctionArgs.append([i])
        self.nameImage.image = self.fontRender.render(self.playerName, True, (255, 255, 255))
        self.nameImage.show()

        if any(isinstance(x, m.CuratedBuildMod) for x in self.modifiers):
            if self.rolls < 3:
                self.lockInButton.opacity = 155
                self.lockInButton.functions = []
                self.lockInButton.FunctionArgs = []
            else:
                self.lockInButton.opacity = 255
                self.lockInButton.functions = self.confirmBoxFunction
                self.lockInButton.FunctionArgs = self.confirmBoxArgs

        if any(isinstance(x, m.MoreRollsMod) for x in self.modifiers):
            self.maxRolls = self.defaultRolls + 2
        if any(isinstance(x, m.LessRollsMod) for x in self.modifiers):
            self.maxRolls = self.defaultRolls - 6
        if any(isinstance(x, m.EvenLessRollsMod) for x in self.modifiers):
            self.maxRolls = self.defaultRolls - 9
        self.rollsTextImage.updateText("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls))

    #Hides all the buttons and images
    def hide(self):
        for image in self.loadoutImages:
            image.hide()
        for button in self.selectionButtons:
            button.hide()
        if self.rollButton != None:
            self.rollButton.hide()
        if self.lockInButton != None:
            self.lockInButton.hide()
        self.rollsTextImage.hide()
        self.nameImage.hide()
        for object in self.childObjects:
            object.hide()
        for object in self.ToDestroy:
            object.hide()

    #Shows all the buttons and images
    def show(self):
        self.nameImage.show()
        self.rollsTextImage.show()
        #Ensure the player has actually started the game
        if self.loadout[0] is not None:
            for image in self.loadoutImages:
                image.show()
            for button in self.selectionButtons:
                button.show()
            if not self.lockedIn:
                if self.rollButton != None and not self.pendingChoice:
                    self.rollButton.show()
                if self.lockInButton != None and not self.pendingChoice:
                    self.lockInButton.show()
        else:
            return
        for object in self.childObjects:
            object.show()
        for object in self.ToDestroy:
            object.show()

    #handles button imputs for self and children
    def handleInput(self, event):
        if event.type == g.CONTINUE:
            self.endModifierAnimation()
        if event.type == g.LOCKCONTROLS:
            self.addingModifier = True
        if event.type == g.UNLOCKCONTROLS:
            self.addingModifier = False
        for image in self.loadoutImages:
            if not self.addingModifier:
                image.handleInput(event)   
        for button in self.selectionButtons:
            button.handleInput(event)
        if self.rollButton != None and not self.addingModifier:
            self.rollButton.handleInput(event)
        if self.lockInButton != None and not self.addingModifier:
            self.lockInButton.handleInput(event)
        for object in self.childObjects:
            object.handleInput(event)
        for object in self.ToDestroy:
            object.handleInput(event)
    
    #updates all the buttons and images
    def update(self):
        for image in self.loadoutImages:
            image.update()
        for object in self.ToDestroy:
            if object.destroy():
                self.ToDestroy.remove(object)
            else:
                object.update()
        for object in self.childObjects:
            object.update()
            if object.destroyed:
                self.ToDestroy.append(object)
                self.childObjects.remove(object)

    #draws all the buttons and images
    def draw(self, screen):
        for image in self.loadoutImages:
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

    #Called to reset a build and start over, or to start a new game
    def onStart(self):
        if self.lockedIn == True:
            #We can assume the user is restarting the game, so we need to recreate the buttons
            self.lockedIn = False
            self.lockInButton.show()
            self.rollButton.show()

            self.rolls = 0
            self.refresh()

            #We'll assume the last item in the childObjects list needs to be removed. Should be the restart button
            if len(self.childObjects) > 0:
                self.childObjects[-1].destroy()
                self.ToDestroy.append(self.childObjects.pop())
        
        primaryOptions = []
        secondaryOptions = []
        grenadeOptions = []
        strategemOptions = []
        primaryChances = []
        secondaryChances = []
        grenadeChances = []
        strategemChances = []
        categoryRolls = 0
        categoryChances = [1, 1, 1, 1] #Doesn't matter here, but we need to pass it in

        primaryOptions, secondaryOptions, grenadeOptions, strategemOptions, primaryChances, secondaryChances, grenadeChances, strategemChances, categoryRolls, categoryChances = self.applyModsPreRoll(list(g.PRIMARIES.keys()), list(g.SECONDARIES.keys()), list(g.GRENADES.keys()), list(g.STRATEGEMS.keys()), self.primaries, self.secondaries, self.grenades, self.strategems, categoryChances)
        

        if any(isinstance(x, m.CuratedBuildMod) for x in self.modifiers):
            self.lockInButton.opacity = 155
            self.confirmBoxFunction = self.lockInButton.functions
            self.confirmBoxArgs = self.lockInButton.FunctionArgs
            self.lockInButton.functions = []
            self.lockInButton.FunctionArgs = []
            self.loadout = random.choice(list(g.CURATED_BUILDS.values()))
            self.refresh()
        else:
            #rolls a build and sets the loadout
            for i in range(len(self.loadout)):
                if i == 0:
                    selection = random.choices(range(len(primaryOptions)), primaryChances)[0]
                    #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                    self.primaries[primaryOptions.index(primaryOptions[selection])] /= 1.5
                    for j in range(len(primaryOptions)):
                        if j != selection:
                            self.primaries[primaryOptions.index(primaryOptions[j])] *= 1.01
                            if self.primaries[primaryOptions.index(primaryOptions[j])] > 10:
                                self.primaries[primaryOptions.index(primaryOptions[j])] = 10
                    self.loadout[i] = primaryOptions[selection]
                elif i == 1:
                    selection = random.choices(range(len(secondaryOptions)), secondaryChances)[0]
                    #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                    self.secondaries[secondaryOptions.index(secondaryOptions[selection])] /= 1.5
                    for j in range(len(secondaryOptions)):
                        if j != selection:
                            self.secondaries[secondaryOptions.index(secondaryOptions[j])] *= 1.01
                            if self.secondaries[secondaryOptions.index(secondaryOptions[j])] > 10:
                                self.secondaries[secondaryOptions.index(secondaryOptions[j])] = 10
                    self.loadout[i] = secondaryOptions[selection]
                elif i == 2:
                    selection = random.choices(range(len(grenadeOptions)), grenadeChances)[0]
                    #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                    self.grenades[grenadeOptions.index(grenadeOptions[selection])] /= 1.5
                    for j in range(len(grenadeOptions)):
                        if j != selection:
                            self.grenades[grenadeOptions.index(grenadeOptions[j])] *= 1.01
                            if self.grenades[grenadeOptions.index(grenadeOptions[j])] > 10:
                                self.grenades[grenadeOptions.index(grenadeOptions[j])] = 10
                    self.loadout[i] = grenadeOptions[selection]
                else:
                    selection = random.choices(range(len(strategemOptions)), strategemChances)[0]
                    currentBuild = self.loadout[3:i]
                    bHasVehicle = False
                    for strategem in currentBuild:
                        if "Vehicle" in g.STRATEGEMS[strategem]:
                            bHasVehicle = True
                            break
                    
                    #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                    strategemChances[strategemOptions.index(strategemOptions[selection])] /= 1.5
                    for j in range(len(strategemOptions)):
                        if j != selection:
                            strategemChances[strategemOptions.index(strategemOptions[j])] *= 1.01
                            if strategemChances[strategemOptions.index(strategemOptions[j])] > 10:
                                strategemChances[strategemOptions.index(strategemOptions[j])] = 10
                    self.loadout[i] = strategemOptions[selection]
                    #set the chance of a second vehicle to 0
                    if bHasVehicle:
                        for j in range(len(strategemOptions)):
                            if "Vehicle" in g.STRATEGEMS[strategemOptions[j]]:
                                strategemChances[j] = 0
                    #remove the strategem we got from the list
                    strategemChances.pop(selection)
                    strategemOptions.pop(selection)




                    # selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                    # currentBuild = self.loadout[3:i]
                    # bHasVehicle = False
                    # for strategem in currentBuild:
                    #     if "Vehicle" in g.STRATEGEMS[strategem]:
                    #         bHasVehicle = True
                    #         break
                    # while selection in currentBuild or ("Vehicle" in g.STRATEGEMS[selection] and bHasVehicle):
                    #     #if the strategem is already in the self.loadout, try again
                    #     selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                    # #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                    # self.strategems[list(g.STRATEGEMS).index(selection)] /= 1.5
                    # for j in range(len(self.strategems)):
                    #     if j != list(g.STRATEGEMS).index(selection):
                    #         self.strategems[j] *= 1.01
                    #         if self.strategems[j] > 10:
                    #             self.strategems[j] = 10
                    # self.loadout[i] = selection
                    # self.loadoutImages[i].setImage(self.strategemImages[list(g.STRATEGEMS).index(selection)])
                    # if "Backpack" in g.STRATEGEMS[selection] or "Weapon" in g.STRATEGEMS[selection]:
                    #     self.loadoutImages[i].functions.append(self.openReplacementMenu)
                    #     self.loadoutImages[i].FunctionArgs.append([i])

        for image in self.loadoutImages:
            image.show()

        # #Create a roll gameObjects.Button
        self.rollButton.show()
        self.lockInButton.show()
        self.refresh()

        #New addition, roll mods
        self.rollModifier()

        

        pg.event.post(pg.event.Event(g.SAVEGAME))


        # print("Player " + self.playerName + "'s Loadout:")
        # for i in range(len(self.loadout)):
        #     print(self.loadout[i])

    #Replaces a slot in the loadout with a new item
    def replaceSlot(self, slot, item):
        #if the slot is a primary, secondary, or grenade
        if slot < 3:
            if item in g.PRIMARIES.keys():
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.primaryImages[list(g.PRIMARIES.keys()).index(item)])
            elif item in g.SECONDARIES:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.secondaryImages[list(g.SECONDARIES.keys()).index(item)])
            elif item in g.GRENADES:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.grenadeImages[list(g.GRENADES.keys()).index(item)])
        #slot is a strategem
        else:
            self.loadout[slot] = item
            self.loadoutImages[slot].setImage(self.strategemImages[list(g.STRATEGEMS).index(item)])
            self.loadoutImages[slot].functions = []
            self.loadoutImages[slot].FunctionArgs = []
            #New addition, if the slot is a Backpack, or a weapon, we have to add functions to them.
            if "Backpack" in g.STRATEGEMS[item] or "Weapon" in g.STRATEGEMS[item]:
                self.loadoutImages[slot].functions.append(self.openReplacementMenu)
                self.loadoutImages[slot].FunctionArgs.append([slot])
        pg.event.post(pg.event.Event(g.SAVEGAME))

    #Opens a menu that lets the player choose a replacement for a slot, namely a backpack or weapon
    def openReplacementMenu(self, slot):
        if self.addingModifier:
            return
        if self.lockedIn:
            return
        self.hide()
        buttons = []
        itemNumber, i, j = 0, 0, 0 
        keys = list(g.STRATEGEMS.keys())
        tag = ""
        if "Weapon" in g.STRATEGEMS[self.loadout[slot]]:
            tag = "Weapon"
        elif "Backpack" in g.STRATEGEMS[self.loadout[slot]]:
            tag = "Backpack"

        while itemNumber < len(keys):
            i = 0
            while i < 7:
                if itemNumber < len(keys):
                    if keys[itemNumber] in self.loadout or tag not in g.STRATEGEMS[keys[itemNumber]]:
                        itemNumber += 1
                        continue
                    button = gameObjects.Button(None, (0, 0), functions=[self.replaceSlot, self.show], FunctionArgs=[[slot, keys[itemNumber]]])
                    button.setImage(self.strategemImages[itemNumber])
                    button.positionByTopMiddle(((self.nameImage.getBottomMiddle()[0] - button.getWidth() * 3) + i * button.getWidth(), self.nameImage.getBottomMiddle()[1] + 10 + j * 80))
                    buttons.append(button)
                    self.childObjects.append(button)
                    itemNumber += 1
                    i += 1

                else:
                    break
            j += 1
            if itemNumber >= len(keys):
                break

        
                
            
        #Back button
        backButton = gameObjects.Button(None, (0, 0), function=self.show)
        backButton.setImage(self.fontRender.render("Back", True, (255, 0, 0)))
        backButton.positionByTopMiddle(self.nameImage.getTopMiddle())
        buttons.append(backButton)
        self.childObjects.append(backButton)



        #append the destroy functions of all buttons to each button
        for button in buttons:
            for buttonTwo in buttons:
                button.functions.append(buttonTwo.destroy)
            
    #Called when the player has made a decision on what to do with the slot
    def madeDecision(self):
        self.pendingChoice = False
        self.selectionButtons = []
        self.rollButton.show()
        self.lockInButton.show()

        if any(isinstance(x, m.CuratedBuildMod) for x in self.modifiers):
            if self.rolls < 3:
                self.lockInButton.opacity = 150
                self.lockInButton.functions = []
                self.lockInButton.FunctionArgs = []
            else:
                self.lockInButton.opacity = 255
                self.lockInButton.functions = self.confirmBoxFunction
                self.lockInButton.FunctionArgs = self.confirmBoxArgs
        
        #A ramping up chance of auto locking in the player's build
        if any(isinstance(x, m.IsMyLockInBrokenMod) for x in self.modifiers):
            chance = self.rolls / self.maxRolls
            if random.randint(1, 100) <= chance * 100:
                self.lockIn()
        #if the player is out of rolls, we lock in for them
        elif self.rolls == self.maxRolls:
            self.lockIn()
        else:
            pg.event.post(pg.event.Event(g.SAVEGAME))


    #Rolls a few gear options for the player
    def roll(self):
        if self.addingModifier:
            return
        categoryChances = [1.3, 1.3, 1.3, 4] #Chance of getting a primary, secondary, grenade, or strategem. Strategems are weighted higher because theres 4 of them


        categorySelections = []
        #Roll 3 categories

        primaryOptions = []
        secondaryOptions = []
        grenadeOptions = []
        strategemOptions = []
        primaryChances = []
        secondaryChances = []
        grenadeChances = []
        strategemChances = []
        categoryRolls = 0

        #Apply mods that change the chances of getting certain items
        primaryOptions, secondaryOptions, grenadeOptions, strategemOptions, primaryChances, secondaryChances, grenadeChances, strategemChances, categoryRolls, categoryChances = self.applyModsPreRoll(list(g.PRIMARIES.keys()), list(g.SECONDARIES.keys()), list(g.GRENADES.keys()), list(g.STRATEGEMS.keys()), self.primaries, self.secondaries, self.grenades, self.strategems, categoryChances)

        #Remove items that are already in the loadout
        for item in self.loadout:
            if item in primaryOptions:
                primaryChances.pop(primaryOptions.index(item))
                primaryOptions.remove(item)
            if item in secondaryOptions:
                secondaryChances.pop(secondaryOptions.index(item))
                secondaryOptions.remove(item)
            if item in grenadeOptions:
                grenadeChances.pop(grenadeOptions.index(item))
                grenadeOptions.remove(item)
            if item in strategemOptions:
                strategemChances.pop(strategemOptions.index(item))
                strategemOptions.remove(item)


        if any(isinstance(x, m.MoreChoicesMod) for x in self.modifiers) and any(isinstance(x, m.NoStrategemsMod) for x in self.modifiers):
            categorySelections = [0, 1, 2, 3] #If the player has a bonus roll, but the noStrategems mod, they'll HAVE to get a single strategem roll, plus guarenteed primary, secondary, and grenade
            if primaryOptions == []:
                categorySelections[0] = 3 #If the player has no primary options, they'll have to get a strategem
            if secondaryOptions == []:
                categorySelections[1] = 3
            if grenadeOptions == []:
                categorySelections[2] = 3
        else:
            for i in range(categoryRolls):
                categorySelections.append(random.choices(range(4), categoryChances)[0])
                #If the category is a primary, secondary, or grenade, we can't have more than one of each
                if categorySelections[i] < 3:
                    categoryChances[categorySelections[i]] = 0 #Set the chance of getting that category to 0
                #If the category is a primary, we check if there's still enough options to roll another stratagem. If not, we set the category chance to 0
                if categorySelections[i] == 3:
                    numStrategemCategories = 0
                    for j in range(len(categorySelections)):
                        if categorySelections[j] == 3:
                            numStrategemCategories += 1
                    if numStrategemCategories == len(strategemOptions):
                        categoryChances[3] = 0

        
        #Roll the selections, store them in a list so the player can choose which one they want, or if they want all 3
        selections = []
        i = 0
        while i < categoryRolls:
            if categorySelections[i] == 0:
                selection = random.choices(range(len(primaryOptions)), primaryChances)[0]
                #Shouldn't need this any more, because we removed items that are already in the loadout
                # while list(g.PRIMARIES.keys())[selection] in self.loadout:
                #     selection = random.choices(range(len(g.PRIMARIES.keys())), self.primaries)[0]
                selections.append(primaryOptions[selection])
                #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                self.primaries[primaryOptions.index(primaryOptions[selection])] /= 1.5
                #changed to only effect the primaries that we can get, so that the chances of others don't skyrocket
                for j in range(len(primaryOptions)):
                    if j != selection:
                        self.primaries[primaryOptions.index(primaryOptions[j])] *= 1.01
                        if self.primaries[primaryOptions.index(primaryOptions[j])] > 10:
                            self.primaries[primaryOptions.index(primaryOptions[j])] = 10
            elif categorySelections[i] == 1:
                selection = random.choices(range(len(secondaryOptions)), secondaryChances)[0]
                #ensure the selection isn't already in the build
                # while g.SECONDARIES[selection] in self.loadout:
                #     selection = random.choices(range(len(g.SECONDARIES)), self.secondaries)[0]
                selections.append(secondaryOptions[selection])
                #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                self.secondaries[secondaryOptions.index(secondaryOptions[selection])] /= 1.5
                for j in range(len(secondaryOptions)):
                    if j != selection:
                        self.secondaries[secondaryOptions.index(secondaryOptions[j])] *= 1.01
                        if self.secondaries[secondaryOptions.index(secondaryOptions[j])] > 10:
                            self.secondaries[secondaryOptions.index(secondaryOptions[j])] = 10
            elif categorySelections[i] == 2:
                selection = random.choices(range(len(grenadeOptions)), grenadeChances)[0]
                #ensure the selection isn't already in the build
                # while g.GRENADES[selection] in self.loadout:
                #     selection = random.choices(range(len(g.GRENADES)), self.grenades)[0]
                selections.append(grenadeOptions[selection])
                #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                self.grenades[grenadeOptions.index(grenadeOptions[selection])] /= 1.5
                for j in range(len(grenadeOptions)):
                    if j != selection:
                        self.grenades[grenadeOptions.index(grenadeOptions[j])] *= 1.01
                        if self.grenades[grenadeOptions.index(grenadeOptions[j])] > 10:
                            self.grenades[grenadeOptions.index(grenadeOptions[j])] = 10
            else:
                

                selection = random.choices(range(len(strategemOptions)), strategemChances)[0]
                #ensure the selection isn't already in the build or that there isn't a discrepensy (like a second mech)
                selection = strategemOptions[selection]
                selections.append(selection)

                #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                self.strategems[strategemOptions.index(selection)] /= 1.5
                for j in range(len(strategemOptions)):
                    if j != strategemOptions.index(selection):
                        self.strategems[j] *= 1.01
                        if self.strategems[j] > 10:
                            self.strategems[j] = 10

                #if the selection is a vehicle, remove the chance of getting another vehicle
                if "Vehicle" in g.STRATEGEMS[selection]:
                    for j in range(len(strategemOptions)):
                        if "Vehicle" in g.STRATEGEMS[strategemOptions[j]]:
                            strategemChances[j] = 0 #Can't really remove it, saver to do it this way

                #remove the selection from the options
                strategemChances.pop(strategemOptions.index(selection))
                strategemOptions.remove(selection)

                
            i += 1
        #For each Stratagem, select a random slot to replace. The entry in the list is the index of the selection
        strategemSlots = [0, 0, 0, 0]
        #find out how many self.strategems where selected
        strategemCount = 0
        for i in range(len(categorySelections)):
            if categorySelections[i] == 3:
                strategemCount += 1
        
        #check to see if the build has a mech and the selections have a mech
        vehicleSlot = 0
        vehicleindex = 0
        bVehicleEquipped = False
        for item in self.loadout:
            if item in list(g.STRATEGEMS.keys()):
                if "Vehicle" in g.STRATEGEMS[item]:
                    vehicleSlot = self.loadout.index(item) - 3
                    for selection in selections:
                        if selection in list(g.STRATEGEMS.keys()):
                            vehicleindex += 1
                            if "Vehicle" in g.STRATEGEMS[selection]:
                                strategemSlots[vehicleSlot] = selections.index(selection) + 1
                                bVehicleEquipped = True
                                break
                    if bVehicleEquipped:
                        break
        
        #roll a random slot for each strategem
        for i in range(strategemCount):
            if bVehicleEquipped:
                if vehicleindex == i + 1:
                    continue
                
            slot = random.randint(0, 3)
            #ensure the slot isn't already taken
            while strategemSlots[slot] != 0:
                slot = random.randint(0, 3)
            #find the index in the selections list of the strategem to put in the slot
            selectionIndex = 0
            skips = i
            for j in range(len(selections)):
                if selections[j] in list(g.STRATEGEMS.keys()):
                    if skips == 0:
                        selectionIndex = j
                        break
                    skips -= 1
            #put the selection in the slot
            strategemSlots[slot] = selectionIndex + 1 #So its not 0 indexed

        #If the player has a NoChoicesMod, we'll randomly select one of the options for them
        if any(isinstance(x, m.NoChoicesMod) for x in self.modifiers):
            noChoiceChances = []
            noChoiceChances.append(0.25)
            for i in range(len(selections)):
                noChoiceChances.append(1)
            selection = random.choices(range(len(selections) + 1), noChoiceChances)[0]
            if selection == 0: #select all
                for i in range(len(selections)):
                    if i + 1 in strategemSlots:
                        self.replaceSlot(3 + strategemSlots.index(i+1), selections[i])
                    else:
                        self.replaceSlot(categorySelections[i], selections[i])
            else:
                if selection in strategemSlots:
                    self.replaceSlot(3 + strategemSlots.index(selection), selections[selection - 1])
                else:
                    self.replaceSlot(categorySelections[selection - 1], selections[selection - 1])

        
        else:
            #We'll Create buttons under each of the slots we've chosen, so the player can select which one they want
            #We'll also create a button that lets them select all of them
            #Show the selections to the player, and let them choose which ones they want
            for i in range(len(selections)):
                slotNum = 0
                if i + 1 in strategemSlots:
                    slotNum = 3 + strategemSlots.index(i+1)
                else:
                    slotNum = categorySelections[i]
                
                button = None
                if not any(isinstance(x, m.AllInMod) for x in self.modifiers):
                    button = gameObjects.Button(None, (0, 0), functions=[self.replaceSlot, self.madeDecision], FunctionArgs=[[slotNum, selections[i]]])
                else:
                    button = gameObjects.Button(None, (0, 0), functions=[], FunctionArgs=[]) #If the player has an AllInMod, these buttons are unusable
                    button.opacity = 155
                

                if i + 1 in strategemSlots: #The index is in the self.strategems
                    x = self.loadoutImages[3 + strategemSlots.index(i+1)].getCenter()[0]
                    y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                    button.positionByTopMiddle((x, y))
                    if any(isinstance(x, m.JammerMod) for x in self.modifiers):
                        #if the strategem has a Eagle tag, we'll change the color of the button
                        if "Eagle" in g.STRATEGEMS[selections[i]] or "Orbital" in g.STRATEGEMS[selections[i]]:
                            button.setImage(self.fontRender.render("???", True, (255, 0, 0)))
                        elif "Sentry" in g.STRATEGEMS[selections[i]]:
                            button.setImage(self.fontRender.render("???", True, (0, 255, 0)))
                        elif "Backpack" in g.STRATEGEMS[selections[i]] or "Weapon" in g.STRATEGEMS[selections[i]] or "Vehicle" in g.STRATEGEMS[selections[i]]:
                            button.setImage(self.fontRender.render("???", True, (0, 0, 255)))
                        else:
                            button.setImage(self.fontRender.render("???", True, (255, 102, 0)))
                    elif any(isinstance(x, m.ScramblerMod) for x in self.modifiers) and random.randint(1, 100) <= 30:
                        button.setImage(self.strategemImages[random.randint(0, len(g.STRATEGEMS) - 1)])
                    else:
                        button.image = self.strategemImages[list(g.STRATEGEMS).index(selections[i])]

                else:
                    x = self.loadoutImages[categorySelections[i]].getCenter()[0]
                    y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                    button.positionByTopMiddle((x, y))
                    if any(isinstance(x, m.JammerMod) for x in self.modifiers):
                        button.setImage(self.fontRender.render("???", True, (255, 102, 0)))
                    else:
                        if selections[i] in g.PRIMARIES.keys():
                            if any(isinstance(x, m.ScramblerMod) for x in self.modifiers) and random.randint(1, 100) <= 30:
                                button.setImage(self.primaryImages[random.randint(0, len(g.PRIMARIES) - 1)])
                            else:
                                button.image = self.primaryImages[list(g.PRIMARIES.keys()).index(selections[i])]
                        elif selections[i] in g.SECONDARIES.keys():
                            if any(isinstance(x, m.ScramblerMod) for x in self.modifiers) and random.randint(1, 100) <= 30:
                                button.setImage(self.secondaryImages[random.randint(0, len(g.SECONDARIES) - 1)])
                            else:
                                button.image = self.secondaryImages[list(g.SECONDARIES.keys()).index(selections[i])]
                        elif selections[i] in g.GRENADES.keys():
                            if any(isinstance(x, m.ScramblerMod) for x in self.modifiers) and random.randint(1, 100) <= 30:
                                button.setImage(self.grenadeImages[random.randint(0, len(g.GRENADES) - 1)])
                            else:
                                button.image = self.grenadeImages[list(g.GRENADES.keys()).index(selections[i])]
                button.show()
                self.selectionButtons.append(button)

            #Create a button that lets the player select all of the options
            slotNums = []
            for i in range(len(selections)):
                if i + 1 in strategemSlots:
                    slotNums.append(3 + strategemSlots.index(i+1))
                else:
                    slotNums.append(categorySelections[i])
            button = gameObjects.Button(None, (0, 0))
            for i in range(len(slotNums)):
                button.addOnClickFunction(self.replaceSlot, [slotNums[i], selections[i]])
            button.addOnClickFunction(self.madeDecision, [])
            middleOfSlot3 = self.loadoutImages[3].getBottomMiddle()
            middleOfSlot3 = (middleOfSlot3[0], middleOfSlot3[1] + round(button.getHeight()))
            button.positionByTopMiddle(middleOfSlot3)
            button.setImage(self.fontRender.render("All", True, (255, 0, 0)))
            button.show()
            self.selectionButtons.append(button)



        self.rolls += 1
        self.rollsTextImage.updateText("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls))
        self.rollsTextImage.show()

        #Don't let the player lock in until they've made a decision
        self.rollButton.hide()
        self.lockInButton.hide()
        self.pendingChoice = True

        if any(isinstance(x, m.NoChoicesMod) for x in self.modifiers):
            self.madeDecision()
        
    #Stops the player from making more decisions, this is the endgame
    def lockIn(self):
        self.lockedIn = True
        self.lockInButton.hide()
        self.rollButton.hide()
        self.childObjects.append(gameObjects.Button(self.fontRender.render("Restart", True, (255, 0, 0)), (0, 0), function=self.onStart))
        x = self.nameImage.getBottomMiddle()[0]
        y = self.rollsTextImage.getBottomMiddle()[1] + 5
        self.childObjects[-1].positionByTopMiddle((x, y))
        self.childObjects[-1].show()
        pg.event.post(pg.event.Event(g.SAVEGAME))

    def applyModsOnStart(self):
        pass

    #Adjusts the lists of chances and options based on the mods
    def applyModsPreRoll(self, primaries, secondaries, grenades, strategems, primaryChances, secondaryChances, grenadeChances, strategemChances, categoryChances):
        
        primaryOptions = primaries
        secondaryOptions = secondaries
        grenadeOptions = grenades
        strategemOptions = strategems
        numCatagorySelections = 3

        pChances = copy.deepcopy(primaryChances)
        sChances = copy.deepcopy(secondaryChances)
        gChances = copy.deepcopy(grenadeChances)
        stChances = copy.deepcopy(strategemChances)

        if any(isinstance(x, m.MoreChoicesMod) for x in self.modifiers):
            numCatagorySelections += 1
        if any(isinstance(x, m.LessChoicesMod) for x in self.modifiers):
            numCatagorySelections -= 1
        if any(isinstance(x, m.EvenLessChoicesMod) for x in self.modifiers):
            numCatagorySelections -= 2

        if any(isinstance(x, m.MoreStrategemsMod) for x in self.modifiers):
            categoryChances[3] *= 1.5
        if any(isinstance(x, m.LessStrategemsMod) for x in self.modifiers):
            categoryChances[3] *= 0.5
        if any(isinstance(x, m.LessGrenadesMod) for x in self.modifiers):
            categoryChances[2] *= 0.5
        if any(isinstance(x, m.NoGrenadesMod) for x in self.modifiers) or any(isinstance(x, m.KnivesOnlyMod) for x in self.modifiers):
            categoryChances[2] = 0
        if any(isinstance(x, m.LessGrenadesMod) for x in self.modifiers):
            categoryChances[2] *= 0.5
        if any(isinstance(x, m.NoStrategemsMod) for x in self.modifiers):
            categoryChances[3] = 0

        if primaryOptions == []:
            categoryChances[0] = 0
        if secondaryOptions == []:
            categoryChances[1] = 0
        if grenadeOptions == []:
            categoryChances[2] = 0
        if strategemOptions == []:
            categoryChances[3] = 0

        if any(isinstance(x, m.BaseGameOnlyMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Base Game" not in g.STRATEGEMS[strategemOptions[i]] and "Mobilize" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1
            i = 0
            while i < len(primaryOptions):
                if "Base Game" not in g.PRIMARIES[primaryOptions[i]] and "Mobilize" not in g.PRIMARIES[primaryOptions[i]]:
                    pChances.pop(i)
                    primaryOptions.pop(i)
                else:
                    i += 1
            i = 0
            while i < len(secondaryOptions):
                if "Base Game" not in g.SECONDARIES[secondaryOptions[i]] and "Mobilize" not in g.SECONDARIES[secondaryOptions[i]]:
                    sChances.pop(i)
                    secondaryOptions.pop(i)
                else:
                    i += 1
            i = 0
            while i < len(grenadeOptions):
                if "Base Game" not in g.GRENADES[grenadeOptions[i]] and "Mobilize" not in g.GRENADES[grenadeOptions[i]]:
                    gChances.pop(i)
                    grenadeOptions.pop(i)
                else:
                    i += 1
        if any(isinstance(x, m.OopsOnlyBackpacksMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Backpack" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1
        if any(isinstance(x, m.OopsOnlyWeaponsMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Weapon" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1
        if any(isinstance(x, m.OopsOnlyEaglesMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Eagle" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1
        if any(isinstance(x, m.OopsOnlyOrbitalsMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Orbital" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1
        if any(isinstance(x, m.OopsOnlyTurretsMod) for x in self.modifiers):
            i = 0
            while i < len(strategemOptions):
                if "Sentry" not in g.STRATEGEMS[strategemOptions[i]]:
                    stChances.pop(i)
                    strategemOptions.pop(i)
                else:
                    i += 1

        
        return primaryOptions, secondaryOptions, grenadeOptions, strategemOptions, pChances, sChances, gChances, stChances, numCatagorySelections, categoryChances

    def applyModsPostRoll(self):
        pass


class Game:
    def __init__(self):
        self.version = "0.9.2"
        self.running = True
        self.clock = pg.time.Clock()
        self.font = g.FONT_PATH
        self.fontRender = pg.font.Font(self.font, 36)
        self.screen = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Helldivers Gear Generator: " + self.version)
        self.MaxRolls = 12
        self.numRolls = 0
        self.gameObjects = []
        self.addPlayerButtons = [] #So we can remove them when we're done
        self.numPlayers = 0
        self.players = []
        #self.startGame()
        # Generate chance lists, so that we can weight the random selection to favor items that aren't being selected as often
        self.primaries = []
        self.primaryImages = []
        for i in range(len(g.PRIMARIES)):
            self.primaries.append(1)
            try:
                self.primaryImages.append(pg.image.load(g.IMAGEBASEPATH + list(g.PRIMARIES.keys())[i] + ".png"))
            except:
                self.primaryImages.append(None)
        self.secondaries = []
        self.secondaryImages = []
        for i in range(len(g.SECONDARIES)):
            self.secondaries.append(1)
            try:
                self.secondaryImages.append(pg.image.load(g.IMAGEBASEPATH + list(g.SECONDARIES.keys())[i] + ".png"))
            except:
                self.secondaryImages.append(None)
        self.grenades = []
        self.grenadeImages = []
        for i in range(len(g.GRENADES)):
            self.grenades.append(1)
            try:
                self.grenadeImages.append(pg.image.load(g.IMAGEBASEPATH + list(g.GRENADES.keys())[i] + ".png"))
            except:
                self.grenadeImages.append(None)
        self.strategems = []
        self.strategemImages = []
        for key in g.STRATEGEMS:
            self.strategems.append(1)
            try:
                self.strategemImages.append(pg.image.load(g.IMAGEBASEPATH + key + ".png"))
            except:
                self.strategemImages.append(None)
        
        self.bControlsLocked = False
    #TODO: add a game profile
    def loadGame(self):
        self.gameObjects = []
        try:
            file = open("save.dat", "r")
        except:
            return
        data = file.read()
        file.close()
        lines = data.split("\n")

        playersInGame = {}
        for player in self.players:
            playersInGame[player.playerName] = 0 #default to do not load
        self.players = []

        #Directory will always have an index value at the top of the file
        directoryLocation = 0
        directoryLocation = lines[0].split(": ")[1]
        directoryLocation = int(directoryLocation)

        #Each player will have a name, and then a number that represents the index of the player's data
        i = directoryLocation + 1
        while i < len(lines):
            if lines[i] == "":
                break
            playerName = lines[i]
            if playerName in playersInGame:
                playersInGame[playerName] = int(lines[i + 1])
            i += 2

        #Now we load each player that exsists in the save file. We can assume by this point that all of them exsist in the save file.
        numPlayers = 0
        for playerData in playersInGame:
            playerIndex = playersInGame[playerData]
            playerName = lines[playerIndex]
            numPlayers -= -1 #Because Toby said so
            playerNameImage = None
            playerNameImage = gameObjects.Button(self.fontRender.render(playerName, True, (255, 255, 255)), (0, 0), functions=[self.changeName], FunctionArgs=[[numPlayers]])
            playerNameImage.rightClickFunctions.append(self.removePlayer)
            playerNameImage.rightClickFunctionArgs.append([numPlayers])
            self.gameObjects.append(playerNameImage)
            if numPlayers == 1:
                playerNameImage.positionByTopMiddle((320, 0))
            if numPlayers == 2:
                playerNameImage.positionByTopMiddle((960, 0))
            if numPlayers == 3:
                playerNameImage.positionByTopMiddle((320, 360))
            if numPlayers == 4:
                playerNameImage.positionByTopMiddle((960, 360))
            player = Player(playerName, playerNameImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls)
            
            player.loadoutImages[0].addOnClickFunction(self.viewPrimaries, [numPlayers])
            
            player.loadout = [lines[playerIndex + 1], lines[playerIndex + 2], lines[playerIndex + 3], lines[playerIndex + 4], lines[playerIndex + 5], lines[playerIndex + 6], lines[playerIndex + 7]]
            player.rolls = int(lines[playerIndex + 8])
            

            player.confirmBoxFunction = [self.openConfirmBox]
            player.confirmBoxArgs = [[numPlayers]]

            if lines[playerIndex + 9] == "True":
                player.rollButton = None
                player.lockInButton = None
            else:
                player.lockInButton.addOnClickFunction(self.openConfirmBox, [numPlayers])
            
            if lines[playerIndex + 10] != "[]":
                i = playerIndex + 10
                while lines[i] != "]":
                    for mod in m.MODIFIERS:
                        if lines[i] == mod.__name__:
                            player.modifiers.append(mod())
                            break
                    i += 1

            player.show()
            player.refresh()
            self.players.append(player)
        self.numPlayers = numPlayers

        #Re-Adding the player buttons
        i = 4
        while i > numPlayers:
            self.gameObjects.append(self.addPlayerButtons[i - 1])
            i -= 1
    
    def saveGame(self):
        #error handle if the file is not found
        try:
            file = open("save.dat", "r")
        except:
            file = open("save.dat", "w")
            #Write the default save File
            
            file.write("Directory: 4\n")
            file.write("Version: " + self.version + "\n")
            file.write("\n")
            file.write("Directory")
            file.close()

        #open the save and read the data
        file = open("save.dat", "r")
        data = file.read()

        #split the data into lines
        lines = data.split("\n")
        if "Directory:" not in lines[0]:
            file.close()
            file = open("save.dat", "w")
            file.write("Directory: 4\n")
            file.write("Version: " + self.version + "\n")
            file.write("\n")
            file.write("Directory")
            file.close()
            file = open("save.dat", "r")
            data = file.read()  

        lines = data.split("\n")
        file.close()


        if lines[-1] == "":
            lines.pop(-1)
        
        #Get the current player names
        players = []
        for player in self.players:
            if player.loadout[0] != None: #The user hasn't rolled yet
                players.append(player)

        #Read in the directoryLocation
        directoryLocation = 0
        directoryLocation = lines[0].split(": ")[1]
        directoryLocation = int(directoryLocation)

        #get the saved player names
        savedPlayerNames = []
        i = directoryLocation + 1
        while i < len(lines):
            savedPlayerNames.append(lines[i])
            i += 2

        #See if we can simply quick save
        bQuickSave = True
        notSaved = []
        for i in range(len(players)):
            if players[i].playerName not in savedPlayerNames:
                bQuickSave = False
                notSaved.append(players[i].playerName)
        if not bQuickSave:
            #We have to make 1 or more new save profiles, and generate a new directory location
            blankProfile = [
                "Primary",
                "Secondary",
                "Grenade",
                "Stratagem1",
                "Stratagem2",
                "Stratagem3",
                "Stratagem4",
                "Rolls",
                "bHasLockedIn",
                "[]",
            ]
            profileLocation = directoryLocation - 1

            for i in range(len(notSaved)):
                if directoryLocation != 4:
                    lines.insert(profileLocation, "")
                    profileLocation += 1
                #Add a blank line
                savedPlayerNames.append(notSaved[i])
                # lines.insert(profileLocation, "\n")
                lines.insert(profileLocation, notSaved[i])
                for j in range(len(blankProfile)):
                    lines.insert(profileLocation + 1 + j, blankProfile[j])
                if directoryLocation == 4:
                    lines.insert(profileLocation + 1 + len(blankProfile), "")
                lines.append(notSaved[i])
                lines.append(str(profileLocation))
                profileLocation += 11
            #Update the directory location
            lines[0] = "Directory: " + str(profileLocation + 1)
            # lines.insert(profileLocation + 1, "\n")
            #Save the file
            file = open("save.dat", "w")
            for line in lines:
                file.write(line + "\n")
            file.close()
            bQuickSave = True


        
        if bQuickSave:
            #Quick save requires only that the player names are already in the save file, which means the file doesn't need to change in length
            #We can simply overwrite the data
            directoryLocation = int(lines[0].split(": ")[1])
            for i in range(len(players)):
                playerProfileLocation = int(lines[directoryLocation + 2 * (savedPlayerNames.index(players[i].playerName) + 1)])
                lines[playerProfileLocation + 1] = players[i].loadout[0]
                lines[playerProfileLocation + 2] = players[i].loadout[1]
                lines[playerProfileLocation + 3] = players[i].loadout[2]
                lines[playerProfileLocation + 4] = players[i].loadout[3]
                lines[playerProfileLocation + 5] = players[i].loadout[4]
                lines[playerProfileLocation + 6] = players[i].loadout[5]
                lines[playerProfileLocation + 7] = players[i].loadout[6]
                lines[playerProfileLocation + 8] = str(players[i].rolls)
                if players[i].lockInButton == None:
                    lines[playerProfileLocation + 9] = "True"
                else:
                    lines[playerProfileLocation + 9] = "False"
                if lines[playerProfileLocation + 10] == "[]":
                    lines[playerProfileLocation + 10] = "["
                    for i in range(len(players[i].modifiers)):
                        lines.insert(playerProfileLocation + 11 + i, players[i].modifiers[i].name)
                        directoryLocation += 1
                    lines.insert(playerProfileLocation + 11 + len(players[i].modifiers), "]")
                    directoryLocation += 1
                else:
                    #We'll have to clear the old modifiers
                    while lines[playerProfileLocation + 11] != "]":
                        lines.pop(playerProfileLocation + 11) #Remove the modifier
                        directoryLocation -= 1
                    for j in range(len(players[i].modifiers)):
                        lines.insert(playerProfileLocation + 11 + j, players[i].modifiers[j].__class__.__name__)
                        directoryLocation += 1

                #We'll have to update the directory location
                lines[0] = "Directory: " + str(directoryLocation)
                

            file = open("save.dat", "w")
            for line in lines:
                file.write(line + "\n")
            file.close()

    def changeProfileName(self, oldProfileName, newProfileName):
        try:
            file = open("save.dat", "r")
        except:
            return
        data = file.read()
        file.close()
        lines = data.split("\n")

        #Get the current player names
        playerNames = []
        for player in self.players:
            if player.loadout[0] != None: #The user hasn't rolled yet
                playerNames.append(player.playerName)

        #Read in the directoryLocation
        directoryLocation = 0
        directoryLocation = lines[0].split(": ")[1]
        directoryLocation = int(directoryLocation)

        i = directoryLocation + 1
        while i < len(lines):
            if lines[i] == oldProfileName:
                lines[i] = newProfileName
                profileLocation = int(lines[i + 1])
                lines[profileLocation] = newProfileName
                break
            i += 2

        file = open("save.dat", "w")
        for line in lines:
            file.write(line + "\n")
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
            if event.type == g.SAVEGAME:
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
        addPlayerButton1 = gameObjects.Button(None, (320, 180), functions=[self.addPlayer])
        addPlayerButton2 = gameObjects.Button(None, (960, 180), functions=[self.addPlayer])
        addPlayerButton3 = gameObjects.Button(None, (320, 540), functions=[self.addPlayer])
        addPlayerButton4 = gameObjects.Button(None, (960, 540), functions=[self.addPlayer])

        addPlayerButton1.positionByTopMiddle((320, 180))
        addPlayerButton2.positionByTopMiddle((960, 180))
        addPlayerButton3.positionByTopMiddle((320, 540))
        addPlayerButton4.positionByTopMiddle((960, 540))

        addPlayerButton1.setImage(self.fontRender.render("Add Player", True, (255, 0, 0)))
        addPlayerButton2.setImage(self.fontRender.render("Add Player", True, (255, 0, 0)))
        addPlayerButton3.setImage(self.fontRender.render("Add Player", True, (255, 0, 0)))
        addPlayerButton4.setImage(self.fontRender.render("Add Player", True, (255, 0, 0)))

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
        self.gameObjects.append(gameObjects.TextBox(int(center[0] - boxSize[0] * 0.5), int(center[1] - boxSize[1] * 0.5), 400, 200, "Enter your name", (255, 255, 255), (0, 0, 0), self.font))
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
        self.gameObjects.append(gameObjects.TextBox(int(center[0] - boxSize[0] * 0.5), int(center[1] - boxSize[1] * 0.5), 400, 200, self.players[playerNum - 1].playerName, (255, 255, 255), (0, 0, 0), self.font))
        self.gameObjects[-1].SetExitFunction(self.returnFromNameChange, [playerNum])

    #Refreshes the players in the game. Also saves the game.
    def refresh(self):
        self.saveGame()
        self.loadGame()

    #Removes a player from the game, allowing the user to add a new player in their place
    def removePlayer(self, playerNum):
        self.players.pop(playerNum - 1)
        self.refresh()





    #Opens a confirmation window to ensure the player wants to lock in their loadout
    def openConfirmBox(self, playerNum):
        if self.players[playerNum - 1].addingModifier:
            return

        #Confirms if the player wants to lock in
        #hide everything
        self.hideAll()

        #ARE YOU SURE YOU WANT TO LOCK IN? text
        textImage = gameObjects.gameTextImage("Are you sure you want to lock in?", (640, 180), self.font)
        textImage.positionByTopMiddle((640, 180))
        self.gameObjects.append(textImage)
        self.gameObjects[-1].show()

        #Create 2 buttons, one for yes, one for no
        for i in range(2):
            button = gameObjects.Button(None, (0, 0))
            self.gameObjects.append(button)
            position = textImage.getBottomMiddle()
            #Fun little bit of code, for 2 items, ((i - 0.5) * 2) will equal -1 for i = 0, and 1 for i = 1
            position = (position[0] + ((i - 0.5) * 2) * button.getWidth(), position[1] + 10)
            button.positionByTopMiddle(position)
            #Set the text of the buttons and their functions
            if i == 0:
                button.setImage(self.fontRender.render("Yes", True, (255, 0, 0)))
                button.addOnClickFunction(self.players[playerNum - 1].lockIn)
                button.addOnClickFunction(self.showAll)
            else:
                button.setImage(self.fontRender.render("No", True, (255, 0, 0)))
                button.addOnClickFunction(self.showAll)
            button.show()
        
        #Add the destroy functions to the buttons, so that they clean each other up
        for i in range(2):
            self.gameObjects[-(i + 1)].addOnClickFunction(self.gameObjects[-1].destroy)
            self.gameObjects[-(i + 1)].addOnClickFunction(self.gameObjects[-2].destroy)
            self.gameObjects[-(i + 1)].addOnClickFunction(textImage.destroy)

    #Shows all the game objects
    def showAll(self):
        for object in self.gameObjects:
            object.show()
        for player in self.players:
            player.show()

    #Hides all the game objects
    def hideAll(self):
        for object in self.gameObjects:
            object.hide()
        for player in self.players:
            player.hide()

    #Closes the text box for changing the player's name
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
        
        #if the name exists in the game, don't change the name
        currentPlayerNames = []
        for player in self.players:
            currentPlayerNames.append(player.playerName)
        if textBox.text in currentPlayerNames:
            return
        
        #if the name exists in the save file, save the game, change the name, and load the save
        #This is assuming the player simply wants to swap profiles
        if self.CheckForProfile(textBox.text):
            self.saveGame()
            self.players[playerNum - 1].playerName = textBox.text
            self.players[playerNum - 1].nameImage.setImage(self.fontRender.render(textBox.text, True, (255, 255, 255)))
            self.loadGame()
            return
        
        self.changeProfileName(self.players[playerNum - 1].playerName, textBox.text)
        self.players[playerNum - 1].playerName = textBox.text
        self.players[playerNum - 1].nameImage.setImage(self.fontRender.render(textBox.text, True, (255, 255, 255)))
        self.saveGame()

        

    def viewPrimaries(self, playerNum):
        if self.players[playerNum - 1].lockedIn:
            return

        #hide everything
        for object in self.gameObjects:
            object.hide()
        for player in self.players:
            player.hide()
        #we'll make buttons for each primary weapon, and a wild card, rows of 15
        #we'll also have a button to go back
        weaponNum, i, j = 0, 0, 0
        while weaponNum < len(g.PRIMARIES.keys()):
            for i in range(15):
                if weaponNum < len(g.PRIMARIES.keys()):
                    weapon = gameObjects.Button(self.primaryImages[weaponNum], (0, 0), functions=[self.returnFromPrimarySelection, self.players[playerNum - 1].replaceSlot], FunctionArgs=[[], [0, list(g.PRIMARIES.keys())[weaponNum]]])
                    weapon.positionByTopMiddle((80 + i * 80, 100 + j * 80))
                    #weapon.setImage(self.fontRender.render(PRIMARIES[weaponNum + i], True, (255, 0, 0)))
                    self.gameObjects.append(weapon)
                    weaponNum += 1
            j += 1

        backButton = gameObjects.Button(None, (0, 0), functions=[self.returnFromPrimarySelection])
        backButton.positionByTopMiddle((640, 540))
        backButton.setImage(self.fontRender.render("Back", True, (255, 0, 0)))
        self.gameObjects.append(backButton)

    def returnFromPrimarySelection(self):
        self.gameObjects = self.gameObjects[:len(self.gameObjects) - (len(g.PRIMARIES.keys()) + 1)] #remove all the buttons that will be at the end of the list
        self.showAll()
        
    def CheckForProfile(self, playerName):
        #checks if the profile exists in save.dat
        try:
            file = open("save.dat", "r")
        except:
            return False
        data = file.read()
        file.close()
        lines = data.split("\n")
        if "Directory:" not in lines[0] or lines[0] == "Directory: 4":
            return False
        directoryLocation = 0
        directoryLocation = lines[0].split(": ")[1]
        directoryLocation = int(directoryLocation)
        i = directoryLocation + 1
        while i < len(lines):
            if lines[i] == "":
                break
            if playerName == lines[i]:
                return True
            i += 2
        return False

    def returnFromTextBox(self):
        #remove the text box
        textBox = self.gameObjects.pop() #it'll always be the last object
        #show everything
        for object in self.gameObjects:
            object.show()
        for player in self.players:
            player.show()

        if textBox.text == "":
            return

        currentPlayerNames = []
        for player in self.players:
            currentPlayerNames.append(player.playerName)
        if textBox.text in currentPlayerNames:
            return            
        #remove the first button
        self.numPlayers += 1
        self.gameObjects.remove(self.addPlayerButtons[self.numPlayers - 1])   

        #TODO: replace this with a "Load profile" screen
        if self.CheckForProfile(textBox.text):
            self.players.append(Player(textBox.text, gameObjects.Button(None, (0, 0)), self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))
            self.loadGame()
            return
        


        if self.numPlayers == 1:
            #position a name at top middle of quadrant 1
            textImage = gameObjects.Button(self.fontRender.render(textBox.text, True, (255, 255, 255)), (320, 0), functions=[self.changeName], FunctionArgs=[[1]], RightClickFunctions=[self.removePlayer], RightClickFunctionArgs=[[1]])
            textImage.positionByTopMiddle((320, 0))
            self.gameObjects.append(textImage)
            
            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[0].onStart])
            startButton.image = self.fontRender.render("Start", True, (255, 255, 255))
            startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
            startButton.positionByTopMiddle(textImage.getBottomMiddle())
            self.gameObjects.append(startButton)

            self.players[0].lockInButton.functions.append(self.openConfirmBox)
            self.players[0].lockInButton.FunctionArgs.append([1])
            self.players[0].loadoutImages[0].functions = [self.viewPrimaries]
            self.players[0].loadoutImages[0].FunctionArgs = [[1]]
        elif self.numPlayers == 2:
            #position a name at top middle of quadrant 2
            textImage = gameObjects.Button(self.fontRender.render(textBox.text, True, (255, 255, 255)), (960, 0), functions=[self.changeName], FunctionArgs=[[2]], RightClickFunctions=[self.removePlayer], RightClickFunctionArgs=[[2]])
            textImage.positionByTopMiddle((960, 0))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[1].onStart])
            startButton.image = self.fontRender.render("Start", True, (255, 255, 255))
            startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
            startButton.positionByTopMiddle(textImage.getBottomMiddle())
            self.gameObjects.append(startButton)

            self.players[1].lockInButton.functions.append(self.openConfirmBox)
            self.players[1].lockInButton.FunctionArgs.append([2])
            self.players[1].loadoutImages[0].functions = [self.viewPrimaries]
            self.players[1].loadoutImages[0].FunctionArgs = [[2]]
        elif self.numPlayers == 3:
            #position a name at top middle of quadrant 3
            textImage = gameObjects.Button(self.fontRender.render(textBox.text, True, (255, 255, 255)), (320, 360), functions=[self.changeName], FunctionArgs=[[3]], RightClickFunctions=[self.removePlayer], RightClickFunctionArgs=[[3]])
            textImage.positionByTopMiddle((320, 360))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[2].onStart])
            startButton.image = self.fontRender.render("Start", True, (255, 255, 255))
            startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
            startButton.positionByTopMiddle(textImage.getBottomMiddle())
            self.gameObjects.append(startButton)

            self.players[2].lockInButton.functions.append(self.openConfirmBox)
            self.players[2].lockInButton.FunctionArgs.append([3])
            self.players[2].loadoutImages[0].functions = [self.viewPrimaries]
            self.players[2].loadoutImages[0].FunctionArgs = [[3]]
        elif self.numPlayers == 4:
            #position a name at top middle of quadrant 4

            textImage = gameObjects.Button(self.fontRender.render(textBox.text, True, (255, 255, 255)), (960, 360), functions=[self.changeName], FunctionArgs=[[4]], RightClickFunctions=[self.removePlayer], RightClickFunctionArgs=[[4]])
            #textImage.image = self.fontRender.render(textBox.text, True, (255, 255, 255))
            textImage.positionByTopMiddle((960, 360))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[3].onStart])
            startButton.image = self.fontRender.render("Start", True, (255, 255, 255))
            startButton.functions.append(startButton.destroy) #gross, but i cant be asked to make ANOTHER helper function
            startButton.positionByTopMiddle(textImage.getBottomMiddle())
            self.gameObjects.append(startButton)

            self.players[3].lockInButton.functions.append(self.openConfirmBox)
            self.players[3].lockInButton.FunctionArgs.append([4])
            self.players[3].loadoutImages[0].functions = [self.viewPrimaries]
            self.players[3].loadoutImages[0].FunctionArgs = [[4]]

    def draw(self):
        self.screen.fill((0, 0, 0))
        for object in self.gameObjects:
            object.draw(self.screen)
        for player in self.players:
            player.draw(self.screen)
        pg.display.flip()
        self.clock.tick(60)  

