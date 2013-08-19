from flvlib import tags
from collections import defaultdict
import sys
from StringIO import StringIO

import bitreader

lengthSizeMinusOne = -1
   
def bytes_to_num(bytes):
    l = len(bytes)
    acc = 0
    for byte in bytes:
        acc += ord(byte)*256**(l-1)
        l -= 1
    return acc

def read_sequence_paramter_set(data):
    # TODO: Implement:
    #        - sgolomb() in bitreader
    #        - vui_paramaters()
    #        - make these part of an actual object
    bitdata = bitreader.BitReader(data)
    profile_idc = bitdata.read_bits(8)
    constraint_set0_flag = bitdata.read_bits(1)
    constraint_set2_flag = bitdata.read_bits(1)
    constraint_set2_flag = bitdata.read_bits(1)
    reserved_zero_5bits = bitdata.read_bits(5)
    level_idc = bitdata.read_bits(8)
    seq_paramter_set_id = bitdata.read_ugolomb()
    log2_max_frame_num_minus4 = bitdata.read_ugolomb()
    pic_order_cnt_type = bitdata.read_ugolomb()
    if pic_order_cnt_type == 0:
        log2_max_pic_order_cnt_lsb_minus4 = bitdata.read_ugolomb()
    elif (pic_order_cnt_type == 1):
        delta_pic_order_always_zero_flag = bitdata.read_bits(1)
        offset_for_non_ref_pic = bitdata.read_sgolomb()
        offset_for_top_to_bottom_filed = bitdata.read_sgolomb()
        num_ref_frames_in_pic_order_cnt_cycle = bitdata.read_ugolomb()
        for i in range(num_ref_frames_in_pic_order_cnt_cycle):
            offset_for_ref_frame.append(bitdata.read_sgolomb)
    num_ref_frames = bitdata.read_ugolomb()
    gaps_in_frame_num_value_allowed_flag = bitdata.read_bits(1)
    pic_width_in_mbs_minus1 = bitdata.read_ugolomb()
    pic_height_in_map_units_minus1 = bitdata.read_ugolomb()
    frame_mbs_only_flag = bitdata.read_bits(1)
    if not frame_mbs_only_flag:
        mb_adapative_frame_field_flag = bitdata.read_bits(1)
    direct_8x8_inference_flag = bitdata.read_bits(1)
    frame_cropping_flag = bitdata.read_bits(1)
    if frame_cropping_flag:
        frame_crop_left_offst = bitdata.read_ugolomb()
        frame_crop_right_offset = bitdata.read_ugolomb()
        frame_crop_top_offset = bitdata.read_ugolomb()
        frame_crop_bottom_offset = bitdata.read_ugolomb()
    vui_paramaters_present_flag = bitdata.read_bits(1)
    if vui_paramaters_present_flag:
        vui_paramaters()

def read_picture_paramter_set(data):
    bitdata = bitreader.BitReader(data)
    pic_parameter_set_id = bitdata.read_ugolomb()
    seq_parameter_set_id = bitdata.read_ugolomb()
    entropy_coding_mode_flag = bitdata.read_bits(1)
    num_slice_groups_minus1 = bitdata.read_ugolomb()
    if num_slice_groups_minus1 > 0:
        slice_group_map_type = bitdata.read_ugolomb()
        if slice_group_map_type == 0:
            run_length_minus1 = []
            for iGroup in range(num_slice_groups_minus1 + 1):
                run_length_minus1.append(bitdata.read_ugolomb())
        elif slice_group_map_type == 2:
            top_left = []
            bottom_right = []
            for iGroup in range(num_slice_groups_minus1 + 1):
                top_left.append(bitdata.read_ugolomb())
                bottom_right.append(bitdata.read_ugolomb())
        elif slice_group_map_type in [3,4,5]:
            slice_group_change_direction_flag = bitdata.read_bits(1)
            slice_gropu_change_rate_minus1 = bitdata.read_ugolomb()
        elif slice_group_map_type == 6:
            pic_size_in_map_units_minus1 = bitdata.read_ugolomb()
            slice_group_id = []
            for i in range(pic_size_in_map_units_minus1):
                slice_group_id.append(bitdata.read_bits(1))
    num_ref_idx_l0_active_minus1 = bitdata.read_ugolomb()
    num_ref_idx_l1_active_minus1 = bitdata.read_ugolomb()
    weighted_pred_flag = bitdata.read_bits(1)
    weighted_bipred_idc = bitdata.read_bits(2)
    pic_init_qp_minus26 = bitdata.read_sgolomb()
    pic_init_qs_minus26 = bitdata.read_sgolomb()
    chroma_qp_index_offset = bitdata.read_sgolomb()
    deblocking_filter_control_present_flag = bitdata.read_bits(1)
    redundant_pic_cnt_present_flag = bitdata.read_bits(1)
    #rbsp trail
            
def read_tag_headers(flvtag, flvfile):
    pos = flvfile.tell() # save position
    flvfile.seek(flvtag.offset)
    tagtype = flvfile.read(1)
    datasize = bytes_to_num(flvfile.read(3))
    timestamp = flvfile.read(3)
    timestampext = flvfile.read(1)
    streamid = flvfile.read(3)
    # FLV AVC warpper
    bytes_to_num(flvfile.read(1))
    bytes_to_num(flvfile.read(1)) 
    bytes_to_num(flvfile.read(3))
    data = flvfile.read(datasize) # AVC wrapper
    flvfile.seek(pos)
    return data
    
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
    bytes_to_num(flvfile.read(1)) 
    bytes_to_num(flvfile.read(3))

    # This is one more piece of AVC metadata, unfortunately, I can't find the
    # standard document to figure out how to parse it. At the moment
    # ignoring the next 4 bytes seems to work. I think it's length
    # info.
    bytes_to_num(flvfile.read(lengthSizeMinusOne + 1)) 
    data = flvfile.read(datasize) # h264 goodness! mmHHMM!  
    flvfile.seek(pos) # return to original position
    return data

def h264_nalu(data):
    datasize = len(data)
    bitdata = bitreader.BitReader(StringIO(data))
    zero_bit = bitdata.read_bits(1)
    nal_ref_idc = bitdata.read_bits(2)
    nal_unit_type = bitdata.read_bits(5)
    rbsp_bytes = data[1:].replace("\x00\x00\x03","\x00\x00")
    return zero_bit, nal_ref_idc, nal_unit_type, rbsp_bytes

def readAVCDecoderConfigurationRecord(data):
    global lengthSizeMinusOne
    flvfile = StringIO(data)
    bitdata = bitreader.BitReader(flvfile)
    configurationVersion = bitdata.read_bits(8)
    print "configurationVersion:", configurationVersion
    AVCProfileIndication = bitdata.read_bits(8)
    profile_compatibility= bitdata.read_bits(8)
    AVCLevelIndication = bitdata.read_bits(8)
    reserved = bitdata.read_bits(6)
    print "reserved",reserved
    lengthSizeMinusOne = bitdata.read_bits(2)
    print "lengthSizeMinusOne:", lengthSizeMinusOne
    reserved = bitdata.read_bits(3)
    print "reserved:",reserved
    numOfSequenceParameterSets = bitdata.read_bits(5)
    sps = []
    print "numOfSequenceParameterSets", numOfSequenceParameterSets
    for i in range(numOfSequenceParameterSets):
        length = bitdata.read_bits(16)
        sps.append(flvfile.read(length))
    numOfPictureParameterSets = bitdata.read_bits(5)
    pps = []
    print "numOfPictureParameterSets", numOfPictureParameterSets
    for i in range(numOfPictureParameterSets):
        length = bitdata.read_bits(16)
        pps.append(flvfile.read(length))
    return lengthSizeMinusOne, sps, pps

def h264_read(flv, f):
    stats = defaultdict(int)
    for i, tag in enumerate(flv.iter_tags(), 1):
        if isinstance(tag, tags.VideoTag) and tag.h264_packet_type==0:
            avcdata = read_tag_headers(tag, f)
            result = readAVCDecoderConfigurationRecord(avcdata)
        if isinstance(tag, tags.VideoTag) and tag.h264_packet_type==1:
            print tag
            zero_bit, nal_ref_idc, nal_unit_type, datasize = h264_nalu(extract_frame_flv(tag, f))
            result = zero_bit, nal_ref_idc, nal_unit_type
            stats[result] += 1
            #print "Tag #%d" % i, result[:-1], datasize
    print stats

def main(args):
    print tags.strict_parser()
    inputfile = open(args[0], 'rb')
    flv = tags.FLV(inputfile)
    h264_read(flv, inputfile)

main(sys.argv[1:])
