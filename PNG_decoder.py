import cv2
import Chunks
import FFT
import struct
import Encryption
import png
import zlib,os
from pathlib import Path
class PNG_decoder:

    def __init__(self,file,cv_image):
        self.image = file
        self.cv_image = cv_image
        self.chunk_list = []

    def read_chunks(self):
        while True:
            chunk_type, chunk_data, chunk_crc, chunk_length = Chunks.read_chunk(self.image)
            self.chunk_list.append((chunk_type, chunk_data, chunk_crc,chunk_length))
            if chunk_type == b'IEND':
                break

    def print_chunks_list(self):
        print("CHUNKS TYPE: ", [chunk_type for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list])

    def fourier_transform(self):
        image = FFT.Fourier(self.cv_image)
        image.show_fft()

    def display_image(self):
        cv2.imshow("Image",self.cv_image)
        cv2.waitKey(0)

    def IHDR_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'IHDR':
                data = Chunks.IHDR(chunk_type,chunk_data,chunk_crc, chunk_length)
                data.print_chunk()
                break
            elif chunk_type == b'IEND':
                print("File does not contain IHDR chunk")

    def PLTE_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc, chunk_length)
        for chunk_type, chunk_data, chunk_crc, chunk_length in self.chunk_list:
            if chunk_type == b'PLTE':
                data = Chunks.PLTE(chunk_type,chunk_data,chunk_crc)
                data.check_chunk(check.color_type)
                data.print_chunk(check.bit_depth)
            elif chunk_type == b'IEND':
                print("File does not contain PLTE chunk")

    def IDAT_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc, chunk_length)
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list if chunk_type == b'IDAT')
        data = Chunks.IDAT(chunk_type,idat_data,chunk_crc,check.width,check.height,check.color_type, chunk_length)
        if data:
            data.plot_image()
        else:
            raise Exception("IDAT error")

    def IEND_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'IEND':
                data = Chunks.IEND(chunk_type,chunk_data,chunk_crc, chunk_length)
                data.print_chunk()


    def tIME_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'tIME':
                data = Chunks.tIME(chunk_type,chunk_data,chunk_crc, chunk_length)
                data.print_chunk()
            elif chunk_type == b'IEND':
                print("File does not contain tIME chunk")


    def gAMA_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'gAMA':
                data = Chunks.gAMA(chunk_type,chunk_data,chunk_crc, chunk_length)
                data.print_chunk()
                break
            elif chunk_type == b'IEND':
                print("File does not contain gAMA chunk")

    def cHRM_chunk(self):
        for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list:
            if chunk_type == b'cHRM':
                data = Chunks.cHRM(chunk_type,chunk_data,chunk_crc, chunk_length)
                data.print_chunk()
                break
            elif chunk_type == b'IEND':
                print("File does not contain cHRM chunk")

    def clean_ancillary_chunks(self,new_file_name):
        def get_ancillary_chunks():
            ancillary_chunks = [
                b'IHDR',
                b'IDAT',
                b'PLTE',
                b'IEND'
            ]
            return ancillary_chunks

        ancillary_chunks = get_ancillary_chunks()
        new_file = open(new_file_name, 'wb')
        new_file.write(b'\x89PNG\r\n\x1a\n')

        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type in ancillary_chunks:
                new_file.write(struct.pack('>I', len(chunk_data)))
                new_file.write(chunk_type)
                new_file.write(chunk_data)
                new_file.write(struct.pack('>I', chunk_crc))
        new_file.close()
        print("New png file without ancillary chunks created. File_name: " + new_file_name + "\n")


    def save_file(self,file,data):
        img_path = "./images/{}".format(file)
        if Path(img_path).is_file():
            os.remove(img_path)
        temporary_file = open(img_path, 'wb')
        temporary_file.write(b'\x89PNG\r\n\x1a\n')
        for chunk_type, chunk_data, chunk_crc, chunk_length in self.chunk_list:
            if chunk_type in [b'IDAT']:
                new_data = zlib.compress(data, 9)
                new_crc = zlib.crc32(new_data, zlib.crc32(struct.pack('>4s', b'IDAT')))
                chunk_len = len(new_data)
                temporary_file.write(struct.pack('>I', chunk_len))
                temporary_file.write(chunk_type)
                temporary_file.write(new_data)
                temporary_file.write(struct.pack('>I', new_crc))
            else:
                temporary_file.write(struct.pack('>I', chunk_length))
                temporary_file.write(chunk_type)
                temporary_file.write(chunk_data)
                temporary_file.write(struct.pack('>I', chunk_crc))
        temporary_file.close()

    def ecb_encrypt(self,e,n,key_size,d):

        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc,chunk_length in self.chunk_list if chunk_type == b'IDAT')
        idat_data = zlib.decompress(idat_data)

        data,after= Encryption.ecb_encrypt(idat_data, e, n, key_size)
        self.save_file("after_ecb_encryption.png",data)
        data = Encryption.ecb_decrypt(data, d,n,key_size,after)
        self.save_file("decrypted_ecb.png", data)



    def cbc_encrypt(self,e,n,key_size,d):
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc, chunk_length in self.chunk_list if chunk_type == b'IDAT')
        idat_data = zlib.decompress(idat_data)

        data,vector,after= Encryption.cbc_encrypt(idat_data,e,n,key_size)

        self.save_file("after_cbc_encryption.png",data)
        data = Encryption.cbc_decrypt(data,d,n,key_size,vector,after )
        self.save_file("decrypted_cbc.png",data)

    def library_encrypt(self,e,n,key_size):
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc, chunk_length in self.chunk_list if chunk_type == b'IDAT')
        idat_data = zlib.decompress(idat_data)

        data, after_data = Encryption.library_encrypt(idat_data,e,n,key_size)
        self.save_file("after_library_encryption.png",data)





















