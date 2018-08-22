#!/usr/bin/env python3.6

import os
import struct
import json
from PIL import Image, ImageDraw

import tokens
from enum import Enum, IntFlag
from location import Location

# TODO: Not sure about this one...
directions = ['north', 'east', 'south', 'west']

classes = {
    0x00: "Fighter",
    0x01: "Ranger",
    0x02: "Paladin",
    0x03: "Mage",
    0x04: "Cleric",
    0x05: "Thief",
    0x06: "Fighter/Cleric",
    0x07: "Fighter/Thief",
    0x08: "Fighter/Mage",
    0x09: "Fighter/Mage/Thief",
    0x0A: "Thief/Mage",
    0x0B: "Cleric/Thief",
    0x0C: "Fighter/Cleric/Mage",
    0x0D: "Ranger/Cleric",
    0x0E: "Cleric/Mage",
    0x0F: '0x0F',
    0x10: '0x10'
}

races = {
    0x00: 'human male',
    0x01: 'human female',
    0x02: 'elf male',
    0x03: 'elf female',
    0x04: 'half-elf male',
    0x05: 'half-elf female',
    0x06: 'dwarf male',
    0x07: 'dwarf female',
    0x08: 'gnome male',
    0x09: 'gnome female',
    0x0A: 'halfling male',
    0x0B: 'halfling female',
}

alignments = {
    0x00: "Lawful Good",
    0x01: "Neutral Good",
    0x02: "Chaotic Good",
    0x03: "Lawful Neutral",
    0x04: "True Neutral",
    0x05: "Chaotic Neutral",
    0x06: "Lawful Evil",
    0x07: "Neutral Evil",
    0x08: "Chaotic Evil",
}


class ClassUage(IntFlag):
    """

    """
    Null = 0x00
    Fighter = 0x01
    Mage = 0x02
    Cleric = 0x04
    Thief = 0x08


class HandFlags(IntFlag):
    """

    """
    Primary = 0x0,
    Secondary = 0x1,
    Both = 0x2,


class ItemFlags(IntFlag):
    """
    Item's flags
    """
    Nothing = 0x00,
    Flag01 = 0x01
    ArmorBonus = 0x02
    Flag04 = 0x04           # Enchanted ??
    isVampiric = 0x08       # Sucks damage points from target to attacker
    SpeedBonus = 0x10
    isCursed = 0x20
    isIdentified = 0x40
    GlowMagic = 0x80


class ProfessionFlags(IntFlag):
    """

    """
    Fighter = 0x01    #
    Ranger = 0x02    #
    Paladin = 0x04    #
    Mage = 0x08    #
    Cleric = 0x10    #
    Thief = 0x20    #


class ItemSlotFlags(IntFlag):
    """

    """
    Quiver = 0x01,
    Armour = 0x02,
    Bracers = 0x04,
    Backpack = 0x08,
    Boots = 0x10,
    Helmet = 0x20,
    Necklace = 0x40,
    Belt = 0x80,
    Ring = 0x100,


ItemAction = {
    '0': 'Nothing',
    '1': '1',
    '2': 'Ammunition',
    '3': 'Use ammunition',
    '4': 'Amulet | coin | eye of talon...',
    '5': 'Open mage spell window',
    '6': 'Open cleric spell window',
    '7': "Food",
    '8': "Bones",
    '9': "Glass sphere | Magic dust | Scroll",
    '10': "Scroll",
    '11': "Parchment (something to read)",
    '12': "Stone item (Cross, Dagger, Gem...)",
    '13': "Key",
    '14': "Potion",
    '15': "Gem",
    '18': "0x12",
    '19': "Blow horn (N/S/W/E wind...)",
    '20': "Amulet of Life or Death",
    '128': "Range Party member",
    '129': "Range Close",
    '130': "Range Medium",
    '131': "Range Long",
    '132': "Lock picks",
    '138': "Amulet",
    '144': "Crimson ring",
    '146': "Wand",
}


class BinaryReader:
    """

    """
    def __init__(self, filename):

        self.filename = filename
        self.handle = None

    def __enter__(self):
        """

        :return:
        """
        self.handle = open(self.filename, 'rb')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        if self.handle:
            self.handle.close()
            self.handle = None

    @property
    def offset(self):
        """

        :return:
        """
        if not self.handle:
            return None

        return self.handle.tell()

    @property
    def offset_hex(self):
        """

        :return:
        """
        return hex(self.offset)

    def read_ubyte(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}B'.format(count=count), self.handle.read(count))

        if count == 1:
            return val[0]
        return val

    def read_byte(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}b'.format(count=count), self.handle.read(count))
        if count == 1:
            return val[0]
        return val

    def peek_ubyte(self, count=1):
        """

        :param count:
        :return:
        """
        s = struct.unpack('{count}B'.format(count=count), self.handle.read(count))
        self.handle.seek(-count, 1)
        if count == 1:
            return s[0]

        return list(s[:count])

    def peek_byte(self, count=1):
        """

        :param count:
        :return:
        """
        value = struct.unpack('{count}b'.format(count=count), self.handle.read(count))[0]
        self.handle.seek(-count, 1)
        return value

    def read_ushort(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}H'.format(count=count), self.handle.read(count*2))
        if count == 1:
            return val[0]
        return val

    def read_short(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}h'.format(count=count), self.handle.read(count*2))
        if count == 1:
            return val[0]
        return val

    def peek_ushort(self, count=1):
        """

        :param count:
        :return:
        """
        value = struct.unpack('{count}H'.format(count=count), self.handle.read(count*2))[0]
        self.handle.seek(-count * 2, 1)
        return value

    def peek_short(self, count=1):
        """

        :param count:
        :return:
        """
        value = struct.unpack('{count}h'.format(count=count), self.handle.read(count*2))[0]
        self.handle.seek(-count * 2, 1)
        return value

    def read_uint(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}I'.format(count=count), self.handle.read(count*4))
        if count == 1:
            return val[0]
        return val

    def read_int(self, count=1):
        """

        :param count:
        :return:
        """
        val = struct.unpack('{count}i'.format(count=count), self.handle.read(count*4))[0]
        if count == 1:
            return val[0]
        return val

    def read_string(self, length=0):
        """

        :param length:
        :return:
        """

        buff = struct.unpack('{length}s'.format(length=length), self.handle.read(length))[0]

        string = ''
        for c in buff:
            if c == 0:
                break
            string += chr(c)

        return string

    def peek_string(self, length=0):
        str = self.read_string(length)
        self.rewind(length)
        return str

    def search_string(self):
        """

        :return:
        """

        string = ''

        while True:
            b = self.read_ubyte()

            if b == 0x0:
                return string

            string += chr(b)

    def rewind(self, offset):
        """
        Move offset backward
        :param offset:
        :return:
        """

        self.handle.seek(-offset, 1)

    def seek(self, offset):
        """
        Set offset
        :param offset:
        :return:
        """

        self.handle.seek(offset)


class Monster:
    """
    flags:
    0 = default
    1 = ?
    2 = ?
    3 = ?
    4 = ?
    5 = ?
    6 = ?
    7 = ?
    8 = fear ?
    9 = ?
    10 = ?

        01h-> Active (fighting) has attacked MO_ACT
        02h-> is hit                        MO_HIT
        04h-> Flipflag                      MO_FLIP
        08h-> UNDEAD "Turned"               MO_TURNED
        10h-> set if "turned undead"        MO_FLEE
        20h-> turned to stone               MO_STONE
        40h-> Inactive (at start)           MO_INACT


    Phases:
         -1: raise weapon
         -2: Hit!
          0: Move forward
          1: Move Backwards
          2: Move Left
          3: Move Right
          4: Adjust-Turn
          5: Turn Left
          6: Turn Right
          7: AdjNextHit
          8: Inactive
          9: Walk
         10: Is Hit

    """

    def __init__(self, reader=None):
        """

        """
        self.index = None
        self.timer_id = None
        self.location = None
        self.sub_position = None
        self.direction = None
        self.type = None
        self.picture_index = None
        self.phase = None
        self.pause = None
        self.weapon = None
        self.pocket_item = None

        self.decode(reader)

    def decode(self, reader):
        if not reader:
            return

        self.index = reader.read_ubyte()
        self.timer_id = reader.read_ubyte()
        self.location = Location(reader)
        self.sub_position = reader.read_ubyte()
        self.direction = reader.read_ubyte()
        self.type = reader.read_ubyte()
        self.picture_index = reader.read_ubyte()
        self.phase = reader.read_ubyte()
        self.pause = reader.read_ubyte()
        self.pocket_item = reader.read_ushort()
        self.weapon = reader.read_ushort()

    def __str__(self):
        """

        :return:
        """

        return "ID {index} @ {location}|{subposition} [direction: {direction}, Timer:{timer}, type:{type}, " \
               "picture:{picture}, phase:{phase}, pause:{pause}, weapon:{weapon}, pocket:{pocket}]".format(
            index=self.index, location=self.location, subposition=self.sub_position, direction=directions[self.direction],
            timer=self.timer_id, type=self.type, picture=self.picture_index, phase=self.phase, pause=self.pause,
            weapon=self.weapon, pocket=self.pocket_item
        )


class Dice:
    """

    """
    def __init__(self, reader=None):
        self.rolls = 0
        self.sides = 0
        self.base = 0

        self.process(reader)

    def process(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.rolls = reader.read_ubyte()
        self.sides = reader.read_ubyte()
        self.base = reader.read_ubyte()

    def decode(self):
        return {
            'rolls': self.rolls,
            'sides': self.sides,
            'base': self.base,
        }

    def __str__(self):

        return "({rolls}d{sides})+{base}".format(rolls=self.rolls, sides=self.sides, base=self.base)


class Rectangle:
    """

    """
    x = 0
    y = 0
    width = 0
    height = 0

    def decode(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

    def __str__(self):
        """

        :return:
        """

        return "[x:{x} y:{y} - width:{width} height:{height}]".format(
            x=self.x, y=self.y, width=self.width, height=self.height
        )


class Point:
    """

    """
    x = 0
    y = 0

    def decode(self):
        return {
            "x": self.x,
            "y": self.y,
        }

    def __str__(self):
        """

        :return:
        """
        return "[x:{x} y:{y}]".format(x=self.x, y=self.y)


class WallMapping:
    """
    Wall-Types: Who can pass
    WF_PASSNONE			0x00  Can be passed by no one
    WF_PARTYPASS		0x01  Can be passed by the player, big item
    WF_SMALLPASS		0x02  Can be passed by a small item
    WF_MONSTERPASS		0x04  Can be passed by a monster
    WF_PASSALL			0x07  Can be passed by all
    WF_ISDOOR			0x08  Is a door
    WF_DOOROPEN			0x10  The door is open
    WF_DOORCLOSED		0x20  The door is closed
    WF_DOORKNOB			0x40  The door has a knob
    WF_ONLYDEC			0x80  No wall, only decoration, items visible

    Wall-Types: Kind
    WT_SOLID			0x01  Is a solid wall, draw top
    WT_SELFDRAW			0x02  Is a stair, for example, no bottom
    WT_DOORSTUCK		0x04  The door is stuck
    WT_DOORMOVES		0x08  The door is opening
    WT_DOOROPEN			0x10  The door is open
    WT_DOORCLOSED		0x20  The door is closed
    """

    def __init__(self):
        self.index = 0              # This is the index used by the .maz file
        self.type = 0               # Index to what backdrop wall type that is being used
        self.decorationId = 0       # Index to an optional overlay decoration image in the DecorationData.decorations
        # array in the [[eob.dat |.dat]] files
        self.eventMask = 0          #
        self.flags = 0              #

    @property
    def is_blocking(self):

        return self.flags & 0x00 == 0x00

    @property
    def is_door(self):

        return self.flags & 0x08 == 0x08

    def __str__(self):

        type = ""
        if self.type & 0x01 == 0x01: type += "WT_SOLID, "
        if self.type & 0x02 == 0x02: type += "WT_SELFDRAW, "
        if self.type & 0x04 == 0x04: type += "WT_DOORSTUCK, "
        if self.type & 0x08 == 0x08: type += "WT_DOORMOVES, "
        if self.type & 0x10 == 0x10: type += "WT_DOOROPEN, "
        if self.type & 0x20 == 0x20: type += "WT_DOORCLOSED, "

        flags = ""
        if self.flags & 0x00 == 0x00: flags += "WF_PASSNONE, "
        if self.flags & 0x01 == 0x01: flags += "WF_PARTYPASS, "
        if self.flags & 0x02 == 0x02: flags += "WF_SMALLPASS, "
        if self.flags & 0x04 == 0x04: flags += "WF_MONSTERPASS, "
        if self.flags & 0x07 == 0x07: flags += "WF_PASSALL, "
        if self.flags & 0x08 == 0x08: flags += "WF_ISDOOR, "
        if self.flags & 0x10 == 0x10: flags += "WF_DOOROPEN, "
        if self.flags & 0x20 == 0x20: flags += "WF_DOORCLOSED, "
        if self.flags & 0x40 == 0x40: flags += "WF_DOORKNOB, "
        if self.flags & 0x80 == 0x80: flags += "WF_ONLYDEC, "

        return "Type: {type} - Flags: {flags}".format(type=type, flags=flags)


class DecorationInfo:
    """

    """

    def __init__(self):
        self.files = None
        self.wallMapping = None

    def __str__(self):
        if self.files:
            return "File '{file}'".format(file=self.files)

        else:
            return "mapping '{mapping}'".format(mapping=self.wallMapping)


class DecorationFilename:
    """
    """

    def __init__(self):
        self.gfx = ""
        self.dec = ""

    def __str__(self):
        return 'gfx: {gfx}.cps - dec:{dec}'.format(gfx=self.gfx, dec=self.dec)


class ScriptTokens(Enum):
    TOKEN_SET_WALL = 0xff,
    TOKEN_CHANGE_WALL = 0xfe,
    TOKEN_OPEN_DOOR = 0xfd,
    TOKEN_CLOSE_DOOR = 0xfc,
    TOKEN_CREATE_MONSTER = 0xfb,
    TOKEN_TELEPORT = 0xfa,
    TOKEN_STEAL_SMALL_ITEMS = 0xf9,
    TOKEN_MESSAGE = 0xf8,
    TOKEN_SET_FLAG = 0xf7,
    TOKEN_SOUND = 0xf6,
    TOKEN_CLEAR_FLAG = 0xf5,
    TOKEN_HEAL = 0xf4,
    TOKEN_DAMAGE = 0xf3,
    TOKEN_JUMP = 0xf2,
    TOKEN_END = 0xf1,
    TOKEN_RETURN = 0xf0,
    TOKEN_CALL = 0xef,
    TOKEN_CONDITIONAL = 0xee,
    TOKEN_CONSUME = 0xed,
    TOKEN_CHANGE_LEVEL = 0xec,
    TOKEN_GIVE_XP = 0xeb,
    TOKEN_NEW_ITEM = 0xea,
    TOKEN_LAUNCHER = 0xe9,
    TOKEN_TURN = 0xe8,
    TOKEN_IDENTIFY_ITEMS = 0xe7,
    TOKEN_ENCOUNTER = 0xe6,
    TOKEN_WAIT = 0xe5,


class ConditionValue(Enum):
    OPERATOR_EQ = 0xff,
    OPERATOR_NEQ = 0xfe,
    OPERATOR_LT = 0xfd,
    OPERATOR_LTE = 0xfc,
    OPERATOR_GT = 0xfb,
    OPERATOR_GTE = 0xfa,
    OPERATOR_AND = 0xf9,
    OPERATOR_OR = 0xf8,
    VALUE_GET_WALL_NUMBER = 0xf7,
    VALUE_COUNT_ITEMS = 0xf5,
    VALUE_COUNT_MONSTERS = 0xf3,
    VALUE_CHECK_PARTY_POSITION = 0xf1,
    VALUE_GET_GLOBAL_FLAG = 0xf0,
    VALUE_END_CONDITIONAL = 0xee,
    VALUE_GET_PARTY_DIRECTION = 0xed,
    VALUE_GET_WALL_SIDE = 0xe9,
    VALUE_GET_POINTER_ITEM = 0xe7,
    VALUE_GET_TRIGGER_FLAG = 0xe0,
    VALUE_CONTAINS_RACE = 0xdd,
    VALUE_CONTAINS_CLASS = 0xdc,
    VALUE_ROLL_DICE = 0xdb,
    VALUE_IS_PARTY_VISIBLE = 0xda,
    VALUE_CONTAINS_ALIGNMENT = 0xce,
    VALUE_GET_LEVEL_FLAG = 0xef,


class Class(Enum):
    Fighter = 0x0,
    Ranger = 0x1,
    Paladin = 0x2,
    Mage = 0x3,
    Cleric = 0x4,
    Thief = 0x5,
    FighterCleric = 0x6,
    FighterThief = 0x7,
    FighterMage = 0x8,
    FighterMageThief = 0x9,
    ThiefMage = 0xa,
    ClericThief = 0xb,
    FighterClericMage = 0xc,
    RangerCleric = 0xd,
    ClericMage = 0xe,


class Race(Enum):
    HumanMale = 0x0,
    HumanFemale = 0x1,
    ElfMale = 0x2,
    ElfFemale = 0x3,
    HalfElfMale = 0x4,
    HalfElfFemale = 0x5,
    DwarfMale = 0x6,
    DwarfFemale = 0x7,
    GnomeMale = 0x8,
    GnomeFemale = 0x9,
    HalflingMale = 0xa,
    HalflingFemale = 0xb,


class Alignment(Enum):
    LawfullGood = 0,
    NeutralGood = 1,
    ChaoticGood = 2,
    LawfullNeutral = 3,
    TrueNeutral = 4,
    ChaoticNeutral = 5,
    LawfullEvil = 6,
    NeutralEvil = 7,
    ChaoticEvil = 8,


class DoorInfo:
    """
    http://eab.abime.net/showpost.php?p=533880&postcount=374
    http://eab.abime.net/showpost.php?p=579468&postcount=405
    """
    def __init__(self):
        self.command = None
        self.idx = None
        self.type = None
        self.knob = None
        self.gfxFile = ""
        self.doorRectangles = [Rectangle() for i in range(3)]        # rectangles in door?.cps size [3]
        self.buttonRectangles = [Rectangle() for i in range(2)]    # rectangles in door?.cps size [2]
        self.buttonPositions = [Point() for i in range(2)]         # x y position where to place door button size [2,2]

    def decode(self):
        return {
            "command": self.command,
            "idx": self.idx,
            "type": self.type,
            "knob": self.knob,
            "gfxFile": self.gfxFile,
            "doorRectangle": [rect.decode() for rect in self.doorRectangles],
            "buttons": {
                "rectangles": [rect.decode() for rect in self.buttonRectangles],
                "positions":  [point.decode() for point in self.buttonPositions],
            }
        }


class MonsterType:
    """

    """
    def __init__(self):
        self.index = 0
        self.unk0 = None
        self.thac0 = 0
        self.unk1 = None
        self.hp_dice = Dice()
        self.number_of_attacks = 0
        self.attack_dice = [Dice() for i in range(3)]
        self.special_attack_flag = 0
        self.abilities_flags = 0
        self.unk2 = None
        self.exp_gain = 0
        self.size = 0
        self.attack_sound = 0
        self.move_sound = 0
        self.unk3 = None
        self.is_attack2 = 0
        self.distant_attack = 0
        self.max_attack_count = 0
        self.attack_list = [None for i in range(5)]
        self.turn_undead_value = 0
        self.unk4 = None
        self.unk5 = [None for i in range(3)]

    def decode(self):
        return {
            "index": self.index,
            "unknown0": self.unk0,
            "thac0": self.thac0,
            "unknown1": self.unk1,
            "hp": self.hp_dice.decode(),
            "attacks": {
                "count": self.number_of_attacks,
                "dices": [dice.decode() for dice in self.attack_dice],
                "special_flags": self.special_attack_flag,
                "abilities_flags": self.abilities_flags,
                "sound": self.attack_sound,
                "distant": self.distant_attack,
            },
            "unknown2": self.unk2,
            "exp_gain": self.exp_gain,
            "size": self.size ,
            "move_sound": self.mouve_sound,
            "unknown3": self.unk3,
            "is_attack2": self.is_attack2,
            "max_attack_count": self.max_attack_count,
            "attack_list": [i for i in self.attack_list],
            "turn_undead": self.turn_undead_value,
            "unknown4": self.unk4,
            "unknown5": [i for i in self.unk5],
        }


class MonsterGfx:
    """

    """

    def __init__(self):
        self.used = False
        self.load_prog = None
        self.unk0 = None
        self.unk1 = None
        self.label = ""

    def decode(self):
        return {
            "used": self.used,
            "load_prog": self.load_prog,
            "unknown0": self.unk0,
            "unknown1": self.unk1,
            "label": self.label
        }

    def __str__(self):

        return self.label


class Trigger:
    """

    """

    def __init__(self, reader=None):
        """

        :param reader:
        """
        self.location = None
        self.flags = None
        self.offset = None

        self.decode(reader)

        """
        flags:
            A = 0x01,
            B = 0x02,
            C = 0x04,
            OnPartyEnter = 0x08,	# Confirmed
            D = 0x10,
            HoleOrPressure = 0x20,
            F = 0x40,
            G = 0x80,
            H = 0x100,
            I = 0x200,
            K = 0x400,
            OnClick = 0x800,
            M = 0x1000,
            N = 0x2000,
            O = 0x4000,
            P = 0x8000,
                        // item drop
                        // item taken
                        // party enter
                        // party leave
        
        """
    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.location = Location(reader)
        self.flags = reader.read_ushort()
        self.offset = reader.read_ushort()

    def run(self, maze, assets):
        """

        :return:
        """
        return {
            "offset": self.offset,
            "flags": self.flags,
        }

    def __str__(self):
        return "{location}: offset: 0x{offset:04X}, flags: 0x{flags:02X}".format(
            location=self.location, offset=self.offset, flags=self.flags
        )


class Header:
    """

    """
    def __init__(self):
        self.mazeName = None
        self.vmpVncName = None
        self.paletteName = None
        self.soundName = None
        self.doors = [DoorInfo() for i in range(2)]
        self.monsterGfx = [MonsterGfx() for i in range(2)]
        self.monsterTypes = [] # [MonsterType() for i in range(35)]
        self.decorations = []
        self.max_monsters = None
        self.next_hunk = None

    def decode(self):
        return {
            "mazeName": self.mazeName,
            "vmpVncName": self.vmpVncName,
            "palette": self.paletteName,
            "sound": self.soundName,
            "doors": [door.decode() for door in self.doors],
            "monsters": {
                "gfx": [gfx.decode() for gfx in self.monsterGfx],
                "types": [type.decode() for type in self.monsterTypes],
            },
            "decorations": [None for deco in self.decorations],
            "max_monsters": self.max_monsters,
            'next_hunk': self.next_hunk,
        }


class Script:
    """

    """
    def __init__(self, reader=None):
        """

        """
        self.tokens = {}

        self.decompile(reader)

    def decompile(self, reader):
        """

        :return:
        """
        if not reader:
            return

        start = reader.offset
        length = reader.read_ushort()

        while reader.offset < start + length:

            # if debug:
            #     print("[0x{:04X}]: ".format(reader.offset - start), end='')
            offset = reader.offset - start
            token = None
            opcode = reader.read_ubyte()
            if opcode == 0xff:
                token = tokens.SetWall(reader)
            elif opcode == 0xfe:
                token = tokens.ChangeWall(reader)
            elif opcode == 0xfd:
                token = tokens.OpenDoor(reader)
            elif opcode == 0xfc:
                token = tokens.CloseDoor(reader)
            elif opcode == 0xfb:
                token = tokens.CreateMonster(reader)
            elif opcode == 0xfa:
                token = tokens.Teleport(reader)
            elif opcode == 0xf9:
                token = tokens.StealSmallItem(reader)
            elif opcode == 0xf8:
                token = tokens.Message(reader)
            elif opcode == 0xf7:
                token = tokens.SetFlag(reader)
            elif opcode == 0xf6:
                token = tokens.Sound(reader)
            elif opcode == 0xf5:
                token = tokens.ClearFlag(reader)
            elif opcode == 0xf4:
                token = tokens.Heal(reader)
            elif opcode == 0xf3:
                token = tokens.Damage(reader)
            elif opcode == 0xf2:
                token = tokens.Jump(reader)
            elif opcode == 0xf1:
                token = tokens.End(reader)
            elif opcode == 0xf0:
                token = tokens.Return(reader)
            elif opcode == 0xef:
                token = tokens.Call(reader)
            elif opcode == 0xee:
                token = tokens.Conditional(reader)
            elif opcode == 0xed:
                token = tokens.ConsumeItem(reader)
            elif opcode == 0xec:
                token = tokens.ChangeLevel(reader)
            elif opcode == 0xeb:
                token = tokens.GiveXP(reader)
            elif opcode == 0xea:
                token = tokens.NewItem(reader)
            elif opcode == 0xe9:
                token = tokens.Launcher(reader)
            elif opcode == 0xe8:
                token = tokens.Turn(reader)
            elif opcode == 0xe7:
                token = tokens.IdentifyAllItems(reader)
            elif opcode == 0xe6:
                token = tokens.Sequence(reader)
            elif opcode == 0xe5:
                token = tokens.Wait(reader)
            elif opcode == 0xe4:
                token = tokens.UpdateScreen(reader)
            elif opcode == 0xe3:
                token = tokens.Dialog(reader)
            elif opcode == 0xe2:
                token = tokens.SpecialEvent(reader)

            if token:
                self.tokens[offset] = token
            else:
                print("###########[ERROR] unknown opcode: 0x{opcode:02X}".format(opcode=opcode))

    def run(self, maze, assets):
        for id, offset in enumerate(self.tokens):
            msg = self.tokens[offset].run(maze, assets)
            print('[0x{offset:04X}] {token}'.format(offset=offset, token=msg))


class Inf:
    """

    """
    def __init__(self, name):

        self.name = name
        self.timers = []
        self.monsters = []
        self.headers = [Header() for i in range(2)]
        self.hunks = [0, 0]
        self.triggers = []
        self.messages = []
        self.script = None

        self.width = 0
        self.height = 0
        # self.walls = []

    def process(self, filename):
        """

        :param filename:
        :return:
        """

        # http://grimwiki.net/wiki/EobConverter
        # LEVEL*.MAZ files are stored in PAK files, so you need to extract PAK to extract them first. MAZ files
        # contain dungeon layout (walls, doors, buttons etc.). It does not contain information about items.
        #
        # First 6 bytes constitute a header:
        #
        #     uint16_t width - specifies dungeon width (EOB1 levels always use 32)
        #     uint16_t height - specifies dungeon height (EOB1 levels always use 32)
        #     uint16_t unknown - EOB1 levels seem to have value 0x0004 here. One interpretation is that it may be a
        #                        number of bytes for each grid.
        #
        # Header is followed by width x height grid definitions. Each grid takes 4 bytes. For all EOB1 MAZ levels,
        # that gives 32x32x4 = 4096 bytes. Together with 6 bytes (header), this results in each file having length
        #  of 4102 bytes.
        #
        # Each grid is described by 4 octets. Each character specifies how a given grid looks from W, S, E and N,
        # respectively. It is possible to define inconsistent grids (e.g. look like doors when looked up front, but
        # look like a pressure plate when seen from sides).
        #
        #     0x00 - empty corridor
        #     0x01 - wall (pattern 1)
        #     0x02 - wall (pattern 2)
        #     0x03 - door without a button (closed) opening
        #     0x04 - door opening 1
        #     0x05 - door opening1
        #     0x07 - door opened
        #     0x08 - door with a button (closed)
        #     0x09 - door opening2
        #     0x0a - door opening2
        #     0x0b - door opening2
        #     0x0c - a ladder leading down
        #     0x0d - door with a button (open)
        #     0x11 - door opened
        #     0x12 - door closed
        #     0x13 - door opening4
        #     0x14 - door opening4
        #     0x15 - door opening4
        #     0x16 - door opened
        #     0x17 - up stair/ladder
        #     0x18 - fake ladder leading down (used in inaccessible part of level 1, probably by EOB developers for testing)
        #     0x19 - blocker
        #     0x1a - hole in the ceiling (from upper level)
        #     0x1b - pressure plate
        #     0x1c - pressure plate
        #     0x1d - normal alcove
        #     0x1f - pressure plate
        #     0x20 - switch
        #     0x23 - dalle(inter)
        #     0x24 - dalle(inter)
        #     0x25 - hole (ceilar)
        #     0x26 - hole (floor)
        #     0x27 - hidden button (large pushable brick)
        #     0x2a - hidden switch
        #     0x2b - drainage at the floor level (decoration)
        #     0x2c - "rat hole" - drainage at the floor level with eyes (decoration) or teleport
        #     0x33 - door to force
        #     0x36 - stone portal
        #     0x37 - lever
        #     0x3c - normal button, small brick sized
        #     0x3e - rat hole
        #     0x3f - sewer pipe (in the middle)
        #     0x41 - rune 'entrance'
        #     0x45 - cave-in or stone portal

        with BinaryReader(filename + '.INF') as reader:

            # hunk 1
            self.hunks[0] = reader.read_ushort()

            # region Headers
            for header in self.headers:

                if reader.offset < self.hunks[0]:
                    header.next_hunk = reader.read_ushort()
                    b = reader.read_ubyte()
                    if b == 0xEC:
                        header.mazeName = reader.read_string(13)
                        header.vmpVncName = reader.read_string(13)

                    b = reader.read_ubyte()
                    if b != 0xFF:
                        header.paletteName = reader.read_string(13)

                    header.soundName = reader.read_string(13)

                    # region Door name & Positions + offset
                    for door in header.doors:

                        b = reader.read_ubyte()
                        if b in (0xEC, 0xEA):
                            door.gfxFile = reader.read_string(13)
                            door.idx = reader.read_ubyte()
                            door.type = reader.read_ubyte()
                            door.knob = reader.read_ubyte()

                            for rect in door.doorRectangles:
                                rect.x = reader.read_ushort()
                                rect.y = reader.read_ushort()
                                rect.width = reader.read_ushort()
                                rect.height = reader.read_ushort()

                            for rect in door.buttonRectangles:
                                rect.x = reader.read_ushort()
                                rect.y = reader.read_ushort()
                                rect.width = reader.read_ushort()
                                rect.height = reader.read_ushort()

                            for pt in door.buttonPositions:
                                pt.x = reader.read_ushort()
                                pt.y = reader.read_ushort()
                    # endregion

                    # region Monsters graphics informations
                    header.max_monsters = reader.read_ushort()
                    for i in range(2):
                        b = reader.read_ubyte()
                        if b == 0xEC:
                            gfx = MonsterGfx()
                            gfx.load_prog = reader.read_ubyte()
                            gfx.unk0 = reader.read_ubyte()
                            gfx.label = reader.read_string(13)
                            gfx.unk1 = reader.read_ubyte()

                            header.monsterGfx[i] = gfx
                    # endregion

                    # region Monster definitions
                    while True:
                        b = reader.read_ubyte()
                        if b == 0xFF:
                            break

                        type = MonsterType()
                        type.index = b
                        type.unk0 = reader.read_ubyte()
                        type.thac0 = reader.read_ubyte()
                        type.unk1 = reader.read_ubyte()

                        type.hp_dice.process(reader)

                        type.number_of_attacks = reader.read_ubyte()
                        for dice in type.attack_dice:
                            dice.process(reader)

                        type.special_attack_flag = reader.read_ushort()
                        type.abilities_flags = reader.read_ushort()
                        type.unk2 = reader.read_ushort()
                        type.exp_gain = reader.read_ushort()
                        type.size = reader.read_ubyte()
                        type.attack_sound = reader.read_ubyte()
                        type.move_sound = reader.read_ubyte()
                        type.unk3 = reader.read_ubyte()

                        b = reader.read_ubyte()
                        if b != 0xFF:
                            type.is_attack2 = True
                            type.distant_attack = reader.read_ubyte()
                            type.max_attack_count = reader.read_ubyte()
                            for i in range(type.max_attack_count):
                                type.attack_list[i] = reader.read_ubyte()
                                reader.read_ubyte()

                        type.turn_undead_value = reader.read_byte()
                        type.unk4 = reader.read_ubyte()
                        type.unk5 = reader.read_ubyte(3)

                        header.monsterTypes.append(type)

                    # endregion

                    # region Wall decorations
                    b = reader.read_ubyte()
                    if b != 0xFF:
                        decorateblocks = reader.read_ushort()
                        for i in range(decorateblocks):
                            b = reader.read_ubyte()
                            deco = DecorationInfo()
                            if b == 0xEC:
                                deco.files = DecorationFilename()
                                deco.files.gfx = reader.read_string(13)
                                deco.files.dec = reader.read_string(13)
                            elif b == 0xFB:
                                deco.wallMapping = WallMapping()
                                deco.wallMapping.shapeId = reader.read_byte()
                                deco.wallMapping.type = reader.read_ubyte()
                                deco.wallMapping.decorationId = reader.read_byte()
                                deco.wallMapping.eventMask = reader.read_ubyte()
                                deco.wallMapping.flags = reader.read_ubyte()
                            else:
                                pass

                            header.decorations.append(deco)
                    # endregion

                    # Padding
                    while reader.read_uint() != 0xFFFFFFFF:
                        pass
            # endregion

            self.hunks[1] = reader.read_ushort()

            # region Monsters
            b = reader.read_ubyte()
            if b != 0xFF:
                # Timers
                while reader.read_ubyte() != 0xFF:
                    self.timers.append(reader.read_ubyte())

                # Descriptions
                for i in range(30):
                    monster = Monster()
                    monster.index = reader.read_byte()
                    monster.timer_id = reader.read_ubyte()
                    monster.location = Location(reader)
                    monster.sub_position = reader.read_ubyte()
                    monster.direction = reader.read_ubyte()
                    monster.type = reader.read_ubyte()
                    monster.picture_index = reader.read_ubyte()
                    monster.phase = reader.read_ubyte()
                    monster.pause = reader.read_ubyte()
                    monster.weapon = reader.read_ushort()
                    monster.pocket_item = reader.read_ushort()

                    self.monsters.append(monster)

            # endregion

            # Scripts
            self.script = Script(reader)

            # region Messages
            while reader.offset < self.hunks[1]:
                self.messages.append(reader.search_string())

            # endregion

            # region Triggers
            trigger_count = reader.read_ushort()
            for i in range(trigger_count):
                trigger = Trigger(reader)
                self.triggers.append(trigger)

            # endregion

    def decode(self, assets):
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "timers": [timer for timer in self.timers],
            "headers": [header.decode() for header in self.headers],
            "hunks": [hunk for hunk in self.hunks],
            "triggers": {trigger.location.coordinates(): trigger.run(self, assets) for trigger in self.triggers},
            "messages": {k: v for k, v in enumerate(self.messages)},
            "scripts": self.script.run(self, assets),
            "monsters": [],
        }


class Maz:
    """

    """
    def __init__(self):

        self.width = None
        self.height = None
        self.faces = None
        self.walls = []

    def process(self, filename):
        with BinaryReader('data/{file}.MAZ'.format(file=filename)) as reader:

            self.width = reader.read_ushort()
            self.height = reader.read_ushort()
            self.faces = reader.read_ushort()

            self.walls = [[None for y in range(self.height)] for x in range(self.width)]

            for y in range(self.height):
                for x in range(self.width):
                    n = reader.read_ubyte()
                    s = reader.read_ubyte()
                    w = reader.read_ubyte()
                    e = reader.read_ubyte()

                    self.walls[x][y] = {
                        'n': n,
                        's': s,
                        'w': w,
                        'e': e,
                    }

    def _decode(self):

        blocks = [['#' for y in range(self.height)] for x in range(self.width)]

        for y in range(self.height):
            for x in range(self.width):
                block = self.walls[y][x]

                if block['n'] == 0 and block['e'] == 0 and block['s'] == 0 and block['w'] == 0:
                    blocks[y][x] = " "

                # if block['n'] in (1, 2):
                #     blocks[y][x] = "#"
                #
                # if block['s'] in (1, 2) and y < self.height -1:
                #     blocks[y][x] = "#"
                #
                # if block['w'] in (1, 2):
                #     blocks[y][x] = "#"
                #
                # if block['e'] in (1, 2) and x < self.width -1:
                #     blocks[y][x] = "#"

                # if block['n'] == 0 and block['e'] == 0 and block['s'] == 0 and block['w'] == 0:
                #     wall = ' '
                # else:
                #     wall = '#'
                #
                # blocks[y][x] = wall

        return [''.join(row) for row in blocks]


class Champion(object):

    name = None

    def __str__(self):
        return "{name} ({classe})".format(name=self.name, classe=self.class_)


class Savegame:

    def __init__(self, filename):
        self._filename = filename
        self.champions = []

        with BinaryReader(filename) as reader:
            self.name = reader.read_string(20)

            # Champions
            for i in range(6):
                champion = Champion()
                champion.id = reader.read_ubyte()
                champion.flags = reader.read_ubyte()
                champion.name = reader.read_string(11)
                champion.strength = {
                    "current": reader.read_byte(),
                    "max": reader.read_byte()
                }
                champion.strength_extra = {
                    "current": reader.read_byte(),
                    "max": reader.read_byte()
                }

                champion.intelligence = reader.read_byte(2)
                champion.wisdom = reader.read_byte(2)
                champion.dexterity = reader.read_byte(2)
                champion.constitution = reader.read_byte(2)
                champion.charisma = reader.read_byte(2)
                champion.hitpoint = reader.read_short(2)
                champion.armorclass = reader.read_byte(1)
                champion.disabled_slots = reader.read_byte()

                champion.race = races[reader.read_byte()]
                champion.class_ = classes[reader.read_byte()]
                champion.alignment = alignments[reader.read_byte()]
                champion.portrait = reader.read_byte()
                champion.food = reader.read_byte()
                champion.level = reader.read_byte(3)

                champion.experience = reader.read_uint(3)

                champion.pad_01 = reader.read_ubyte(4)

                champion.mage_spells = reader.read_byte(80)
                champion.cleric_spells = reader.read_byte(80)
                champion.mage_spells_available_flags = reader.read_ushort()

                champion.pad_02 = reader.read_ushort(1)

                champion.hand_left = reader.read_ushort()
                champion.hand_right = reader.read_ushort()
                champion.backpack = reader.read_ushort(14)
                champion.quiver = reader.read_ushort()
                champion.armor = reader.read_ushort()
                champion.wrists = reader.read_ushort()
                champion.helmet = reader.read_ushort()
                champion.necklace = reader.read_ushort()
                champion.boots = reader.read_ushort()
                champion.belt = reader.read_ushort(3)
                champion.rings = reader.read_ushort(2)

                champion.timers = reader.read_uint(10)
                champion.events = reader.read_ubyte(10)
                champion.effects_remainder = reader.read_ubyte(4)
                champion.effect_flags = reader.read_uint()

                champion.damage_taken = reader.read_byte()
                champion.slot_status = reader.read_byte(5)

                champion.pad_03 = reader.read_ubyte(6)

                self.champions.append(champion)

            # Game states
            assert reader.offset == 2090
            self.current_level = reader.read_ushort()
            self.sub_position = reader.read_short()
            self.position = Location(reader)
            self.direction = directions[reader.read_ushort()]
            self.item_in_hand = reader.read_ushort()
            self.has_tmp_data = reader.read_ushort()
            self.party_effect_flags = reader.read_ushort()
            self.pad_02 = reader.read_byte()
            self.prevent_rest = reader.read_byte()
            self.state_flags = reader.read_ushort(18)
            self.pad_03 = reader.read_byte(40)

            # items
            self.items = []
            item_names = assets['item_names']
            assert reader.offset == 2182
            for i in range(600):
                item = {
                    "name_unidentified" : item_names[reader.read_ubyte()],
                    "name": item_names[reader.read_ubyte()],
                    "flags": reader.read_ubyte(),
                    "icon": reader.read_byte(),
                    "type": reader.read_byte(),
                    "position": reader.read_byte(),
                    "location": Location(reader),
                    "next": reader.read_short(),
                    "previous": reader.read_short(),
                    "level": reader.read_ubyte(),
                    "value": reader.read_byte(),
                }
                self.items.append(item)

            # Levels
            self.levels = []
            for id in range(17):
                level = {
                    "walls_encoded": reader.read_ubyte(1200)
                }
                # level['walls'] = decode_frame_4(level['walls_encoded'], 4096)

                monsters = []
                for i in range(30):
                    monster = Monster()
                    monster.type = reader.read_ubyte()
                    monster.unit = reader.read_ubyte()
                    monster.location = Location(reader)
                    monster.sub_position = reader.read_ubyte()
                    monster.direction = reader.read_ubyte()
                    monster.anim_step = reader.read_ubyte()
                    monster.frame = reader.read_ubyte()
                    monster.mode = reader.read_byte()
                    monster.f_9 = reader.read_byte()
                    monster.current_attack_frame = reader.read_ubyte()
                    monster.spell_status_left = reader.read_byte()
                    monster.hp_max = reader.read_short()
                    monster.hp_current = reader.read_short()
                    monster.dest = Location(reader)
                    monster.weapon = reader.read_ushort()
                    monster.pocket_item = reader.read_ushort()
                    monster.flags = reader.read_ubyte()
                    monster.idle_anim = reader.read_ubyte()
                    monster.remote_weapon = reader.read_byte()
                    monster.remote_attacks = reader.read_byte()
                    monster.palette = reader.read_byte()
                    monster.direction_changed = reader.read_byte()
                    monster.steps_until_remote_attack = reader.read_byte()
                    monster.pad_01 = reader.read_byte()

                    monsters.append(monster)
                level['monsters'] = monsters

                # Walls of force
                level['walls_of_force'] = []
                for i in range(5):
                    wof = {
                        "location": Location(reader),
                        "duration": reader.read_uint(),
                    }

                    level['walls_of_force'].append(wof)

                self.levels.append(level)

            # Game options
            assert reader.offset == 46792
            # reader.seek(46792)
            self.options = {
                "mouse_switch": reader.read_byte(),
                "with_sounds": reader.read_byte(),
                "bars_as_graph": reader.read_byte(),
            }

            # Special hand-spells which are special itemtypes [id from 51 to 57]
            # Offset: 46795
            assert reader.offset == 46795
            # reader.seek(46795)
            for i in range(51, 57):
                type = {
                    'slots':           str(ItemSlotFlags(reader.read_ushort())),
                    'flags':           str(ItemFlags(reader.read_ushort())),
                    'armor_class':     reader.read_byte(),
                    'allowed_classes': str(ProfessionFlags(reader.read_ubyte())),
                    'required_hand':   str(HandFlags(reader.read_ubyte())),
                    'damage_vs_small': str(Dice(reader)),
                    'damage_vs_big':   str(Dice(reader)),
                    'unknown':         reader.read_ubyte(),
                    'extra':           reader.read_ushort(),
                }
                assets['item_types'][i] = type

            c = self.champions[3]
            i = 1


def decode_frame_4(data, size):
    dst = [None] * size
    offset_src = 0
    offset_dst = 0

    while True:
        count = size - offset_dst
        if count == 0:
            break

        code = data[offset_src]
        offset_src += 1
        if (code & 0x80) != 0x80:
            length = min(count, (code >> 4) + 3)
            offs = ((code & 0xF) << 8)

        elif (code & 0x40) == 0x40:
            i = 2
        elif code != 0x80:
            length = min(count, code & 0x3F)
            for i in range(length):
                dst[offset_src + i] = data[offset_dst + i]
            offset_src += length
            offset_dst += length




def decode_itemtypes():
    """

    types:
     47 => rings
     31 => eatable/food
    """
    item_types = []
    with BinaryReader('data/ITEMTYPE.DAT') as reader:
        count = reader.read_ushort()
        for i in range(count):
            type = {
                # At which position in inventory it is allowed to be put. See InventoryUsage
                'slots': str(ItemSlotFlags(reader.read_ushort())),
                'flags': str(ItemFlags(reader.read_ushort())),
                'armor_class': reader.read_byte(),        # Adds to armor class
                'allowed_classes': str(ProfessionFlags(reader.read_ubyte())),    # Allowed for this profession. See ClassUsage
                'required_hand': str(HandFlags(reader.read_ubyte())),   # Allowed for this hand
                'damage_vs_small': str(Dice(reader)),
                'damage_vs_big': str(Dice(reader)),
                # 'damage_incs': reader.read_ubyte(),
                'unknown': reader.read_ubyte(),
                'extra': reader.read_ushort(),
            }

            item_types.append(type)

    return item_types
    # print("Item types :", json.dumps(item_types, indent=2, sort_keys=True))


def decode_items():
    items = []          # ITEM.DAT
    with BinaryReader('data/ITEM.DAT') as reader:
        count = reader.read_ushort()
        for i in range(count):
            item = {
                'unidentified_name': reader.read_ubyte(),
                'identified_name': reader.read_ubyte(),
                'flags': reader.read_ubyte(),
                'picture': reader.read_ubyte(),
                'type': reader.read_ubyte(),           # See types below

                # Where the item lies at position
                # In Maze:
                #      0..3-> Bottom
                #      4..7-> Wall (N,E,S,W)
                # For EotB I: 0..3-> Floor NW,NE,SW,SE
                #                8-> Compartment
                # If in inventory:
                #      0..26-> Position in Inventory
                'sub_position': reader.read_ubyte(),

                # Position in maze x + y * 32 | 0 => Consumed
                'coordinate': reader.read_ushort(),
                'next': reader.read_ushort(),
                'previous': reader.read_ushort(),

                # Level, where the item lies, 0 <= no level
                'level': reader.read_ubyte(),

                # The value of item, -1 if consumed
                'value': reader.read_byte(),
            }
            pos = divmod(item['coordinate'], 32)
            item['coordinate'] = {'x': pos[1], 'y': pos[0]}
            items.append(item)

        count = reader.read_ushort()
        for i in range(count):
            name = reader.read_string(35)
            assets['item_names'].append(name)

        for item in items:
            item['unidentified_name'] = assets['item_names'][item['unidentified_name']]
            item['identified_name'] = assets['item_names'][item['identified_name']]

    return items


def decode_maz():
    # Read wall decorations
    files = [
        'LEVEL1',
        'LEVEL2',
        'LEVEL3',
        'LEVEL4',
        'LEVEL5',
        'LEVEL6',
        'LEVEL7',
        'LEVEL8',
        'LEVEL9',
        'LEVEL10',
        'LEVEL11',
        'LEVEL12',
        'LEVEL13',
        'LEVEL14',
        'LEVEL15',
    ]
    mazes = {}
    for file in files:

        maze = Maz()
        maze.process(file)
        mazes[file] = maze

    return mazes


def decode_inf():
    # .INF
    files = [
        'LEVEL1',
        'LEVEL2',
        'LEVEL3',
        'LEVEL4',
        'LEVEL5',
        'LEVEL6',
        'LEVEL7',
        'LEVEL8',
        'LEVEL9',
        'LEVEL10',
        'LEVEL11',
        'LEVEL12',
        'LEVEL13',
        'LEVEL14',
        'LEVEL15',
        'LEVEL16',
    ]
    infs = {}

    for file in files:
        inf = Inf(file)
        inf.process('data/{file}'.format(file=file))
        infs[file] = level

    return infs


def decode_dec():
    # .DEC

    files = ['AZURE.DEC', 'BROWN.DEC', 'CRIMSON.DEC', 'FOREST.DEC', 'MEZZ.DEC', 'SILVER.DEC']
    decorations = {}

    for file in files:
        decorations[file] = {
            'decorations': [],
            'shapes': [],
        }
        with BinaryReader('data/{file}'.format(file=file)) as reader:
            count = reader.read_ushort()

            for i in range(count):
                deco = {
                    'shapes':  [-1 if value == 255 else value for value in reader.read_ubyte(10)],
                    'next':    reader.read_byte(),
                    'flags':   reader.read_byte(),          # horizontal/vertical flip ?
                    'shape_x': reader.read_short(10),
                    'shape_y': reader.read_short(10),
                }
                decorations[file]['decorations'].append(deco)

            count = reader.read_ushort()
            for i in range(count):
                rect = list(reader.read_ushort(4))
                rect[0] *= 8
                rect[2] *= 8
                decorations[file]['shapes'].append(rect)

    return decorations


def decode_texts():
    file = 'data/TEXT.DAT'
    offsets = []
    msg = []
    with BinaryReader(file) as reader:
        while True:
            offset = reader.read_ushort()
            offsets.append(offset)
            if reader.offset >= offsets[0]:
                break

        for id, offset in enumerate(offsets):

            if id == len(offsets) - 1:
                length = os.path.getsize(file) - offsets[id]
            else:
                length = offsets[id + 1] - offsets[id]

            msg.append(reader.read_string(length))

    return msg


def decode_vmp():
    files = ['CRIMSON.VMP', 'DUNG.VMP', 'FOREST.VMP', 'MEZZ.VMP', 'SILVER.VMP']
    vmp = {}

    for file in files:

        with BinaryReader('data/{file}'.format(file=file)) as reader:
            count = reader.read_ushort()
            codes = reader.read_ushort(count)

        vmp[file] = {
            'count': count,
            'codes': codes,
        }

    return vmp


def decode_pal():

    files = [ 'AZURE.PAL', 'CRIMSON.PAL', 'DUNG.PAL', 'FINALE_0.PAL', 'FINALE_1.PAL', 'FINALE_2.PAL', 'FINALE_3.PAL',
              'FINALE_4.PAL', 'FINALE_5.PAL', 'FINALE_6.PAL', 'FINALE_7.PAL', 'FOREST.PAL', 'MEZZ.PAL', 'PALETTE0.PAL',
              'PALETTE1.PAL', 'PALETTE2.PAL', 'PALETTE3.PAL', 'PALETTE4.PAL', 'SILVER.PAL' ]
    pal = {}

    for file in files:
        colors = []

        with BinaryReader('data/{file}'.format(file=file)) as reader:
            for i in range(256):
                r = reader.read_byte()
                g = reader.read_byte()
                b = reader.read_byte()

                colors.append({
                    "r": r,
                    "g": g,
                    "b": b,
                })

                i = 1

        pal[file] = colors

    return pal





def decode_vcn():
    files = ['CRIMSON.VCN', 'DUNG.VCN', 'FOREST.VCN', 'MEZZ.VCN', 'SILVER.VCN']
    vcn = {}

    for file in files:
        vcn[file] = {}

        with BinaryReader('data/{file}'.format(file=file)) as reader:
            data = decode_format80(reader)

            with open("data/{file}.uncps".format(file=file), "wb") as handle:
                s = struct.pack('{count}B'.format(count=len(data)), *data)
                handle.write(s)

            # continue
        with BinaryReader('data/{file}.uncps'.format(file=file)) as reader:

            vcn[file]['count'] = reader.read_ushort()
            vcn[file]['palette_backdrop'] = reader.read_ubyte(16)
            vcn[file]['palette_wall'] = reader.read_ubyte(16)
            shapes = []
            for i in range(vcn[file]['count']):
                raw = reader.read_byte(32)
                shapes.append(raw)
            vcn[file]['shapes'] = shapes
            i = 1

    return vcn


def decode_format80(reader):
    size = reader.read_ushort()
    type = reader.read_ushort()
    uncompressed = reader.read_uint()
    palette = reader.read_ushort()

    if type != 0x4:
        raise TypeError

    data = [None] * uncompressed
    dst_offset = 0
    while True:
        code = reader.read_ubyte()

        # end code
        if code == 0x80:
            return data

        # 0b10######
        elif code & 0xC0 == 0x80:
            count = code & 0x3f
            for i in range(count):
                data[dst_offset] = reader.read_ubyte()
                dst_offset += 1

        # 0b11######
        elif code & 0xC0 == 0xC0:
            count = code & 0x3f

            # Large copy
            if count < 0x3E:
                count += 3
                offset = reader.read_ushort()
                for i in range(offset, offset + count):
                    data[dst_offset] = data[i]
                    dst_offset += 1

            # Very large copy
            elif count == 0x3F:
                pass

            else:
                i = 1

        # 0b0#######
        elif code & 0x80 == 0:
            count = ((code & 0x70) >> 4) + 3
            offset = reader.read_ubyte() + ((code & 0x0F) << 8)
            offset = dst_offset - offset
            for i in range(offset, offset + count):
                data[dst_offset] = data[i]
                dst_offset += 1

        else:
            i = 1





def decode_dcr():
    files = ['BEHOLDER.DCR', 'CLERIC1.DCR', 'CLERIC2.DCR', 'CLERIC3.DCR', 'DRAGON.DCR', 'GUARD1.DCR', 'GUARD2.DCR', 'MAGE.DCR', 'MANTIS.DCR']
    dcr = {}

    for file in files:
        dcr[file] =  []
        with BinaryReader('data/{file}'.format(file=file)) as reader:
            count = reader.read_ushort()
            for i in range(count):
                sides = []
                for j in range(6):
                    side = {
                        "cps_x": reader.read_ubyte() * 8,
                        "cps_y": reader.read_ubyte(),
                        "width": reader.read_ubyte() * 8,
                        "height": reader.read_ubyte(),
                        "screen_x": reader.read_ubyte(),
                        "screen_y": reader.read_ubyte()
                    }

                    sides.append(side)
                dcr[file].append(sides)

            i = 1
    return dcr


def dump(name, data):
    path = './build'
    if not os.path.exists(path):
        os.makedirs(path)

    with open('{path}/{name}'.format(path=path, name=name), 'w') as handle:
        json.dump(data, handle, indent=True, sort_keys=True)


def generate_decorations():
    path = "build/"
    for name in assets['decorations']:
        decoration = assets['decorations'][name]
        img = Image.new('RGB', (320, 200))

        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 640, 480], 'white')
        for rect in decoration['rectangles']:
            x = rect[0]
            y = rect[1]
            right = x + rect[2]
            bottom = y + rect[3]
            d.rectangle([x, y, right, bottom], 'blue', 'red')

        img.save('{path}{name}.png'.format(path=path, name=name))


def gen_crimson():
    deco = assets['decorations']['CRIMSON.DEC']
    cps = Image.open('data/CRIMSON.PNG')

    img = Image.new('RGB', (320, 200))


    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 640, 480], 'white')

    for rect in deco['rectangles']:
        x = rect[0]
        y = rect[1]
        right = x + rect[2]
        bottom = y + rect[3]

        region = cps.crop([x, y, right, bottom])
        img.paste(region,box=[x, y])

        img.save('build/CRIMSON_decoded.PNG')

        i = 1


def draw_dec():
    files = ['AZURE', 'BROWN', 'CRIMSON', 'FOREST', 'MEZZ', 'SILVER']

    for file in files:
        dec = assets['dec'][file + '.DEC']
        i = 1


def draw_vmp():
    files = ['CRIMSON', 'DUNG', 'FOREST', 'MEZZ', 'SILVER']

    for file in files:
        vcn = assets['vcn'][file + '.VCN']
        vmp = assets['vmp'][file + '.VMP']
        i = 1


def draw_dcr():
    files = ['BEHOLDER', 'CLERIC1', 'CLERIC2', 'CLERIC3', 'DRAGON', 'GUARD1', 'GUARD2', 'MAGE', 'MANTIS']
    path = './data/'

    for file in files:
        dcr = assets['dcr'][file + '.DCR']

        for id in range(len(dcr)):
            data = dcr[id]
            img = Image.open("{path}{file}.PNG".format(path=path, file=file), 'r')
            # img.convert('RGBA')

            for face in range(6):
                d = data[face]

                x = d['cps_x']
                y = d['cps_y']
                right = x + d['width']
                lower =  y + d['height']

                bg = Image.new('RGBA', (320, 200), (255, 0, 0, 0))
                bg.paste(img, (0, 0))

                crop = bg.crop((x, y, right, lower))
                # crop.convert('RGBA')


                x = d['screen_x']
                y = d['screen_y']
                bg.paste(crop, (x, y), )

                bg.save("{path}{file}_{id}_{face}.PNG".format(path=path, file=file, id=id, face=face), format='png')

            i = 1


assets = {
    "items": [],
    "item_types": [],
    "item_names": [],
    'text.dat': [],
    'level_items': [],
    'inf': {},
    'maz': {},
    'pal': {},
    'vmp': {},
    'vcn': {},
    'dec': {}
}

if __name__ == '__main__':

    # PAL: color palettes
    assets['pal'] = decode_pal()

    # DEC: decoration rectangle
    assets['dec'] = decode_dec()

    # VMP: information about how to put together the blocks defined in the corresponding vcn files, into proper walls
    assets['vmp'] = decode_vmp()

    # VCN: graphics for the walls including the background
    assets['vcn'] = decode_vcn()

    # DCR: monster graphics
    assets['dcr'] = decode_dcr()

    # TEXT.DAT
    assets['text.dat'] = decode_texts()
    dump('text.json', assets['text.dat'])

    # ITEMTYPE.DAT
    assets['item_types'] = decode_itemtypes()
    dump('item_types.json', assets['item_types'])

    # ITEM.DAT
    assets['items'] = decode_items()
    dump('items.json', assets['items'])

    # Rebuild items in levels
    level_items = [{
        'flags': str(ItemFlags(item['flags'])),
        'type': assets['item_types'][item['type']],
        'picture': item['picture'],
        'value': item['value'],
        'coordinate': {
            'level': item['level'],
            'x': item['coordinate']['x'],
            'y': item['coordinate']['y'],
        }
    } for item in assets['items']]
    dump('level_items.json', level_items)

    # INF
    assets['inf'] = decode_inf()

    # MAZ
    assets['maz'] = decode_maz()

    # Savegame
    savegame = Savegame('data/EOBDATA2.SAV')

    draw_dcr()
    # draw_vmp()
    # draw_dec()

    exit()

    gen_crimson()

    exit()

