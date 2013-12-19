# Author: Peter Sovietov

import sys

Header = '''\
is_ym 0
clock_rate 1773400
frame_rate 50
frame_count %d
pan_a 50
pan_b 0
pan_c 0
volume 140
frame_data
%s
'''

def afx_to_text(afx_data): 
  frame = '%d %d 0 0 0 0 %d %d %d 0 0 0 0 255 0 0\n'
  volume = 0
  tone = 0
  noise = 0
  t_off = 0
  n_off = 0
  status = 0
  frame_data = ''
  frame_count = 0
  index = 0
  while index < len(afx_data):
    status = ord(afx_data[index])
    volume = status & 0xf
    t_off = (status & 0x10) != 0
    n_off = (status & 0x80) != 0
    index += 1
    if status & 0x20:
      tone = ord(afx_data[index]) | (ord(afx_data[index + 1]) << 8)
      index += 2
    if status & 0x40:
      noise = ord(afx_data[index])
      index += 1
    if noise == 0x20:
      break
    frame_data += frame % (tone & 0xff,
      (tone >> 8) & 0xf, noise, t_off | (n_off << 3), volume)
    frame_count += 1
  return Header % (frame_count, frame_data)

if len(sys.argv) != 3:
  print('afx_to_text input.afx output.txt')
  sys.exit(0)
f = open(sys.argv[1], 'rb')
afx_data = f.read()
f.close()
f = open(sys.argv[2], 'wb')
f.write(afx_to_text(afx_data))
f.close
