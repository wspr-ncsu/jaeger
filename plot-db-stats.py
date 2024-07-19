import pandas as pd
import matplotlib.pyplot as plt

test_fetch = 'db.fetch'
test_insert = 'db.insert'
conversion_factors = {
    'b': 1,
    'kib': 1024,
    'mib': 1024**2,
    'gib': 1024**3,
    'tib': 1024**4,
}

def convert_size(size_str, target_unit='gib'):
    num, unit = size_str.split()
    return float(num) * conversion_factors[unit.lower()] / conversion_factors[target_unit]

def get_test_stats(daf, test_name):
    df: pd.DataFrame = daf[daf['test_name'] == test_name]
    df = df.groupby('size')['duration_in_ms'].agg(['mean', 'max', 'min', 'std']).reset_index()
    # print(test_name)
    # print(df)
    return df

def main():
    # Load the data
    df = pd.read_csv('results/queries.csv')
    df['size'] = df['size'].apply(convert_size)

    fetch_df = get_test_stats(df, test_fetch)
    insert_df = get_test_stats(df, test_insert)

    # Plot Fetch data
    plt.errorbar(fetch_df['size'], fetch_df['mean'], yerr=fetch_df['std'], label='Fetch', fmt='-o', capsize=5)

    # Plot Insert data
    plt.errorbar(insert_df['size'], insert_df['mean'], yerr=insert_df['std'], label='Insert', fmt='-o', capsize=5)

    # Adding labels and title
    plt.xlabel('Size (GB)')
    plt.ylabel('Time (ms)')
    plt.title('Query performance as size increases')

    # Adding legend
    plt.legend()

    plt.savefig('results/query_performance.png', format='png')

    # Display the plot
    plt.show()

if __name__ == '__main__':
    main()