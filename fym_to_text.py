# Author: Peter Sovietov

import sys
import struct
import zlib

Header_template = {
  'pan_a': 10,
  'pan_b': 50,
  'pan_c': 90,
  'volume': 50
}

def save_text(name, header, frame_data):
  header_data = ''
  for k, v in sorted(header.items()):
    header_data += '%s %d\n' % (k, v)
  f = open(name, 'wb')
  f.write(header_data + 'frame_data\n' + frame_data)
  f.close

def frames_to_text(frame_data):
  text = ''
  for i in range(len(frame_data)):
    for j in range(15):
      text += str(frame_data[i][j]) + ' '
    text += str(frame_data[i][15]) + '\n'
  return text

def get_frame_data(header, file_data):
  for k, v in Header_template.items():
    header[k] = v
  fym_data = zlib.decompress(file_data)
  fym_header = struct.unpack('<IIIII', fym_data[:20])
  fym_header_size = fym_header[0]
  header['frame_count'] = fym_header[1]
  header['clock_rate'] = fym_header[3]
  header['frame_rate'] = fym_header[4]
  fym_data = fym_data[fym_header_size:]
  frame_data = []
  for i in range(header['frame_count']):
    frame_data.append([0] * 16)
  for i in range(14):
    for j in range(header['frame_count']):
      frame_data[j][i] = ord(fym_data[i * header['frame_count'] + j])
  return frames_to_text(frame_data)

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print('fym_to_text input.fym output.txt')
    sys.exit(0)
  f = open(sys.argv[1], 'rb')
  file_data = f.read()
  f.close()
  frame_data = get_frame_data(Header_template, file_data)
  if not frame_data:
    print('Unknown format')
    sys.exit(0)
  save_text(sys.argv[2], Header_template, frame_data)
