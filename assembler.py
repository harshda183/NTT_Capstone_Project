#!/usr/bin/env python3
"""Two-pass Hack assembler for the Nand2Tetris Hack machine.
Usage: python assembler.py Box.asm
Outputs Box.hack and (for this assignment's K mod 3 = 0 feature) symbols.txt.
"""
import re
import sys
from pathlib import Path

DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
COMP = {
    "0":"0101010", "1":"0111111", "-1":"0111010",
    "D":"0001100", "A":"0110000", "M":"1110000",
    "!D":"0001101", "!A":"0110001", "!M":"1110001",
    "-D":"0001111", "-A":"0110011", "-M":"1110011",
    "D+1":"0011111", "A+1":"0110111", "M+1":"1110111",
    "D-1":"0001110", "A-1":"0110010", "M-1":"1110010",
    "D+A":"0000010", "D+M":"1000010",
    "D-A":"0010011", "D-M":"1010011",
    "A-D":"0000111", "M-D":"1000111",
    "D&A":"0000000", "D&M":"1000000",
    "D|A":"0010101", "D|M":"1010101"
}
PREDEFINED = {"SP":0, "LCL":1, "ARG":2, "THIS":3, "THAT":4,
              "SCREEN":16384, "KBD":24576}
for i in range(16):
    PREDEFINED[f"R{i}"] = i

def clean_lines(path):
    result=[]
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line=raw.split("//",1)[0].strip()
        if line:
            result.append((line_number, "".join(line.split())))
    return result

def assemble(path):
    lines=clean_lines(path)
    symbols=dict(PREDEFINED)
    rom=0
    for line_number, line in lines:
        if line.startswith("(") and line.endswith(")"):
            label=line[1:-1]
            if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", label):
                raise ValueError(f"Line {line_number}: invalid label declaration")
            if label in symbols:
                raise ValueError(f"Line {line_number}: duplicate/reserved label '{label}'")
            symbols[label]=rom
        else:
            rom += 1

    next_variable=16
    machine=[]
    for line_number, line in lines:
        if line.startswith("(") and line.endswith(")"):
            continue
        if line.startswith("@"):
            value=line[1:]
            if value.isdigit():
                address=int(value)
            else:
                if value not in symbols:
                    symbols[value]=next_variable
                    next_variable += 1
                address=symbols[value]
            if not 0 <= address <= 32767:
                raise ValueError(f"Line {line_number}: A-instruction address out of range")
            machine.append(f"{address:016b}")
        else:
            if line.count("=")>1 or line.count(";")>1:
                raise ValueError(f"Line {line_number}: invalid C-instruction")
            if "=" in line:
                dest, rest=line.split("=",1)
            else:
                dest, rest="",line
            if ";" in rest:
                comp,jump=rest.split(";",1)
            else:
                comp,jump=rest,""
            if dest not in DEST:
                raise ValueError(f"Line {line_number}: invalid destination '{dest}'")
            if comp not in COMP:
                raise ValueError(f"Line {line_number}: invalid computation '{comp}'")
            if jump not in JUMP:
                raise ValueError(f"Line {line_number}: invalid jump '{jump}'")
            machine.append("111"+COMP[comp]+DEST[dest]+JUMP[jump])

    output=Path(path).with_suffix(".hack")
    output.write_text("\n".join(machine)+"\n", encoding="utf-8")
    # Assignment feature for K mod 3 = 0: save every symbol and its address.
    symbol_file=Path(path).parent/"symbols.txt"
    symbol_file.write_text(
        "\n".join(f"{name}\t{address}" for name,address in sorted(symbols.items(), key=lambda item:(item[1],item[0])))+"\n",
        encoding="utf-8"
    )
    return output, symbol_file, len(machine)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)
    try:
        hack, symbol_file, count=assemble(sys.argv[1])
        print(f"Success: {count} instructions written to {hack}")
        print(f"Symbol table written to {symbol_file}")
    except (ValueError, OSError) as error:
        print(error)
        sys.exit(1)
