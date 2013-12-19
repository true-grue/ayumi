# Author: Peter Sovietov

import sys
import struct

Header = '''\
is_ym 1
clock_rate %d
frame_rate %d
frame_count %d
pan_a 10
pan_b 50
pan_c 90
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

def ym_to_text(ym_data): 
  header = struct.unpack('>4s8sIIHIHIH', ym_data[:34])
  frame_count = header[2]
  interleaved = header[3] & 1
  sample_count = header[4]
  clock_rate = header[5]
  frame_rate = header[6]
  ym_data = ym_data[34:]
  for i in range(sample_count):
    sample_size = struct.unpack('>I', ym_data[:4])[0]
    ym_data = ym_data[4 + sample_size:]
  zero = ym_data.find('\0')
  ym_data = ym_data[zero + 1:]
  zero = ym_data.find('\0')
  ym_data = ym_data[zero + 1:]
  zero = ym_data.find('\0')
  ym_data = ym_data[zero + 1:]
  frame_data = []
  for i in range(frame_count):
    frame_data.append([0] * 16)
  if interleaved:
    for i in range(16):
      for j in range(frame_count):
        frame_data[j][i] = ord(ym_data[i * frame_count + j])
  else:
    for i in range(frame_count):
      for j in range(16):
        frame_data[i][j] = ord(ym_data[i * 16 + j])
  return generate_text(clock_rate, frame_rate, frame_count, frame_data)

if len(sys.argv) != 3:
  print('ym_to_text input.ym output.txt')
  sys.exit(0)
f = open(sys.argv[1], 'rb')
ym_data = f.read()
f.close()
if ym_data[4:12] != 'LeOnArD!':
  print('Compressed file?')
  sys.exit(0)
f = open(sys.argv[2], 'wb')
f.write(ym_to_text(ym_data))
f.close
