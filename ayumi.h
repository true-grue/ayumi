/* Author: Peter Sovietov */

#ifndef AYUMI_H
#define AYUMI_H

enum {
  SOUND_CHANNELS = 3,
  DECIMATOR_FACTOR = 8,
  DECIMATOR_SIZE = 192,
  DC_FILTER_SIZE = 1024
};

struct sound_channel {
  int tone_period;
  int tone_counter;
  int tone;
  int t_off;
  int n_off;
  int e_on;
  int volume;
  double pan_left;
  double pan_right;
};

struct dc_filter {
  double sum;
  double delay[DC_FILTER_SIZE];
};

struct ayumi {
  struct sound_channel channels[SOUND_CHANNELS];
  int noise_period;
  int noise_counter;
  int noise;
  int envelope_counter;
  int envelope_period;
  int envelope_shape;
  int envelope_segment;
  int envelope;
  const double* dac_table;
  double step;
  double point;
  double y_left[4];
  double y_right[4];
  double decimator_left[DECIMATOR_SIZE];
  double decimator_right[DECIMATOR_SIZE];
  int eqp_on;
  int dc_filter_on;
  int dc_index;
  struct dc_filter dc_left;
  struct dc_filter dc_right;
  double left;
  double right;
};

void ayumi_configure(struct ayumi* ay, int is_ym, double clock_rate, int sr);
void ayumi_set_pan(struct ayumi* ay, int index, double pan);
void ayumi_set_tone(struct ayumi* ay, int index, int period);
void ayumi_set_noise(struct ayumi* ay, int period);
void ayumi_set_mixer(struct ayumi* ay, int index, int t_off, int n_off, int e_on);
void ayumi_set_volume(struct ayumi* ay, int index, int volume);
void ayumi_set_envelope(struct ayumi* ay, int period);
void ayumi_set_envelope_shape(struct ayumi* ay, int shape);
void ayumi_process(struct ayumi* ay);
void ayumi_process_without_dc(struct ayumi* ay);

#endif
