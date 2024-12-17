
#Import OS library to read file.
import os
#Import Reed Solomon library.
#import unireedsolomon as rs
#import reedsolo as rs
#Import datamatrix, image, numpy and cv2 for image and video generation.
from pylibdmtx.pylibdmtx import encode
from PIL import Image
import numpy as np
import cv2

#Import Pyjnius (import Java classes, classpath to JAR file is needed.)
import jnius_config
jnius_config.set_classpath(r'E:\Android\FLCoSRT01\app\libs\JavaReedSolomon.jar')
from jnius import autoclass

#Constants (and descriptions)
DM_BYTES = 112 #Capacity of DM: https://jpgraph.net/download/manuals/chunkhtml/ch26.html
RS_DATA_SIZE = 54 #Data capacity of Reed Solomon encoding.
RS_PARITY_SIZE = 23 #Parity size of Reed Solomon encoding.
RS_TOTAL_SIZE = 77 #Total size of Reed Solomon message.

#Reed Solomon encoder. We define the prime number generator to match the Java Backblaze (29).
#coder = rs.RSCoder(RS_TOTAL_SIZE,RS_DATA_SIZE,generator=2,prim=0x11d,c_exp=8)#,fcr=29)
#coder = rs.RSCodec(nsym=30,prim=0x11d,generator=2,nsize=175,fcr=0)
#We use the Reed Solomon defined in Java
RS = autoclass('com.backblaze.erasure.ReedSolomon')
rs = RS.create(RS_DATA_SIZE,RS_PARITY_SIZE)

#1)FILE READING IN BINARY MODE TO READ BYTES.
#
#File to read.
dir=r'E:\01 PhD - VLC\08 Experiments\05 QR test'
os.chdir(dir)
file = open('blackcat1.txt','rb')
file_bytes = file.read()

#Total bytes in a batch (QR v1, 17 bytes: 1 byte for numbering, 16 bytes for data).
#totalBytes = 16*145

file_matrix = [] # Holds the file data read in bytes.

#Loop to fill the file matrix with the 16 bytes of data.
#for i in range(RS_DATA_SIZE):
#    file_matrix.append(file_bytes[i*(DM_BYTES-1):i*(DM_BYTES-1)+(DM_BYTES-1)])
for i in range(RS_DATA_SIZE):
    row = bytearray(file_bytes[i*(DM_BYTES-1):i*(DM_BYTES-1)+(DM_BYTES-1)])
    file_matrix.append(row)

for i in range(RS_DATA_SIZE,RS_TOTAL_SIZE):
    row = bytearray([0 for x in range(DM_BYTES-1)])
    file_matrix.append(row)

[print(i) for i in file_matrix]
#rs_matrix_t = [] #Holds the Reed Solomon output (Data + Parity) bytes, but the results are transposed.

#ENCODING USING REED SOLOMON (NEW)
#-Using Java class ReedSolomon to encode the parity data in the matrix.
rs.encodeParity(file_matrix,0,DM_BYTES-1)

#3)CREATE QR SEQUENCE AND SAVE A VIDEO FILE
#
#Initialize variables.
img_array = []
black=(0,0,0)
white=(255,255,255)

#The sequence consists of 175 QR codes.
for i in range(RS_TOTAL_SIZE):
    #Create data as list of bytes.
    data = bytes(bytes([i])+bytes(file_matrix[i][0:DM_BYTES]))#bytes(rs_matrix[i])) #added encoded
    print([b for b in data])
    #Create Datamatrix sequence
    encoded = encode(data,scheme = 'Base256') #'Base256'
    imgdm = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    #Convert QR image to OpenCV.
    img = np.array(imgdm)
    #Resuze
    finalQR = cv2.resize(img,dsize=(540,540),interpolation=cv2.INTER_AREA)
    #Add borders to get a 720x480px image.
    border = int(540/12) #int(encoded.width / 12)
    #finalQR = cv2.copyMakeBorder(img,10,10,10,10,cv2.BORDER_CONSTANT,value=white)
    finalQR = cv2.copyMakeBorder(finalQR,0,0,border,border,cv2.BORDER_CONSTANT,value=black)
    finalQR = cv2.copyMakeBorder(finalQR,0,0,border,border,cv2.BORDER_CONSTANT,value=white)
    #Replace black with gray
    #finalQR = cv2.add(finalQR,(128,128,128,0))
    #Add to image array
    img_array.append(finalQR)
    #Test: Display image
    cv2.imshow('DM',finalQR)
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