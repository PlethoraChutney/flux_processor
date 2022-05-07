library(tidyverse)
library(ggokabeito)

filename <- list.files(pattern = 'processed.*\\.csv')[1]
base_name <- str_replace(filename, 'processed_flux_assay_', '')
base_name <- str_replace(base_name, '.csv', '')
raw_data <- read_csv(filename, col_types = 'dffffd')

data <- raw_data %>% 
  filter(Plate == 'Equilibration') %>% 
  filter(Time == max(Time)) %>% 
  select(Row, Column, 'Equil_Flr' = Fluorescence) %>% 
  right_join(raw_data, by = c('Row', 'Column')) %>% 
  mutate(Fluorescence = Fluorescence / Equil_Flr)


processed <- data %>% 
  group_by(Condition, Time, Plate) %>% 
  summarize(Mean_Fluorescence = mean(Fluorescence), SD = sd(Fluorescence)) %>% 
  mutate(Low = Mean_Fluorescence - SD, High = Mean_Fluorescence + SD)

plates <- data %>% 
  group_by(Plate) %>% 
  summarize(start = min(Time), end = max(Time))

joiners <- processed %>% 
  group_by(Plate, Condition) %>% 
  filter(Time == max(Time) | Time == min(Time)) %>% 
  group_by(Condition) %>% 
  mutate(Plate = lead(Plate)) %>% 
  drop_na()

processed %>% 
  ggplot(aes(x = Time, y = Mean_Fluorescence, color = Condition, group = interaction(Condition, Plate))) +
  theme_minimal() +
  geom_rect(
    inherit.aes = FALSE,
    data = plates,
    aes(xmin = start, xmax = end, fill = Plate),
    ymin = -Inf,
    ymax = Inf,
    alpha = 0.05
  ) +
  geom_line(
    data = joiners,
    aes(x = Time, y = Mean_Fluorescence, group = interaction(Condition, Plate), color = Condition),
    inherit.aes = FALSE,
    size = 2,
    linetype = 'dotted',
    lineend = 'round'
  ) +
  geom_line(size = 2, lineend = 'round') +
  scale_color_okabe_ito() +
  scale_fill_manual(values = c(
    "#0077bb",
    "#009988",
    "#cc3311",
    "#ee3377"
  )) +
  scale_y_continuous(
    breaks = seq(0, 1, 0.25)
  ) +
  labs(
    y = 'Relative Fluorescence',
    x = 'Time (s)',
    color = 'Condition',
    fill = 'Reagent added'
  ) +
  expand_limits(y = c(0, 1))
ggsave(paste0(base_name, '_Mean.png'), width = 7, height = 4, bg = 'white')

data %>% 
  ggplot(aes(x = Time, y = Fluorescence, color = Condition, group = interaction(Row, Column, Plate))) +
  theme_minimal() +
  geom_rect(
    inherit.aes = FALSE,
    data = plates,
    aes(xmin = start, xmax = end, fill = Plate),
    ymin = -Inf,
    ymax = Inf,
    alpha = 0.05
  ) +
  geom_line(lineend = 'round') +
  scale_color_okabe_ito() +
  scale_fill_manual(values = c(
    "#0077bb",
    "#009988",
    "#cc3311",
    "#ee3377"
  )) +
  scale_y_continuous(
    breaks = seq(0, 1, 0.25)
  ) +
  labs(
    y = 'Relative Fluorescence',
    x = 'Time (s)',
    color = 'Condition',
    fill = 'Reagent added'
  ) +
  expand_limits(y = c(0, 1))
ggsave(paste0(base_name, '_Raw.png'), width = 7, height = 4, bg = 'white')
