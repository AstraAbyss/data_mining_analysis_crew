"""
@File: utils/file_utils.py
@Desc: 文件与目录辅助函数。
"""

import os


def ensure_dirs() -> None:
    for path in [
        "data/raw",
        "data/processed",
        "outputs",
    ]:
        os.makedirs(path, exist_ok=True)
