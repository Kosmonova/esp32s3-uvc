# SPDX-FileCopyrightText: 2022 Espressif Systems (Shanghai) CO LTD
# SPDX-License-Identifier: Unlicense OR CC0-1.0
import socket

import cv2
import numpy as np
import binascii

frame_count = 0
stream = bytearray()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect(('esp-cam.local', 2222))

    print('Receiving data ')
    while True:
        data = sock.recv(4096)

        if not data:
            break
        stream += data
        print('.', end='', flush=True)

        a = stream.find(b'\xff\xd8')
        b = stream.find(b'\xff\xd9', a)

        if a != -1 and b != -1:
            jpg = stream[a + 2:b]
            stream = stream[b + 2:]
            buffer = np.frombuffer(jpg, dtype=np.uint8)
            print(len(buffer))

            if len(buffer) != 38400:
                continue

            #with np.printoptions(threshold=np.inf):
                #print(buffer)
            height = 120
            width = 160
            frame = np.zeros((height,width,3), dtype=np.uint8)

            bY = buffer.reshape(height, width, 2)[:,:,0]

            bU = buffer[1::4]
            bU = [*sum(zip(bU,bU),())]
            bU = np.reshape(bU, (height, width))
            bU = np.int_(bU)

            bV = buffer[3::4]
            bV = [*sum(zip(bV,bV),())]
            bV = np.reshape(bV, (height, width))
            bV = np.int_(bV)

            c = bY - 16
            d = bU - 128
            e = bV - 128

            bR = (298 * c + 409 * e + 128) >> 8
            bG = (298 * c - 100 * d - 208 * e + 128) >> 8
            bB = (298 * c + 516 * d + 128) >> 8

            #bR = bY + 1.4075 * (bV - 128)
            #bG = bY - 0.3455 * (bU - 128) - (0.7169 * (bV - 128))
            #bB = bY + 1.7790 * (bU - 128)

            frame[:,:,0] = np.clip(bB, 0, 255)
            frame[:,:,1] = np.clip(bG, 0, 255)
            frame[:,:,2] = np.clip(bR, 0, 255)

            frame = cv2.resize(frame, (640, 480))
            cv2.imshow('Stream', frame)
            if cv2.waitKey(10) == 27:
                exit(0)
            frame_count += 1

print('\nFrames received ', frame_count)
