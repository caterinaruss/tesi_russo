import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime


# ============
wb_path = r"dataset_90/1_225-40_input.xlsx"
workbook = openpyxl.load_workbook(wb_path)

# ============
sheet = workbook["Sheet1"]
count = 0
for row in sheet.iter_rows(min_row=2, max_row=16):
    cell = row[0]
    if cell.value == "Victor":
        count += 1
print(count)

# ============
workbook.save(r"results1/SENZA_preprocessing/1_225-40_input/workbook_new.xlsx")

# ============
workbook.save(r"results1/SENZA_preprocessing/1_225-40_input/workbook_new.xlsx")