# Author: Peter Sovietov

import os
import sys
import locale
import subprocess
from Tkinter import *
import tkFileDialog
import psg_to_text
import fym_to_text
import afx_to_text
import ym_to_text

Header_template = {
  'is_ym': 1,
  'clock_rate': 1750000,
  'frame_rate': 48.828125,
  'frame_count': 0,
  'pan_a': 10,
  'pan_b': 50,
  'pan_c': 90,
  'volume': 50,
  'sample_rate': 96000,
  'eqp_stereo_on' : 0,
  'dc_filter_on' : 1
}

def get_module_path():
  if hasattr(sys, 'frozen'):
    return sys.executable
  else:
    return sys.argv[0]

class Ayumi_render_window:
  def __init__(self):
    self.root = Tk()
    self.header = {
      'sample_rate': StringVar(),
      'eqp_stereo_on': StringVar(),
      'dc_filter_on': StringVar(),
      'is_ym': StringVar(),
      'clock_rate': StringVar(),
      'frame_rate': StringVar(),
      'frame_count': StringVar(),
      'pan_a': StringVar(),
      'pan_b': StringVar(),
      'pan_c': StringVar(),
      'volume': StringVar()
    }
    Button(self.root, text='Load', command=lambda: load(self)).grid(row=0, column=0, sticky=W+E)
    Button(self.root, text='Save', command=lambda: save(self)).grid(row=1, column=0, sticky=W+E)
    self.l_load = Label(self.root)
    self.l_save = Label(self.root)
    self.l_load.grid(row=0, column=1, columnspan=4)
    self.l_save.grid(row=1, column=1, columnspan=4)
    i = 2
    Button(self.root, text='1750000', command=lambda:
      self.header['clock_rate'].set(1750000)).grid(row=2, column=2, sticky=W+E)
    Button(self.root, text='1773400', command=lambda:
      self.header['clock_rate'].set(1773400)).grid(row=2, column=3, sticky=W+E)
    Button(self.root, text='2000000', command=lambda:
      self.header['clock_rate'].set(2000000)).grid(row=2, column=4, sticky=W+E)
    Button(self.root, text='48.828125', command=lambda:
      self.header['frame_rate'].set(48.828125)).grid(row=6, column=2, sticky=W+E)
    Button(self.root, text='50', command=lambda:
      self.header['frame_rate'].set(50)).grid(row=6, column=3, sticky=W+E)
    Button(self.root, text='AY-3-8910', command=lambda:
      self.header['is_ym'].set(0)).grid(row=7, column=2, sticky=W+E)
    Button(self.root, text='YM2149', command=lambda:
      self.header['is_ym'].set(1)).grid(row=7, column=3, sticky=W+E)
    Button(self.root, text='44100', command=lambda:
      self.header['sample_rate'].set(44100)).grid(row=11, column=2, sticky=W+E)
    Button(self.root, text='48000', command=lambda:
      self.header['sample_rate'].set(48000)).grid(row=11, column=3, sticky=W+E)
    Button(self.root, text='96000', command=lambda:
      self.header['sample_rate'].set(96000)).grid(row=11, column=4, sticky=W+E)
    Button(self.root, text='Disable', command=lambda:
      self.header['pan_a'].set(-1)).grid(row=8, column=2, sticky=W+E)
    Button(self.root, text='Disable', command=lambda:
      self.header['pan_b'].set(-1)).grid(row=9, column=2, sticky=W+E)
    Button(self.root, text='Disable', command=lambda:
      self.header['pan_c'].set(-1)).grid(row=10, column=2, sticky=W+E)
    for k, v in sorted(self.header.items()):
      Label(self.root, text=k).grid(row=i, column=0)
      Entry(self.root, textvariable=v).grid(row=i, column=1, sticky=W+E)
      i += 1
    get_last_settings()
    for k, v in Header_template.items():
      self.header[k].set(v)
    self.frame_data = False
    self.root.resizable(0, 0)
    self.root.title('Ayumi render GUI by Peter Sovietov')
    self.root.mainloop()

def get_last_settings():
  if os.path.isfile('temp.txt'):
    f = open('temp.txt', 'r')
    for line in f:
      c = line.split()
      if c[0] == 'frame_data':
        return
      if c[0] == 'frame_rate':
        Header_template[c[0]] = float(c[1])
      else:
        Header_template[c[0]] = int(c[1])

def load(self):
  self.frame_data = False
  file_to_load = tkFileDialog.askopenfilename(filetypes=
    [('FYM', '.fym'), ('PSG', '.psg'), ('YM', '.ym'), ('AFX', '.afx')])
  if not file_to_load:
    return
  self.l_load['text'] = file_to_load
  self.l_save['text'] = ''
  f = open(file_to_load, 'rb')
  file_data = f.read()
  f.close()
  header = {}
  ext = os.path.splitext(file_to_load)[-1].lower()
  if ext == '.psg':
    self.frame_data = psg_to_text.get_frame_data(header, file_data)
  elif ext == '.fym':
    self.frame_data = fym_to_text.get_frame_data(header, file_data)
  elif ext == '.afx':
    self.frame_data = afx_to_text.get_frame_data(header, file_data)
  elif ext == '.ym':
    self.frame_data = ym_to_text.get_frame_data(header, file_data)
  if not self.frame_data:
    self.l_load['text'] = 'Unknown format'
    return
  for k, v in header.items():
    self.header[k].set(v)

def save_text(name, header, frame_data):
  header_data = ''
  for k, v in sorted(header.items()):
    header_data += '%s %s\n' % (k, v.get())
  f = open(name, 'wb')
  f.write(header_data + 'frame_data\n' + frame_data)
  f.close

def start_ayumi_render(self, command):
  localized = map(lambda x: x.encode(locale.getpreferredencoding()), command)
  startupinfo = subprocess.STARTUPINFO()
  startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
  p = subprocess.Popen(localized, startupinfo=startupinfo)
  if p.wait():
    self.l_save['text'] = 'Save error'
  else:
    self.l_save['text'] = command[-1]
   
def save(self):
  file_to_save = tkFileDialog.asksaveasfilename(filetypes=[('WAV', '.wav')], defaultextension='.wav')
  if not file_to_save or not self.frame_data:
    return
  path = os.path.split(get_module_path())[0]
  save_text(os.path.join(path, 'temp.txt'), self.header, self.frame_data)
  self.l_save['text'] = 'Please wait...'
  self.root.after(100, start_ayumi_render, self,
    [os.path.join(path, 'ayumi_render'), os.path.join(path, 'temp.txt'), file_to_save])

Ayumi_render_window()
