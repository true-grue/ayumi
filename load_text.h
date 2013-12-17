/* Author: Peter Sovietov */

#ifndef LOAD_TEXT_H
#define LOAD_TEXT_H

struct text_data {
  int is_ym;
  int clock_rate;
  int frame_rate;
  int frame_count;
  double pan[3];
  double volume;
  unsigned int* frame_data;
};

struct text_parser {
  int index;
  int size;
  char* text;
};

int load_text_file(const char* name, struct text_data* d);

#endif
