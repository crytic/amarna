# Amarna

Amarna is a static-analyzer for the Cairo programming language.

## Features
 - find arithmetic operations
 - output results to sarif

## Usage
 - analyze all `.cairo` files in current directory: `amarna . -o out.sarif`
 - analyze the `deleverage.cairo` file: `amarna deleverage.cairo -o deleverage.sarif`

```
usage: command_line.py [-h] [-p] [-o OUTPUT] -f

Analyze Cairo programs!

positional arguments:
  -f                    the name of the .cairo file or directory with .cairo files to analyze

optional arguments:
  -h, --help            show this help message and exit
  -p, --print
  -o OUTPUT, --output OUTPUT
                        file to write the output results in sarif format
```