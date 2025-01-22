import pandas as pd
import glob

## ** USER INPUT ** -------------------
logs_path = input(r"Enter logs path: ")
output_fname = "Logs.csv"
# (NOTE: log file will be created in same folder as entered log path)
## ------------------------------------

# This searches the entered log path and any subdirectories for log CSV files.
files = glob.glob('**/*log.csv',root_dir=logs_path,recursive=True)
print("Found",str(len(files)),"log files")

# Base creation for the Annual TDV standard/proposed table
header = ["Case Name", "Conditioned Floor Area (SF)", "HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT","PROC. MTRS",\
              "PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS","OTH LGHT",\
                "PROC. MTRS","PV","BATTERY","HTG","CLG","FANS","HREJ","PUMPS","DHW","IND LGHT","RECEPT","PROCESS",\
                    "OTH LGHT","PROC. MTRS","PV","BATTERY"]
output_df = pd.DataFrame()

# Stepping through every log file found to pull the correct numbers / perform math and get annual values.
for filename in files:
  # This will save the start date and filename for each run to be appended with data 
  fpath = logs_path + "\\" + filename
  df = pd.read_csv(fpath,index_col=False,skiprows=2)

  # In case multiple runs within one log file, this will step through each run and append.
  # NOTE: this may result in keeping unwanted results. Read the output log file carefully.
  for i in range(len(df.index)):
    dt = df.iloc[i,0]
    casename = df.iloc[i,1]
    area = df.iloc[i,5]
    arr = df.to_numpy()
    li = arr.tolist()

    b_l1 = arr[i][86:93]+29.3*arr[i][101:108]+0.293*arr[i][114:121]/1000
    b_l2 = arr[i][94:98]+29.3*arr[i][108:112]+0.293*arr[i][122:126]/1000
    p_l1 = arr[i][14:21]+29.3*arr[i][29:36]+0.293*arr[i][42:49]/1000
    p_l2 = arr[i][22:26]+29.3*arr[i][37:41]+0.293*arr[i][50:54]/1000

    standard = [casename, area]+li[i][127:134]+li[i][135:141]+li[i][262:269]+li[i][270:276]+b_l1.tolist()+b_l2.tolist()+li[i][98:100]
    proposed = [casename, area]+li[i][55:62]+li[i][64:70]+li[i][247:254]+li[i][255:261]+p_l1.tolist()+p_l2.tolist()+li[i][26:28]

    # This appends the calculated run information to the output dataframe
    if output_df.empty:
      output_df = pd.DataFrame([standard,proposed],index=[dt+" Standard",dt+" Proposed"],columns=header)
    else:
      output_df = pd.concat([output_df,pd.DataFrame([standard,proposed],index=[dt+" Standard",dt+" Proposed"],columns=header)])

# This saves all the annual TDV calculations for each run into the original log path with the given output file name "output_fname"
output_df.to_csv(logs_path+"\\"+output_fname)
