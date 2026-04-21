*This project has been created as part of the 42 curriculum by ayhirose.*

# Call Me Maybe

### Description
This program analyzes natural language prompts and forces a Large Language Model (LLM) to generate structured function calls in JSON format. By utilizing "Constrained Decoding"—a technique that directly manipulates the LLM's output probabilities (logits) token by token—the program guarantees the generation of valid JSON objects instead of unstructured natural language.


Directory Structure
```
.
├── Makefile
├── README.md             # English documentation (This file)
├── README_ja.md          # Japanese documentation
├── pyproject.toml        # Configuration for dependencies and linters (flake8, mypy)
├── uv.lock
│
├── src/
│   ├── call_me_maybe.py  # Entry point
│   ├── model.py          # Core logic and state machine for constrained decoding
│   ├── parser.py         # Input validation using Pydantic
│   └── utils.py          # Argument parsing
│
├── llm_sdk/              # Provided wrapper for LLM operations
└── data/
    ├── input/            # Test function definitions and prompt JSONs
    └── output/           # Destination for generated results
```

### Instructions
This program requires Python 3.10 or higher. Package management is handled by uv.

1. **installation**
```bash
make install
```
This builds the virtual environment (.venv) and installs necessary dependencies such as pydantic and numpy.
2. **Excution**
```bash
make run
```
Runs the program with default settings, outputting the results to data/output/function_calls.json.

```bash
uv run python src/call_me_maybe.py -f edge_functions.json -i edge_inputs.json
```

```bash
-f or -functions_definition : function_definition_file
-i or –input : input_file
-o or –output : output_file
```
Available flags

```bash
sorce .venv/bin/activate
```
(Note: If you wish to strictly follow the project's PDF and run commands manually, activate the virtual environment beforehand by running source .venv/bin/activate. To exit the virtual environment, run deactivate.)

3. **Other `Makefile` Commands**
```bash
make lint
make lint-strict
```
Executes static type checking and style linting using flake8 and mypy.
```bash
make debug
```
Runs the program in debug mode using pdb.
```bash
make clean
```
Removes cache files. You can also use make fclean which additionally removes the virtual environment.
## Additional sections

### Algorithm explanation
In the standard natural language generation process, the model selects tokens and appends them to the prompt. This program controls the output by programmatically restricting which tokens the model is allowed to select at any given step.

Since the desired output format (JSON structure) remains mostly identical regardless of the prompt, we can control the macro-structure by rejecting tokens that deviate from this format. The true challenge lies in controlling the function names, argument values, and their specific types.
To manage function names, we process the smallest tokenizable units as a 2D list, allowing the state machine to narrow down the selected function by index. Once a function is determined, its argument types are strictly fixed. For instance, if an argument is a NUMBER, we can restrict the allowed tokens exclusively to - and 0-9. Finally, the algorithm carefully accounts for the tokenizer's specific chunking habits to ensure the JSON syntax never breaks.

## Design decisions
As specified by the assignment requirements, we utilized Pydantic for rigorous input validation. Argparse is used for fetching command-line arguments, and Numpy is implemented to optimize calculation speeds during logit manipulation.
However, it should be noted that the primary performance bottleneck in this program lies within the execution speed of the pre-provided functions inside llm_sdk/__init__.py. Therefore, our internal optimizations do not drastically affect the overall execution time of the project.

## Performance analysis
Thanks to the strict control imposed by constrained decoding, the system consistently generates JSON that 100% matches the specified schema.
Regarding execution speed, as mentioned above, it is bound by the llm_sdk execution speed. In our testing and development environment, the processing speed averages around 1 minute per function call.

## Challenges faced
During development, we faced a critical issue where Python's json.loads inherently consumed escape characters. This resulted in passing "raw newlines" or "unescaped double quotes" directly to the LLM, which physically broke the output JSON syntax.
We resolved this by creating an absolute rejection list (shield) that permanently blocks tokens containing these specific, dangerous characters from ever being selected.

## Testing strategy
In addition to the provided standard tests, we validated the robustness of the implementation using custom test JSONs containing extreme "Edge cases," including:
- Empty strings and extremely long strings.
- Consecutive special symbols, emojis (👾), and escape characters.
- "Mean prompts (Wrong types)" that intentionally request data types different from the schema.
- Ambiguous prompts where identifying the correct function is logically difficult.

## Example
```
1. Request logits
--- Pre Limit Token ---
ID:   5209 | Score:   18.86 | Token: ' Please'
ID:   4710 | Score:   17.98 | Token: ' \n\n'
ID:    220 | Score:   17.57 | Token: ' '
ID:   3555 | Score:   17.00 | Token: ' What'
ID:   7281 | Score:   16.89 | Token: ' Also'
2. <<< Constrain logits >>>
--- Post Limit Token ---
ID:    515 | Score:    4.81 | Token: '{\n'
ID:      0 | Score:    -inf | Token: '!'
ID:      1 | Score:    -inf | Token: '"'
ID:      2 | Score:    -inf | Token: '#'
ID:      3 | Score:    -inf | Token: '$'
3. Select the token with the highest score
4. Generate the restriction token to be used next
```
The constraint decoding is split into the current state for each token and outputted.

### Resources

AI
- Used as a sounding board for designing the algorithm and debugging the Logits manipulation in constrained decoding.
- Assisted in analyzing flake8 and mypy error logs, and optimizing the pyproject.toml configuration.
- Provided support for English translation and structural formatting of Docstrings and this README.
