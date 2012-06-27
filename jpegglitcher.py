
from jpegparser import JpegParser
from random import randint
from struct import pack

class JpegGlitcher(JpegParser):

    def find_parts(self):
        self.huffmans = []
        for p in self.structures:
            if p.tag == '\xC4':
                self.huffmans.append(p)

        self.quantizes = []
        for p in self.structures:
            if p.tag == '\xDB':
                self.quantizes.append(p)

        self.compressed_data = []
        for p in self.structures:
            if p.tag == '\xDA':
                self.compressed_data.append(p)

    def huffman_glitch(self):
        for ht in self.huffmans:
            for i in range(len(ht.group_data)):
                if randint(1, 100) < 2:
                    newval = randint(1, 254)
                    print("Writing " + str(newval) + " to position " + str(i))
                    ht.group_data[i] = pack('B', newval)

    def quantize_glitch(self):
        for qt in self.quantizes:
            for i in range(3, qt.size - 2): #skip first 3 bytes of data
                if randint(1, 100) < 60:
                    qt.data[i] = pack('B', randint(1, 254))

    def data_rand_glitch(self):
        for sd in self.compressed_data:
            for i in range(sd.size - 2):
                if randint(1, 10000) < 10:
                    if sd.data[i-1] == '\xFF':
                        sd.data[i-1] = pack('B', randint(1, 254))
                    sd.data[i] = pack('B', randint(1, 254))

    def data_move_glitch(self):
        for sd in self.compressed_data:
            pos1 = randint(1, sd.size-2)
            pos2 = randint(1, sd.size-2)
            size = randint(1, int(sd.size/20))
            if sd.data[pos1-1] == '\xFF':
                sd.data[pos1-1] = pack('B', randint(1, 254))
            for i in range(size):
                sd.data[pos1+i] = sd.data[pos2+i]
            if sd.data[pos2+size] == '\xFF':
                sd.data[pos2+size] = pack('B', randint(1, 254))

    def data_reverse_glitch(self):
        for sd in self.compressed_data:
            pos  = randint(1, sd.size-2)
            size = randint(1, int(sd.size/20))
            templist = sd.data[pos:pos+size]
            templist.reverse()
            for i in range(size):
                sd.data[pos+i] = templist[i]
            for i in range(sd.size - 2):
                if sd.data[i] == '\xFF':
                    sd.data[i+1] = '\x00'

