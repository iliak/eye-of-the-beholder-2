

class Location:
    """

    """

    def __init__(self, reader=None):
        """

        :param reader:
        """
        self.x = None
        self.y = None
        self.value = None
        self.h = None
        self.l = None
        self.decode(reader)

    def decode(self, reader):

        if not reader:
            return

        self.h = reader.read_byte()
        self.l = reader.read_byte()

        self.value = (self.l << 8) + self.h
        self.x = self.value & 0x1f
        self.y = (self.value >> 5) & 0x1f

    def is_valid(self):
        return self.h < 0x1f or self.l < 0x1f

    @property
    def raw(self):
        return "0x{:04x}".format(self.value)

    def __str__(self):
        return self.coordinates()

    def coordinates(self):
        return '{x:02}x{y:02}'.format(x=self.x, y=self.y)

