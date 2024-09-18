import pandas as pd
import glob

## ** USER INPUT ** -------------------
logs_path = r"C:\Models\Seawall\CBECC 2022"
output_fname = "Logs.csv"
## ------------------------------------

files = glob.glob('**/*log.csv',root_dir=logs_path,recursive=True)

# print("Found",str(len(files)),"log files")
header = ["HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT","PROC. MTRS",\
              "PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT",\
                "PROC. MTRS","PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS",\
                    "OTH LGHT","PROC. MTRS","PV","BATTERY"]
output_df = pd.DataFrame()

for filename in files:
  fpath = logs_path + "\\" + filename
  df = pd.read_csv(fpath,index_col=False,skiprows=2)

  for i in range(len(df.index)):
    casename = df.iloc[i,0]+" "+df.iloc[i,1]
    arr = df.to_numpy()
    li = arr.tolist()

    b_l1 = arr[i][86:93]+29.3*arr[i][101:108]+0.293*arr[i][114:121]/1000
    b_l2 = arr[i][94:98]+29.3*arr[i][108:112]+0.293*arr[i][122:126]/1000
    p_l1 = arr[i][14:21]+29.3*arr[i][29:36]+0.293*arr[i][42:49]/1000
    p_l2 = arr[i][22:26]+29.3*arr[i][37:41]+0.293*arr[i][50:54]/1000

    standard = li[i][127:134]+li[i][135:141]+li[i][262:269]+li[i][270:276]+b_l1.tolist()+b_l2.tolist()+li[i][98:100]
    proposed = li[i][55:62]+li[i][64:70]+li[i][247:254]+li[i][255:261]+p_l1.tolist()+p_l2.tolist()+li[i][26:28]

    if output_df.empty:
      output_df = pd.DataFrame([standard,proposed],index=[casename+" Standard",casename+" Proposed"],columns=header)
    else:
      output_df = pd.concat([output_df,pd.DataFrame([standard,proposed],index=[casename+" Standard",casename+" Proposed"],columns=header)])

# print(output_df)
output_df.to_csv(logs_path+"\\"+output_fname)
