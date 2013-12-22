# Author: Peter Sovietov

import sys
import struct

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
  if file_data[4:12] != 'LeOnArD!':
    return False
  ym_header = struct.unpack('>4s8sIIHIHIH', file_data[:34])
  header['frame_count'] = ym_header[2]
  interleaved = ym_header[3] & 1
  sample_count = ym_header[4]
  header['clock_rate'] = ym_header[5]
  header['frame_rate'] = ym_header[6]
  file_data = file_data[34:]
  for i in range(sample_count):
    sample_size = struct.unpack('>I', file_data[:4])[0]
    file_data = file_data[4 + sample_size:]
  zero = file_data.find('\0')
  file_data = file_data[zero + 1:]
  zero = file_data.find('\0')
  file_data = file_data[zero + 1:]
  zero = file_data.find('\0')
  file_data = file_data[zero + 1:]
  frame_data = []
  for i in range(header['frame_count']):
    frame_data.append([0] * 16)
  for i in range(14):
    for j in range(header['frame_count']):
      frame_data[j][i] = ord(file_data[i * header['frame_count'] + j])
  return frames_to_text(frame_data)

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print('ym_to_text input.ym output.txt')
    sys.exit(0)
  f = open(sys.argv[1], 'rb')
  file_data = f.read()
  f.close()
  frame_data = get_frame_data(Header_template, file_data)
  if not frame_data:
    print('Unknown format')
    sys.exit(0)
  save_text(sys.argv[2], Header_template, frame_data)
