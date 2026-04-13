import numpy as np
from pandas import DataFrame
from scipy import stats


def strip_values_outside_standard_deviations(df: DataFrame, columns: list[str], num_deviations: int) -> DataFrame:
    """
    Filters rows in a DataFrame by removing any rows that have values in `columns` that fall outside the bounds
    specified by being `num_deviations` from the column's mean.

    :param df: The DataFrame to be filtered.
    :param columns: The list of columns to filter by.
    :param num_deviations: The number of standard deviations from the mean
    that a column's value can be before being omitted.
    :return: The `df` with values from `columns` outside `num_deviations` standard deviations from the mean omitted.
    """

    filters_per_column = ((np.abs(stats.zscore(df[column])) < num_deviations) for column in columns)

    filter_list = (any(i) for i in zip(*filters_per_column))

    return df.loc[filter_list, :]
