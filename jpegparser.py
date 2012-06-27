
from struct import pack, unpack

class JpegParser(object):

    def __init__(self, filename):
        self.filename = filename
        self.structures = []
        self.parsers    = []
        self.setup_parsers()

    def parse_file(self):
        with open(self.filename, "rb") as fp:
            byte = fp.read(1)
            while byte != b"":
                if byte == '\xFF':
                    byte = fp.read(1)
                    self.check_tag(byte, fp)
                byte = fp.read(1)

    def output_file(self, filename):
        print("Outputting File")
        with open(filename, "wb") as fp:
            for p in self.structures:
                p.about()
                p.write_data(fp)

    def check_tag(self, tag, fp):
        for p in self.parsers:
            if p.parse(tag):
                newstruct = p.get_new()
                newstruct.read_data(fp)
                newstruct.tag = tag
                newstruct.about()
                self.structures.append(newstruct)
                return True
        return False


    def setup_parsers(self):
        self.parsers.append(SOI())
        self.parsers.append(SOF0())
        self.parsers.append(SOF2())
        self.parsers.append(DHT())
        self.parsers.append(DQT())
        self.parsers.append(SOS())
        self.parsers.append(APP())
        self.parsers.append(COM())
        self.parsers.append(EOI())


class JpegStructure(object):

    def __init__(self):
        self.info = "Base Structure"
        self.data = b""
        self.size = 0

    def about(self):
        print(self.info)

    def parse(self, tag):
        if tag == self.tag:
            return True
        else:
            return False

    def get_new(self):
        return self.__class__()

    def read_data(self, fp):
        data = fp.read(2)
        size = unpack('>H', data)[0]
        self.size = size
        #read size - 2 because size includes the 2 bytes
        #that store the size information
        self.data = list(fp.read(size - 2))

    def write_data(self, fp):
        fp.write('\xFF')
        fp.write(self.tag)
        fp.write(pack('>H', self.size))
        fp.write("".join(self.data))




class SOI(JpegStructure):
    def __init__(self):
        self.tag  = '\xD8'
        self.info = "Start of File"

    def read_data(self, fp):
        pass

    def write_data(self, fp):
        fp.write('\xFF')
        fp.write(self.tag)

class SOF0(JpegStructure):
    def __init__(self):
        self.tag  = '\xC0'
        self.info = "Start of Baseline Frame"

class SOF2(JpegStructure):
    def __init__(self):
        self.tag  = '\xC2'
        self.info = "Start of Progressive Frame"

class DHT(JpegStructure):
    def __init__(self):
        self.tag  = '\xC4'
        self.info = "Huffman Table"

    def read_data(self, fp):
        self.size = unpack('>H', fp.read(2))[0]
        #read size - 2 because size includes the 2 bytes
        #that store the size information
        temp_data        = list(fp.read(self.size - 2))
        self.miscbits    = temp_data[0]
        self.group_sizes = temp_data[1:17]
        self.group_data  = temp_data[17:]



    def write_data(self, fp):
        fp.write('\xFF')
        fp.write(self.tag)
        fp.write(pack('>H', self.size))
        fp.write(self.miscbits)
        fp.write("".join(self.group_sizes))
        fp.write("".join(self.group_data))

class DQT(JpegStructure):
    def __init__(self):
        self.tag  = '\xDB'
        self.info = "Quantization Table"

class SOS(JpegStructure):
    def __init__(self):
        self.tag  = '\xDA'
        self.info = "Start of Scan"

    def read_data(self, fp):
        super(SOS, self).read_data(fp)
        self.header_data = self.data
        self.header_size = self.size

        #find the size of the rest of the data
        pos = fp.tell()
        byte = fp.read(1)
        i = 1
        while byte != b"":
            if byte == '\xFF':
                next_byte = fp.read(1)
                if next_byte != '\x00':
                    i -= 1
                    break
                else:
                    i += 1
            if byte == b"":
                print("Real Error Here")
                break
            byte = fp.read(1)
            i += 1

        fp.seek(pos)
        self.data = list(fp.read(i))
        self.size = i

    def write_data(self, fp):
        fp.write('\xFF')
        fp.write(self.tag)
        fp.write(pack('>H', self.header_size))
        fp.write(''.join(self.header_data))
        fp.write(''.join(self.data))

class APP(JpegStructure):
    def __init__(self):
        self.tag_list = [0xE0, 0xEF]
        self.tag = b''
        self.info = "App Specific"

    def parse(self, tag):
        tag = unpack('B', tag)[0]
        if tag >= self.tag_list[0] and tag <= self.tag_list[1]:
            return True
        else:
            return False


class COM(JpegStructure):
    def __init__(self):
        self.tag  = '\xFE'
        self.info = "Comment"

    def about(self):
        print(self.info)
        print(unpack('>'+str(self.size-2)+'s', "".join(self.data))[0])


class EOI(JpegStructure):
    def __init__(self):
        self.tag  = '\xD9'
        self.info = "End of Image"

    def read_data(self, fp):
        self.data = fp.read(1)

    def write_data(self, fp):
        fp.write('\xFF')
        fp.write(self.tag)
        fp.write(self.data)

