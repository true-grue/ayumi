# Author: Peter Sovietov

import sys
import struct
import zlib

Header = '''\
is_ym 1
clock_rate %d
frame_rate %d
frame_count %d
pan_a 10
pan_b 90
pan_c 50
volume 50
frame_data
'''

def generate_text(clock_rate, frame_rate, frame_count, frame_data):
  text = Header % (clock_rate, frame_rate, frame_count)
  for i in range(len(frame_data)):
    for j in range(15):
      text += str(frame_data[i][j]) + ' '
    text += str(frame_data[i][15]) + '\n'
  return text

def fym_to_text(fym_data): 
  header = struct.unpack('<IIIII', fym_data[:20])
  header_size = header[0]
  frame_count = header[1]
  clock_rate = header[3]
  frame_rate = header[4]
  fym_data = fym_data[header_size:]
  frame_data = []
  for i in range(frame_count):
    frame_data.append([0] * 16)
  for i in range(14):
    for j in range(frame_count):
      frame_data[j][i] = ord(fym_data[i * frame_count + j])
  return generate_text(clock_rate, frame_rate, frame_count, frame_data)

if len(sys.argv) != 3:
  print('fym_to_text input.fym output.txt')
  sys.exit(0)
f = open(sys.argv[1], 'rb')
fym_data = zlib.decompress(f.read())
f.close()
f = open(sys.argv[2], 'wb')
f.write(fym_to_text(fym_data))
f.close
