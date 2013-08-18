import StringIO
import math 

class BitReader():
    def __init__(self, byte_stream):
        self.bytes = byte_stream
        self.current_num = 0
        self.available_bits = 0
    def bytes_to_num(self, bytes):
        l = len(bytes)
        acc = 0
        for byte in bytes:
            acc += ord(byte)*256**(l-1)
            l -= 1
        return acc
    def maybe_read_more(self, n):
        if self.available_bits < n:
            more_bytes = int(math.ceil((n-self.available_bits)/8.0))
            new_bytes = self.bytes.read(more_bytes)
            if new_bytes == '':
                raise Exception("Insufficient bits")
            self.current_num = 256**more_bytes*self.current_num
            self.current_num += self.bytes_to_num(new_bytes)
            self.available_bits += 8*more_bytes

    def read_bits(self, n):
        self.maybe_read_more(n)
        ones_mask = 2**self.available_bits-1
        low_bits = 2**(self.available_bits-n) - 1
        high_bits = ones_mask - low_bits
        nbits = self.current_num & high_bits
        self.current_num -= nbits
        nbits = nbits >> (self.available_bits - n)
        self.available_bits -= n
        return nbits

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

def test():
    testReadPastByte("\xff")
    testReadBytes("\xff\xff", [2,8,6])
    testReadBytes("\x0f\x0f", [2,8,6])
    testReadBytes("\x00\x00", [2,8,6])
    
def main():
    test()
main()
