/* Author: Peter Sovietov */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "load_text.h"

static void skip(struct text_parser* p, int (*is_valid)(int)) {
  for (; p->index < p->size && is_valid(p->text[p->index]); p->index += 1) {
  }
}

static int scan(struct text_parser* p, int (*is_valid)(int)) {
  int end = p->index;
  for (; end < p->size && is_valid(p->text[end]); end += 1) {
  }
  return end - p->index;
}

static int ends_with(struct text_parser* p, const char* text, int size) {
  if (p->size - p->index < size || memcmp(&p->text[p->index], text, size)) {
    return 0;
  }
  return 1;
}

static int parse_next(struct text_parser* p, const char* name) {
  int size = strlen(name);
  skip(p, isspace);
  if (!ends_with(p, name, size)) {
    return 0;
  }
  p->index += size;
  return 1;
}

static unsigned int text_to_number(char* text, int size) {
  int i;
  int d = 1;
  unsigned int n = 0;
  for(i = size - 1; i >= 0; i -= 1) {
    n += (text[i] - '0') * d;
    d *= 10;
  }
  return n;
}

static int parse_number(struct text_parser* p, unsigned int* n) {
  int size;
  skip(p, isspace);
  size = scan(p, isdigit);
  if (size == 0) {
    return 0;
  }
  *n = text_to_number(&p->text[p->index], size);
  p->index += size;
  return 1;
}

static int parse_frames(struct text_parser* p, unsigned int* frame_data, int frame_count) {
  int i;
  unsigned int* buffer = frame_data;
  for (i = 0; i < frame_count * 16; i += 1) {
    if(!parse_number(p, buffer)) {
      return 0;
    }
    buffer += 1;
  }
  return 1;
}

static int load_file(const char* name, char** buffer, int* size) {
  FILE* f = fopen(name, "rb");
  if (f == NULL) {
    return 0;
  }
  fseek(f, 0, SEEK_END);
  *size = ftell(f);
  rewind(f);
  *buffer = (char*) malloc(*size + 1);
  if (*buffer == NULL) {
    fclose(f);
    return 0;
  }
  if ((int) fread(*buffer, 1, *size, f) != *size) {
    free(*buffer);
    fclose(f);
    return 0;
  }
  fclose(f);
  (*buffer)[*size] = 0;
  return 1;
}

static int is_not_space(int c) {
  return !isspace(c);
}

int load_text_file(const char* name, struct text_data* d) {
  unsigned int n;
  struct text_parser p;
  int ok = 1;
  if (!load_file(name, &p.text, &p.size)) {
    return 0;
  }
  memset(d, 0, sizeof(struct text_data));
  p.index = 0;
  while (p.index < p.size) {
    if (parse_next(&p, "is_ym") && parse_number(&p, &n)) {
      d->is_ym = n;
    } else if (parse_next(&p, "clock_rate") && parse_number(&p, &n)) {
      d->clock_rate = n;
    } else if (parse_next(&p, "frame_rate") && parse_number(&p, &n)) {
      d->frame_rate = n;
    } else if (parse_next(&p, "pan_a") && parse_number(&p, &n)) {
      d->pan[0] = n / 100.;
    } else if (parse_next(&p, "pan_b") && parse_number(&p, &n)) {
      d->pan[1] = n / 100.;
    } else if (parse_next(&p, "pan_c") && parse_number(&p, &n)) {
      d->pan[2] = n / 100.;
    } else if (parse_next(&p, "volume") && parse_number(&p, &n)) {
      d->volume = n / 100.;
    } else if (parse_next(&p, "enable_eqp_stereo")) {
      d->eqp_on = 1;
    } else if (parse_next(&p, "disable_dc_filter")) {
      d->dc_filter_off = 1;
    } else if (parse_next(&p, "frame_count") && parse_number(&p, &n)) {
      d->frame_data = (unsigned int*) malloc(n * 16 * sizeof(int));
      if (d->frame_data == NULL) {
        ok = 0;
        break;
      }
      d->frame_count = n;
    } else if (parse_next(&p, "frame_data") && parse_frames(&p, d->frame_data, d->frame_count)) {
      break;
    } else {
      skip(&p, is_not_space);
    }
  }
  free(p.text);
  return ok;
}
