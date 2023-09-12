
class element:
    def __init__(self, rev, layer, cid, size, addr, parent=None):
        self.revision = rev
        self.layer = layer
        self.classid = cid
        self.size = size
        self.address = addr
        self.parent = parent
        self.classname = None
        self.data = b""
        self.header_size = 8 #bytes
        self.obj_id = id(self)

    def calc_size(self):
        # Return element size (in word unit)
        return (self.header_size + len(self.data)) >> 1

    def encode(self):
        return self.encode_header() + self.data

    def encode_header(self):
        hdr = ((self.revision << 30)\
                | (self.layer << 28)
                | (self.classid << 22)\
                | (self.size)).to_bytes(4, "little")
        hdr += self.address.to_bytes(4, "little")
        return hdr

    def update(self):
        self.size = self.calc_size()


class container(element):
    def __init__(self, rev, layer, cid, size, addr, parent=None):
        super().__init__(rev, layer, cid, size, addr, parent)
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)

    def del_child(self, objid):
        for i in range(len(self.children)):
            child = self.children[i]
            if child.obj_id == objid:
                self.children.pop(i)
                return 0
        return 1

    def calc_size(self):
        # Return container size (in word unit)
        container_size = self.header_size >> 1
        for child in self.children:
            container_size += child.calc_size()
        return container_size

    def encode(self):
        code = self.encode_header()
        for child in self.children:
            code += child.encode()
        return code

    def update(self):
        self.size = self.header_size >> 1
        for child in self.children:
            child.update()
            self.size += child.size


class block(container):
    """
    Class ID: 0 / 1 / 2
    Layer: 0
    """
    def __init__(self, cid, size, addr, rev=0, parent=None):
        super().__init__(rev, 0, cid, size, addr, parent)
        if cid == 0:
            self.classname = "Event Fragment"
        elif cid == 1:
            self.classname = "Event Assembly"
        elif cid == 2:
            self.classname = "Event Assembly Fragment"


class block_ender(element):
    """
    Class ID: 9
    Layer: 1
    """
    def __init__(self, addr, rev=0, parent=None):
        super().__init__(rev, 1, 9, 6, addr, parent)
        self.classname = "Block Ender"
        self.blocksize = None
        self.header_size = 8 #bytes

    def calc_size(self):
        return self.size

    def encode(self):
        return self.encode_header() + self.blocksize.to_bytes(4, "little")

    def update(self):
        self.size = self.calc_size()
        if isinstance(self.parent, block):
            self.blocksize = self.parent.size


class block_number(element):
    """
    Class ID: 8
    Layer: 1
    """
    def __init__(self, addr, rev=0, parent=None):
        super().__init__(rev, 1, 8, 6, addr, parent)
        self.classname = "Block Number"
        self.blocknumber = None
        self.header_size = 8 #bytes

    def calc_size(self):
        return self.size
 
    def encode(self):
        return self.encode_header() + self.blocknumber.to_bytes(4, "little")


class comment(element):
    """
    Class ID: 5
    Layer: 1 or 2
    """
    def __init__(self, layer, size, addr, rev=0, parent=None):
        super().__init__(rev, layer, 5, size, addr, parent)
        self.classname = "Comment"
        self.date = None
        self.id = None
        self.data = None
        self.header_size = 16 #bytes

    def set_comment(self, comid, date, data):
        self.date = date
        self.id = comid
        self.data = data

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.date.to_bytes(4, "little")
        hdr += self.id.to_bytes(4, "little")
        return hdr


class event(container):
    """
    Class ID: 3
    Layer: 1
    """
    def __init__(self, size, addr, rev=0, parent=None):
        super().__init__(rev, 1, 3, size, addr, parent)
        self.classname = "Event"
        self.eventnumber = None
        self.header_size = 12 #bytes

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.eventnumber.to_bytes(4, "little")
        return hdr


class event_ts(container):
    """
    Class ID: 6
    Layer: 1
    """
    def __init__(self, size, addr, rev=0, parent=None):
        super().__init__(rev, 1, 6, size, addr, parent)
        self.classname = "Event with Timestamp"
        self.eventnumber = None
        self.timestamp = None
        self.header_size = 20 #bytes

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.eventnumber.to_bytes(4, "little")
        hdr += self.timestamp.to_bytes(8, "little")
        return hdr


class segment(element):
    """
    Class ID: 4
    Layer: 2
    """
    def __init__(self, size, addr, rev=0, parent=None):
        super().__init__(rev, 2, 4, size, addr, parent)
        self.classname = "Segment"
        self.id = None
        self.data = None
        self.header_size = 12 #bytes

    def set_payload(self, segid, data):
        self.id = segid
        self.data = data

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.id.to_bytes(4, "little")
        return hdr


class timestamp(element):
    """
    Class ID: 16
    Layer: 2
    """
    def __init__(self, size, addr, rev=0, parent=None):
        super().__init__(rev, 2, 16, size, addr, parent)
        self.classname = "Timestamp"
        self.data = None

    def set_payload(self, data):
        self.data = data


class scaler(element):
    """
    Class ID: 11 / 12 / 13
    Layer: 1 or 2
    """
    def __init__(self, layer, cid, size, addr, rev=0, parent=None):
        super().__init__(rev, layer, cid, size, addr, parent)
        if cid == 11:
            self.classname = "Non Clear Scaler(24bit)"
        elif cid == 12:
            self.classname = "Clear Scaler(24bit)"
        elif cid == 13:
            self.classname = "Non Clear Scaler(32bit)"
        self.id = None
        self.date = None
        self.data = None
        self.header_size = 16 #bytes

    def set_payload(self, scaid, date, data):
        self.id = scaid
        self.date = date
        self.data = data

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.date.to_bytes(4, "little")
        hdr += self.id.to_bytes(4, "little")
        return hdr


class status(element):
    """
    Class ID: 21
    Layer: 1 or 2
    """
    def __init__(self, layer, size, addr, rev=0, parent=None):
        super().__init__(rev, layer, 21, size, addr, parent)
        self.classname = "Status"
        self.id = None
        self.date = None
        self.data = None
        self.header_size = 16 #bytes

    def set_payload(self, staid, date, data):
        self.id = staid
        self.date = date
        self.data = data

    def encode_header(self):
        hdr = super().encode_header()
        hdr += self.date.to_bytes(4, "little")
        hdr += self.id.to_bytes(4, "little")
        return hdr


