from difflib import Differ
import os

## ** USER INPUT ** -------------------
# File Names to compare:
f1 = input(r"Input First File: ")
if len(f1) == 0:
    exit("Enter a file.")
f2 = input(r"Enter Second File: ")
if len(f2) == 0:
    exit("Enter a file.")
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
