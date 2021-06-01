import cv2
import Chunks
import FFT
import struct
import Encryption
import png


class PNG_decoder:

    def __init__(self,file,cv_image):
        self.image = file
        self.cv_image = cv_image
        self.chunk_list = []

    def read_chunks(self):
        while True:
            chunk_type, chunk_data, chunk_crc = Chunks.read_chunk(self.image)
            self.chunk_list.append((chunk_type, chunk_data, chunk_crc))
            if chunk_type == b'IEND':
                break

    def print_chunks_list(self):
        print("CHUNKS TYPE: ", [chunk_type for chunk_type, chunk_data, chunk_crc in self.chunk_list])

    def fourier_transform(self):
        image = FFT.Fourier(self.cv_image)
        image.show_fft()

    def display_image(self):
        cv2.imshow("Image",self.cv_image)
        cv2.waitKey(0)

    def IHDR_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IHDR':
                data = Chunks.IHDR(chunk_type,chunk_data,chunk_crc)
                data.print_chunk()
                break
            elif chunk_type == b'IEND':
                print("File does not contain IHDR chunk")

    def PLTE_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc)
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'PLTE':
                data = Chunks.PLTE(chunk_type,chunk_data,chunk_crc)
                data.check_chunk(check.color_type)
                data.print_chunk(check.bit_depth)
            elif chunk_type == b'IEND':
                print("File does not contain PLTE chunk")

    def IDAT_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc)
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc in self.chunk_list if chunk_type == b'IDAT')
        data = Chunks.IDAT(chunk_type,idat_data,chunk_crc,check.width,check.height,check.color_type)
        if data:
            data.plot_image()
        else:
            raise Exception("IDAT error")

    def IEND_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IEND':
                data = Chunks.IEND(chunk_type,chunk_data,chunk_crc)
                data.print_chunk()


    def tIME_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'tIME':
                data = Chunks.tIME(chunk_type,chunk_data,chunk_crc)
                data.print_chunk()
            elif chunk_type == b'IEND':
                print("File does not contain tIME chunk")


    def gAMA_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'gAMA':
                data = Chunks.gAMA(chunk_type,chunk_data,chunk_crc)
                data.print_chunk()
                break
            elif chunk_type == b'IEND':
                print("File does not contain gAMA chunk")

    def cHRM_chunk(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'cHRM':
                data = Chunks.cHRM(chunk_type,chunk_data,chunk_crc)
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

    def png_writer(self):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc)
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc in self.chunk_list if chunk_type == b'IDAT')
        data = Chunks.IDAT(chunk_type, idat_data, chunk_crc, check.width, check.height, check.color_type)
        print(data.bytes_per_pixel)
        if data.bytes_per_pixel == 1:
            png_writer = png.Writer(data.width, data.height, greyscale=True)
        elif data.bytes_per_pixel == 2:
            png_writer = png.Writer(data.width, data.height, greyscale=True, alpha=True)
        elif data.bytes_per_pixel == 3:
            png_writer = png.Writer(data.width, data.height, greyscale=False)
        elif data.bytes_per_pixel == 4:
            png_writer = png.Writer(data.width, data.height, greyscale=False, alpha=True)
        return png_writer,data.width, data.height, data.bytes_per_pixel

    def save_image_with_png_writer(self, data, name):
        png_writer, width, height, bytes_per_pixel = self.png_writer()
        print(bytes_per_pixel)
        bytes_row_width = width * bytes_per_pixel
        pixels_grouped_by_rows = [data[i: i + bytes_row_width] for i in range(0, len(data), bytes_row_width)]

        writer = png.Writer(width, height , greyscale=False, alpha=True)
        f = open(name, 'wb')
        writer.write(f, pixels_grouped_by_rows)
        f.close()



    def ecb_encrypt(self,e,n,key_size):
        for chunk_type, chunk_data, chunk_crc in self.chunk_list:
            if chunk_type == b'IHDR':
                check = Chunks.IHDR(chunk_type,chunk_data,chunk_crc)
        idat_data = b''.join(chunk_data for chunk_type, chunk_data, chunk_crc in self.chunk_list if chunk_type == b'IDAT')
        data3 = Chunks.IDAT(chunk_type, idat_data, chunk_crc, check.width, check.height, check.color_type)
        data3.reconstructed_pixel_data()
        data = Encryption.ecb_encrypt(data3.data, e, n,key_size)
        print(data)
        self.save_image_with_png_writer(data,"dwe.png")





















