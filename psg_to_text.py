# Author: Peter Sovietov

import sys

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

def frame_to_text(r, old_shape):
  frame = '%d ' * 15 + '%d\n'
  if r[13] != old_shape:
    old_shape = r[13]
  else:
    r[13] = 255
  return frame % tuple(r), old_shape

def get_frame_data(header, file_data):
  for k, v in Header_template.items():
    header[k] = v
  if file_data[:4] != 'PSG\x1a':
    return False
  r = [0] * 16
  old_shape = 255
  frame_data = ''
  header['frame_count'] = 0
  index = 0
  while index < len(file_data):
    command = ord(file_data[index])
    index += 1
    if command < 16:
      r[command] = ord(file_data[index])
      index += 1
    elif command == 0xfd:
      break
    elif command == 0xff:
      frame, old_shape = frame_to_text(r, old_shape)
      frame_data += frame
      header['frame_count'] += 1
    elif command == 0xfe:
      count = ord(file_data[index])
      index += 1
      for i in range(count * 4):
        frame, old_shape = frame_to_text(r, old_shape)
        frame_data += frame
        header['frame_count'] += 1
  return frame_data

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print('psg_to_text input.psg output.txt')
    sys.exit(0)
  f = open(sys.argv[1], 'rb')
  file_data = f.read()
  f.close()
  frame_data = get_frame_data(Header_template, file_data)
  if not frame_data:
    print('Unknown format')
    sys.exit(0)
  save_text(sys.argv[2], Header_template, frame_data)
