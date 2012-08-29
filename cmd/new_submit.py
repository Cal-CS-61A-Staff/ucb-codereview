#! /usr/bin/env python3

import sys
from subprocess import Popen, PIPE
import argparse
import os
import io

GMAILS_FILE = "MY.GMAILS"
SECTIONS_FILE = "MY.SECTIONS"
LOGINS_FILE = "MY.PARTNERS"
important_files = (GMAILS_FILE, SECTIONS_FILE, LOGINS_FILE)

def run_submit(assign):
    """Runs submit. Basic, slightly dumb version."""
    # print "running command {}".format(cmd)
    # print "cwd {}".format(os.getcwd())
    bs = lambda x: bytes(x, "utf-8")
    dec = lambda x: x.decode('utf-8')
    def get_char(stream):
        got = stream.read(1)
        # print('got {}'.format(got))
        return dec(got)
    def goto_newline(stream):
        s = ""
        c = ""
        while c != "\n":
            c = get_char(stream)
            s += c
        return s
    def read_question(stream):
        char = get_char(stream)
        s = char
        while True:
            if s.endswith("[yes/no] "):
                break
            if s.endswith("turn in..."):
                print('first')
                s += goto_newline(stream)
                return s
            if s.startswith("Submitting"):
                print('second')
                s += goto_newline(stream)
                return s
            s += get_char(stream)            
        return s
    cmd = "submit " + assign
    temp_file = open('.temp', 'w')
    reader = open('.temp', 'r')
    proc = Popen(cmd.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    while True:
        print('read {}'.format(read_question(proc.stderr)))        
        # print('read {}'.format(read_question(proc.stdout)))
        proc.stdin.write(bs('no\n'))
        proc.stdin.flush()
        

def my_prompt(initial_message, prompt, defaults_file):
    defaults = None
    if os.path.exists(defaults_file):
        defaults = open(defaults_file, 'r').read().split()
    print(initial_message)
    print("Enter '.' to stop. Hit enter to use the remaining defaults.")
    captured = []
    while True:
        output = prompt
        if defaults:
            output += " " + str(defaults)
        output += ":"
        print(output, end="")
        sys.stdout.flush()
        value = sys.stdin.readline()
        if value == '\n':
            print("Using defaults")
            sys.stdout.flush()
            break
        if len(value) < 3 and '.' in value:
            break
        if defaults:
            defaults.pop(0)
        captured.append(value)
    if defaults:
        captured.extend(defaults)
    return captured

def write_defaults(defaults, filename, string_to_join="\n"):
    out = open(filename, 'w')
    string = string_to_join.join(defaults)
    if not string[-1] == "\n":
        string = string + "\n"
    out.write(string)
    out.flush()
    out.close()

def get_gmails():
    """
    Prompts the user for their gmails, and stores the file in the GMAILS_FILE file
    """
    gmails = my_prompt("Enter you and your partner's gmail addresses.", "GMail", GMAILS_FILE)
    write_defaults(gmails, GMAILS_FILE)
    return gmails

def get_partners():
    """
    Prompts the user for their gmails, and stores the file in the GMAILS_FILE file
    """
    partners = my_prompt("Enter you and your partner's logins.", "Login", LOGINS_FILE)
    write_defaults(partners, LOGINS_FILE, string_to_join=" ")
    return partners

def get_sections():
    sections = my_prompt("Enter you and your partner's section numbers.", "Section Number", SECTIONS_FILE)
    write_defaults(sections, SECTIONS_FILE)
    return sections

def main(assign):
    gmails = get_gmails()
    sections = get_sections()
    partners = get_partners()
    run_submit(assign)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Submits the assignment, \
        assuming the correct files are in the given directory.")    
    parser.add_argument('assign', type=str,
                        help='the assignment to submit')
    args = parser.parse_args()
    main(args.assign)