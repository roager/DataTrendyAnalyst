from datatrendyanalyst.race import load_and_prepare_data
df = load_and_prepare_data("data/world_tourism_sample.csv", "year", "country", "arrivals_millions", steps_per_period=48)
print("Time at index 1:")
frame_1 = df[df['year'] == df['year'].unique()[1]]
print(frame_1.head(20))
