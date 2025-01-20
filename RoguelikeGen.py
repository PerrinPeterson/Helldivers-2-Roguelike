import pygame as pg
import Game as hdr

#PERRIN: How to make an exe:
#1. Install pyinstaller
#1.5. If you haven't yet, run pyinstaller HD2RoguelikeGen/RoguelikeGen.py to create the necessary files
#2. Run the command: pyinstaller --onefile --noconsole --icon=icon.ico HD2RoguelikeGen/RoguelikeGen.py

# GEAR LISTS

if __name__ == "__main__":
    pg.init()
    pg.font.init()
    game = hdr.Game()
    game.startGame()
    game.run()

    