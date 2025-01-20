import pygame as pg
import math
import random
import numpy as np
import copy

class GameObject:
    def __init__(self, pos, image, parent = None, rotation = 0, scale = 1, opacity = 255):
        self.image = image
        self.BASEIMAGE = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hidden = False
        self.destroyed = False
        self.parent = parent
        self.rotation = rotation
        self.StoredRotation = rotation
        self.scale = scale
        self.opacity = opacity
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

    def draw(self, screen):
        if not self.hidden and not self.destroyed:
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
            #opacity
            s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
            s.blit(self.image, (0, 0))
            s.set_alpha(self.opacity)
            screen.blit(s, self.rect)

        if self.children != []:
            for child in self.children:
                child.draw(screen)
            for child in self.toDestroy:
                if child.destroy():
                    self.toDestroy.remove(child)
                else:
                    child.draw(screen)

class Button:
    #To use the function args, you must pass a list of the arguments you want to pass to the function
    def __init__(self, image, pos, function = None, functions = [], FunctionArgs = [], RightClickFunctions = [], RightClickFunctionArgs = [], heldFunctions = [], heldFunctionArgs = [], heldTimeLimit = 1, textOverlay = "", textOverlayFontPath = None, toolTip = "", toolTipEnabled = False):
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

        self.textOverlayImage = None
        self.textOverlay = textOverlay
        if self.textOverlay != "":
            self.font = pg.font.Font(textOverlayFontPath, 36)
            self.textOverlayImage = gameTextImage(self.textOverlay, self.rect.topleft, self.font, self.rect.width, self.rect.height)
        
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
        self.opacity = 255
        self.children = []
        self.toDestroy = []

        self.rightClickFunctions = []
        for i in range(len(RightClickFunctions)):
            self.rightClickFunctions.append(RightClickFunctions[i])
        self.rightClickFunctionArgs = []
        for i in range(len(RightClickFunctionArgs)):
            self.rightClickFunctionArgs.append(RightClickFunctionArgs[i])

        self.toolTip = toolTip
        self.toolTipImage = None
        self.toolTipBackground = None
        self.toolTipEnabled = toolTipEnabled
        if toolTip != "":
            self.toolTipBackground = Button(None, (0, 0))
            poition = (self.rect.centerx, self.rect.top - 10)
            self.toolTipBackground.positionByBottomMiddle(poition)   #Just temporary, we'll adjust the position later
            self.toolTipBackground.hide()
            self.toolTipImage = gameTextImage(toolTip, (0, 0), textOverlayFontPath, 300, 100)
            self.toolTipImage.positionByTopMiddle(poition)
            self.toolTipImage.hide()
        else:
            self.toolTipEnabled = False

        self.hoverTime = 0
        self.maxHoverTime = 120
        self.hoverPos = (0, 0)
        self.hoverPosForgiveness = 0 #in case the mouse moves a little bit, we don't want to instantly hide the tooltip





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
        child.setParent(self)
        


    #TODO: Preserve the original rect, so that we can recalculate the center and edges with the scale.
    #We'll just do what we did for gameTextImage, and use a temporary surface and rect to draw with the new scale
    def draw(self, screen):
        if not self.hidden and not self.destroyed: #if the object is destroyed, don't draw it, only draw its children, because we assume we're trying to clean them up
            tempRect = copy.deepcopy(self.rect)
            if self.image == None:
                # pg.draw.rect(screen, (255, 255, 255), self.rect)
                #Now with OPACITY
                s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
                s.fill((255, 255, 255, self.opacity))
                screen.blit(s, self.rect)
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
                    tempRect = self.image.get_rect()
                    tempRect.center = oldCenter
            else:
                #Handle the rotation
                if self.StoredRotation != self.rotation:
                    oldCenter = self.rect.center
                    originalImage = self.BASEIMAGE
                    self.image = originalImage
                    self.image = pg.transform.rotate(self.image, self.rotation)
                    tempRect = self.image.get_rect()
                    tempRect.center = oldCenter
                    self.StoredRotation = self.rotation
                if self.scale != 1:
                    oldCenter = self.rect.center
                    originalImage = self.BASEIMAGE
                    self.image = originalImage
                    self.image = pg.transform.scale(self.image, (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale)))
                    if self.StoredRotation != 0:
                        self.image = pg.transform.rotate(self.image, self.StoredRotation)
                    tempRect = self.image.get_rect()
                    tempRect.center = oldCenter
                #opacity
                s = pg.Surface((tempRect.width, tempRect.height), pg.SRCALPHA)
                s.blit(self.image, (0, 0))
                s.set_alpha(self.opacity)
                screen.blit(s, tempRect)

            if self.toolTipEnabled:
                self.toolTipBackground.draw(screen)
                self.toolTipImage.draw(screen)

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
        if self.toolTipEnabled:
            self.toolTipBackground.update()
            self.toolTipImage.update()
            if pg.mouse.get_pos() != self.hoverPos:
                self.hoverTime = 0
                if self.toolTipBackground.hidden == False:
                    self.toolTipBackground.hide()
                    self.toolTipImage.hide()
            #if the mouse is hovering over the button, increase the hover time
            if self.rect.collidepoint(pg.mouse.get_pos()):
                self.hoverPos = pg.mouse.get_pos()
            if pg.mouse.get_pos() == self.hoverPos and self.hoverTime < self.maxHoverTime and self.rect.collidepoint(pg.mouse.get_pos()):
                self.hoverTime += 1
            if self.hoverTime >= self.maxHoverTime and self.rect.collidepoint(pg.mouse.get_pos()):
                self.toolTipBackground.show()
                self.toolTipImage.show()
            
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
        x = self.rect.centerx
        y = self.rect.centery - self.rect.height * self.scale / 2
        return (x, y)
    
    def positionByBottomMiddle(self, pos):
        self.rect.bottom = pos[1]
        self.rect.centerx = pos[0]

    def getBottomMiddle(self):
        return (self.rect.centerx, self.rect.bottom)
    
    def positionByCenter(self, pos):
        self.rect.center = pos

    def getCenter(self):
        return self.rect.center
    


    def addOnClickFunction(self, function, args = []):
        self.functions.append(function)
        self.FunctionArgs.append(args)

    def addOnRightClickFunction(self, function, args = []):
        self.rightClickFunctions.append(function)
        self.rightClickFunctionArgs.append(args)

    def addOnHoldFunction(self, function, args = []):
        self.heldFunctions.append(function)
        self.heldFunctionArgs.append(args)
    
    def setOpacity(self, opacity):
        self.opacity = opacity
        
    def getOpacity(self):
        return self.opacity
    

    def handleInput(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = pg.mouse.get_pos()
                if self.isClicked(pos):
                    self.held = True
            if event.button == 3:
                pos = pg.mouse.get_pos()
                if self.isClicked(pos):
                    self.OnRightClick()
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

    def OnRightClick(self):
        for i in range(len(self.rightClickFunctions)):
            if self.rightClickFunctions[i] != None:
                #Maybe this works, maybe it doesn't. I'm not sure if this will work with multiple functions
                if len(self.rightClickFunctionArgs) > i:
                    #We know there is a list of parameters for this function in the list of function args
                    arguments = []
                    for j in range(len(self.rightClickFunctionArgs[i])):
                        arguments.append(self.rightClickFunctionArgs[i][j])
                    self.rightClickFunctions[i](*arguments)
                else:
                    self.rightClickFunctions[i]()
    
    def onHover(self):
        if self.toolTipEnabled:
            self.toolTip.show()

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

class gameTextImage():
    def __init__(self, text, pos, font, width = 0, height = 0, fontSize = 36, centerText = True):
        self.text = text
        self.font = pg.font.Font(font, fontSize)
        self.surface = pg.Surface((1, 1), pg.SRCALPHA)
        #Handling new lines by creating a new surface for each line
        lines = text.split("\n")
        self.images = []
        self.rects = []
        for line in lines:
            self.images.append(self.font.render(line, True, (255, 255, 255)))
            self.rects.append(self.images[-1].get_rect())
        self.pos = pos
        maxW = 0
        totalH = 0
        self.centerText = centerText
        for i in range(len(self.images)):
            if self.images[i].get_width() > maxW:
                maxW = self.images[i].get_width()
            totalH += self.images[i].get_height()
        self.surface = pg.Surface((maxW, totalH), pg.SRCALPHA)

        self.rect = self.surface.get_rect()
        self.scale = 1
        
        self.rect.topleft = pos
        self.hidden = False
        self.destroyed = False
        self.opacity = 255
        self.parent = None
        self.parentPos = [0, 0]
        self.parentOffset = [0, 0] 
        self.parentRotation = 0 
        self.parentScale = 1
        self.scaleLastFrame = 1


    def destroy(self):
        self.destroyed = True

    def positionByTopMiddle(self, pos):
        #updated for scaling
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
    
    def setParent(self, parent):
        self.parent = parent
        if self.parent != None:
            self.parentPos = parent.getCenter()
            self.parentOffset = [self.rect.center[0] - self.parentPos[0], self.rect.center[1] - self.parentPos[1]]
            self.parentOffset = [self.parentOffset[0] / self.parent.scale, self.parentOffset[1] / self.parent.scale] #Adjust the offset based on the parent's scale
            self.parentRotation = parent.rotation
            self.parentScale = parent.scale
            self.parent.children.append(self)
            self.scaleLastFrame = self.parent.scale
    
    def draw(self, screen):
        if not self.hidden:
            #transparency
            # s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
            # s.blit(self.image, (0, 0))
            # s.set_alpha(self.opacity)
            # screen.blit(s, self.rect)
            tempRect = copy.deepcopy(self.rect)
            if self.centerText:
                # Scale the images, keeping the same center point
                # Make a surface for the text, all at the base scale
                s = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
                #self.surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
                if self.images:
                    for i in range(len(self.images)):
                        s.blit(self.images[i], (self.rect.width // 2 - self.rects[i].width // 2, self.rects[i].height * i))
                    s.set_alpha(self.opacity)

                # Scale the surface
                oldCenter = self.rect.center
                s = pg.transform.scale(s, (int(s.get_width() * self.scale), int(s.get_height() * self.scale)))
                rect = s.get_rect()
                rect.center = oldCenter
                screen.blit(s, rect)
            else:
                for i in range(len(self.images)):
                    self.surface.blit(self.images[i], (0, self.rects[i].height * i))
                self.surface.set_alpha(self.opacity)
                screen.blit(self.surface, self.rect)


            

    def updateText(self, text):
        position = self.rect.center
        self.text = text
        self.images = []
        self.rects = []
        lines = text.split("\n")
        for line in lines:
            self.images.append(self.font.render(line, True, (255, 255, 255)))
            self.rects.append(self.images[-1].get_rect())
        maxW = 0
        totalH = 0
        for i in range(len(self.images)):
            if self.images[i].get_width() > maxW:
                maxW = self.images[i].get_width()
            totalH += self.images[i].get_height()
        self.surface = pg.Surface((maxW, totalH), pg.SRCALPHA)
        self.rect = self.surface.get_rect()
        self.rect.center = position


    def update(self):
        if self.parent is not None:
            # Update the position based on the parent's position, rotation, and scale
            self.pos = [self.parentPos[0] + self.parentOffset[0], self.parentPos[1] + self.parentOffset[1]]
            self.parentRotation = self.parent.rotation
            self.parentScale = self.parent.scale
            self.pos = self.rotatePoint(self.pos, self.parentPos, self.parentRotation)
            self.pos = self.scalePoint()

            #update internal scale, so we can adjust the text size based on the parent's scale
            if self.scaleLastFrame != self.parent.scale:
                self.scale += (self.parent.scale - self.scaleLastFrame) #Adjust the scale based on the difference between the last frame's scale and the current scale
                self.scaleLastFrame = self.parent.scale

            self.pos = [round(self.pos[0]), round(self.pos[1])]
            self.opacity = self.parent.getOpacity()
            self.rect.center = self.pos

    def rotatePoint(self, point, center, angle):
        angle = math.radians(-angle)
        x = point[0] - center[0]
        y = point[1] - center[1]
        x1 = x * math.cos(angle) - y * math.sin(angle)
        y1 = x * math.sin(angle) + y * math.cos(angle)
        return [x1 + center[0], y1 + center[1]]
    
    #Adjusts the position and scale based on the center of the parent and the new scale
    def scalePoint(self):
        x = self.parent.getCenter()[0] + self.parentOffset[0] * self.parent.scale
        y = self.parent.getCenter()[1] + self.parentOffset[1] * self.parent.scale
        return [x, y]




    def handleInput(self, event):
        pass

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def setOpacity(self, opacity):
        self.opacity = opacity

    def getOpacity(self):
        return self.opacity

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
        self.animationEndArgs = []
        self.animationEndFuncs = []
        

    def destroy(self):
        self.destroyed = True
        return True
    
    def setParent(self, parent):
        self.parent = parent
        parent.children.append(self)

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

    #Not sure if this will work, but it's worth a shot
    def flatten_outer(self, lst):
        """Helper function to flatten only the outermost list."""
        flattened = []
        for item in lst:
            if isinstance(item, list) and not all(isinstance(i, list) for i in item):
                flattened.extend(item)
            else:
                flattened.append(item)
        return flattened


    def update(self):
        for animation in self.animations:
            animation[0](*animation[1])

        if len(self.animations) == 0:
            for i in range(len(self.animationEndFuncs)):
                if len(self.animationEndArgs[i]) > 0:
                    self.animationEndFuncs[i](*self.animationEndArgs[i])
                else:
                    self.animationEndFuncs[i]()
            self.destroyed = True

    def lerpOpacityTo(self, opacity, time):
        self.animations.append([self.lerpOpacity, [opacity, self.index]])
        self.times.append((time, time))

    def lerpOpacity(self, opacity, timeIndex):
        start = self.parent.getOpacity()
        diff = opacity - start
        step = diff / self.times[timeIndex][0]
        start += step
        self.parent.setOpacity(int(start))
        self.times[timeIndex] = (self.times[timeIndex][0] - 1, self.times[timeIndex][1])
        if self.times[timeIndex][0] <= 0:
            self.animations.remove(self.animations[timeIndex])
            self.times.remove(self.times[timeIndex])
            self.index -= 1


    def setOnAnimationEnd(self, function, args = []):
        self.animationEndFuncs = [function]
        self.animationEndArgs = [args]
    
    def addOnAnimationEnd(self, function, args = []):
        self.animationEndFuncs.append(function)
        self.animationEndArgs.append(args)
        


    def draw(self, screen):
        pass

    def handleInput(self, event):
        pass

class TextBox():
    def __init__(self, x, y, width, height, text, color, textColor, font, fontSize = 36):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.textColor = textColor
        self.font = font
        self.fontRenderer = pg.font.Font(font, fontSize)
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
        text = self.fontRenderer.render(self.text, True, self.textColor)
        cursor = self.fontRenderer.render(self.cursor, True, self.textColor)
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


