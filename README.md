# Amarna

Amarna is a static-analyzer and linter for the Cairo programming language.

## Features
 - Finds code-smells and potential vulnerabilities in Cairo code
 - Compiler-identical parsing of Cairo code and StarkNet contracts
 - Supports creating local and global rules
 - Exports the parsed AST of a Cairo file
 - Exports static-analysis results to the [SARIF](https://sarifweb.azurewebsites.net/) format.


### Currently supported rules

| #   | Rule                        | What it finds                                                                                                             | Impact  | Precision |
| --- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------- | --------- |
| 1   | Arithmetic operations       | All uses of arithmetic operations +, -, *, and /                                                                          | Info    | High      |
| 2   | Unused arguments            | Function arguments that are not used in the functions in which they appear                                                | Warning | High      |
| 3   | Unused imports              | Unused imports                                                                                                            | Info    | High      |
| 4   | Mistyped decorators         | Mistyped code decorators                                                                                                  | Info    | High      |
| 5   | Unused functions            | Functions that are never called                                                                                           | Info    | Medium    |
| 6   | Error codes                 | Function calls that have return values that must be checked                                                               | Info    | High      |
| 7   | Inconsistent assert usage   | Asserts that use the same constant in different ways, e.g., `assert_le(amount, BOUND)` and `assert_le(amount, BOUND - 1)` | Warning | High      |
| 8   | Dead stores                 | Variables that are assigned values but not used before a return statement                                                 | Info    | Medium    |
| 9   | Unchecked overflows         | Function calls that ignore the returned overflow flags, e.g., `uint256_add`                                               | Warning | High      |
| 10  | Caller address return value | Function calls to the `get_caller_address` function.                                                                      | Info    | High      |
| 11  | Storage variable collision  | Multiple `@storage_var` with the same name.                                                                               | Warning | High      |
| 12  | Implicit function import    | Function with decorator `@external, @view, @l1_handler` that is being implicitly imported.                                | Info    | High      |


## Usage
Analyze a Cairo project in the current directory and export results to a file:
 ```bash
 amarna . -o out.sarif
 ```

Analyze a single file `deleverage.cairo` and export results to a file:
 ```bash
 amarna deleverage.cairo -o deleverage.sarif
 ```

Analyze a single file `code.cairo` and print a summary of the results:
 ```bash
 amarna code.cairo -s
 ```
 
Parse a Cairo file and output the recovered AST in `png`:
 ```bash
 amarna file.cairo -png
 ```

Analyze a Cairo file with the unused_import rule:
 ```bash
 amarna file.cairo --rules=unused-imports
 ```

Analyze a Cairo file using all rules except the arithmetic-add rule:
 ```bash
 amarna file.cairo --except-rules=arithmetic-add
 ```

The full help menu is:
```
usage: amarna [-h] [-p] [-o OUTPUT] [-s] [-png] [-rules RULES] [-exclude-rules EXCLUDE_RULES] [-show-rules] [-disable-inline] -f

Amarna is a static-analyzer for the Cairo programming language.

positional arguments:
  -f                    the name of the .cairo file or directory with .cairo files to analyze

optional arguments:
  -h, --help            show this help message and exit
  -p, --print           print output
  -o OUTPUT, --output OUTPUT
                        file to write the output results in sarif format
  -s, -summary, --summary
                        output summary
  -png, --png           save a png with the AST of a file
  -rules RULES, --rules RULES
                        Only run this set of rules. Enter rule names comma-separated, e.g., dead-store,unused-arguments
  -exclude-rules EXCLUDE_RULES, --exclude-rules EXCLUDE_RULES
                        Exclude these rules from the analysis. Enter rule names comma-separated, e.g., dead-store,unused-arguments
  -show-rules, --show-rules
                        Show all supported rules and descriptions.
  -disable-inline, --disable-inline
                        Disable rules with inline comments. The comments should be the first line and of the form: # amarna: disable=rulename1,rulename2
```

## SARIF file format
The [SARIF](https://sarifweb.azurewebsites.net/) file format is a standard format for static-analysis tools and can be viewed in vscode with the [official extension](https://github.com/Microsoft/sarif-vscode-extension/).


## Installation
```bash
git clone git@github.com:trailofbits/amarna.git && cd amarna
pip install -e .
```


## How the rules work
The static-analysis rules can be:
   - local rules, which analyse each file independently.
   - gatherer rules, which analyse each file independently and gather data to be used in post-process rules.
   - post-process rules, which run after all files were analyzed can use the data gathered in the gatherer rules.

Examples of these are:
 - local rules: find all arithmetic operations in a file
 - gatherer rules: gather all declared functions, and called functions
 - post-process rules: find unused functions using the gathered data, i.e., functions that were declared but never called.


## Rule allowlist, denylist and inline comments

### Rule names
Obtain the names of the currently implemented rules with:
```bash
 amarna --show-rules .
```

### Rule allowlist
Run amarna with a defined set of rules using
```bash
 amarna --rules=rule1,rule2 .
```

The following command will only run the `unused-imports` rule and print the summary result
```bash
 amarna --rules=unused-imports . -s
```

### Rule denylist
Run amarna with all rules except a defined set of rules using
```bash
 amarna --exclude-rules=arithmetic-add,arithmetic-sub . -s
```

### Inline rule disabling comments
You can change the first line of a cairo file to disable a specific rule set on that file.
For example, adding the line
```python
# amarna: disable=arithmetic-div,arithmetic-sub,arithmetic-mul,arithmetic-add
```
as the first line of `file.cairo` and running amarna with
```bash
amarna directory/ --disable-inline -s
```
will not report any arithmetic rule to the `file.cairo` file.




----

# Roadmap: Cairo patterns to implement in the future
 - [ ] find uninitialized variables
 - [ ] using ap and fp registers manually
 - [ ] call and jmp and revoked references
 - [ ] undefined behavior when using [ap] directly
 - [ ] callback before tempvars -- the callback might overwrite local variable memory.

