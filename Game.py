import pygame as pg
import random
import PyGameObjects as gameObjects
import Globals as g

class Player:
    def __init__(self, playerName, playerNameImage, font, primaryImages, secondaryImages, grenadeImages, strategemImages, primaryChances, secondaryChances, grenadeChances, strategemChances, maxRolls = 12):
        self.playerName = playerName
        self.loadout = [None, None, None, None, None, None, None]
        self.rolls = 0
        self.nameImage = playerNameImage #So I can position everything based on the name image
        self.font = font
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

        #Create the roll and lock in buttons
        for i in range(2):
            button = gameObjects.Button(None, (0, 0))
            position = self.nameImage.getBottomMiddle()
            position = (position[0] + ((i - 0.5) * 2) * (button.getWidth()), position[1] + button.getHeight() * 3)
            button.positionByTopMiddle(position)
            button.hide()
            if i == 0:
                button.setImage(self.font.render("Roll", True, (255, 0, 0)))
                button.addOnClickFunction(self.roll)
                self.rollButton = button
            else:
                button.setImage(self.font.render("Lock In", True, (255, 0, 0)))
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
        
    #Replaces a loadout image with WILD text, if the user doesn't have access to the specific item
    def replaceWithWildCard(self, button):
        
        buttonSlotIndex = self.loadoutImages.index(button)
        newButton = gameObjects.Button(None, (0, 0))
        newButton.addOnHoldFunction(self.transitionToWildCard, [newButton])
        newButton.setImage(self.font.render("Wild", True, (255, 255, 0)))
        newButton.positionByCenter(button.getCenter())
        self.loadoutImages[self.loadoutImages.index(button)] = newButton

        if not button.destroy():
            self.ToDestroy.append(button)

        self.loadout[buttonSlotIndex] = "Wild"
        pg.event.post(pg.event.Event(g.SAVEGAME))

    #Starts the effects of transitioning to a WILD card
    def transitionToWildCard(self, button):
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
                self.loadoutImages[i].setImage(self.font.render("Wild", True, (255, 255, 0)))
            elif i == 0:
                self.loadoutImages[i].setImage(self.primaryImages[g.PRIMARIES.index(self.loadout[i])])
            elif i == 1:
                self.loadoutImages[i].setImage(self.secondaryImages[g.SECONDARIES.index(self.loadout[i])])
            elif i == 2:
                self.loadoutImages[i].setImage(self.grenadeImages[g.GRENADES.index(self.loadout[i])])
            else:
                self.loadoutImages[i].setImage(self.strategemImages[list(g.STRATEGEMS).index(self.loadout[i])])
                if "Backpack" in g.STRATEGEMS[self.loadout[i]] or "Weapon" in g.STRATEGEMS[self.loadout[i]]:
                    self.loadoutImages[i].functions.append(self.openReplacementMenu)
                    self.loadoutImages[i].FunctionArgs.append([i])
        self.nameImage.image = self.font.render(self.playerName, True, (255, 255, 255))
        self.nameImage.show()
        self.rollsTextImage.image = self.font.render("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls), True, (255, 255, 255))

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

    #handles button imputs for self and children
    def handleInput(self, event):
        for image in self.loadoutImages:
            image.handleInput(event)   
        for button in self.selectionButtons:
            button.handleInput(event)
        if self.rollButton != None:
            self.rollButton.handleInput(event)
        if self.lockInButton != None:
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

        #rolls a build and sets the loadout
        for i in range(len(self.loadout)):
            if i == 0:
                selection = random.choices(range(len(g.PRIMARIES)), self.primaries)[0]
                #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                self.primaries[selection] /= 1.5
                for j in range(len(self.primaries)):
                    if j != selection:
                        self.primaries[j] *= 1.01
                        if self.primaries[j] > 10:
                            self.primaries[j] = 10
                self.loadout[i] = g.PRIMARIES[selection]
                self.loadoutImages[i].setImage(self.primaryImages[selection])
            elif i == 1:
                selection = random.choices(range(len(g.SECONDARIES)), self.secondaries)[0]
                #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                self.secondaries[selection] /= 1.5
                for j in range(len(self.secondaries)):
                    if j != selection:
                        self.secondaries[j] *= 1.1
                        if self.secondaries[j] > 10:
                            self.secondaries[j] = 10
                self.loadout[i] = g.SECONDARIES[selection]
                self.loadoutImages[i].setImage(self.secondaryImages[selection])
            elif i == 2:
                selection = random.choices(range(len(g.GRENADES)), self.grenades)[0]
                #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                self.grenades[selection] /= 1.5
                for j in range(len(self.grenades)):
                    if j != selection:
                        self.grenades[j] *= 1.01
                        if self.grenades[j] > 10:
                            self.grenades[j] = 10
                self.loadout[i] = g.GRENADES[selection]
                self.loadoutImages[i].setImage(self.grenadeImages[selection])
            else:
                selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                currentBuild = self.loadout[3:i]
                bHasVehicle = False
                for strategem in currentBuild:
                    if "Vehicle" in g.STRATEGEMS[strategem]:
                        bHasVehicle = True
                        break
                while selection in currentBuild or ("Vehicle" in g.STRATEGEMS[selection] and bHasVehicle):
                    #if the strategem is already in the self.loadout, try again
                    selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                self.strategems[list(g.STRATEGEMS).index(selection)] /= 1.5
                for j in range(len(self.strategems)):
                    if j != list(g.STRATEGEMS).index(selection):
                        self.strategems[j] *= 1.01
                        if self.strategems[j] > 10:
                            self.strategems[j] = 10
                self.loadout[i] = selection
                self.loadoutImages[i].setImage(self.strategemImages[list(g.STRATEGEMS).index(selection)])
                if "Backpack" in g.STRATEGEMS[selection] or "Weapon" in g.STRATEGEMS[selection]:
                    self.loadoutImages[i].functions.append(self.openReplacementMenu)
                    self.loadoutImages[i].FunctionArgs.append([i])

        for image in self.loadoutImages:
            image.show()

        # #Create a roll gameObjects.Button
        self.rollButton.show()
        self.lockInButton.show()

        pg.event.post(pg.event.Event(g.SAVEGAME))


        # print("Player " + self.playerName + "'s Loadout:")
        # for i in range(len(self.loadout)):
        #     print(self.loadout[i])

    #Replaces a slot in the loadout with a new item
    def replaceSlot(self, slot, item):
        #if the slot is a primary, secondary, or grenade
        if slot < 3:
            if item in g.PRIMARIES:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.primaryImages[g.PRIMARIES.index(item)])
            elif item in g.SECONDARIES:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.secondaryImages[g.SECONDARIES.index(item)])
            elif item in g.GRENADES:
                self.loadout[slot] = item
                self.loadoutImages[slot].setImage(self.grenadeImages[g.GRENADES.index(item)])
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
        backButton.setImage(self.font.render("Back", True, (255, 0, 0)))
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

        #if the player is out of rolls, we lock in for them
        if self.rolls == self.maxRolls:
            self.lockIn()
        else:
            pg.event.post(pg.event.Event(g.SAVEGAME))

    #Rolls a few gear options for the player
    def roll(self):
        categoryChances = [1.3, 1.3, 1.3, 4] #Chance of getting a primary, secondary, grenade, or strategem. Strategems are weighted higher because theres 4 of them
        categorySelections = []
        #Roll 3 categories
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
                selection = random.choices(range(len(g.PRIMARIES)), self.primaries)[0]
                #ensure the selection isn't already in the build
                while g.PRIMARIES[selection] in self.loadout:
                    selection = random.choices(range(len(g.PRIMARIES)), self.primaries)[0]
                selections.append(g.PRIMARIES[selection])
                #reduce the chance of getting the same primary again, and increase the chance of getting the other ones
                self.primaries[selection] /= 1.5
                for j in range(len(self.primaries)):
                    if j != selection:
                        self.primaries[j] *= 1.01
                        if self.primaries[j] > 10:
                            self.primaries[j] = 10
            elif categorySelections[i] == 1:
                selection = random.choices(range(len(g.SECONDARIES)), self.secondaries)[0]
                #ensure the selection isn't already in the build
                while g.SECONDARIES[selection] in self.loadout:
                    selection = random.choices(range(len(g.SECONDARIES)), self.secondaries)[0]
                selections.append(g.SECONDARIES[selection])
                #reduce the chance of getting the same secondary again, and increase the chance of getting the other ones
                self.secondaries[selection] /= 1.5
                for j in range(len(self.secondaries)):
                    if j != selection:
                        self.secondaries[j] *= 1.01
                        if self.secondaries[j] > 10:
                            self.secondaries[j] = 10
            elif categorySelections[i] == 2:
                selection = random.choices(range(len(g.GRENADES)), self.grenades)[0]
                #ensure the selection isn't already in the build
                while g.GRENADES[selection] in self.loadout:
                    selection = random.choices(range(len(g.GRENADES)), self.grenades)[0]
                selections.append(g.GRENADES[selection])
                #reduce the chance of getting the same grenade again, and increase the chance of getting the other ones
                self.grenades[selection] /= 1.5
                for j in range(len(self.grenades)):
                    if j != selection:
                        self.grenades[j] *= 1.01
                        if self.grenades[j] > 10:
                            self.grenades[j] = 10
            else:
                selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                #ensure the selection isn't already in the build or that there isn't a discrepensy (like a second mech)
                bHasVehicle = False
                for item in selections:
                    if item in list(g.STRATEGEMS.keys()):
                        if "Vehicle" in g.STRATEGEMS[item]:
                            bHasVehicle = True
                            break
                while selection in self.loadout or selection in selections or ("Vehicle" in g.STRATEGEMS[selection] and bHasVehicle):
                    selection = random.choices(list(g.STRATEGEMS.keys()), self.strategems)[0]
                selections.append(selection)
                #reduce the chance of getting the same strategem again, and increase the chance of getting the other ones
                self.strategems[list(g.STRATEGEMS).index(selection)] /= 1.5
                for j in range(len(self.strategems)):
                    if j != list(g.STRATEGEMS).index(selection):
                        self.strategems[j] *= 1.01
                        if self.strategems[j] > 10:
                            self.strategems[j] = 10
        #For each Stratagem, select a random slot to replace. The entry in the list is the index of the selection
        strategemSlots = [0, 0, 0, 0]
        #find out how many self.strategems where selected
        strategemCount = 0
        for i in range(3):
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

        #We'll Create buttons under each of the slots we've chosen, so the player can select which one they want
        #We'll also create a button that lets them select all of them
        #Show the selections to the player, and let them choose which ones they want
        for i in range(len(selections)):
            slotNum = 0
            if i + 1 in strategemSlots:
                slotNum = 3 + strategemSlots.index(i+1)
            else:
                slotNum = categorySelections[i]
            button = gameObjects.Button(None, (0, 0), functions=[self.replaceSlot, self.madeDecision], FunctionArgs=[[slotNum, selections[i]]])
            if i + 1 in strategemSlots: #The index is in the self.strategems
                x = self.loadoutImages[3 + strategemSlots.index(i+1)].getCenter()[0]
                y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                button.positionByTopMiddle((x, y))
                button.image = self.strategemImages[list(g.STRATEGEMS).index(selections[i])]
            else:
                x = self.loadoutImages[categorySelections[i]].getCenter()[0]
                y = self.nameImage.getBottomMiddle()[1] + 80 + 10
                button.positionByTopMiddle((x, y))
                if selections[i] in g.PRIMARIES:
                    button.image = self.primaryImages[g.PRIMARIES.index(selections[i])]
                elif selections[i] in g.SECONDARIES:
                    button.image = self.secondaryImages[g.SECONDARIES.index(selections[i])]
                elif selections[i] in g.GRENADES:
                    button.image = self.grenadeImages[g.GRENADES.index(selections[i])]
            button.show()
            self.selectionButtons.append(button)

        #Create a button that lets the player select all of the options
        slotNums = [0, 0, 0]
        for i in range(3):
            if i + 1 in strategemSlots:
                slotNums[i] = 3 + strategemSlots.index(i+1)
            else:
                slotNums[i] = categorySelections[i]
        button = gameObjects.Button(None, (0, 0), functions=[self.replaceSlot, self.replaceSlot, self.replaceSlot, self.madeDecision], FunctionArgs=[[slotNums[0], selections[0]], [slotNums[1], selections[1]], [slotNums[2], selections[2]]])
        middleOfSlot3 = self.loadoutImages[3].getBottomMiddle()
        middleOfSlot3 = (middleOfSlot3[0], middleOfSlot3[1] + round(button.getHeight()))
        button.positionByTopMiddle(middleOfSlot3)
        button.setImage(self.font.render("All", True, (255, 0, 0)))
        button.show()
        self.selectionButtons.append(button)

        self.rolls += 1
        self.rollsTextImage.updateText("Rolls: " + str(self.rolls) + "/" + str(self.maxRolls))
        self.rollsTextImage.show()

        #Don't let the player lock in until they've made a decision
        self.rollButton.hide()
        self.lockInButton.hide()
        self.pendingChoice = True

    #Stops the player from making more decisions, this is the endgame
    def lockIn(self):
        self.lockedIn = True
        self.lockInButton.hide()
        self.rollButton.hide()
        self.childObjects.append(gameObjects.Button(self.font.render("Restart", True, (255, 0, 0)), (0, 0), function=self.onStart))
        x = self.nameImage.getBottomMiddle()[0]
        y = self.rollsTextImage.getBottomMiddle()[1] + 5
        self.childObjects[-1].positionByTopMiddle((x, y))
        self.childObjects[-1].show()
        pg.event.post(pg.event.Event(g.SAVEGAME))

class Game:
    def __init__(self):
        self.running = True
        self.clock = pg.time.Clock()
        self.font = pg.font.Font("Hacked-KerX.ttf", 36)
        self.screen = pg.display.set_mode((1280, 720))
        pg.display.set_caption("Helldivers Gear Generator")
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
                self.primaryImages.append(pg.image.load(g.IMAGEBASEPATH + g.PRIMARIES[i] + ".png"))
            except:
                self.primaryImages.append(None)
        self.secondaries = []
        self.secondaryImages = []
        for i in range(len(g.SECONDARIES)):
            self.secondaries.append(1)
            try:
                self.secondaryImages.append(pg.image.load(g.IMAGEBASEPATH + g.SECONDARIES[i] + ".png"))
            except:
                self.secondaryImages.append(None)
        self.grenades = []
        self.grenadeImages = []
        for i in range(len(g.GRENADES)):
            self.grenades.append(1)
            try:
                self.grenadeImages.append(pg.image.load(g.IMAGEBASEPATH + g.GRENADES[i] + ".png"))
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
            playerNameImage = gameObjects.Button(self.font.render(playerName, True, (255, 255, 255)), (0, 0), functions=[self.changeName], FunctionArgs=[[numPlayers]])
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
            
            player.loadoutImages[0].addOnClickFunction(self.viewPrimaries, [0])
            
            player.loadout = [lines[playerIndex + 1], lines[playerIndex + 2], lines[playerIndex + 3], lines[playerIndex + 4], lines[playerIndex + 5], lines[playerIndex + 6], lines[playerIndex + 7]]
            player.rolls = int(lines[playerIndex + 8])

            if lines[playerIndex + 9] == "True":
                player.rollButton = None
                player.lockInButton = None
            else:
                player.lockInButton.addOnClickFunction(self.openConfirmBox, [numPlayers])

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
            file.write("Directory: 3\n")
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
            file.write("Directory: 3\n")
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
        playerNames = []
        for player in self.players:
            playerNames.append(player.playerName)

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
        for i in range(len(playerNames)):
            if playerNames[i] not in savedPlayerNames:
                bQuickSave = False
                notSaved.append(playerNames[i])
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
            ]
            profileLocation = directoryLocation - 1

            for i in range(len(notSaved)):
                if directoryLocation != 3:
                    lines.insert(profileLocation, "")
                    profileLocation += 1
                #Add a blank line
                savedPlayerNames.append(notSaved[i])
                # lines.insert(profileLocation, "\n")
                lines.insert(profileLocation, notSaved[i])
                for j in range(len(blankProfile)):
                    lines.insert(profileLocation + 1 + j, blankProfile[j])
                if directoryLocation == 3:
                    lines.insert(profileLocation + 1 + len(blankProfile), "")
                lines.append(notSaved[i])
                lines.append(str(profileLocation))
                profileLocation += 10
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
            for i in range(len(playerNames)):
                playerProfileLocation = int(lines[directoryLocation + 2 * (savedPlayerNames.index(playerNames[i]) + 1)])
                lines[playerProfileLocation + 1] = self.players[i].loadout[0]
                lines[playerProfileLocation + 2] = self.players[i].loadout[1]
                lines[playerProfileLocation + 3] = self.players[i].loadout[2]
                lines[playerProfileLocation + 4] = self.players[i].loadout[3]
                lines[playerProfileLocation + 5] = self.players[i].loadout[4]
                lines[playerProfileLocation + 6] = self.players[i].loadout[5]
                lines[playerProfileLocation + 7] = self.players[i].loadout[6]
                lines[playerProfileLocation + 8] = str(self.players[i].rolls)
                if self.players[i].lockInButton == None:
                    lines[playerProfileLocation + 9] = "True"
                else:
                    lines[playerProfileLocation + 9] = "False"
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
        pg.event.post(pg.event.Event(g.SAVEGAME))   

    #Refreshes the players in the game. Also saves the game.
    def refresh(self):
        self.saveGame()
        self.loadGame()

    #Removes a player from the game, allowing the user to add a new player in their place
    def removePlayer(self, playerNum):
        #hide everything
        for object in self.gameObjects:
            object.hide()
        for player in self.players:
            player.hide()

        #remove the player
        self.gameObjects.remove(self.players[playerNum - 1].nameImage)
        self.players.pop(playerNum - 1)
        self.numPlayers -= 1

        #show everything
        for object in self.gameObjects:
            object.show()
        for player in self.players:
            player.show()

        self.refresh()
        pg.event.post(pg.event.Event(g.SAVEGAME))

    #Opens a confirmation window to ensure the player wants to lock in their loadout
    def openConfirmBox(self, playerNum):
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
                button.setImage(self.font.render("Yes", True, (255, 0, 0)))
                button.addOnClickFunction(self.players[playerNum - 1].lockIn)
                button.addOnClickFunction(self.showAll)
            else:
                button.setImage(self.font.render("No", True, (255, 0, 0)))
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
        while weaponNum < len(g.PRIMARIES):
            for i in range(15):
                if weaponNum < len(g.PRIMARIES):
                    weapon = gameObjects.Button(self.primaryImages[weaponNum], (0, 0), functions=[self.returnFromPrimarySelection, self.players[playerNum - 1].replaceSlot], FunctionArgs=[[], [0, g.PRIMARIES[weaponNum]]])
                    weapon.positionByTopMiddle((80 + i * 80, 100 + j * 80))
                    #weapon.setImage(self.font.render(PRIMARIES[weaponNum + i], True, (255, 0, 0)))
                    self.gameObjects.append(weapon)
                    weaponNum += 1
            j += 1

        backButton = gameObjects.Button(None, (0, 0), functions=[self.returnFromPrimarySelection])
        backButton.positionByTopMiddle((640, 540))
        backButton.setImage(self.font.render("Back", True, (255, 0, 0)))
        self.gameObjects.append(backButton)

    def returnFromPrimarySelection(self):
        self.gameObjects = self.gameObjects[:len(self.gameObjects) - (len(g.PRIMARIES) + 1)] #remove all the buttons that will be at the end of the list
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
        if "Directory:" not in lines[0] or lines[0] == "Directory: 3":
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
        #remove the first button
        self.numPlayers += 1
        self.gameObjects.remove(self.addPlayerButtons[self.numPlayers - 1])   

        #For testing purposes
        # particalArgs = [[0, 0], (255, 0, 0, 255), 3, [0, 0], 10, [1, 1], 60, True, 0.1, 30, 0.01]
        # particalGen = gameObjects.particalGenerator([600, 400], gameObjects.BasicParticle, particalCountPerFrame=10, particalConstructorArgs=particalArgs)
        # self.gameObjects.append(particalGen)

        # animator = gameObjects.Animator(particalGen)
        # animator.lerpTo([1000, 400], 60)
        # self.gameObjects.append(animator)

        #TODO: replace this with a "Load profile" screen
        if self.CheckForProfile(textBox.text):
            self.players.append(Player(textBox.text, gameObjects.Button(None, (0, 0)), self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))
            self.loadGame()
            return
        


        if self.numPlayers == 1:
            #position a name at top middle of quadrant 1
            textImage = gameObjects.Button(self.font.render(textBox.text, True, (255, 255, 255)), (320, 0), functions=[self.changeName], FunctionArgs=[[1]])
            textImage.positionByTopMiddle((320, 0))
            self.gameObjects.append(textImage)
            
            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[0].onStart])
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
            textImage = gameObjects.Button(self.font.render(textBox.text, True, (255, 255, 255)), (960, 0), functions=[self.changeName], FunctionArgs=[[2]])
            textImage.positionByTopMiddle((960, 0))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[1].onStart])
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
            textImage = gameObjects.Button(self.font.render(textBox.text, True, (255, 255, 255)), (320, 360), functions=[self.changeName], FunctionArgs=[[3]])
            textImage.positionByTopMiddle((320, 360))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[2].onStart])
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

            textImage = gameObjects.Button(self.font.render(textBox.text, True, (255, 255, 255)), (960, 360), functions=[self.changeName], FunctionArgs=[[4]])
            #textImage.image = self.font.render(textBox.text, True, (255, 255, 255))
            textImage.positionByTopMiddle((960, 360))
            self.gameObjects.append(textImage)

            self.players.append(Player(textBox.text, textImage, self.font, self.primaryImages, self.secondaryImages, self.grenadeImages, self.strategemImages, self.primaries, self.secondaries, self.grenades, self.strategems, maxRolls=self.MaxRolls))

            #Add a button to start under the player name
            startButton = gameObjects.Button(None, textImage.getBottomMiddle(), functions=[self.players[3].onStart])
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
        