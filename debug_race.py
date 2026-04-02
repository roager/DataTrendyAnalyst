from datatrendyanalyst.race import load_and_prepare_data

df = load_and_prepare_data("data/world_tourism_sample.csv", "year", "country", "arrivals_millions", steps_per_period=48)
print(f"Total rows: {len(df)}")
print(f"Unique years: {df['year'].nunique()}")
print(df.head(20))
