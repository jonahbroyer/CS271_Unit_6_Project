#!/usr/bin/env python
"""
    Assembler that translates programs written in Hack assembly language into binary code.
    Author: Jonah Broyer
"""
import os
import sys

# Dictionaries for the C-Instruction
comp = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}

dest = {
    "null": "000",
    "M": "001",
    "D": "010",
    "A": "100",
    "MD": "011",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

jump = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

# table of symbols also written as a dictionary
table = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}

# Loop for Ram[0] -> RAM[16] shortcut
for i in range(0, 16):
    label = "R" + str(i)
    table[label] = i

# Deal with variables starting at RAM[16]
variable_cursor = 16
root = sys.argv[1]


# function to remove whitespace and comments
def strip(line):
    char = line[0]
    if char == "\n" or char == "/":
        return ""
    elif char == " ":
        return strip(line[1:])
    else:
        return char + strip(line[1:])


# function to create appropriate 16 bit instructions if dest and jump are undefined
def generate(line):
    line = line[:-1]
    if "=" not in line:
        line = "null=" + line
    if ";" not in line:
        line = line + ";null"
    return line


# function to add new variables
def add_variable(label):
    global variable_cursor
    table[label] = variable_cursor
    variable_cursor += 1
    return table[label]


# function to assemble an a-instruction
def a_translate(line):
    if line[1].isalpha():
        label = line[1:-1]
        a_value = table.get(label, -1)
        if a_value == -1:
            a_value = add_variable(label)
    else:
        a_value = int(line[1:])
    binary_value = bin(a_value)[2:].zfill(16)
    return binary_value


# function to return a c-instruction
def c_translate(line):
    line = generate(line)
    temp = line.split("=")
    dest_part = dest.get(temp[0], "dest_bit_fail")
    temp = temp[1].split(";")
    comp_part = comp.get(temp[0], "comp_bit_fail")
    jump_part = jump.get(temp[1], "jump_bit_fail")
    return comp_part, dest_part, jump_part


# function to check between a- and c-instructions
def find_instruction(line):
    if line[0] == "@":
        return a_translate(line)
    else:
        c_instruction = c_translate(line)
        return "111" + c_instruction[0] + c_instruction[1] + c_instruction[2]


# function to pass through the file the first time
def first_pass():
    in_file = open(root + ".asm")
    out_file = open(root + ".tmp", "w")

    line_number = 0
    for line in in_file:
        strip_line = strip(line)
        if strip_line != "":
            if strip_line[0] == "(":
                label = strip_line[1:-1]
                table[label] = line_number
                strip_line = ""
            else:
                line_number += 1
                out_file.write(strip_line + "\n")

    in_file.close()
    out_file.close()


# function to pass through the file a second time and assemble into hack
def assemble():
    in_file = open(root + ".tmp")
    out_file = open(root + ".hack", "w")

    for line in in_file:
        find_line = find_instruction(line)
        out_file.write(find_line + "\n")

    in_file.close()
    out_file.close()
    os.remove(root + ".tmp")


# main driver for the program
    first_pass()
    assemble()
