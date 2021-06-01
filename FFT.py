import cv2
import matplotlib.pyplot as plot
import numpy as np

class Fourier:
    def __init__(self, image):
        self.image = image

    def show_fft(self):
        image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        fft = np.fft.fft2(image)
        fft_shifted = np.fft.fftshift(fft)
        phase = np.angle(fft_shifted)
        back_to_org = np.fft.ifft2(fft)

        plot.subplot(141), plot.imshow(image, 'gray'), plot.title("Image")
        plot.subplot(142), plot.imshow(np.log(1+np.abs(fft_shifted)), 'gray'), plot.title("Centered spectrum")
        plot.subplot(143), plot.imshow(phase, 'gray'), plot.title("Phase spectrum")
        plot.subplot(144), plot.imshow(np.abs(back_to_org), "gray"), plot.title("Processed Image")
        plot.show()