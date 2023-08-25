
from . import element

class ridf:
    endian = 'little'
    word_size = 2 #bytes
    token_size = 4 #bytes
    hd1_revision_mask  = 0xc000_0000
    hd1_revision_shift = 30
    hd1_layer_mask     = 0x3000_0000
    hd1_layer_shift    = 28
    hd1_classid_mask   = 0x0fc0_0000
    hd1_classid_shift  = 22
    hd1_blksize_mask   = 0x003f_ffff
    hd1_blksize_shift  = 0
    current_blk = None
    current_event = None

    def __init__(self, fname: str):
        self.file = open(fname, 'rb')
        self.content = self.file.read()
        self.cursor = 0
        self.size = len(self.content) #bytes
        self.block = []
        self.event = []

    def parse(self, maxblock=None):
        while self.cursor < self.size:
            if maxblock is not None:
                if len(self.block) > maxblock:
                    self.block.pop()
                    break

            hd1  = self.readint(0,self.token_size)
            rev  = (hd1 & self.hd1_revision_mask) >> self.hd1_revision_shift
            ly   = (hd1 & self.hd1_layer_mask) >> self.hd1_layer_shift
            cid  = (hd1 & self.hd1_classid_mask) >> self.hd1_classid_shift
            size = (hd1 & self.hd1_blksize_mask) >> self.hd1_blksize_shift
            addr = self.readint(self.token_size, 2*self.token_size)
            
            if ly == 0:
                # Global Block Header
                self.current_blk = element.block(cid, size, addr)
                self.block.append(self.current_blk)
                self.cursor += self.current_blk.header_size
                print(f"cursor: {self.cursor}")

            elif ly == 1:
                if cid == 8:
                    # Block Number
                    blk = element.block_number(addr, parent=self.current_blk)
                    blk.blocknumber = self.readint(8,12)
                    self.current_blk.add_child(blk)
                    self.cursor += size*self.word_size
                    print(f"blkn: {blk.blocknumber}")
                    
                elif cid == 5:
                    # Comment
                    com = element.comment(ly, size, addr, parent=self.current_blk)
                    date = self.readint(8,12)
                    comid = self.readint(12,16)
                    data = self.readbytes(com.header_size, size*self.word_size)
                    com.set_comment(comid, date, data)
                    self.current_blk.add_child(com)
                    self.cursor += size*self.word_size

                elif cid == 3:
                    # Event Data
                    self.current_evt = element.event(size, addr, parent=self.current_blk)
                    self.current_evt.eventnumber = self.readint(8,12) 
                    self.current_blk.add_child(self.current_evt)
                    self.event.append(self.current_evt)
                    self.cursor += self.current_evt.header_size

                elif cid == 6:
                    # Event Data w/ Time stamp
                    self.current_evt = element.event_ts(size, addr, parent=self.current_blk)
                    self.current_evt.eventnumber = self.readint(8,12)
                    self.current_evt.timestamp = self.readint(12,20)
                    self.current_blk.add_child(self.current_evt)
                    self.event.append(self.current_evt)
                    self.cursor += self.current_evt.header_size
                    print(f"evtn: {self.current_evt.eventnumber}")

                elif cid == 11 or cid == 12 or cid == 13:
                    # Scaler
                    sca = element.scaler(ly, cid, size, addr, parent=self.current_blk)
                    date = self.readint(8,12)
                    scaid = self.readint(12,16)
                    data = self.readbytes(sca.header_size, size*self.word_size)
                    sca.set_payload(scaid, date, data)
                    self.current_blk.add_child(sca)
                    self.cursor += size*self.word_size

                elif cid == 21:
                    # Status
                    sta = element.status(ly, size, addr, parent=self.current_blk)
                    date = self.readint(8,12)
                    staid = self.readint(12,16)
                    data = self.readbytes(sta.header_size, size*self.word_size)
                    sta.set_payload(staid, date, data)
                    self.current_blk.add_child(sta)
                    self.cursor += size*self.word_size

                elif cid == 9:
                    # Block Ender
                    blk = element.block_ender(addr, parent=self.current_blk)
                    blk.blocksize = self.readint(8,12)
                    self.current_blk.add_child(blk)
                    self.cursor += size*self.word_size

            elif ly == 2:
                if cid == 4:
                    # Segment Data
                    seg = element.segment(size, addr, parent=self.current_evt)
                    segid = self.readint(8,12)
                    data = self.readbytes(seg.header_size, size*self.word_size)
                    seg.set_payload(segid, data)
                    self.current_evt.add_child(seg)
                    self.cursor += size*self.word_size

                elif cid == 5:
                    # Comment
                    com = element.comment(ly, size, addr, parent=self.current_evt)
                    date = self.readint(8,12)
                    comid = self.readint(12,16)
                    data = self.readbytes(com.header_size, size*self.word_size)
                    com.set_comment(comid, date, data)
                    self.current_evt.add_child(com)
                    self.cursor += size*self.word_size

                elif cid == 16:
                    # Timestamp
                    ts = element.timestamp(size, addr, parent=self.current_evt)
                    data = self.readbytes(ts.header_size, size*self.word_size)
                    ts.set_payload(data)
                    self.current_evt.add_child(ts)
                elif cid == 11 or cid == 12 or cid == 13:
                    # Scaler
                    sca = element.scaler(ly, cid, size, addr, parent=self.current_evt)
                    date = self.readint(8,12)
                    scaid = self.readint(12,16)
                    data = self.readbytes(sca.header_size, size*self.word_size)
                    sca.set_payload(scaid, date, data)
                    self.current_evt.add_child(sca)
                    self.cursor += size*self.word_size

                elif cid == 21:
                    # Status
                    sta = element.status(ly, size, addr, parent=self.current_evt)
                    date = self.readint(8,12)
                    staid = self.readint(12,16)
                    data = self.readbytes(sta.header_size, size*self.word_size)
                    sta.set_payload(staid, date, data)
                    self.current_evt.add_child(sta)
                    self.cursor += size*self.word_size


    def readint(self, start, end):
        return int.from_bytes(
                self.content[self.cursor+start:self.cursor+end],
                self.endian)
    
    def readbytes(self, start, end):
        return self.content[self.cursor+start:self.cursor+end]

    def encode(self):
        code = b""
        for blk in self.block:
            code += blk.encode()
        return code
