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
table1_rows = sheet[2:8]
table2_rows = sheet[11:17]

# ============
table1_victor_count = 0
for row in table1_rows:
    for cell in row:
        if cell.value == "Victor":
            table1_victor_count += 1
print(table1_victor_count)

# ============
table2_victor_count = 0
for row in table2_rows:
    for cell in row:
        if cell.value == "Victor":
            table2_victor_count += 1
print(table2_victor_count)

# ============
total_victor_count = table1_victor_count + table2_victor_count
print(total_victor_count)

# ============
workbook.save(r"results1/CON_preprocessing/1_225-40_input/workbook_new.xlsx")

# ============
workbook.save(r"results1/CON_preprocessing/1_225-40_input/workbook_new.xlsx")