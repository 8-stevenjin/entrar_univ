import pandas as pd
import math

def get_weights(univ, major_type, weights_df):
    row = weights_df[
        (weights_df["대학명"] == univ) &
        (weights_df["학과명"] == major_type)
    ]
    if not row.empty:
        return row.iloc[0][["국어", "수학", "영어", "탐구"]].astype(float).to_dict()

    default = weights_df[
        (weights_df["대학명"] == "전체") &
        (weights_df["학과명"] == "전체")
    ]
    return default.iloc[0][["국어", "수학", "영어", "탐구"]].astype(float).to_dict()

def get_english_score(univ, grade, english_df):
    row = english_df[
        (english_df["대학명"] == univ) &
        (english_df["등급"] == grade)
    ]
    if not row.empty:
        return row.iloc[0]["점수"]

    default = english_df[
        (english_df["대학명"] == "전체") &
        (english_df["등급"] == grade)
    ]
    if not default.empty:
        return default.iloc[0]["점수"]

    return 60

def calculate_score(input_data, univ, major_type, weights_df, english_df):
    weights = get_weights(univ, major_type, weights_df)

    국어 = input_data["국어"]["백분위"]
    수학 = input_data["수학"]["백분위"]
    탐1 = input_data["탐구1"]["백분위"]
    탐2 = input_data["탐구2"]["백분위"]
    탐_avg = (탐1 + 탐2) / 2
    영어점수 = get_english_score(univ, input_data["영어"]["등급"], english_df)

    total = (
        국어 * weights["국어"] +
        수학 * weights["수학"] +
        영어점수 * weights["영어"] +
        탐_avg * weights["탐구"]
    )

    return math.floor(total * 100) / 100  # 소수 둘째자리에서 버림
