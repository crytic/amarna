# Amarna

Amarna is a static-analyzer for the Cairo programming language.

## Features
 - find arithmetic operations
 - find functions with unused arguments
 - find unused imports
 - find mistyped decorators
 - find functions that return error codes
 - find unused functions
 - output results to sarif

----

# Cairo patterns to implement
 - [ ] terminating code blocks with dead stores
 - [ ] find calls to uint256_add that do not check overflow (missing the assert https://github.com/OpenZeppelin/cairo-contracts/blob/main/contracts/token/ERC20.cairo#L102-L104 or using _)
 - [ ] find unused local variables

 - [ ] using ap and fp registers manually
 - [ ] call and jmp and revoked references
 - [ ] undefined behavior when using [ap] directly
 - [ ] callback before tempvars -- the callback might overwrite local variable memory.



## Usage
 - analyze all `.cairo` files in current directory: `amarna . -o out.sarif`
 - analyze the `deleverage.cairo` file: `amarna deleverage.cairo -o deleverage.sarif`

```
usage: command_line.py [-h] [-p] [-o OUTPUT] [-png] -f

Analyze Cairo programs!

positional arguments:
  -f                    the name of the .cairo file or directory with .cairo files to analyze

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           print output
  -o OUTPUT, --output OUTPUT
                        file to write the output results in sarif format
  -png, --png           save a png with the AST of a file
```