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
    df = df.max(level=0)

    # Calculate flows
    # df["Influentdebiet"] = np.where(df['7019 BC_A130_O'] == 1, df["7003 RGI_FTxyz_PW"]/2, df["7003 RGI_FTxyz_PW"])
    df["Influentdebiet"] = df["7003 RGI_FTxyz_PW"]/2
    df["Opstroomsnelheid"] = df["Influentdebiet"]/opp
    
    # Seperate data into two methods: complete uses 7019 BC_A130_D, incomplete 7009 AT_LT114_AM
    df_compleet = df[df["7019 BC_A130_D"].notnull()]
    df_incompleet = df[(df["7019 BC_A130_D"].isnull()) & (df["7009 AT_LT114_AM"].notnull())]


    # Loop and find cycles and average upwards flow in cycle
    count = 0
    results_at1 = []
    results_at2 = []

    m_i = 0
    begin_cyclus = []

    # Incompleet
    while m_i < len(df_incompleet.index):
        m = df.index[m_i]

        i_m108 = m - datetime.timedelta(minutes=108)
        i_p108 = m + datetime.timedelta(minutes=108)
        if df.loc[m, "7009 AT_LT114_AM"] == df.loc[i_m108:i_p108, "7009 AT_LT114_AM"].min():
            i_m1 = m - datetime.timedelta(minutes=1)
            i_p1 = m + datetime.timedelta(minutes=1)
            if (df.loc[m, "7009 AT_LT114_AM"] <= df.loc[i_m1, "7009 AT_LT114_AM"]) and\
                (df.loc[m, "7009 AT_LT114_AM"] <= df_incompleet.loc[i_p1, "7009 AT_LT114_AM"]):
                print(m)
                begin_cyclus.append([m,1,np.nan,np.nan,np.nan,np.nan,np.nan])
                m_i += 50
        
        else:
            # Laat alle die niet de start van de cyclus zijn op 0 staan.
            # begin_cyclus[m] = 0
            m_i += 1

    for a in range(len(begin_cyclus)-1):
        duur = begin_cyclus[a+1][0] - begin_cyclus[a][0]
        begin_cyclus[a][2] = duur

        if datetime.timedelta(minutes=270) < duur < datetime.timedelta(minutes=292):
            start_date = begin_cyclus[a][0] + datetime.timedelta(minutes=168)

        elif datetime.timedelta(minutes=200) < duur < datetime.timedelta(minutes=230):
            start_date = begin_cyclus[a][0] + datetime.timedelta(minutes=126)
        
        end = False
        
        try:
            j = start_date
            while not end:
                j += datetime.timedelta(minutes=1)
                try:
                    if df.loc[j, "7009 AT_QT112_AM"] < 0.1:
                        end_date = j
                        end = True
                except:
                    continue
                
                average = np.mean(df.loc[start_date:end_date, "Opstroomsnelheid"])
                duration = end_date-start_date
                hours = duration.total_seconds()/3600
                begin_cyclus.append([start_date, np.nan, np.nan, df.loc[start_date, "7009 AT_QT112_AM"],\
                    df.loc[start_date, "7009 AT_LT114_AM"], average, hours])
        except:
            continue

    df_temp = pd.DataFrame(begin_cyclus, columns=["sTime", "Begin Cyclus", "Cyclusduur", "Slibgehalte", "Waterhoogte", "Opstroomsnelheid", "Duur"])
    df_temp = df_temp.set_index(keys="sTime", drop=True)
    df = df.append(df_temp)
    print(df["Slibgehalte"])

    # for i in df_compleet.index:
    #     i_1 = i - datetime.timedelta(minutes=1)

    #     # AT 2
    #     if df_compleet.loc[i, "7019 BC_A130_D"] > 0 and df_compleet.loc[i_1, "7019 BC_A130_D"] == 0:
    #         start_date = i_1
    #         print(start_date)

    #         end = False
    #         j = i
    #         while not end:
    #             j += datetime.timedelta(minutes=1)
    #             try:
    #                 if df_compleet.loc[j, "7009 AT_QT112_AM"] < 0.1:
    #                     end_date = j
    #                     count += 1
    #                     end = True

    #                 elif j == df_compleet.index[-1]:
    #                     print("True")
    #                     end =True
    #             except:
    #                 continue
            
    #         average = np.mean(df_compleet.loc[start_date:end_date, "Opstroomsnelheid"])
    #         duration = end_date-start_date
    #         hours = duration.total_seconds()/3600
            
    #         results_at1.append([start_date, df_compleet.loc[start_date, "7009 AT_QT112_AM"],\
    #              df_compleet.loc[start_date,"7009 AT_LT114_AM"], average, hours])     

    #     # AT 2
    #     if df_compleet.loc[i, "7019 BC_A151_D"] > 0 and df_compleet.loc[i_1, "7019 BC_A151_D"] == 0:
    #         start_date = i_1
    #         print(start_date)

    #         end = False
    #         j = i
    #         while not end:
    #             j += datetime.timedelta(minutes=1)
    #             try:
    #                 if df_compleet.loc[j, "7010 AT_QT112_AM"] < 0.1:
    #                     end_date = j
    #                     count += 1
    #                     end = True

    #                 elif j == df_compleet.index[-1]:
    #                     print("True")
    #                     end =True
    #             except:
    #                 continue
            
    #         average = np.mean(df_compleet.loc[start_date:end_date, "Opstroomsnelheid"])
    #         duration = end_date-start_date
    #         hours = duration.total_seconds()/3600
            
    #         results_at1.append([start_date, df_compleet.loc[start_date, "7010 AT_QT112_AM"],\
    #              df_compleet.loc[start_date,"7010 AT_LT114_AM"], average, hours])     

    #     # if count == 2:
    #     #     break;

    # print("Create dataframe AT1")
    # df_results_at1 = pd.DataFrame(results_at1, columns=["Tijd", "Slibgehalte", "Waterhoogte", "Opstroomsnelheid", "Duur"])
    # df_results_at1.set_index("Tijd")
    # print("Writing csv ...")
    # print(df_results_at1.head())
    # df_results_at1.to_excel(r"P:\1263819\Biologische opstart Weesp\Berend\Plan van aanpak onderzoek\Data-analyse\cyclussen_at1.xlsx")

    # print("Create dataframe AT2")
    # df_results_at2 = pd.DataFrame(results_at2, columns=["Tijd", "Slibgehalte", "Waterhoogte", "Opstroomsnelheid", "Duur"])
    # df_results_at2.set_index("Tijd")
    # print("Writing csv ...")
    # print(df_results_at2.head())
    # df_results_at2.to_excel(r"P:\1263819\Biologische opstart Weesp\Berend\Plan van aanpak onderzoek\Data-analyse\cyclussen_at2.xlsx")