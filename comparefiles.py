from difflib import Differ
import os

## ** USER INPUT ** -------------------
# File Names to compare:
f1 = "INPUT_FIRST_FILENAME_HERE.cibd22x"
f2 = "INPUT_SECOND_FILENAME_HERE.cibd22x"
## ------------------------------------

if os.path.isfile("differences.txt"):
    wr_fname = open("differences.txt", "w")
else:
    wr_fname = open("differences.txt", "x")

with open(f1) as file_1, open(f2) as file_2:
    differ = Differ()

    for line in differ.compare(file_1.readlines(), file_2.readlines()):
        wr_fname.write(line)

wr_fname.close()
print("Differences Logged!")
