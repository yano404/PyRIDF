
def make_segid(dev, fp, det, mod, rev=0):
    return ((((rev<<6 | dev)<<6 | fp) << 6) | det)<<8 | mod


def parse_segid(segid):
    mod = segid & 0xff
    det = (segid >> 8) & 0x3f
    fp  = (segid >> 14) & 0x3f
    dev = (segid >> 20) & 0x3f
    rev = (segid >> 26) & 0x3f
    return {
        "rev": rev,
        "dev": dev,
        "fp": fp,
        "det" : det,
        "mod" : mod
    }
