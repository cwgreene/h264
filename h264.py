from flvlib import tags
from collections import defaultdict

class BitReader():
    def __init__(bytes):
        self.bytes = bytes
        self.offset_bits = 0
        self.offset_bytes = 0
    def bitmask(n):
        return 256-1 - 2**(8-n)

def bytes_to_num(bytes):
    l = len(bytes)
    acc = 0
    for byte in bytes:
        acc += ord(byte)*256**(l-1)
        l -= 1
    return acc

def extract_frame_flv(flvtag, flvfile):
    flvfile.seek(flvtag.offset)
    tagtype = flvfile.read(1)
    datasize = bytes_to_num(flvfile.read(3))
    timestamp = flvfile.read(3)
    timestampext = flvfile.read(1)
    streamid = flvfile.read(3)
    data = flvfile.read(datasize)
    return data

def h264_nalu(data):
    datasize = len(data)
    zero_bit = bytes_to_num(data[0]) & 128
    nal_ref_idc = bytes_to_num(data[0]) & (127-31)
    nal_unit_type = bytes_to_num(data[0]) & 31
    return zero_bit, nal_ref_idc, nal_unit_type

def h264_read(flv, f):
    stats = defaultdict(int)
    for i, tag in enumerate(flv.iter_tags()):
        if isinstance(tag, tags.VideoTag):
            result = h264_nalu(extract_frame_flv(tag, f))
            stats[result] += 1
            print "Tag #%d" % i, result
    print stats
