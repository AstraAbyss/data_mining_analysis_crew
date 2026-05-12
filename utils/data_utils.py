"""
@File: utils/data_utils.py
@Desc: 生成数据挖掘 Demo 使用的样例客户数据。
"""

import os
import pandas as pd


def create_sample_customer_data(file_path: str = "data/raw/sample_customer_data.csv") -> str:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    df = pd.DataFrame({
        "customer_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
        "age": [23, 35, 45, 29, 52, 41, 37, 60, 31, None],
        "gender": ["F", "M", "M", "F", "F", "M", "F", "M", "F", "M"],
        "region": ["East", "West", "East", "North", "South", "East", "West", "South", "North", "East"],
        "monthly_spend": [120.5, 320.0, 210.0, 95.0, 450.0, 380.5, 180.0, 520.0, 130.0, 75.0],
        "login_count": [18, 6, 9, 25, 3, 4, 12, 2, 20, 1],
        "days_since_last_login": [2, 14, 9, 1, 32, 25, 7, 40, 3, 60],
        "complaint_count": [0, 1, 0, 0, 3, 2, 1, 4, 0, 5],
        "membership_level": ["Silver", "Gold", "Silver", "Bronze", "Platinum", "Gold", "Silver", "Platinum", "Bronze", "Bronze"],
        "churn": [0, 0, 0, 0, 1, 1, 0, 1, 0, 1],
    })

    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"[OK] 已生成样例数据: {file_path}")
    return file_path
