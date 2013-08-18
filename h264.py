from flvlib import tags
from collections import defaultdict
import sys
from StringIO import StringIO

import bitreader
   
def bytes_to_num(bytes):
    l = len(bytes)
    acc = 0
    for byte in bytes:
        acc += ord(byte)*256**(l-1)
        l -= 1
    return acc

def extract_frame_flv(flvtag, flvfile):
    pos = flvfile.tell() # save position
    flvfile.seek(flvtag.offset)
    tagtype = flvfile.read(1)
    datasize = bytes_to_num(flvfile.read(3))
    timestamp = flvfile.read(3)
    timestampext = flvfile.read(1)
    streamid = flvfile.read(3)
    # AVC Packet metadata, we should already be a NALU
    bytes_to_num(flvfile.read(1))
    assert(bytes_to_num(flvfile.read(1)) == 1)
    assert(bytes_to_num(flvfile.read(3)) == 0)

    # This is one more piece of AVC metadata, unfortunately, I can't find the
    # standard document to figure out how to parse it. At the moment
    # ignoring the next 4 bytes seems to work. I think it's length
    # info.
    bytes_to_num(flvfile.read(4)) 
    data = flvfile.read(datasize) # h264 goodness! mmHHMM!  
    flvfile.seek(pos) # return to original position
    return data

def h264_nalu(data):
    datasize = len(data)
    bitdata = bitreader.BitReader(StringIO(data))
    zero_bit = bitdata.read_bits(1)
    nal_ref_idc = bitdata.read_bits(2)
    nal_unit_type = bitdata.read_bits(5)
    return zero_bit, nal_ref_idc, nal_unit_type, datasize

def h264_read(flv, f):
    stats = defaultdict(int)
    for i, tag in enumerate(flv.iter_tags(), 1):
        if isinstance(tag, tags.VideoTag) and tag.h264_packet_type==1:
            print tag
            zero_bit, nal_ref_idc, nal_unit_type, datasize = h264_nalu(extract_frame_flv(tag, f))
            result = zero_bit, nal_ref_idc, nal_unit_type
            stats[result] += 1
            print "Tag #%d" % i, result, datasize
    print stats

def main(args):
    print tags.strict_parser()
    inputfile = open(args[0], 'rb')
    flv = tags.FLV(inputfile)
    h264_read(flv, inputfile)

main(sys.argv[1:])
