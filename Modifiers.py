#region test
#Modifiers are difficulty tweeks for the game, they are added when the player restarts the game, as a prestige system
class Modifier:
    def __init__(self):
        self.name = "Default Name - If you have this, something went wrong"
        self.description = "Default Description - If you have this, something went wrong"
        self.icon = None
        self.tier = 0
        self.upgrades = {} #{UpgradedModifier: [chance]}
        self.incompatibilities = [] #Modifiers that can't be active at the same time

#Implemented [/]     
class AllInMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "All In"
        self.description = "The ability to select 1 swap is removed.\nThe player must select all."
        self.tier = 3
        self.incompatibilities = [NoChoicesMod]

#Implemented [/]
class NoChoicesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "No Choices"
        self.description = "The player is not given any choices.\nA random selection is made for them, with a low chance to recieve all 3."
        self.tier = 3
        self.upgrades = {AllInMod: 0.1}

#Implemented [/]
class NoStrategemsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "No Strategems"
        self.description = "The player is not given any strategem choices.\n\nIf the player has a bonus choice,\nthey will get 1 strategem option per roll."
        self.tier = 3
        self.incompatibilities = [OopsOnlyTurretsMod, OopsOnlyWeaponsMod, OopsOnlyBackpacksMod, OopsOnlyEaglesMod, OopsOnlyOrbitalsMod, MoreStrategemsMod, LessGrenadesMod]

#Implemented [/]
class LessStrategemsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Less Strategems"
        self.description = "The chance to roll a strategem\nis reduced by 50%."
        self.tier = 2
        self.upgrades = {NoStrategemsMod: 1}
        self.incompatibilities = [MoreStrategemsMod]

#Implemented [/]
class MoreStrategemsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "More Strategems"
        self.description = "The chance to roll a strategem\nis increased by 50%."
        self.tier = 1
        self.upgrades = {LessStrategemsMod: 0.75, NoStrategemsMod: 0.25}

#Implemented [/]
class NoGrenadesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "No Grenades"
        self.description = "The player is not given\nany grenade choices."
        self.tier = 2
        self.upgrades = {KnivesOnlyMod: 1}

#Implemented [/]
class KnivesOnlyMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Knives Only"
        self.description = "The player is only given knife choices."
        self.tier = 3
        self.incompatibilities = [NoGrenadesMod]
        self.upgrades = {UnbindGrenadesMod: 0.1}

#Implemented [/]
class LessGrenadesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Less Grenades"
        self.description = "The chance to roll a grenade is reduced by 50%."
        self.tier = 2
        self.upgrades = {NoGrenadesMod: 1}

#Implemented [/]
class BaseGameOnlyMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Base Game Only"
        self.description = "The player is only given\nbase game choices.\n\nNon-Premium warbonds are included."
        self.tier = 3

#Implemented [/]
class OopsOnlyTurretsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Oops! All Turrets"
        self.description = "The strategem selections can\nonly consist of turrets."
        self.tier = 2
        self.incompatibilities = [NoStrategemsMod]
        self.upgrades = {OopsOnlyWeaponsMod: 0.1, OopsOnlyBackpacksMod: 0.1, OopsOnlyEaglesMod: 0.4, OopsOnlyOrbitalsMod: 0.4}

#Implemented [/]
class OopsOnlyWeaponsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Oops! All Weapons"
        self.description = "The strategem selections can\nonly consist of weapons."
        self.tier = 3
        self.incompatibilities = [NoStrategemsMod]
        self.upgrades = {OopsOnlyTurretsMod: 0.3, OopsOnlyBackpacksMod: 0.1, OopsOnlyEaglesMod: 0.3, OopsOnlyOrbitalsMod: 0.3}

#Implemented [/]
class OopsOnlyBackpacksMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Oops! All Backpacks"
        self.description = "The strategem selections can\nonly consist of backpacks."
        self.tier = 3
        self.incompatibilities = [NoStrategemsMod]
        self.upgrades = {OopsOnlyWeaponsMod: 0.1, OopsOnlyTurretsMod: 0.3, OopsOnlyEaglesMod: 0.3, OopsOnlyOrbitalsMod: 0.3}

#Implemented [/]
class OopsOnlyEaglesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Oops! All Eagles"
        self.description = "The strategem selections can\nonly consist of eagles."
        self.tier = 2
        self.incompatibilities = [NoStrategemsMod]
        self.upgrades = {OopsOnlyWeaponsMod: 0.1, OopsOnlyBackpacksMod: 0.1, OopsOnlyTurretsMod: 0.4, OopsOnlyOrbitalsMod: 0.4}

#Implemented [/]
class OopsOnlyOrbitalsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Oops! All Orbitals"
        self.description = "The strategem selections can\nonly consist of orbitals."
        self.tier = 2
        self.incompatibilities = [NoStrategemsMod]
        self.upgrades = {OopsOnlyWeaponsMod: 0.1, OopsOnlyBackpacksMod: 0.1, OopsOnlyEaglesMod: 0.4, OopsOnlyTurretsMod: 0.4}

#Implemented [/]
class IsMyLockInBrokenMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Is My Lock In Broken?"
        self.description = "The player has a random chance of having\ntheir loadout lock in automatically after a selection."
        self.tier = 3

#Implemented [/]
class MoreRollsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "More Rolls"
        self.description = "The player is given 2 additional rolls."
        self.tier = 1
        self.upgrades = {LessRollsMod: 0.9, EvenLessRollsMod: 0.1}

#Implemented [/]
class LessRollsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Less Rolls"
        self.description = "The player is given 6 fewer rolls."
        self.tier = 2
        self.incompatibilities = [MoreRollsMod]
        self.upgrades = {EvenLessRollsMod: 1}

#Implemented [/]
class EvenLessRollsMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Even Less Rolls"
        self.description = "The player is given 9 fewer rolls."
        self.tier = 3
        self.incompatibilities = [MoreRollsMod, LessRollsMod]

#Implemented [/]
class ScramblerMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Scrambler"
        self.description = "The player's choices\nhave a chance to be changed to a new one.\n\nThis was so fun in the game,\nwhy not here? /s"
        self.incompatibilities = [JammerMod]
        self.tier = 3

#Implemented [/] 
class JammerMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Jammer"
        self.description = "The players choices are hidden,\nonly the slots are shown."
        self.incompatibilities = [ScramblerMod]
        self.tier = 3

#Implemented [/]
class UnbindGrenadesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Unbind Grenades"
        self.description = "The player has to unbind all controls\nlinked to throwing grenades.\n('g' and '4' by default)"
        self.tier = 2
        self.incompatibilities = [NoGrenadesMod, LessGrenadesMod, KnivesOnlyMod]

#Implemented [/]
class MoreChoicesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "More Choices"
        self.description = "The player is given an\nadditional choice for each roll."
        self.tier = 1
        self.upgrades = {LessChoicesMod: 0.9, EvenLessChoicesMod: 0.1}

#Implemented [/]
class LessChoicesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Less Choices"
        self.description = "The player is given 1 fewer choice for each roll."
        self.tier = 2
        self.incompatibilities = [MoreChoicesMod]
        self.upgrades = {EvenLessChoicesMod: 1}

#Implemented [/]
class EvenLessChoicesMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Even Less Choices"
        self.description = "The player is given 2 fewer choices for each roll."
        self.tier = 3
        self.incompatibilities = [MoreChoicesMod, LessChoicesMod, AllInMod, JammerMod]

#Implemented [/]
class CuratedBuildMod(Modifier):
    def __init__(self):
        Modifier.__init__(self)
        self.name = "Curated Build"
        self.description = "The player is given a curated loadout.\nBut the player can't lock in for 3 rolls."
        self.tier = 1

#endregion

MODIFIERS = [AllInMod, NoChoicesMod, NoStrategemsMod, LessStrategemsMod, MoreStrategemsMod, NoGrenadesMod, KnivesOnlyMod, LessGrenadesMod, BaseGameOnlyMod, OopsOnlyTurretsMod, OopsOnlyWeaponsMod, OopsOnlyBackpacksMod, OopsOnlyEaglesMod, OopsOnlyOrbitalsMod, IsMyLockInBrokenMod, MoreRollsMod, LessRollsMod, EvenLessRollsMod, ScramblerMod, JammerMod, UnbindGrenadesMod, MoreChoicesMod, LessChoicesMod, EvenLessChoicesMod, CuratedBuildMod]