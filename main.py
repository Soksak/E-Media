import cv2
import PNG_decoder
import key_gen


def menu():
    print("[1] - Wyswietl plik PNG")
    print("[2] - Wyswietl transformacje Fouriera")
    print("[3] - Wyswietl listę chunków pliku")
    print("[4] - Chunk IHDR")
    print("[5] - Chunk PLTE")
    print("[6] - Chunk IDAT")
    print("[7] - Chunk IEND")
    print("[8] - Chunk gAMA")
    print("[9] - Chunk tIME")
    print("[10] - Chunk cHRM")
    print("[11] - Anonimizacja pliku PNG")
    print("[12] - Szyforwanie ECB")
    print("[13] - Szyfrowanie CBC")
    print("[14] - Szyfowanie gotowa funkcją z biblioteki")
    print("[0] - Zakończenie działania")



image = "images/1.png"
png_file1 = cv2.imread(image)
png_file = open(image, 'rb')
PngSignature = b'\x89PNG\r\n\x1a\n'
if png_file.read(len(PngSignature)) != PngSignature:
    raise Exception('Invalid PNG Signature')

var = PNG_decoder.PNG_decoder(png_file,png_file1)
var.read_chunks()
keys = key_gen.RSA_key(1024)

menu()
opt = int(input("Wybierz opcje: "))
while opt != 0:
    if opt == 1:
        var.display_image()
    elif opt == 2:
        var.fourier_transform()
    elif opt == 3:
        var.print_chunks_list()
    elif opt == 4:
        var.IHDR_chunk()
    elif opt == 5:
        var.PLTE_chunk()
    elif opt == 6:
        var.IDAT_chunk()
    elif opt == 7:
        var.IEND_chunk()
    elif opt == 8:
        var.gAMA_chunk()
    elif opt == 9:
        var.tIME_chunk()
    elif opt == 10:
        var.cHRM_chunk()
    elif opt == 11:
        file_name = input("Podaj nazwe nowego pliku: ")
        var.clean_ancillary_chunks(file_name)
    elif opt == 12:
        var.ecb_encrypt(keys.public_key[0], keys.public_key[1], 1024, keys.private_key[0])
        print("\nZapisano pliki:\nafter_ecb_encryption.png\ndecrypted_ecb.png\n")
    elif opt == 13:
        var.cbc_encrypt(keys.public_key[0], keys.public_key[1], 1024, keys.private_key[0])
        print("\nZapisano pliki:\nafter_cbc_encryption.png\ndecrypted_cbc.png\n")
    elif opt == 14:
        var.library_encrypt(keys.public_key[0], keys.public_key[1], 1024)
        print("\nZapisano plik: after_library_encryption.png\n")
    else:
        print("Bledna opcja")
    opt = int(input("Wybierz opcje: "))