import csv
import os

import krippendorff
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison
from statsmodels.stats.inter_rater import fleiss_kappa


def get_selected_systems(meaning_i):
    if meaning_i is False:
        value = 0
    elif meaning_i is True:
        value = 1
    else:
        raise ValueError(f"Unexpected value: {meaning_i}")
    return value


def filter_attention_checks(results_df):
    """
    when the system is 'distractor', the output is a random sample with a completely different meaning,
    and should never be chosen as best for 'meaning'.
    HITs where either of these controls were failed were rejected and resubmitted to MTurk.
    :param results_df:
    :return:
    """
    attention_check_list = ["distractor", "golds", "inputs"]

    system_a_is_ditractor = results_df[results_df["systema"] == "distractor"]
    system_b_is_distractor = results_df[results_df["systemb"] == "distractor"]

    desired_task_uuid = "df51b2dd-7f64-437d-824a-f472ffc011cd"

    matching_task_uuid = results_df[results_df["task_uuid"] == desired_task_uuid]

    system_a_is_distractor_and_selected = system_a_is_ditractor[
        system_a_is_ditractor["selected_system"] == 0
    ]
    system_b_is_distractor_and_selected = system_b_is_distractor[
        system_b_is_distractor["selected_system"] == 1
    ]

    distractor_is_selected = pd.concat(
        [
            system_a_is_distractor_and_selected,
            system_b_is_distractor_and_selected,
        ]
    )
    invalid_task_uuid_list = distractor_is_selected["task_uuid"].tolist()

    users_with_failed_attention_checks = system_a_is_distractor_and_selected[
        "participant_id"
    ].tolist()
    users_with_failed_attention_checks += system_b_is_distractor_and_selected[
        "participant_id"
    ].tolist()

    users_with_attention_checks = system_a_is_ditractor["participant_id"].tolist()
    users_with_attention_checks += system_b_is_distractor["participant_id"].tolist()

    users_with_failed_attention_checks = list(set(users_with_failed_attention_checks))

    # Three round plates filled with artistically presented food.,T
    # wo halves of an onion and a carrot positioned to represent either a Goofy face or male Genetalia.,
    # Three pans filled with different types of food.
    print(f"Users with failed attention checks: {users_with_failed_attention_checks}")
    print(f"Task UUIDs with failed attention checks: {invalid_task_uuid_list}")

    results_with_failed_attention_checks = results_df[
        results_df["participant_id"].isin(users_with_failed_attention_checks)
    ]

    users_without_attention_checks = results_df[
        ~results_df["participant_id"].isin(users_with_attention_checks)
    ]["participant_id"].tolist()

    print(f"Users without attention checks: {len(users_without_attention_checks)}")

    # print(f"Warning, redo analysis with the line below uncommented")
    filtered_results_df = results_df[
        ~results_df["participant_id"].isin(users_with_failed_attention_checks)
    ]
    # filtered_results_df = results_df

    filtered_results_df = filtered_results_df[
        ~filtered_results_df["systema"].isin(attention_check_list)
    ]
    filtered_results_df = filtered_results_df[
        ~filtered_results_df["systemb"].isin(attention_check_list)
    ]

    return filtered_results_df


def preprocess_responses_df(responses_df):
    results_list = []

    for _, row in responses_df.iterrows():
        for i in range(32):
            selected_system = row[f"meaning{i}"]
            results_dict = dict()
            results_dict["systema"] = row[f"systema{i}"]
            results_dict["systemb"] = row[f"systemb{i}"]
            system_a_and_b = [results_dict["systema"], results_dict["systemb"]]

            # if any([x in attention_check_list for x in system_a_and_b]):
            #     # it is not clear what to do when a participant fails the attention check
            #     continue

            results_dict["dataset"] = row[f"dataset{i}"]
            results_dict["dataset_index"] = row[f"ix{i}"]
            results_dict["dataset_id"] = f"{row[f'dataset{i}']}-{row[f'ix{i}']}"
            results_dict["selected_system"] = selected_system
            results_dict["input"] = row[f"input{i}"]
            results_dict["outputa"] = row[f"outputa{i}"]
            results_dict["outputb"] = row[f"outputb{i}"]
            results_dict["task_id"] = (
                f"{row[f'dataset{i}']}-{row[f'ix{i}']}-{row[f'systema{i}']}-{row[f'systemb{i}']}"
            )
            results_dict["task_uuid"] = row["task_id"]
            results_dict["participant_id"] = row["prolific_pid"]

            results_list.append(results_dict)

    results_df = pd.DataFrame(results_list)

    results_df = filter_attention_checks(results_df)

    results_df["selected_system"] = results_df["selected_system"].apply(int)

    return results_df


def load_and_preprocess_responses():
    responses_df = pd.read_csv("responses/responses.csv")
    responses_processed_df = preprocess_responses_df(responses_df)
    return responses_processed_df


def report_fleiss_kappa(responses_processed_df):
    # need itemx x category matrix
    # n columns, represents the options
    # m rows, represents the each task

    matrix = (
        responses_processed_df.groupby(["task_id", "selected_system"])
        .size()
        .unstack(fill_value=0)
    )

    fleiss_kappa_value = fleiss_kappa(matrix.values, method="fleiss")

    with open("results/lab1/fleiss_kappa.txt", "w") as f:
        f.write(f"Fleiss Kappa: {fleiss_kappa_value:.3f}")

    matrix.to_csv(
        "results/lab1/fleiss_kappa_matrix.csv",
        index=True,
        quoting=csv.QUOTE_NONNUMERIC,
    )


def report_krippendorff_alpha(responses_processed_df):
    reliability_data = (
        responses_processed_df[["task_id", "participant_id", "selected_system"]]
        .pivot_table(
            index="participant_id",
            columns="task_id",
            values="selected_system",
            aggfunc="first",
        )
        .reset_index(drop=True)
    )

    reliability_data.to_csv(
        "results/lab1/reliability_data.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
    )

    alpha = krippendorff.alpha(
        reliability_data.to_numpy(), level_of_measurement="nominal"
    )

    with open("results/lab1/krippendorff_alpha.txt", "w") as f:
        f.write(f"Krippendorff's Alpha: {alpha:.3f}")
    print(f"Krippendorff's Alpha: {alpha:.3f}")
    return alpha


def report_datasets_used(responses_processed_df):
    responses_processed_df.sort_values(by=["dataset_id", "systema", "systemb"])
    datasets_and_index = responses_processed_df[
        ["dataset", "dataset_index"]
    ].drop_duplicates(keep="first")
    datasets_grouped = (
        datasets_and_index[["dataset"]]
        .groupby("dataset")
        .agg(count=("dataset", "size"))
        .reset_index()
    )

    os.makedirs("results/lab1/tables", exist_ok=True)

    datasets_grouped.to_csv(
        "results/lab1/tables/datasets_used.csv",
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
    )
    datasets_grouped.to_latex(
        "results/lab1/tables/datasets_used.tex",
        index=False,
        escape=True,
        float_format="%.2f",
    )
    print(datasets_grouped)

    # hrq:a vae:b lbow:c sep_ae:d
    # a b -
    # a c -
    # a d -
    # b c -
    # b d
    # c d -


def calculate_metrics_alternative_2(responses_processed_df):
    system_order_dict = {"vae": 0, "sep_ae": 1, "lbow": 1, "dips": 3}

    system_count_dict = {system: 0 for system in system_order_dict.keys()}

    scores_list = []

    for _, row in responses_processed_df.iterrows():
        system_a_dict = {"system": row["systema"]}
        system_b_dict = {"system": row["systemb"]}
        if row["selected_system"] == 0:
            system_a_dict["score"] = 1
            system_b_dict["score"] = -1
        elif row["selected_system"] == 1:
            system_a_dict["score"] = -1
            system_b_dict["score"] = 1
        else:
            raise ValueError(f"Unexpected value: {row['selected_system']}")
        scores_list.append(system_a_dict)
        scores_list.append(system_b_dict)

    scores_df = pd.DataFrame(scores_list)

    return scores_df, system_count_dict


def get_task_scores(responses_processed_df):
    dataset_id_list = responses_processed_df["dataset_id"].unique().tolist()

    system_order_dict = {"vae": 0, "sep_ae": 1, "lbow": 1, "dips": 3}

    system_count_dict = {system: 0 for system in system_order_dict.keys()}

    scores_list = []
    for dataset_id in dataset_id_list:
        task_responses_df = responses_processed_df[
            responses_processed_df["dataset_id"] == dataset_id
        ]
        system_scores = {system: 0 for system in system_order_dict.keys()}
        for _, row in task_responses_df.iterrows():
            if row["selected_system"] == 0:
                system_scores[row["systema"]] += 1
                system_scores[row["systemb"]] -= 1
            elif row["selected_system"] == 1:
                system_scores[row["systemb"]] += 1
                system_scores[row["systema"]] -= 1
            else:
                raise ValueError(f"Unexpected value: {row['selected_system']}")

            system_count_dict[row["systema"]] += 1
            system_count_dict[row["systemb"]] += 1

        scores_list.append(system_scores)

    scores_df = pd.DataFrame(scores_list)

    return scores_df, system_count_dict


def report_significant_testing(responses_processed_df):
    scores_df, system_count_dict = get_task_scores(responses_processed_df)

    statistic, p = stats.f_oneway(*(scores_df.values.T).tolist())
    print("One-way ANOVA")
    print("=============")

    print("F value:", statistic)
    print("P value", p, "\n")

    # unpivot vae, lbow, sep_ae, hrq into a single column called system
    scores_melted_df = scores_df.melt(var_name="system", value_name="score")

    mc = MultiComparison(scores_melted_df["score"], scores_melted_df["system"])
    result = mc.tukeyhsd()
    print(result)

    with open("results/lab1/anova_tukeyhsd.txt", "w") as file:
        file.write("One-way ANOVA\n")
        file.write(f"F value: {statistic}\n")
        file.write(f"P value: {p}\n")
        file.write("Tukey HSD:\n")
        file.write(str(result))
    return scores_df, system_count_dict


def report_metrics(responses_processed_df):
    metrics_list = []

    systems_set = set(
        responses_processed_df["systema"].tolist()
        + responses_processed_df["systemb"].tolist()
    )

    for system in systems_set:
        system_a_matches = responses_processed_df[
            responses_processed_df["systema"] == system
        ]
        system_b_matches = responses_processed_df[
            responses_processed_df["systemb"] == system
        ]

        system_a_wins = len(system_a_matches[system_a_matches["selected_system"] == 0])
        system_a_losses = len(
            system_a_matches[system_a_matches["selected_system"] == 1]
        )
        system_b_wins = len(system_b_matches[system_b_matches["selected_system"] == 1])
        system_b_losses = len(
            system_b_matches[system_b_matches["selected_system"] == 0]
        )
        system_count = len(system_a_matches) + len(system_b_matches)

        wins_count = system_a_wins + system_b_wins
        losses_count = system_a_losses + system_b_losses

        total_count = wins_count + losses_count

        assert total_count == system_count

        best_worst_scale = None
        win_percentage = None

        if wins_count + losses_count != 0:
            best_worst_scale = (wins_count - losses_count) / total_count * 100.0
            win_percentage = wins_count / total_count * 100.0

        metrics_dict = {
            "system": system,
            "wins": wins_count,
            "losses": losses_count,
            "best_worst_score": wins_count - losses_count,
            "best_worst_scale": best_worst_scale,
            "win_percentage": win_percentage,
        }
        metrics_list.append(metrics_dict)
    system_order_dict = {"vae": 0, "sep_ae": 1, "lbow": 1, "dips": 3}

    metrics_list = sorted(metrics_list, key=lambda x: system_order_dict[x["system"]])

    metrics_df = pd.DataFrame(metrics_list)

    metrics_df.to_csv(
        "results/lab1/tables/results.csv", index=False, quoting=csv.QUOTE_NONNUMERIC
    )
    metrics_df.to_latex(
        "results/lab1/tables/results.tex", index=False, escape=True, float_format="%.2f"
    )

    print(metrics_df)

    return metrics_df


def main():
    responses_processed_df = load_and_preprocess_responses()

    report_datasets_used(responses_processed_df)

    report_significant_testing(responses_processed_df)
    report_metrics(responses_processed_df)

    report_fleiss_kappa(responses_processed_df)
    report_krippendorff_alpha(responses_processed_df)


if __name__ == "__main__":
    main()
