from difflib import Differ
import os.path

if os.path.isfile("differences.txt"):
    wr_fname = open("differences.txt", "w")
else:
    wr_fname = open("differences.txt", "x")

with open('NR 3030 Nebraska.cibd22x') as file_1, open('testing.cibd22x') as file_2:
    differ = Differ()

    for line in differ.compare(file_1.readlines(), file_2.readlines()):
        wr_fname.write(line)

wr_fname.close()
