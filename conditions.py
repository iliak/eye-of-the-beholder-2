
from extract import Dice
from extract import Location
from extract import races, classes, directions


class ConditionalD7:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.value = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.value = reader.read_ubyte()

    def run(self, maze, assets):

        return "condition 0xD7(0x{value:02X})".format(
            value=self.value
        )


class ConditionalDF:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.value = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        # self.value = reader.read_ubyte()

    def run(self, maze, assets):

        return "condition 0xDF()".format(value=self.value)


class ConditionalThrowDice:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.dice = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.dice = Dice(reader)

    def run(self, maze, assets):

        return "throw dice {dice}".format(dice=self.dice)


class ConditionalMenuChoice:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.type = None
        self.value = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.type = reader.read_ubyte()
        self.value = reader.read_ushort()

    def run(self, maze, assets):

        return "push menu choice, Push 0x{value:04X}".format(value=self.value)


class ConditionalimmediateShort:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.value = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.value = reader.read_ushort()

    def run(self, maze, assets):

        return "value 0x{value:04X}".format(value=self.value)


class ConditionalOperator:
    """

    """

    def __init__(self, value=None):
        """

        :param reader:
        """
        self.operator = None
        self.text = None

        self.decode(value)

    def decode(self, value):
        """

        :param reader:
        :return:
        """

        self.operator = value
        if self.operator == 0xff: self.text = " == "
        elif self.operator == 0xfe: self.text = " != "
        elif self.operator == 0xfd: self.text = " < "
        elif self.operator == 0xfc: self.text = " <= "
        elif self.operator == 0xfb: self.text = " > "
        elif self.operator == 0xfa: self.text = " >= "
        elif self.operator == 0xf9: self.text = " AND "
        elif self.operator == 0xf8: self.text = " OR "
        else: self.text = " [??] "

    def run(self, maze, assets):

        return "{value}".format(value=self.text)


class ConditionalContainClass:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.id = reader.read_byte()

    def run(self, maze, assets):

        return "check if character with class {name} is present"\
            .format(name=classes[self.id])


class ConditionalContainAlignment:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.id = reader.read_ubyte()

    def run(self, maze, assets):

        return "need alignment {id}".format(id=self.id)


class ConditionalContainRace:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.id = reader.read_ubyte()

    def run(self, maze, assets):

        return "check if character with race {race} is present".format(race=races[self.id])


class ConditionalGetTriggerFlag:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

    def run(self, maze, assets):

        return "get trigger flag"


class ConditionalGetLevelFlag:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.flag = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.flag = reader.read_ubyte()

    def run(self, maze, assets):

        return "get level flag {flag}".format(flag=self.flag)


class ConditionalSetLevelFlag:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.flag = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.flag = reader.read_ubyte()

    def run(self, maze, assets):

        return "set level flag {flag}".format(flag=self.flag)


class ConditionalGetGlobalFlag:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.flag = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.flag = reader.read_ubyte()

    def run(self, maze, assets):

        return "get global flag {flag}".format(flag=self.flag)


class ConditionalSetGlobalFlag:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.flag = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.flag = reader.read_ubyte()

    def run(self, maze, assets):

        return "set Global flag {flag}".format(flag=self.flag)


class ConditionalGetWallSide:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.side = None
        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.side = reader.read_ubyte()
        self.location = Location(reader)

    def run(self, maze, assets):

        return "wall side {side} at {location}".format(side=directions[self.side], location=self.location)


class ConditionalGetPointerItem:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.action = None
        self.id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.action = reader.read_ubyte()
        if self.action == 0xD0:
            self.id = reader.read_ubyte()
        elif self.action == 0xCF:
            self.id = reader.read_ubyte()

    def run(self, maze, assets):

        if self.action == 0xF5:
            return "hand item"
        elif self.action == 0xF6:
            return "hand item value"
        elif self.action == 0xE1:
            return "hand item type"
        elif self.action == 0xD0:
            return "hand item unidentified name id == #{value}".format(value=self.id)
        elif self.action == 0xCF:
            return "hand item identified name id == #{value}".format(value=self.id)


class ConditionalGetWallIndex:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.location = Location(reader)

    def run(self, maze, assets):

        return "wall index at {location}".format(location=self.location)


class ConditionalGetPartyDirection:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

    def run(self, maze, assets):

        return "party direction"


class ConditionalMonsterCount:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return
        self.location = Location(reader)

    def run(self, maze, assets):

        return "monster count at {location}".format(location=self.location)


class ConditionalPushTrue:
    """

    """

    def __init__(self):
        """

        :param reader:
        """

    def run(self, maze, assets):

        return "push True"


class ConditionalPushFalse:
    """

    """

    def __init__(self):
        """

        :param reader:
        """

    def run(self, maze, assets):

        return "push False"


class ConditionalPushValue:
    """
    BOGUS
    """

    def __init__(self, reader=None, value=None):
        """

        :param reader:
        """

        self.value = value
        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        # self.value = reader.read_ushort()

    def run(self, maze, assets):

        # if self.value <= 128:
        return "push 0x{value:04X}".format(value=self.value)
        # else:
        #     return "####0x{value:02X} ({value})".format(value=self.value)


class ConditionalItemCount:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = None
        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        self.type = reader.read_ushort()
        self.location = Location(reader)

    def run(self, maze, assets):

        if self.type == 0xFF00:
            return "maze count items at {location}".format(
                location=self.location
            )
        else:
            return "maze count items of type 0x{type:04X} at {location}".format(
                type=self.type, location=self.location
            )


class ConditionalGetParty:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.code = None
        self.type = None
        self.flags = None
        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return
        self.code = reader.read_ubyte()

        if self.code == 0xF5:   # Count items
            self.type = reader.read_ushort()
            self.flags = reader.read_ubyte()

        else:   # Party position
            self.location = Location(reader)

    def run(self, maze, assets):

        if self.code == 0xF5:
            return "party inventory count of 0x{type:04X} flags: 0x{flags:02X}".format(
                type=self.type, flags=self.flags
                )
        else:
            return "party is at location {location}".format(location=self.location)


class ConditionalPartyVisible:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

    def run(self, maze, assets):

        return "is party visible"


class ConditionalUnknown:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

    def run(self, maze, assets):

        return "Unknown conditional"














