import struct
import zlib
import numpy as np
import matplotlib.pyplot as plot

def read_chunk(f):
    # Returns (chunk_type, chunk_data chunk_crc)
    chunk_length, chunk_type = struct.unpack('>I4s', f.read(8))
    chunk_data = f.read(chunk_length)
    chunk_expected_crc, = struct.unpack('>I', f.read(4))
    chunk_actual_crc = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_type)))
    if chunk_expected_crc != chunk_actual_crc:
        raise Exception('chunk checksum failed')
    return chunk_type, chunk_data, chunk_actual_crc

class Chunk:
    def __init__(self, type_, data, crc):
        self.type_ = type_
        self.data = data
        self.crc = crc

class IHDR(Chunk):
    """The IHDR chunk must appear FIRST.It contains:
    Width: 4 bytes
    Height: 4 bytes
    Bit depth: 1 byte
    Color type: 1 byte
    Compression method: 1 byte
    Filter method: 1 byte
    Interlace method: 1 byte"""

    def __init__(self , type_, data, crc):
        super().__init__( type_, data, crc)
        values = struct.unpack('>iibbbbb', self.data)
        self.width = values[0]
        self.height = values[1]
        self.bit_depth = values[2]
        self.color_type = values[3]
        self.compression_method = values[4]
        self.filter_method = values[5]
        self.interlace_method = values[6]

    def print_chunk(self):
        print("IHDR chunk: \n")
        print("Width: " + str(self.width))
        print("Height: " + str(self.height))
        print("Bit depth: " + str(self.bit_depth))
        if self.color_type == 0:
            print("Color type: Grayscale (0)")
        elif  self.color_type == 2:
            print("Color type: RGB (2)")
        elif  self.color_type == 3:
            print("Color type: Indexed-color (3)")
        elif  self.color_type == 4:
            print("Color type: Grayscale with alpha (4)")
        elif  self.color_type == 6:
            print("Color type: RGB with alpha (6)")
        else:
            raise Exception("Invalid color type ")
        if self.compression_method == 0:
            print("Compression: deflate/inflate compression with a sliding window")
        else:
            raise Exception("Invalid compression_method ")
        if self.filter_method == 0:
            print("Filter method: Adaptive filtering ")
        if self.interlace_method == 0:
            print("Interlace method: no interlace\n")
        elif self.interlace_method == 1:
            print("Interlace method: Adam7 interlace\n")
        else:
            raise Exception("Invalid interlace method")


class PLTE(Chunk):

    def __init__(self,type_,data,crc):
        super().__init__( type_, data, crc)

    def check_chunk(self,color_type):
        if (color_type == 0 or color_type == 4):
            raise Exception("PLTE chunk MUST NOT appear in this image")
        if (len(self.data) % 3 != 0):
            raise Exception("Chunk length not divisible by 3!")

    def print_chunk(self,bit_depth):
        palette = []
        for i in range(0,len(self.data), 3):
            raw_pixel = self.data[i:i+3]
            pixel = (raw_pixel[0], raw_pixel[1], raw_pixel[2])
            palette.append(pixel)
            if (len(palette) > 2 ** bit_depth):
                raise Exception("Incorrect number of entires in palette.")
        palette = np.reshape(palette, (-1,3))
        #print(palette) # duzo danych, mozna odkomentowac dla potrzeby
        plot.imshow(np.array(palette).reshape(1, len(palette), 3), aspect='auto')
        plot.title('Palette in PLTE chunk')
        plot.show()
        print("Displaying palette in PLTE\n")


class IDAT(Chunk):

    def __init__(self,  type_, data, crc, width, height, color_type):
        super().__init__( type_, data, crc)
        self.data = zlib.decompress(data)
        self.Recon = []
        self.width = width
        self.height = height
        if color_type == 0:
            self.bytes_per_pixel = 1
        elif color_type == 2:
            self.bytes_per_pixel = 3
        elif color_type == 3:
            self.bytes_per_pixel = 1
        elif color_type == 4:
            self.bytes_per_pixel = 2
        elif color_type == 6:
            self.bytes_per_pixel = 4
        self.stride = self.width * self.bytes_per_pixel

    def recon_a(self, r, c):
        return self.Recon[r * self.stride + c - self.bytes_per_pixel] if c >= self.bytes_per_pixel else 0

    def recon_b(self, r, c):
        return self.Recon[(r-1) * self.stride + c] if r > 0 else 0

    def recon_c(self, r, c):
        return self.Recon[(r-1) * self.stride + c - self.bytes_per_pixel] if r > 0 and c >= self.bytes_per_pixel else 0

    def paeth_predict(self, a, b, c):
        p = a + b - c
        pa = abs(p - a)
        pb = abs(p - b)
        pc = abs(p - c)
        if pa <= pb and pa <= pc:
            Pr = a
        elif pb <= pc:
            Pr = b
        else:
            Pr = c
        return Pr

    def reconstructed_pixel_data(self):
        i = 0
        for row in range(self.height): # for each scanline
            filter_type = self.data[i] # first byte of scanline is filter type
            i += 1
            for c in range(self.stride): # for each byte in scanline
                filter_x = self.data[i]
                i += 1
                if filter_type == 0: # None
                    recon_x = filter_x
                elif filter_type == 1: # Sub
                    recon_x = filter_x + self.recon_a(row, c)
                elif filter_type == 2: # Up
                    recon_x = filter_x + self.recon_b(row, c)
                elif filter_type == 3: # Average
                    recon_x = filter_x + (self.recon_a(row, c) + self.recon_b(row, c)) // 2
                elif filter_type == 4: # Paeth
                    recon_x = filter_x + self.paeth_predict(self.recon_a(row, c), self.recon_b(row, c), self.recon_c(row, c))
                else:
                    raise Exception('unknown filter type: ' + str(filter_type))
                self.Recon.append(recon_x & 0xff) # truncation to byt

    def plot_image(self):
        self.reconstructed_pixel_data()
        plot.imshow(np.array(self.Recon).reshape((self.height,self.width,self.bytes_per_pixel)))
        plot.show()
        print("Displaying reconstructed image from IDAT chunk\n")


class IEND(Chunk):
    def __init__(self,  type_, data, crc):
        super().__init__( type_, data, crc)

    def print_chunk(self):
        print("IEND chunk just marks the image end. The chunk's data field is empty.\n")

class tIME(Chunk):
    def __init__(self,  type_, data, crc):
        super().__init__( type_, data, crc)

        values = struct.unpack('>hbbbbb', self.data)
        self.year = values[0]
        self.month = values[1]
        self.day = values[2]
        self.hour = values[3]
        self.minute = values[4]
        self.second = values[5]

    def print_chunk(self):
        print("tIME chunk: \n")
        print("Last modification date: "+ str(self.day) + "-" + str(self.month) + "-" + str(self.year))
        print("Time: " + str(self.hour) + ":" + str(self.minute) + ":" + str(self.second)+"\n")

class gAMA(Chunk):
    def __init__(self,  type_, data, crc):
        super().__init__( type_, data, crc)
        # PNG specification says, that stored gamma value is multiplied by 100000
        self.gamma = int.from_bytes(data, 'big') / 100000

    def print_chunk(self):
        print("gAMA chunk: \n\nGamma: " + str(self.gamma)+"\n")

class cHRM(Chunk):
    def __init__(self, type_, data, crc):
        super().__init__(type_, data, crc)

        values = struct.unpack('>iiiiiiii', self.data)
        # PNG specification says, that stored values are multiplied by 100000
        self.WPx = values[0] / 100000
        self.WPy = values[1] / 100000
        self.WPz = 1 - self.WPx - self.WPy
        self.Rx = values[2] / 100000
        self.Ry = values[3] / 100000
        self.Rz = 1 - self.Rx - self.Ry
        self.Gx = values[4] / 100000
        self.Gy = values[5] / 100000
        self.Gz = 1 - self.Gx - self.Gy
        self.Bx = values[6] / 100000
        self.By = values[7] / 100000
        self.Bz = 1 - self.Bx - self.By

    def print_chunk(self):
        print("cHRM chunk:\n")
        print("White point x: " + str(self.WPx) + " y: " + str(self.WPy) + " z: " + str(self.WPz))
        print("Red x: " + str(self.Rx) + " y: " + str(self.Ry) + " z: " + str(self.Rz))
        print("Green  x: " + str(self.Gx) + " y: " + str(self.Gy) + " z: " + str(self.Gz))
        print("Blue  x: " + str(self.Bx) + " y: " + str(self.By) + " z: " + str(self.Bz) + "\n")

