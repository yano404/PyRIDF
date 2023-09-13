
class ridf:
    endian = 'little'
    word_size = 2 #bytes
    token_size = 4 #bytes
    current_blk = None
    current_event = None
    max_blk_size = 0x0080_0000

    def __init__(self):
        self.size = 0 #bytes
        self.block = []
        self.event = []

    def encode(self):
        codes = []
        for blk in self.block:
            codes.append(blk.encode())
        return b"".join(codes)

    def del_block(self, block_id):
        for i in range(len(self.block)):
            blk = self.block[i]
            if blk.obj_id == block_id:
                self.block.pop(i)
                return 0
        return 1

    def update(self):
        self.size = 0
        for blk in self.block:
            blk.update()
            self.size += blk.size

