import csv
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import cv


def sort_by_system_order(df, system_order):
    df["system_order"] = df["system"].map(system_order)
    df = df.sort_values("system_order").drop("system_order", axis=1)
    return df


def calculate_pearson_spearman_correlation(original_df, reproduced_df, system_order):
    # Sort dataframes by the defined system order
    original_df = sort_by_system_order(original_df.copy(), system_order)
    reproduced_df = sort_by_system_order(reproduced_df.copy(), system_order)

    # Calculate correlations
    pearson_corr, pearson_p = pearsonr(
        original_df["best_worst_scale"], reproduced_df["best_worst_scale"]
    )
    spearman_corr, spearman_p = spearmanr(
        original_df["best_worst_scale"], reproduced_df["best_worst_scale"]
    )

    # Create result dataframes with all information
    result_df = pd.DataFrame(
        {
            "system": original_df["system"],
            "original_value": original_df["best_worst_scale"],
            "reproduced_value": reproduced_df["best_worst_scale"],
            "pearson_corr": [pearson_corr] * len(original_df),
            "pearson_p": [pearson_p] * len(original_df),
            "spearman_corr": [spearman_corr] * len(original_df),
            "spearman_p": [spearman_p] * len(original_df),
        }
    )

    # Ensure final result follows system order
    result_df = sort_by_system_order(result_df, system_order)

    # Save results
    result_df.to_csv(
        "results/lab1/tables/correlations.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    result_df.to_latex(
        "results/lab1/tables/correlations.tex",
        float_format="{:0.2f}".format,
        escape=True,
    )
    print("Correlation Results:")
    print(result_df)


def create_cv_summary(df, system_order):
    # Create summary dataframe with only System, O, R, and CV*
    summary_df = pd.DataFrame(
        {"System": df["system"], "O": df["original_unshifted"], "R": df["reproduced_unshifted"], "CV*": df["CV*"]}
    )

    # Ensure summary follows system order
    summary_df = sort_by_system_order(summary_df.rename(columns={"System": "system"}), system_order).rename(columns={"system": "System"})

    # Save summary results
    summary_df.to_csv(
        "results/lab1/tables/cv_summary.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    summary_df.to_latex(
        "results/lab1/tables/cv_summary.tex",
        float_format="{:0.2f}".format,
        escape=True,
    )
    print("\nCV Summary Results:")
    print(summary_df)


def calculate_coefficient_of_variation(original_df, reproduced_df, range_start, range_end, system_order):
    # Sort dataframes by the defined system order
    original_df = sort_by_system_order(original_df.copy(), system_order)
    reproduced_df = sort_by_system_order(reproduced_df.copy(), system_order)

    # Store original values before shifting
    original_unshifted = original_df["best_worst_scale"]
    reproduced_unshifted = reproduced_df["best_worst_scale"]

    # Adjust values if needed
    if range_start < 0:
        original_values = original_df["best_worst_scale"] + abs(range_start)
        reproduced_values = reproduced_df["best_worst_scale"] + abs(range_start)
    else:
        original_values = original_df["best_worst_scale"]
        reproduced_values = reproduced_df["best_worst_scale"]

    full_result_list = []
    for system, orig_unshift, repro_unshift, orig_val, repro_val in zip(
        original_df["system"],
        original_unshifted,
        reproduced_unshifted,
        original_values,
        reproduced_values,
    ):
        values = [orig_val, repro_val]
        precision_results = cv.get_precision_results(values)
        precision_results["system"] = system
        precision_results["original_unshifted"] = orig_unshift
        precision_results["reproduced_unshifted"] = repro_unshift
        precision_results["original_shifted"] = orig_val
        precision_results["reproduced_shifted"] = repro_val
        full_result_list.append(precision_results)

    df = pd.DataFrame(full_result_list)

    # Ensure results follow system order
    df = sort_by_system_order(df, system_order)

    # Reorder columns to put system first
    cols = df.columns.tolist()
    cols = ["system"] + [col for col in cols if col != "system"]
    df = df[cols]

    df.to_csv(
        "results/lab1/tables/cv_2_way.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    df.to_latex(
        "results/lab1/tables/cv_2_way.tex",
        float_format="{:0.2f}".format,
        escape=True,
    )
    print("\nCoefficient of Variation Results:")
    print(df)

    # Create and save summary table
    create_cv_summary(df, system_order)


def main():
    # Define system order in main function
    system_order_dict = {"vae": 0, "sep_ae": 1, "lbow": 2, "dips": 3}
    
    reproduced_results = pd.read_csv("results/lab1/tables/results.csv")
    original_results = pd.read_csv("results/original/results.csv")

    calculate_pearson_spearman_correlation(original_results, reproduced_results, system_order_dict)
    calculate_coefficient_of_variation(original_results, reproduced_results, -100, 100, system_order_dict)


if __name__ == "__main__":
    main()
