import pandas as pd

# Load the CSV file
df = pd.read_csv('results/index-timings.csv')

# Group by 'test_name' and calculate the required statistics
grouped_df = df.groupby('test_name')['avg_duration_in_ms'].agg(['mean', 'min', 'max', 'std'])

# Save the result to a new CSV file
grouped_df.to_csv('results/bench-summary.csv')

# Display the result
print(grouped_df)