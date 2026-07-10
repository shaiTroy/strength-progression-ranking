import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt
import json

os.system('clear')

def importData():
    with open('openipf-2025-05-24-d228cac8.csv', mode='r') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            currentRow = []
            if row[2] != 'SBD' or row[3] != 'Raw' or row[7] == 'Special Olympics' or row[30] == '': continue
            if row[7] == 'Juniors': row[7] = 'Junior'
            if row[7] == 'Sub-Juniors': row[7] = 'Sub-Junior'
            for i in [0, 1, 36, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 24, 30]:
                    currentRow.append(row[i])
            data.append(currentRow)
        return data
    #row format:
    # [0] = Name
    # [1] = Sex
    # [2] = Date
    # [3] = Squat1
    # [4] = Squat2
    # [5] = Squat3
    # [6] = Best Squat
    # [7] = Bench1
    # [8] = Bench2
    # [9] = Bench3
    # [10] = Best Bench
    # [11] = Deadlift1
    # [12] = Deadlift2
    # [13] = Deadlift3
    # [14] = Best Deadlift
    # [15] = GL
    
def sortData(data):
    # Sort by date at index 4
    data.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'))
    # Sort by first and last name at index 0
    data.sort(key=lambda x: (x[0].split()[0], x[0].split()[1]) if len(x[0].split()) > 1 else (x[0].split()[0], ''))
    return data

def updateDates(filtered):
    
    i = 0
    n = len(filtered)
    count_2_fail = 0
    while i < len(filtered)-1:
        count_incorrect = 0
        for j in range(3, 16):
            try:
                filtered[i][j] = float(filtered[i][j])
            except:
                filtered.pop(i)
                i -= 1
                break
            if filtered[i][j] == 0:
                print(f"Found 0 attempt in {filtered[i]}")
                filtered.pop(i)
                i -= 1
                break
            elif filtered[i][j] < 0:
                if count_incorrect == 1:
                    filtered.pop(i)
                    i -= 1
                    count_2_fail += 1
                    break
                else:
                    count_incorrect += 1        
        i += 1
    print(f"Filtered out {count_2_fail} entries with too many failed attempts")
    print(f"Filtered out {n - len(filtered) - count_2_fail} entries with incorrect attempt, {len(filtered)} entries remaining.")
    
    
    first_occurrence_date = None
    current_name = None

    for entry in filtered:
        name = entry[0]
        date_str = entry[2]

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print(f"Skipping entry due to incorrect date format: {date_str}")
            continue
        
        if name != current_name:
            current_name = name
            first_occurrence_date = date_obj
            entry[2] = 0
        else:
            days_difference = (date_obj - first_occurrence_date).days
            entry[2] = days_difference
    i = 0
    n = len(filtered)
    while i < len(filtered)-1:
        if filtered[i][2] == filtered[i+1][2]:
            filtered.pop(i)
        else:
            i += 1 
    if filtered[-1][2] == 0:
        filtered.pop(-1)
    print(f"Filtered out {n - len(filtered)} entries with the same lifter and date, {len(filtered)} entries remaining.")
    
    return filtered

def transform_and_save_arrays(filtered):
    comps = []
    cur_name = None
    holder = []

    for row in filtered:
        if cur_name != row[0]:
            cur_name = row[0]
            holder = [row[1], row[2], float(row[15])]
        else:
            if holder[0] == 'M':
                holder[0] = 1
            else:
                holder[0] = 0
            holder[1] = (row[2] - holder[1])/30
            holder.append((float(row[15]) - holder[2])/holder[1])
            comps.append(holder)
            holder = [row[1], row[2], float(row[15])]
    
    print(f"Number of entries: {len(comps)}")
    
    map = {}
    for i in range(len(comps)):
        key = int(comps[i][2])
        gl_change = comps[i][3] 
        if key in map:
            map[key].append(gl_change)
        else:
            map[key] = [gl_change]
            
    keys = sorted(map.keys())
    values = [sum(map[k]) / len(map[k]) for k in keys if map[k]]

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.bar(keys, values, color='skyblue')
    plt.xlabel('Key')
    plt.ylabel('Count')
    plt.title('Map Key Frequencies')
    plt.xticks(rotation=90)  # Rotate x-labels if they overlap
    plt.tight_layout()
    plt.show()
    
    with open("gl_map.json", "w") as f:
        json.dump(map, f)
    
    
if __name__ == '__main__':
    data = sortData(importData())
    filtered = updateDates(data)
    transform_and_save_arrays(filtered)
    print("Data has been preprocessed and saved to files.")
    
    