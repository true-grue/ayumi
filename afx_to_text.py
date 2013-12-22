# Author: Peter Sovietov

import sys

Header_template = {
  'pan_a': 50,
  'pan_b': 0,
  'pan_c': 0,
  'volume': 140
}

def save_text(name, header, frame_data):
  header_data = ''
  for k, v in sorted(header.items()):
    header_data += '%s %d\n' % (k, v)
  f = open(name, 'wb')
  f.write(header_data + 'frame_data\n' + frame_data)
  f.close

def get_frame_data(header, file_data): 
  for k, v in Header_template.items():
    header[k] = v
  frame = '%d %d 0 0 0 0 %d %d %d 0 0 0 0 255 0 0\n'
  volume = 0
  tone = 0
  noise = 0
  t_off = 0
  n_off = 0
  status = 0
  frame_data = ''
  header['frame_count'] = 0
  index = 0
  while index < len(file_data):
    status = ord(file_data[index])
    volume = status & 0xf
    t_off = (status & 0x10) != 0
    n_off = (status & 0x80) != 0
    index += 1
    if status & 0x20:
      tone = ord(file_data[index]) | (ord(file_data[index + 1]) << 8)
      index += 2
    if status & 0x40:
      noise = ord(file_data[index])
      index += 1
    if noise == 0x20:
      break
    frame_data += frame % (tone & 0xff,
      (tone >> 8) & 0xf, noise, t_off | (n_off << 3), volume)
    header['frame_count'] += 1
  return frame_data

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print('afx_to_text input.afx output.txt')
    sys.exit(0)
  f = open(sys.argv[1], 'rb')
  file_data = f.read()
  f.close()
  frame_data = get_frame_data(Header_template, file_data)
  if not frame_data:
    print('Unknown format')
    sys.exit(0)
  save_text(sys.argv[2], Header_template, frame_data)
