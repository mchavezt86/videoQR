#Import OS library to read file.
import os
#Import Reed Solomon library.
#import unireedsolomon as rs
#import reedsolo as rs
#Import QR, image, numpy and cv2 for image and video generation.
import qrcode
from PIL import Image
import numpy as np
import cv2

#Import Pyjnius (import Java classes, classpath to JAR file is needed.)
import jnius_config
jnius_config.set_classpath(r'E:\Android\FLCoSRT01\app\libs\JavaReedSolomon.jar')
from jnius import autoclass

#Constants (and descriptions)
QR_BYTES = 17 #Capacity of QR, in bytes. Depends on QR version, 17 bytes is for version 1. 32 v2, 53 v3, 78 v4
RS_DATA_SIZE = 54 #Data capacity of Reed Solomon encoding.
RS_PARITY_SIZE = 23 #Parity size of Reed Solomon encoding.
RS_TOTAL_SIZE = 77 #Total size of Reed Solomon message.

#Reed Solomon encoder. We define the prime number generator to match the Java Backblaze (29).
#coder = rs.RSCoder(RS_TOTAL_SIZE,RS_DATA_SIZE,generator=2,prim=0x11d,c_exp=8)#,fcr=29)
#coder = rs.RSCodec(nsym=30,prim=0x11d,generator=2,nsize=175,fcr=0)
#We use the Reed Solomon defined in Java
RS = autoclass('com.backblaze.erasure.ReedSolomon')
rs = RS.create(RS_DATA_SIZE,RS_PARITY_SIZE)

#QR code encoder.
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=20,
    border=2,
)

#1)FILE READING IN BINARY MODE TO READ BYTES.
#
#File to read.
dir=r'E:\01 PhD - VLC\08 Experiments\05 QR test'
os.chdir(dir)
file = open('maps.txt','rb')
file_bytes = file.read()

#Total bytes in a batch (QR v1, 17 bytes: 1 byte for numbering, 16 bytes for data).
#totalBytes = 16*145

file_matrix = [] # Holds the file data read in bytes.

#Loop to fill the file matrix with the 16 bytes of data.
#for i in range(RS_DATA_SIZE):
#    file_matrix.append(file_bytes[i*(QR_BYTES-1):i*(QR_BYTES-1)+(QR_BYTES-1)])
for i in range(RS_DATA_SIZE):
    row = bytearray(file_bytes[i*(QR_BYTES-1):i*(QR_BYTES-1)+(QR_BYTES-1)])
    file_matrix.append(row)

for i in range(RS_DATA_SIZE,RS_TOTAL_SIZE):
    row = bytearray([0 for x in range(QR_BYTES-1)])
    file_matrix.append(row)

[print(i) for i in file_matrix]
#rs_matrix_t = [] #Holds the Reed Solomon output (Data + Parity) bytes, but the results are transposed.

#ENCODING USING REED SOLOMON. (OLD)
#
#Loop to use the file matrix to produce the Reed Solomon parity bytes.
#-Note:
# The file matrix is transposed because it is divided in 16 bytes of data. The Reed Solomon
# encoder's input is a 145 bytes and produces an extre 30 bytes of parity.
# Ex: 
#   Data[145] = [ Data0[16 bytes], Data1[16 bytes], ... Data144[16 bytes] ]
#   Reed Solomon: (after loop)
#       encoded0[175 bytes] = Data0[0],Data1[0], ..., Data144[0], Parity0[0], Parity1[0], ..., Parity29[0]
#       encoded1[175 bytes] = Data0[1],Data1[1], ..., Data144[1], Parity0[1], Parity1[1], ..., Parity29[1]
#           ...
#       encoded15[175 bytes] = Data0[15],Data1[15], ..., Data144[15], Parity0[15], Parity1[15], ..., Parity29[15]
#for i in range(QR_BYTES-1):
#    #row_rs = coder.encode([x[i] for x in file_matrix],poly=True) #poly=True to return an 'integer'
#    row_rs = coder.encode([x[i] for x in file_matrix]) #rs_encode_msg([x[i] for x in file_matrix])
#    #If poly is not False, returns the encoded Polynomial object instead of the polynomial translated back to a string (useful for debugging).
#    #rs_matrix_t.append(row_rs)
#    #rs_matrix_t.append([int(x) & 0xFF for x in row_rs])
#    rs_matrix_t.append(row_rs)
#    print(bytes(row_rs))

#ENCODING USING REED SOLOMON (NEW)
#-Using Java class ReedSolomon to encode the parity data in the matrix.
rs.encodeParity(file_matrix,0,QR_BYTES-1)

#Holds the Reed Solomon output (Data + Parity) bytes.
#rs_matrix = [[rs_matrix_t[j][i] for j in range(len(rs_matrix_t))] for i in range(len(rs_matrix_t[0]))]
#([print(i) for i in rs_matrix])

#[print(x[0:QR_BYTES]) for x in file_matrix]#rs_matrix] #Print results for testing.

#3)CREATE QR SEQUENCE AND SAVE A VIDEO FILE
#
#Initialize variables.
img_array = []
black=(0,0,0)
white=(255,255,255)

#The sequence consists of 175 QR codes.
for i in range(RS_TOTAL_SIZE):
    #Create data as list of bytes.
    data = bytes(bytes([i])+bytes(file_matrix[i][0:QR_BYTES]))#bytes(rs_matrix[i])) #added encoded
    print([b for b in data])
    #Clear QR data and generate new QR. The ouput (for the QR settings) is a 460x460px image.
    qr.clear()
    qr.add_data(data)
    qr.make()
    imgqr = qr.make_image(fill_color="black", back_color="white")
    #Convert QR image to OpenCV.
    imgnp = np.array(imgqr)
    imgnp=imgnp.astype(np.uint8)*255
    img=cv2.cvtColor(imgnp,cv2.COLOR_GRAY2BGR)
    #Add borders to get a 720x480px image.
    #finalQR = cv2.copyMakeBorder(img,10,10,10,10,cv2.BORDER_CONSTANT,value=white)
    #finalQR = cv2.copyMakeBorder(finalQR,0,0,60,60,cv2.BORDER_CONSTANT,value=black)
    #finalQR = cv2.copyMakeBorder(finalQR,0,0,60,60,cv2.BORDER_CONSTANT,value=white)
    border = int(img.shape[0] / 12)
    finalQR = cv2.copyMakeBorder(img,0,0,border,border,cv2.BORDER_CONSTANT,value=black)
    finalQR = cv2.copyMakeBorder(finalQR,0,0,border,border,cv2.BORDER_CONSTANT,value=white)
    #Replace black with gray
    #finalQR = cv2.add(finalQR,(128,128,128,0))
    #Add to image array
    img_array.append(finalQR)
    #Test: Display image
    cv2.imshow('QR',finalQR)
    cv2.waitKey(10)

#Dimensions of the video.
height, width, layers = finalQR.shape
size = (width,height)

#Create video file with VideoWriter.
out = cv2.VideoWriter('seq.avi',cv2.VideoWriter_fourcc(*'DIVX'), 20, size)

#Append each frame.
for i in range(len(img_array)):
    out.write(img_array[i])

#Release video file.
out.release()