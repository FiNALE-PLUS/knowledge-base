import numpy as np
from pandas import DataFrame
from scipy import stats


def strip_values_outside_standard_deviations(df: DataFrame, columns: list[str], num_deviations: int) -> DataFrame:
    filters_per_column = ((np.abs(stats.zscore(df[column])) < num_deviations) for column in columns)

    filter_list = (any(i) for i in zip(*filters_per_column))

    return df.loc[filter_list, :]

    # return df.loc[np.bitwise_and.reduce(np.abs(stats.zscore(df[col])) < num_deviations for col in columns)]
