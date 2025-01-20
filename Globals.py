import pygame as pg

PRIMARIES = {
    "Liberator" :               ["Liberator", "Assult Rifle", "Base Game"], 
    "Liberator Penatrator" :    ["Liberator", "Assult Rifle", "Mobilize"], 
    "Liberator Concussive":     ["Liberator", "Assult Rifle", "Steeled Veterans"],  
    "Liberator Carbine":        ["Liberator", "Assult Rifle", "Viper Commandos"], 
    "Tenderizer" :              ["Assult Rifle", "Polar Patriots"],
    "Adjudicator" :             ["Assult Rifle", "Democratic Detonation"],
    "Cookout" :                 ["Shotgun", "Pellets", "Incendiary", "Round Reloads", "Punisher", "Freedom's Flame"],
    "Purifier":                 ["Energy", "Charge", "Explosive", "Polar Patriots"],
    "Torcher":                  ["Special", "Incendiary", "Flamethrower", "Freedom's Flame"],
    "Knight":                   ["SMG", "One Handed", "Super Citizen"],  
    "Defender":                 ["SMG", "One Handed", "Mobilize"],
    "Pummeler":                 ["SMG", "One Handed", "Polar Patriots"],
    "Punisher":                 ["Shotgun", "Pellets", "Punisher", "Mobilize"],
    "Slugger":                  ["Shotgun", "Slugs", "Round Reloads", "Punisher", "Mobilize"],
    "Breaker":                  ["Breaker", "Shotgun", "Pellets", "Mobilize"],
    "Breaker Incendiary":       ["Breaker", "Shotgun", "Pellets", "Incendiary", "Steeled Veterans"],
    "Breaker Spray & Pray":     ["Breaker", "Shotgun", "Pellets", "Mobilize"],
    "Diligence":                ["Diligence", "Marksman", "Mobilize"], 
    "Diligence Counter Sniper": ["Diligence", "Marksman", "Mobilize"],
    "Scythe":                   ["Assualt Rifle", "Energy", "Lazer", "Cutting Edge"],
    "Sickle":                   ["Energy", "Lazer", "Cutting Edge"],
    "Scorcher":                 ["Energy", "Assault Rifle", "Explosive", "Mobilize"],
    "Punisher Plasma":          ["Energy", "Punisher", "Explosive", "Cutting Edge"],
    "Blitzer":                  ["Energy", "Shotgun", "Electricity", "Cutting Edge"],
    "Dominator":                ["Special", "Shotgun", "Electricity", "Steeled Veterans"],
    "Erupter":                  ["Explosive", "Marksman" "Shrapnel", "Democratic Detonation"],
    "Exploding Crossbow":       ["Explosive", "Crossbow", "Democratic Detonation"],
    "Reprimand":                ["SMG", "Truth Enforcers"],
    "Constitution":             ["Marksman", "Round Reload", "Base Game"],
    "Halt":                     ["Shotgun", "Round Reload", "Truth Enforcers"],
    }

SECONDARIES = {
    "Crisper":                  ["FlameThrower", "Incendiary", "Freedom's Flame"],
    "Dagger":                   ["Lazer", "Cutting Edge"],
    "Peacemaker":               ["Semi", "Base Game"],
    "Redeemer":                 ["Auto", "Semi", "Mobilize"],
    "Grenade Pistol":           ["Explosive", "Democratic Detonation"],
    "Verdict":                  ["Semi", "Polar Patriots"],
    "Senator":                  ["Semi", "Round Reload", "Steeled Veterans"],
    "Stim Pistol":              ["Support", "Chemical Agents"],
    "Bushwhacker":              ["Shotgun", "Semi", "Viper Commandos"],
    "Loyalist":                 ["Energy", "Charge", "Explosive", "Truth Enforcers"],
}

GRENADES = {
    "Gas Grenade":              ["Gas", "Chemical Agents"],
    "Throwing Knife":           ["Viper Commandos"],
    "High Explosive Grenade":   ["Explosive", "Base Game"],
    "Frag Grenade":             ["Explosive", "Shrapnel", "Mobilize"],
    "Impact Grenade":           ["Impact", "Explosive", "Mobilize"],
    "Smoke Grenade":            ["Non-Lethal", "Mobilize"],
    "Incendiary Grenade":       ["Incendiary", "Steeled Veterans"],
    "Stun Grenade":             ["Non-Lethal", "Cutting Edge"],
    "Thermite Grenade":         ["Incendiary", "Democratic Detonation"],
    "Incendiary Impact":        ["Incendiary", "Polar Patriots"],
}

STRATEGEMS = {
    "Eagle Strafing Run":           ["Eagle", "Base Game"],
    "Eagle Airstrike":              ["Eagle", "Base Game"],
    "Eagle Cluster Bomb":           ["Eagle", "Base Game"],
    "Eagle Napalm Strike":          ["Eagle", "Base Game"],
    "Eagle Smoke Strike":           ["Eagle", "Base Game"],
    "Eagle 110MM Rocket Pods":      ["Eagle", "Base Game"],
    "Eagle 500kg Bomb":             ["Eagle", "Base Game"],
    "Orbital Precision Strike":     ["Orbital", "Base Game"],
    "Orbital Airburst Strike":      ["Orbital", "Base Game"],
    "Orbital 120MM HE Barrage":     ["Orbital", "Base Game"],
    "Orbital 380MM HE Barrage":     ["Orbital", "Base Game"],
    "Orbital Walking Barrage":      ["Orbital", "Base Game"],
    "Orbital Laser":                ["Orbital", "Base Game"],
    "Orbital Railcannon Strike":    ["Orbital", "Base Game"],
    "Orbital Gatling Barrage":      ["Orbital", "Base Game"],
    "Orbital Gas Strike":           ["Orbital", "Base Game"],
    "Orbital EMS Strike":           ["Orbital", "Base Game"],
    "Orbital Smoke Strike":         ["Orbital", "Base Game"],
    "Orbital Napalm Barrage":       ["Orbital", "Base Game"],
    "Airburst Rocket Launcher":     ["Weapon", "Base Game"],
    "Autocannon":                   ["Weapon", "Base Game"],
    "Expendable Anti-Tank":         ["Weapon", "Base Game"],
    "Flamethrower":                 ["Weapon", "Base Game"],
    "Laser Cannon":                 ["Weapon", "Base Game"],
    "Stalwart":                     ["Weapon", "Base Game"],
    "Machine Gun":                  ["Weapon", "Base Game"],
    "Arc Thrower":                  ["Weapon", "Base Game"],
    "Grenade Launcher":             ["Weapon", "Base Game"],
    "Anti-Material Rifle":          ["Weapon", "Base Game"],
    "Railgun":                      ["Weapon", "Base Game"],
    "Recoilless Rifle":             ["Weapon", "Base Game"],
    "Spear":                        ["Weapon", "Base Game"],
    "Sterilizer":                   ["Weapon", "Chemical Agents"],
    "Quasar Cannon":                ["Weapon", "Base Game"],
    "Heavy Machine Gun":            ["Weapon", "Base Game"],
    "MLS-4X Commando":              ["Weapon", "Base Game"],
    "Guard Dog Dog Breath":         ["Backpack", "Chemical Agents"],
    "Guard Dog Rover":              ["Backpack", "Base Game"],
    "Guard Dog":                    ["Backpack", "Base Game"],
    "Jump Pack":                    ["Backpack", "Base Game"],
    "Supply Pack":                  ["Backpack", "Base Game"],
    "Shield Generator Pack":        ["Backpack", "Base Game"],
    "Ballistic Shield Backpack":    ["Backpack", "Base Game"],
    "Tesla Tower":                  ["Sentry", "Base Game"],
    "Mortar Sentry":                ["Sentry", "Base Game"],
    "EMS Mortar Sentry":            ["Sentry", "Base Game"],
    "Machine Gun Sentry":           ["Sentry", "Base Game"],
    "Gatling Sentry":               ["Sentry", "Base Game"],
    "Anti-Personnel Minefield":     ["Sentry", "Base Game"],
    "Anti-Tank Mines":              ["Sentry", "Base Game"],
    "Incendiary Mines":             ["Sentry", "Base Game"],
    "Shield Generator Relay":       ["Sentry", "Base Game"],
    "HMG Emplacement":              ["Sentry", "Base Game"],
    "Autocannon Sentry":            ["Sentry", "Base Game"],
    "Rocket Sentry":                ["Sentry", "Base Game"],
    "Patriot Exosuit":              ["Vehicle", "Base Game"],
    "Emancipator Exosuit":          ["Vehicle", "Base Game"],
}

CURATED_BUILDS = {
    "Perrin Bots" : ["Slugger", "Senator", "Thermite Grenade", "Orbital 120MM HE Barrage", "Shield Generator Pack", "Railgun", "Tesla Tower"],
    "Jordan Bots" : ["Dominator", "Stim Pistol", "Stun Grenade", "Orbital 120MM HE Barrage", "Eagle Strafing Run", "Orbital Precision Strike", "Recoilless Rifle"],
    "Perrin Bugs" : ["Breaker Incendiary", "Grenade Pistol", "Gas Grenade", "Orbital 120MM HE Barrage", "Orbital Napalm Barrage", "Autocannon", "Tesla Tower"],
    "Jordan Bugs" : ["Knight", "Stim Pistol", "Frag Grenade", "Orbital 120MM HE Barrage", "Orbital Precision Strike", "Machine Gun", "Supply Pack"],

    "Thor Build" : ["Blitzer", "Grenade Pistol", "Stun Grenade", "Tesla Tower", "Arc Thrower", "Shield Generator Pack", "Eagle 500kg Bomb"],
    "Fire Build" : ["Cookout", "Grenade Pistol", "Incendiary Grenade", "Orbital Napalm Barrage", "Flamethrower", "Eagle Napalm Strike", "Incendiary Mines"],
    "Fire Build 2" : ["Scorcher", "Crisper", "Incendiary Impact", "Orbital Napalm Barrage", "Flamethrower", "Eagle Napalm Strike", "Incendiary Mines"],
    "Gas Build" : ["Tenderizer", "Grenade Pistol", "Gas Grenade", "Orbital Gas Strike", "Sterilizer", "Guard Dog Dog Breath", "Gatling Sentry"],
    "Anti-Tank Build" : ["Breaker Incendiary", "Senator", "Stun Grenade", "Orbital Precision Strike", "Recoilless Rifle", "Orbital Railcannon Strike", "Rocket Sentry"],
    "Wave Clear" : ["Torcher", "Grenade Pistol", "Gas Grenade", "Flamethrower", "Orbital Napalm Barrage", "Eagle Napalm Strike", "Orbital Airburst Strike"]
}

SAVEGAME = pg.USEREVENT + 1
ENDGAME = pg.USEREVENT + 2
LOCKCONTROLS = pg.USEREVENT + 3
UNLOCKCONTROLS = pg.USEREVENT + 4
CONTINUE = pg.USEREVENT + 5

IMAGEBASEPATH = "HD2RoguelikeGen/HD2 Icons/"
DEFAULT_MOD_ICON = "HD2RoguelikeGen/Game Icons/DefaultIcon.png"
FONT_PATH = "Hacked-KerX.ttf"
SCREEN_SIZE = (1280, 720)