from conditions import *
from location import Location
from extract import directions


class Conditional:
    """

    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.tokens = []
        self.target = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """

        if not reader:
            return

        # "IF "
        while True:
            opcode = reader.read_ubyte()
            if opcode == 0xee:
                break

            if 0xf8 <= opcode <= 0xff: token = ConditionalOperator(opcode)
            elif opcode == 0xf7: token = ConditionalGetWallIndex(reader)
            elif opcode == 0xf5: token = ConditionalItemCount(reader)
            elif opcode == 0xf3: token = ConditionalMonsterCount(reader)
            elif opcode == 0xf1: token = ConditionalGetParty(reader)
            elif opcode == 0xf0: token = ConditionalGetGlobalFlag(reader)
            elif opcode == 0xef: token = ConditionalGetLevelFlag(reader)
            elif opcode == 0xee: break
            elif opcode == 0xed: token = ConditionalGetPartyDirection(reader)
            elif opcode == 0xe9: token = ConditionalGetWallSide(reader)
            elif opcode == 0xe7: token = ConditionalGetPointerItem(reader)
            elif opcode == 0xe4: token = ConditionalMenuChoice(reader)
            elif opcode == 0xe0: token = ConditionalGetTriggerFlag(reader)
            elif opcode == 0xdd: token = ConditionalContainRace(reader)
            elif opcode == 0xdc: token = ConditionalContainClass(reader)
            elif opcode == 0xdb: token = ConditionalThrowDice(reader)
            elif opcode == 0xda: token = ConditionalPartyVisible(reader)
            elif opcode == 0xd2: token = ConditionalimmediateShort(reader)
            elif opcode == 0xce: token = ConditionalContainAlignment(reader)
            elif opcode == 0xd7: token = ConditionalD7(reader)
            elif opcode == 0xdf: token = ConditionalDF(reader)
            elif opcode == 0x01: token = ConditionalPushTrue()
            elif opcode == 0x00: token = ConditionalPushFalse()
            else: token = ConditionalPushValue(reader, opcode)

            if not token:
                continue

            self.tokens.append(token)

        self.target = reader.read_ushort()
        i = 1

    def run(self, maze, assets):

        str = "If "
        for token in self.tokens:
            str += token.run(maze, assets) + '|'

        return str + ' else goto 0x{target:04X}'.format(target=self.target)


class SetWall:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = None
        self.location = None
        self.to = None
        self.side = None
        self.direction = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()

        if self.type == -9:    # All sides
            self.location = Location(reader)
            self.to = reader.read_ubyte()

        elif self.type == -23:     # one side
            self.location = Location(reader)
            self.side = reader.read_ubyte()
            self.to = reader.read_ubyte()

        elif self.type == -19:     # change party direction
            self.direction = reader.read_ubyte()

    def run(self, maze, assets):

        if self.type == -9:
            return "Set walls at {location} all sides to {to:02}".format(location=self.location, to=self.to)

        elif self.type == -23:
            return "Set wall at {location} side {side} to {to:02}".format(
                location=self.location, side=self.side, to=self.to)

        elif self.type == -19:
            return "Set party direction to {direction}".format(direction=directions[self.direction])


class CreateMonster:
    """

    :return:
    """

    def __init__(self, reader):

        self.unit = None
        self.timer = None
        self.location = None
        self.pos = None
        self.dir = None
        self.type = None
        self.frame = None
        self.phase = None
        self.pause = None
        self.weapon = None
        self.pocket = None

        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

        self.unit = reader.read_ubyte()
        self.timer = reader.read_ubyte()
        self.location = Location(reader)
        self.pos = reader.read_ubyte()
        self.dir = reader.read_byte()
        self.type = reader.read_ubyte()
        self.frame = reader.read_ubyte()
        self.phase = reader.read_ubyte()
        self.pause = reader.read_ubyte()
        self.pocket = reader.read_ushort()
        self.weapon = reader.read_ushort()

    def run(self, maze, assets):
        return "Create monster #{unit}, timer: {timer}, location: {location}, subpos: {pos}, dir: {dir}, " \
               "frame: {frame}, phase: {phase}, pause: {pause}, pocket: {pocket}, weapon: {weapon}".format(
            unit=self.unit, timer=self.timer, location=self.location, pos=self.pos, dir=directions[self.dir],
            frame=self.frame, phase=self.phase, pause=self.pause, pocket=self.pocket, weapon=self.weapon
        )


class Teleport:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = -1        # a action
        self.source = -1
        self.destination = -1
        self.item_type = -1     # b item type
        self.src_level = -1     # c source block
        self.dst_level = -1     # d target block ?
        self.src_blk = -1       # e Source level ?
        self.dst_blk = -1       # f target level ?
        self.sub = -1
        # self.tmp = -1
        # self.tmp2 = -1
        # self.payload = []

        self.decode(reader)

    def decode(self, reader):
        """
        BOGUS extra data not handled
        :param reader:
        :return:
        """
        self.type = reader.read_byte()

        if self.type == -31:
            self.item_type = reader.read_ushort()

        self.source = Location(reader)

        if self.type == -11:    # Move item
            self.src_level = reader.read_byte()
            self.sub = reader.read_ubyte()
            if self.sub == 0xe5:
                self.dst_level = reader.read_byte()
                self.dst_blk = Location(reader)
            elif self.sub == 0xeb:
                self.dst_blk = Location(reader)
            else:
                self.payload = reader.read_ubyte(4)

        elif self.type == -31:  # Move item by type
            self.src_blk = Location(reader)
            self.dst_blk = Location(reader)

        elif self.type == -13:  # Move monster
            self.destination = Location(reader)

        elif self.type == -24:  # Move party
            self.destination = Location(reader)

        i = 1

    def run(self, maze, assets):

        if self.type == -24:
            return "Teleport team to {dest}".format(dest=self.destination)

        elif self.type == -13:
            return "Teleport monsters from {src} to {dest}".format(src=self.source, dest=self.destination)

        elif self.type == -11:
            # return "Teleport (-11) items tmp: 0x{tmp:02X} src_level: {src_level} payload: [{payload}]".format(
            #     src_level=self.src_level, tmp=self.tmp, payload=''.join("0x{:02X} ".format(x) for x in self.payload)
            # )

            if self.sub == 0xe5:
                return "Teleport (-11) items from level {src_level}:{source} to level {dst_level}:{dst_blk}".format(
                    src_level=self.src_level, source=self.source, dst_level=self.dst_level, dst_blk=self.dst_blk,
                )
            elif self.sub == 0xeb:
                return "Teleport (-11) items in current level from {source} to {dst_blk}".format(
                    source=self.source, dst_blk=self.dst_blk,
                )
            else:
                return "Teleport (-11) ERROR ### #{id} sub {sub} payload: {payload}".format(
                    id=self.type, sub=self.sub, payload=''.join("0x{:02X} ".format(x) for x in self.payload))

        elif self.type == -31:
            return "Teleport item of type {item_type} from {source} to {dest}".format(
                item_type=self.item_type, dest=self.dst_blk, source=self.src_blk)

        else:
            return "Teleport ### #{id}".format(id=self.type)


class Message:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.message_id = None
        self.color = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.message_id = reader.read_ushort()
        self.color = reader.read_ushort()

    def run(self, maze, assets):

        return "Display message '{msg}' color: {color}" \
            .format(color=self.color, msg=maze.messages[self.message_id])


class SetFlag:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.type = None
        self.flag = None
        self.monster_id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()
        if self.type in [-17, -16]:       # Maze or global
            self.flag = reader.read_ubyte()

        elif self.type == -13:     # monster
            self.monster_id = reader.read_ubyte()
            self.flag = reader.read_ubyte()

        elif self.type == -28:     # event
            pass

        elif self.type == -47:     # Party can't sleep ??
            pass

    def run(self, maze, assets):

        if self.type == -17:       # -17 level
            return "Set level flag {flag}".format(flag=self.flag)

        if self.type == -16:       # -16 global
            return "Set global flag {flag}".format(flag=self.flag)

        elif self.type == -13:     # -13 monster
            return "Set monster {monster} flag {flag}".format(monster=self.monster_id, flag=self.flag)

        elif self.type == -28:
            return "Set dialog result to 1"

        elif self.type == -47:
            return "Set 'Prevent rest' flag".format()


class ClearFlag:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.type = None
        self.flag = None
        self.monster_id = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()
        if self.type in [-17, -16]:  # Maze or global
            self.flag = reader.read_ubyte()

        elif self.type == -28:  # event
            pass

        elif self.type == -47:  # Party ??
            pass

    def run(self, maze, assets):

        if self.type == -17:
            return "Clear level flag {flag}".format(flag=self.flag)

        elif self.type == -16:
            return "Clear global flag {flag}".format(flag=self.flag)

        elif self.type == -28:
            return "Clear dialog result flag".format()

        elif self.type == -47:
            return "Clear 'Prevent rest' flag".format()


class Sound:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.id = None
        self.location = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.id = reader.read_ubyte()
        self.location = Location(reader)

    def run(self, maze, assets):

        if self.location.x or self.location.y:
            return "Play environmental sound {id} at {location}".format(id=self.id, location=self.location)
        else:
            return "Play sound {id}".format(id=self.id)


class Jump:
    """

    :return:
    """

    def __init__(self, reader):

        self.addr = None
        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

        self.addr = reader.read_ushort()

    def run(self, maze, assets):
        return "Jump to [0x{target:04X}]".format(target=self.addr)


class End:
    """

    :return:
    """

    def __init__(self, reader):

        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

    def run(self, maze, assets):
        return "End"


class Return:
    """

    :return:
    """

    def __init__(self, reader):

        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

    def run(self, maze, assets):
        return "Return"


class NewItem:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = None
        self.location = None
        self.subpos = None
        self.flags = None
        self.item_id = None
        self.item_value = None
        self.item_flag = None
        self.item_icon = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.item_id = reader.read_ushort()
        self.location = Location(reader)
        self.subpos = reader.read_ubyte()
        self.flags = reader.read_ubyte()

        i = 1
        if self.flags & 1 == 1:
            self.item_value = reader.read_byte()
        if self.flags & 2 == 2:
            self.item_flag = reader.read_byte()
        if self.flags & 4 == 4:
            self.item_icon = reader.read_byte()

    def run(self, maze, assets):

        if self.location.value == -1:
            return "New hand item id: {item_id} (value {value}, flags: {flags} 0x{flags:02x}, icon: {icon}]".format(
                item_id=self.item_id, value=self.item_value, flags=self.flags, icon=self.item_icon)

        elif self.location.value == -2:
            return "New item #{item_id} on current block (value {value}, flags: {flags} 0x{flags:02x}, icon: {icon}]".format(
                item_id=self.item_id, value=self.item_value, flags=self.flags, icon=self.item_icon)

        else:
            return "New item #{item_id} at {location}, sub: {sub} flags: 0x{flags:02x}".format(
                item_id=self.item_id, location=self.location, sub=self.subpos, flags=self.flags)


class Wait:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.delay = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.delay = reader.read_ushort()

    def run(self, maze, assets):

        return "Wait {delay} ticks ({ms} ms)".format(delay=self.delay, ms=self.delay * 55)


class UpdateScreen:
    """

    :param reader:
    :return:
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

        return "Update screen"


class Dialog:
    """

    :return:
    """

    def __init__(self, reader):

        self.type = None
        self.picture_name = None
        self.x = None
        self.y = None
        self.rect = None
        self.flags = None
        self.text_id = None
        self.buttons = [None for i in range(6)]

        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

        self.type = reader.read_byte()

        if self.type == -45:    # Display a picture from a cps file
            self.picture_name = reader.read_string(13)
            self.rect = reader.read_ubyte()
            self.x = reader.read_ushort()
            self.y = reader.read_ushort()
            self.flags = reader.read_short()

        elif self.type == -44:  # Close dialog
            pass

        elif self.type == -43:  # Display background
            pass

        elif self.type == -42:  # Draw dialog box
            pass

        elif self.type == -40:  # Run dialog
            # vm->runDialogue(READ_LE_UINT16(pos),
            # READ_LE_UINT16(pos + 6) == 0xFFFF ? 2 : 3,
            # getString(READ_LE_UINT16(pos + 2)),
            # getString(READ_LE_UINT16(pos + 4)),
            # getString(READ_LE_UINT16(pos + 6)));
            self.text_id = reader.read_short()
            self.buttons[0] = reader.read_short()
            self.buttons[1] = reader.read_short()
            self.buttons[2] = reader.read_short()

        elif self.type == -8:  # Dialog text
            self.x = reader.read_ushort()
            self.y = reader.read_ushort()

    def run(self, maze, assets):

        if self.type == -45:    # Display a picture from a cps file
            return "Draw sequence : \"{picture}\", rect: {rect}, X: {x}, Y: {y}, flags: 0x{flags:04X}".format(
                x=int(self.x / 8), y=self.y, picture=self.picture_name, flags=self.flags, rect=self.rect)

        elif self.type == -44:  # Close dialog
            return "Close dialog"

        elif self.type == -43:  # Init dialog sequence
            return "Init dialog sequence"

        elif self.type == -42:  # Draw dialog box
            return "Draw dialog box"

        elif self.type == -40:  # Run dialog
            return "Run dialog '{txt}', Buttons: ['{b1}', '{b2}', '{b3}']".format(
                text_id=self.text_id,
                txt=assets['texts'][self.text_id - 1],
                b1=maze.messages[self.buttons[0]] if self.buttons[0] != -1 else '',
                b2=maze.messages[self.buttons[1]] if self.buttons[1] != -1 else '',
                b3=maze.messages[self.buttons[2]] if self.buttons[2] != -1 else '',
            )

        elif self.type == -8:  #
            return "Print dialog text: '{txt}' , Text #{y}: '{msg}'".format(
                type=self.type, x=self.x, y=self.y, msg=maze.messages[self.y], txt=assets['texts'][self.x - 1]
            )


class ChangeLevel:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.cmd = None
        self.index = None
        self.level = None
        self.sub = None
        self.location = None
        self.direction = None
        self.monster = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.cmd = reader.read_byte()
        self.index = reader.read_byte()

        if self.cmd == -27:
            self.sub = reader.read_byte()
            self.location = Location(reader)
            self.direction = reader.read_byte()

        else:
            self.level = reader.read_byte()
            self.monster = reader.read_byte(13)

    def run(self, maze, assets):

        if self.cmd == -27:
            return "Entering to level {level}, sub level {sub} at {location} facing to {direction}".format(
                level=self.index, sub=self.sub, location=self.location, direction=directions[self.direction])

        else:
            return "Loading monster shape: {shape}, id: {id} type: {type}".format(
                shape=self.monster[0], id=self.level, type=self.index)


class Call:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.target = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.target = reader.read_ushort()

    def run(self, maze, assets):

        return "Call 0x{target:04X}" \
            .format(target=self.target)


class OpenDoor:
    """

    :param reader:
    :return:
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

        return "Open door at {location}".format(location=self.location)


class CloseDoor:
    """

    :param reader:
    :return:
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

        return "Close door at {location}".format(location=self.location)


class ConsumeItem:
    """

    :param reader:
    :return:
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

        self.type = reader.read_byte()
        if self.type != -1:
            self.location = Location(reader)

    def run(self, maze, assets):

        if self.type == -1:
            return "Consume hand item"
        else:
            return "Consume item of type {type} at {location}".format(type=self.type, location=self.location)


class ChangeWall:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = None
        self.location = None
        self.to = None
        self.side = None
        self.model = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()
        self.location = Location(reader)

        if self.type == -9:   # All side
            self.to = reader.read_ubyte()
            self.model = reader.read_ubyte()

        elif self.type == -23:     # One side
            self.side = reader.read_ubyte()
            self.to = reader.read_ubyte()
            self.model = reader.read_ubyte()

        elif self.type == -22:     # Door
            pass

    def run(self, maze, assets):

        if self.type == -9:
            return "Change wall at {location} all sides from: {model} to: {to}".format(
                location=self.location, model=self.model, to=self.to)

        elif self.type == -23:
            return "Change wall at {location} side: {side} from: {model} to: {to}".format(
                location=self.location, side=self.side, model=self.model, to=self.to)

        elif self.type == -22:
            return "Process door switch at {location}".format(
                location=self.location)


class Launcher:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.type = None
        self.item_id = None
        self.location = None
        self.direction = None
        self.sub_position = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()
        self.item_id = reader.read_ushort()
        self.location = Location(reader)
        self.direction = reader.read_ubyte()
        self.sub_position = reader.read_ubyte()

    def run(self, maze, assets):

        if self.type == -33:
            return "Launching spell #{spell_id} from {location} facing {direction} at subpos {subpos}".format(
                spell_id=self.item_id, location=self.location, direction=directions[self.direction], subpos=self.sub_position
            )

        elif self.type == -20:
            return "Launching item #{item_id} from {location} facing {direction} at subpos {subpos}".format(
                item_id=self.item_id, location=self.location, direction=directions[self.direction], subpos=self.sub_position
            )


class Turn:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """

        self.cmd = None
        self.dir = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.cmd = reader.read_byte()
        self.dir = reader.read_ubyte()
        i = 1

    def run(self, maze, assets):

        if self.cmd == -15:
            return "Change party direction to {dir}".format(dir=directions[self.dir])

        elif self.cmd == -11:
            return "Change flying item direction to {dir}".format(dir=directions[self.dir])

        else:
            return '[ERROR] Turn'


class Heal:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.target = None
        self.points = 0

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.target = reader.read_byte()
        self.points = reader.read_ubyte()

    def run(self, maze, assets):

        if self.target:
            return "Heal champion #{id} of {points} points".format(id=self.target, points=self.points)
        else:
            return "Heal team of {points} points".format(points=self.points)


class Damage:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.target = None
        self.times = None
        self.itemOrPips = None
        self.mod = None
        self.flags = None
        self.savingThrowType = None
        self.savingThrowEffect = None

        self.vs_small = None
        self.vs_big = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.target = reader.read_byte()
        self.times = reader.read_byte()
        self.itemOrPips = reader.read_byte()
        self.mod = reader.read_byte()
        self.flags = reader.read_byte()
        self.savingThrowType = reader.read_byte()
        self.savingThrowEffect = reader.read_byte()

    def run(self, maze, assets):

        target = 'team ' if self.target == -1 else ''
        return "Damage {target}{times} time(s) with item {item}, modifier: {mod}, flags: 0x{flags:02X}, " \
               "savingThrowType: {type}, savingThrowEffect: {effect}".format(
            target=target, times=self.times, item=self.itemOrPips, mod=self.mod, flags=self.flags,
            type=self.savingThrowType, effect=self.savingThrowEffect
        )


class GiveXP:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.type = None
        self.amount = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.type = reader.read_byte()
        self.amount = reader.read_ushort()

    def run(self, maze, assets):

        if self.type == -30:
            return "Give {amount} XP to the team [type: {type}]".format(
                amount=self.amount, type=self.type
            )


class IdentifyAllItems:
    """

    :param reader:
    :return:
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

        return "Identify all items at {location}".format(
            location=self.location
        )


class Sequence:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.cmd = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.cmd = reader.read_byte()

    def run(self, maze, assets):

        """
        nightmare
        kheldran
        dran dragon transformation
        finale
        credits
        intro
        xdeath
        portal

        :return:
        """
        if self.cmd == -1:
            return 'Sequence: Check password'
        elif self.cmd == -2:
            return 'Sequence: Portal'
        elif self.cmd == -3:
            return 'Sequence: Final scene...'

        return "Sequence: NPC #{id}".format(
            id=self.cmd
        )


class StealSmallItem:
    """

    :param reader:
    :return:
    """

    def __init__(self, reader):
        """

        :param reader:
        """
        self.whom = None
        self.location = None
        self.sub_position = None

        self.decode(reader)

    def decode(self, reader):
        """

        :param reader:
        :return:
        """
        if not reader:
            return

        self.whom = reader.read_byte()
        self.location = Location(reader)
        self.sub_position = reader.read_ubyte()

    def run(self, maze, assets):

        if self.whom == -1:
            return "Steal small item and drop it at {location}:{subpos}".format(
                location=self.location, subpos=self.sub_position
            )
        else:
            return "Steal small item member: {member} and drop it at {location}:{subpos}".format(
                member=self.whom, location=self.location, subpos=self.sub_position
            )


class SpecialEvent:
    """

    :param reader:
    :return:
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

        self.id = reader.read_ushort()

    def run(self, maze, assets):

        if self.id == 0:
            return "Special event: lightning"
        elif self.id == 1:
            return "Special event: character selection dialog"
        elif self.id == 2:
            return "Special event: character level gain dialog"
        elif self.id == 3:
            return "Special event: character resurrection dialog"
        elif self.id == 4:
            return "Special event: new party member dialog"
        elif self.id == 5:
            return "Special event: steal items (type: 46, value:5 & 6)"
        elif self.id == 6:
            return "Special event: clear screen"







