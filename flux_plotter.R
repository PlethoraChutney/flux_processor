library(tidyverse)
library(ggokabeito)

raw_data <- read_csv('processed_test_data.csv', col_types = 'ffddff')

data <- raw_data %>% 
  filter(Plate == 'Equilibration') %>% 
  filter(Time == max(Time)) %>% 
  select(Row, Column, 'Equil_Flr' = Fluorescence) %>% 
  right_join(raw_data, by = c('Row', 'Column')) %>% 
  mutate(Fluorescence = Fluorescence / Equil_Flr)


processed <- data %>% 
  group_by(Condition, Time, Plate) %>% 
  summarize(Mean_Fluorescence = mean(Fluorescence))

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
  geom_line(data = data, aes(y = Fluorescence, group = interaction(Row, Column, Plate)), alpha = 0.2) +
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
  labs(
    y = 'Relative Fluorescence',
    x = 'Time (s)',
    color = 'Condition',
    fill = 'Reagent added'
  )
ggsave('flux_plot.png', width = 6, height = 4)
