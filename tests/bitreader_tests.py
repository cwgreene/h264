from bitreader import *

def testReadPastByte(byte):
    bitReader = testReadByte(byte, [2,2,4])
    bitReader = testReadByte(byte, [2,2,2,2])
    try:
        bitReader.read_bits(2)
    except Exception as e:
        print "Correctly detected Overread"

def testReadByte(byte, groups):
    bitReader = BitReader(StringIO.StringIO(byte))
    bits_read = 0
    for bits in groups:
        bits_read += bits
        print bitReader.read_bits(bits)
    if bits_read != 8:
        raise Exception("Entire byte not read: "+bits_read)
    print "Read byte!"
    return bitReader

def testReadBytes(bytes, groups):
    bitReader = BitReader(StringIO.StringIO(bytes))
    bits_read = 0
    for bits in groups:
        bits_read += bits
        print bitReader.read_bits(bits)
    if bits_read != 8*len(bytes):
        raise Exception("Entire bytes not read: %d/%d" 
            % (bits_read, 8*len(bytes)))
    print "Read byte!"

def testuGolomb(byte):
    print bin(ord(byte))
    bitreader = BitReader(StringIO.StringIO(byte))  
    print "Golomb: %s => %d" % (bin(ord(byte)), bitreader.read_ugolomb())

def test():
    testReadPastByte("\xff")
    testReadBytes(chr(1), [8])
    testReadBytes("\xff\xff", [2,8,6])
    testReadBytes("\x0f\x0f", [2,8,6])
    testReadBytes("\x00\x00", [2,8,6])
    testuGolomb(chr(int('10000000',2)))
    testuGolomb(chr(int('00111000',2)))
    

