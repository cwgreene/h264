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

    def read_ugolomb(self):
        def consume_zeros():
            """ Will read up to, and including the next 1 """
            bit = self.read_bits(1)
            count = 0
            while bit == 0:
                count += 1
                bit = self.read_bits(1)
            return count
        try:
            zeros = consume_zeros()
        except:
            raise Exception("Invalid Golomb Code: No 1's found")
        try:
            num = 2**(zeros) + self.read_bits(zeros) - 1
        except Exception as e:
            raise Exception("Invalid Golomb code: Insufficient bits after leading zeros")
        return num
def main():
    import tests.bitreader_tests
    tests.bitreader_tests.test()
if __name__=="__main__":
    main()
