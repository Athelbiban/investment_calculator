import pandas as pd


def drop_duplicates_cashflow(data_frame):
    # Исходный DataFrame
    # data = {
    #     'A': ['bar', 'baz', 'foo', 'qux', 'bar', 'baz', 'foo', 'foo', 'bar', 'baz', 'baz', 'baz'],
    #     'B': [2, 3, 1, 4, 2, 3, 1, 1, 2, 3, 3, 3],
    # }
    # df = pd.DataFrame(data)
    df = data_frame
    # print(df)

    # Шаг 1: подсчёт количества повторений каждой строки
    duplicates_count = df.groupby(list(df.columns)).size().reset_index(name='count')
    # print(duplicates_count)

    # Шаг 2: создание маски для выбора строк
    mask_one_repetition = duplicates_count['count'] == 1
    mask_two_to_three_repetitions = (duplicates_count['count'] >= 2) & (duplicates_count['count'] <= 3)
    mask_four_and_more_repetitions = duplicates_count['count'] > 3
    # print(mask_one_repetition)

    # Собираем конечный результат
    result_list = []

    # Добавляем строки, повторяющиеся 1 раз
    one_rep_rows = df[df.isin(duplicates_count[mask_one_repetition].to_dict(orient='list')).all(axis=1)]
    result_list.extend(one_rep_rows.values.tolist())
    # print(result_list)
    # print(one_rep_rows)
    # print(duplicates_count[mask_one_repetition])

    # Добавляем строки, повторяющиеся 2 или 3 раза, по одному разу
    two_to_three_rep_rows = df[
        df.isin(duplicates_count[mask_two_to_three_repetitions].to_dict(orient='list')).all(axis=1)].drop_duplicates()
    result_list.extend(two_to_three_rep_rows.values.tolist())

    # Добавляем строки, повторяющиеся 4 и более раз, по два раза
    four_and_more_rep_rows = df[
        df.isin(duplicates_count[mask_four_and_more_repetitions].to_dict(orient='list')).all(axis=1)]
    four_and_more_rep_rows = four_and_more_rep_rows.head(
        four_and_more_rep_rows.shape[0] // duplicates_count['count'].max() * 2)
    result_list.extend(four_and_more_rep_rows.values.tolist())

    # Формируем финальный DataFrame
    final_result = pd.DataFrame(result_list, columns=df.columns)

    # print(final_result)
    # print(final_result.groupby(list(final_result.columns)).size().reset_index(name='count'))

    return final_result
