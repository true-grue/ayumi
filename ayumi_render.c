/* Author: Peter Sovietov */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ayumi.h"
#include "load_text.h"

#define SR 44100

#define WAVE_FORMAT_IEEE_FLOAT 3

int save_wave_file(const char* name, float* data, int sample_rate, int sample_count) {
  FILE* f;
  char header[58];
  int channel_count = 2;
  int sample_size = sizeof(float);  
  int data_size = sample_size * channel_count * sample_count;
  int pad = data_size & 1;
  memcpy(&header[0], "RIFF", 4);
  *((int*) (header + 4)) = 50 + data_size + pad;
  memcpy(&header[8], "WAVE", 4);
  memcpy(&header[12], "fmt ", 4);
  *((int*) (header + 16)) = 18;
  *((short*) (header + 20)) = WAVE_FORMAT_IEEE_FLOAT;
  *((short*) (header + 22)) = (short) channel_count;
  *((int*) (header + 24)) = sample_rate;
  *((int*) (header + 28)) = sample_rate * sample_size * channel_count;
  *((short*) (header + 32)) = (short) (sample_size * channel_count);
  *((short*) (header + 34)) = (short) (8 * sample_size);
  *((short*) (header + 36)) = 0;
  memcpy(&header[38], "fact", 4);
  *((int*) (header + 42)) = 4;
  *((int*) (header + 46)) = channel_count * sample_count;
  memcpy(&header[50], "data", 4);
  *((int*) (header + 54)) = data_size;
  f = fopen(name, "wb");
  if (f == NULL) {
    return 0;
  }
  fwrite(header, 1, sizeof(header), f);
  fwrite(data, 1, data_size, f);
  if (pad) {
    fwrite(&pad, 1, 1, f);
  }
  fclose(f);
  return 1;
}

void update_ayumi_state(struct ayumi* ay, unsigned int* r) {
  ayumi_set_tone(ay, 0, (r[1] << 8) | r[0]);
  ayumi_set_tone(ay, 1, (r[3] << 8) | r[2]);
  ayumi_set_tone(ay, 2, (r[5] << 8) | r[4]);
  ayumi_set_noise(ay, r[6]);
  ayumi_set_mixer(ay, 0, r[7] & 1, (r[7] >> 3) & 1, r[8] >> 4);
  ayumi_set_mixer(ay, 1, (r[7] >> 1) & 1, (r[7] >> 4) & 1, r[9] >> 4);
  ayumi_set_mixer(ay, 2, (r[7] >> 2) & 1, (r[7] >> 5) & 1, r[10] >> 4);
  ayumi_set_volume(ay, 0, r[8] & 0xf);
  ayumi_set_volume(ay, 1, r[9] & 0xf);
  ayumi_set_volume(ay, 2, r[10] & 0xf);
  ayumi_set_envelope(ay, (r[12] << 8) | r[11]);
  if (r[13] != 255) {
    ayumi_set_envelope_shape(ay, r[13]);
  }
}

void ayumi_render(struct ayumi* ay, struct text_data* data, float* sample_data) {
  int frame = 0;
  int isr_period = SR / data->frame_rate;
  int isr_counter = 0;
  float* out = sample_data;
  while (frame < data->frame_count) {
    isr_counter += 1;
    if (isr_counter >= isr_period) {
      isr_counter = 0;
      update_ayumi_state(ay, &data->frame_data[frame * 16]);
      frame += 1;
    }
    ayumi_process(ay);
    out[0] = (float) (ay->left * data->volume);
    out[1] = (float) (ay->right * data->volume);
    out += 2;
  }
}

int main(int argc, char** argv) {
  int sample_count;
  float* sample_data;
  struct text_data data;
  struct ayumi ay;
  if (argc != 3) {
    printf("ayumi_render input.txt output.wav\n");
    return 0;
  }
  if(!load_text_file(argv[1], &data)) {
    printf("Load error\n");
    return EXIT_FAILURE;
  }
  sample_count = (SR / data.frame_rate) * data.frame_count;
  sample_data = (float*) malloc(sample_count * sizeof(float) * 2);
  if (sample_data == NULL) {
    printf("Memory allocation error\n");
    return EXIT_FAILURE;
  }
  ayumi_configure(&ay, data.is_ym, data.clock_rate, SR);
  ayumi_set_pan(&ay, 0, data.pan[0]);
  ayumi_set_pan(&ay, 1, data.pan[1]);
  ayumi_set_pan(&ay, 2, data.pan[2]);
  ayumi_render(&ay, &data, sample_data);
  if (!save_wave_file(argv[2], sample_data, SR, sample_count)) {
    printf("Save error\n");
    return EXIT_FAILURE;
  }
  return 0;
}
