# Author: Peter Sovietov

import sys

Header = '''\
is_ym 1
clock_rate 1750000
frame_rate 49
frame_count %d
pan_a 10
pan_b 50
pan_c 90
volume 50
frame_data
%s
'''

def generate_frame(r, old_shape):
  frame = '%d ' * 15 + '%d\n'
  if r[13] != old_shape:
    old_shape = r[13]
  else:
    r[13] = 255
  return frame % tuple(r), old_shape

def psg_to_text(psg_data): 
  r = [0] * 16
  old_shape = 255
  frame_data = ''
  frame_count = 0
  index = 0
  while index < len(psg_data):
    command = ord(psg_data[index])
    index += 1
    if command < 16:
      r[command] = ord(psg_data[index])
      index += 1
    elif command == 0xfd:
      break
    elif command == 0xff:
      frame, old_shape = generate_frame(r, old_shape)
      frame_data += frame
      frame_count += 1
    elif command == 0xfe:
      count = ord(psg_data[index])
      index += 1
      for i in range(count * 4):
        frame, old_shape = generate_frame(r, old_shape)
        frame_data += frame
        frame_count += 1
  return Header % (frame_count, frame_data)

if len(sys.argv) != 3:
  print('psg_to_text input.psg output.txt')
  sys.exit(0)
f = open(sys.argv[1], 'rb')
psg_data = f.read()
f.close()
if psg_data[:4] != 'PSG\x1a':
  print('Unknown format')
  sys.exit(0)
f = open(sys.argv[2], 'wb')
f.write(psg_to_text(psg_data))
f.close
