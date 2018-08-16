
from location import Location


class Monster:
    """

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

        return "ID {index} @ {location}|{subposition} [ID: {direction}, Timer:{timer}, type:{type}, " \
               "picture:{picture}, phase:{phase}, pause:{pause}, weapon:0x{weapon:04X}, pocket:0x{pocket:04X}]".format(
            index=self.index, location=self.location, subposition=self.sub_position, direction=self.direction,
            timer=self.timer_id, type=self.type, picture=self.picture_index, phase=self.phase, pause=self.pause,
            weapon=self.weapon, pocket=self.pocket_item
        )
