import pandas as pd
import numpy as np
from tkinter import Tk
import os
import datetime

opp = 1401
level_sensor = 3.25

def read_excelfiles(extension):
    # Ask for directory
    # from tkinter.filedialog import askdirectory
    # path_files = askdirectory(title='Selecteer de map met alle ruwe input') # shows dialog box and return the path
    file_path = r"C:\Users\hnx\Desktop\Weesp"
    list_files = []

    for filename in os.listdir(file_path):
        if filename.endswith(extension):
            list_files.append(os.path.join(file_path, filename))
        else:
            continue

    return list_files


if __name__ == "__main__":

    convert = False
    if convert:
        extension = ".xlsx"
    else:
        extension = ".csv"

    list_files = read_excelfiles(extension=extension)

    # Convert excel to smaller csv's
    if convert:
        for el in list_files:
            print(el)
            df_i = pd.read_excel(el)
            pre, ext = os.path.splitext(el)
            new_name = pre + ".csv"
            print(new_name)
            df_i.to_csv(new_name, index=False)

    # read csv files
    dfs = [pd.read_csv(el, sep=',',index_col=[0], parse_dates=[0], decimal='.') for el in list_files]
    df = pd.concat(dfs).sort_index()
    df = df.sum(level=0)
    
    # Calculate flows
    df["Influentdebiet"] = np.where(df['7019 BC_A130_O'] == 1, df["7003 RGI_FTxyz_PW"]/2, df["7003 RGI_FTxyz_PW"])
    df["Opstroomsnelheid"] = df["Influentdebiet"]/opp
    
    # Loop and find cycles and average upwards flow in cycle
    count = 0
    results = []

    for i in df.index:
        i_1 = i - datetime.timedelta(minutes=1)
        if df.loc[i, "7019 BC_A130_D"] > 0 and df.loc[i_1, "7019 BC_A130_D"] == 0:
            start_date = i_1
            print(start_date)

            end = False
            j = i
            while not end:
                j += datetime.timedelta(minutes=1)
                try:
                    if df.loc[j, "7010 AT_QT112_AM"] < 0.1:
                        end_date = j
                        count += 1
                        end = True

                    elif j == df.index[-1]:
                        print("True")
                        end =True
                except:
                    continue
            
            average = np.mean(df.loc[start_date:end_date, "Opstroomsnelheid"])
            duration = end_date-start_date
            hours = duration.total_seconds()/3600
            
            results.append([start_date, df.loc[start_date, "7010 AT_QT112_AM"], df.loc[start_date,"7010 AT_LT114_AM"], average, hours])     

        # if count == 2:
        #     break;

    print("Create dataframe")
    df_results = pd.DataFrame(results, columns=["Tijd", "Slibgehalte", "Waterhoogte", "Opstroomsnelheid", "Duur"])
    df_results.set_index("Tijd")
    print("Writing csv ...")
    print(df_results.head())
    df_results.to_excel(r"P:\1263819\Biologische opstart Weesp\Berend\Plan van aanpak onderzoek\Data-analyse\cyclussen.xlsx")