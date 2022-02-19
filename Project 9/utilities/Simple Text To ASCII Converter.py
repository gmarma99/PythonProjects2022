#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import unicodedata
from pathlib import Path


def clear_console():
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    os.system(command)


def text_to_ascii(path_to_file):
    name = path_to_file.split("\\")[-1]
    new_file = str(Path().absolute()) + '\\' + name[:-4] + " (ASCII).txt"

    content = ""
    with open(path_to_file, 'r', encoding="utf8") as file:
        lines = file.readlines()
        for l in lines:
            content += l

    enc_ascii_txt = unicodedata.normalize('NFKD', content).encode('ascii','ignore')
    dec_ascii_txt = enc_ascii_txt.decode("ascii")

    with open(new_file, 'w') as file:
        file.writelines(dec_ascii_txt)
    
    input("\nCompleted! Press enter to continue...")


def main():
    while(True):
        print("Simple Text To ASCII Converter\n"+30*"=")
        print("\nEnter path to the file you wish to convert or type \"exit\" to quit.\nASCII files are exported in the same folder as the converter.\n")
        inpt = input("[!]> ")

        if inpt.lower() == "exit":
            break
        else:
            try:
                text_to_ascii(inpt)
            except:
                input("\nInvalid input. Press enter and try again...")
                
        clear_console()


if __name__ == "__main__":
    main()
    