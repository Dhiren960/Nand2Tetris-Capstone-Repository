#!/usr/bin/env python3
"""Hack assembler (Nand to Tetris, Project 6) in Python.

Usage:  python assembler.py Prog.asm      -> writes Prog.hack
Extra feature (K mod 3 == 2): warn if the same label is defined twice.
"""
import sys

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101", "!A": "0110001",
    "-D": "0001111", "-A": "0110011", "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010", "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000", "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011", "M+1": "1110111",
    "M-1": "1110010", "D+M": "1000010", "D-M": "1010011", "M-D": "1000111",
    "D&M": "1000000", "D|M": "1010101",
}
DEST = {"": "000", "M": "001", "D": "010", "MD": "011",
        "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}


def predefined():
    table = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
             "SCREEN": 16384, "KBD": 24576}
    for i in range(16):
        table["R%d" % i] = i
    return table


def clean(line):
    """Remove comment and all spaces."""
    line = line.split("//")[0]
    return "".join(line.split())


def first_pass(lines, symbols):
    """Record label addresses. Returns list of (line_no, instruction)."""
    program = []
    rom = 0
    seen = {}                      # label -> line where first defined
    for no, raw in enumerate(lines, start=1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith("("):
            if not line.endswith(")") or len(line) < 3:
                print("Line %d: invalid label '%s'" % (no, line), file=sys.stderr)
                continue
            label = line[1:-1]
            if label in seen:      # extra feature
                print("Warning: Line %d: label '%s' already defined on line %d"
                      % (no, label, seen[label]), file=sys.stderr)
            else:
                seen[label] = no
            symbols[label] = rom   # last definition wins (warning given)
        else:
            program.append((no, line))
            rom += 1
    return program


def a_instruction(body, symbols, state):
    if body.isdigit():
        value = int(body)
    else:
        if body not in symbols:
            symbols[body] = state["next_var"]
            state["next_var"] += 1
        value = symbols[body]
    if value > 32767:
        raise ValueError("address too large")
    return "0" + format(value, "015b")


def c_instruction(line):
    dest, jump = "", ""
    if "=" in line:
        dest, line = line.split("=", 1)
    if ";" in line:
        line, jump = line.split(";", 1)
    if dest not in DEST or line not in COMP or jump not in JUMP:
        raise ValueError("invalid instruction")
    return "111" + COMP[line] + DEST[dest] + JUMP[jump]


def second_pass(program, symbols):
    state = {"next_var": 16}
    out, errors = [], 0
    for no, line in program:
        try:
            if line.startswith("@"):
                out.append(a_instruction(line[1:], symbols, state))
            else:
                out.append(c_instruction(line))
        except ValueError as e:
            print("Line %d: %s ('%s')" % (no, e, line), file=sys.stderr)
            errors += 1
    return out, errors


def main():
    if len(sys.argv) != 2 or not sys.argv[1].endswith(".asm"):
        print("Usage: python assembler.py Prog.asm")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        lines = f.read().splitlines()
    symbols = predefined()
    program = first_pass(lines, symbols)
    code, errors = second_pass(program, symbols)
    if errors:
        print("%d error(s); no .hack file written." % errors, file=sys.stderr)
        sys.exit(1)
    outname = sys.argv[1][:-4] + ".hack"
    with open(outname, "w") as f:
        f.write("\n".join(code) + "\n")
    print("Wrote %s (%d instructions)" % (outname, len(code)))


if __name__ == "__main__":
    main()
