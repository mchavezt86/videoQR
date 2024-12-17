#import for QR generation
import os
import qrcode
from PIL import Image
import numpy as np
import cv2

#File to read.
dir=r'E:\01 PhD - VLC\08 Experiments\05 QR test'
os.chdir(dir)
file = open('blackcat.txt','rb')
bytes = file.read()

#Constant: ASCII 32 is 0 to our counting system.
start=32
black=(0,0,0)
white=(255,255,255)

#Variables
i=0
k=1
data=chr(32)
img_array=[]

#QR code settings
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=20,
    border=1,
)

#Loop the file bytes
for byte in bytes:
    data += chr(byte) #New beginning of the set
    i+=1
    if i==16: #Condition for data size
        i=0
        print(data)
        #QR clear, add data, make QR and change it to a OpenCV Mat format.
        #The ouput (for the QR settings) is a 460x460px image.
        qr.clear()
        qr.add_data(data)
        qr.make()
        imgqr = qr.make_image(fill_color="black", back_color="white")
        imgnp = np.array(imgqr)
        imgnp=imgnp.astype(np.uint8)*255
        img=cv2.cvtColor(imgnp,cv2.COLOR_GRAY2BGR)
        #Add borders to get a 720x480px image.
        finalQR = cv2.copyMakeBorder(img,10,10,10,10,cv2.BORDER_CONSTANT,value=white)
        #finalQR = cv2.copyMakeBorder(finalQR,0,0,60,60,cv2.BORDER_CONSTANT,value=black)
        #finalQR = cv2.copyMakeBorder(finalQR,0,0,60,60,cv2.BORDER_CONSTANT,value=white)
        border = int(finalQR.shape[0] / 12)
        finalQR = cv2.copyMakeBorder(finalQR,0,0,border,border,cv2.BORDER_CONSTANT,value=black)
        finalQR = cv2.copyMakeBorder(finalQR,0,0,border,border,cv2.BORDER_CONSTANT,value=white)
        #Add to image array
        img_array.append(finalQR)
        data = chr(start + k)
        k+=1

#Dimensions of the video
height, width, layers = finalQR.shape
size = (width,height)

#Create video file with VideoWriter
out = cv2.VideoWriter('seq001.avi',cv2.VideoWriter_fourcc(*'DIVX'), 60, size)

#Append each frame
for i in range(len(img_array)):
    out.write(img_array[i])
for i in range(len(img_array)):
    out.write(img_array[i])

#Release the file.
out.release()