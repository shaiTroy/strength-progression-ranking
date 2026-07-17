import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt
import json

os.system('clear')

def importData():
    with open('openipf-2026-07-04-9acfa1cf.csv', mode='r') as file:
        reader = csv.reader(file)
        data = []
        for row in reader:
            currentRow = []
            if row[2] != 'SBD' or row[3] != 'Raw' or row[7] == 'Special Olympics' or row[30] == '': continue
            for i in [0, 1, 36, 14, 19, 24, 30]:
                    currentRow.append(row[i])
            data.append(currentRow)
        return data
    #row format:
    # [0] = Name
    # [1] = Sex
    # [2] = Date
    # [3] = Best Squat
    # [4] = Best Bench
    # [5] = Best Deadlift
    # [6] = GL
    
def sortData(data):
    # Sort by date at index 4
    data.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d'))
    # Sort by first and last name at index 0
    data.sort(key=lambda x: (x[0].split()[0], x[0].split()[1]) if len(x[0].split()) > 1 else (x[0].split()[0], ''))
    return data

def updateDates(filtered):
    new_list = []
    fail_count = 0
    for entry in filtered:
        entry[3] = float(entry[3]) if entry[3].replace('.', '', 1).isdigit() else 0.0
        entry[4] = float(entry[4]) if entry[4].replace('.', '', 1).isdigit() else 0.0
        entry[5] = float(entry[5]) if entry[5].replace('.', '', 1).isdigit() else 0.0
        if entry[3] == 0 or entry[4] == 0 or entry[5] == 0:
            fail_count += 1
            continue
        else:
            entry[6] = float(entry[6]) if entry[6].replace('.', '', 1).isdigit() else 0.0
            if entry[6] < 50:
                fail_count += 1
                continue
            else:
                total = entry[3] + entry[4] + entry[5]
                new_list.append([entry[0], entry[1], entry[2], total, entry[6]])
    print(f"Filtered out {fail_count} entries with too many failed attempts")
    print(f"Filtered out {len(filtered) - len(new_list)} entries with incorrect attempt, {len(new_list)} entries remaining.")   
    
    database = {} # name is key, value is: first total, first date, best total, last date, gl, sex, count

    for name, sex, date, total, gl in new_list:
        if name not in database:
            database[name] = [total, date, total, date, gl, sex, 0]
        else:
            if total > database[name][2]:
                database[name][2] = total
                database[name][3] = date
                database[name][4] = gl
            elif total == database[name][2] and date > database[name][3]:
                database[name][3] = date
                database[name][4] = gl
            database[name][6] += 1

    database2 = {}
    onecomp = 0
    lessthan100 = 0
    for lifter in database:
        if database[lifter][6] > 0:
            if database[lifter][4] >= 100:
                database2[lifter] = database[lifter]
            else:
                lessthan100 += 1
        else:
            onecomp += 1
    print(f"Filtered out {onecomp} entries with only one competition, {lessthan100} entries with less than 100 gl, {len(database2)} entries remaining.")
    
    database3 = [] # name, diff in total, diff in dates, sex
    less_than_3_years = 0
    for lifter in database2:
        diff_total = database2[lifter][2] - database2[lifter][0]
        diff_dates = (datetime.strptime(database2[lifter][3], '%Y-%m-%d') - datetime.strptime(database2[lifter][1], '%Y-%m-%d')).days / 365.25
        if diff_dates < 3:
            less_than_3_years += 1
            continue
        database3.append([lifter, diff_total, diff_dates, database2[lifter][5]])
    print(f"Filtered out {less_than_3_years} people with less than 3 years between first and latest competitions.")
    print(f"Final dataset contains {len(database3)} people.")
    return database3

def stats(filtered):
    male_lifters = []
    female_lifters = []
    #both are: name, rate of change
    
    for name, diff_total, diff_dates, sex in filtered:
        rate_of_change = diff_total / diff_dates
        if sex == 'M':
            male_lifters.append((name, rate_of_change))
        elif sex == 'F':
            female_lifters.append((name, rate_of_change))
    
    def plot_rate_of_change(lifters, sex):
        rate_of_change = [x[1] for x in lifters]
        plt.hist(rate_of_change, bins=20, alpha=0.5, label=sex)
        plt.xlabel('Rate of Change (Total / Years)')
        plt.ylabel(f'Number of {sex} Lifters')
        plt.legend()
        plt.show()
        print(f"{sex} lifters: {len(lifters)}")
        #print average rate of change
        avg_rate_of_change = sum(rate_of_change) / len(rate_of_change)
        print(f"Average rate of change per year for {sex} lifters: {avg_rate_of_change:.2f}")
        #print median rate of change
        median_rate_of_change = sorted(rate_of_change)[len(rate_of_change) // 2]
        print(f"Median rate of change per year for {sex} lifters: {median_rate_of_change:.2f}")
        #print top 20 lifters by rate of change
        top_20 = sorted(lifters, key=lambda x: x[1], reverse=True)[:20]
        print(f"Top 20 {sex} lifters by rate of change:")
        for i, (name, rate) in enumerate(top_20, 1):
            print(f"  {i}. {name}: {rate:.2f}")
    
    plot_rate_of_change(male_lifters, 'Male')
    plot_rate_of_change(female_lifters, 'Female')

if __name__ == '__main__':
    data = sortData(importData())
    filtered = updateDates(data)
    stats(filtered)
    
    