library(tidyverse)
library(ggokabeito)

data <- read_csv('processed_test_data.csv', col_types = 'fffdfd')

processed <- data %>% 
  group_by(Condition, Time) %>% 
  summarize(Mean_Fluorescence = mean(Fluorescence), SD = sd(Fluorescence))
  # mutate(Low = Mean_Fluorescence - SD, High = Mean_Fluorescence + SD)

plates <- data %>% 
  group_by(Plate) %>% 
  summarize(start = min(Time), end = max(Time))

processed %>% 
  ggplot(aes(x = Time, y = Mean_Fluorescence, color = Condition)) +
  theme_minimal() +
  geom_rect(
    inherit.aes = FALSE,
    data = plates,
    aes(xmin = start, xmax = end, fill = Plate),
    ymin = -Inf,
    ymax = Inf,
    alpha = 0.2
  ) +
  geom_line(data = data, aes(y = Fluorescence, group = interaction(Row, Column)), alpha = 0.2) +
  geom_line(size = 2) +
  scale_color_okabe_ito() +
  scale_fill_manual(values = c(
    "#0077bb",
    "#009988",
    "#cc3311",
    "#ee3377"
  ))
