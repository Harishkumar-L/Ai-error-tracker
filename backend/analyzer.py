import re

def analyze_error(language, error, context=''):
    patterns = {
        'Python': [('ModuleNotFoundError', r'ModuleNotFoundError: No module named [\'\"]?([^\'\"\n]+)', 'Python cannot find an installed module named `{}`.'), ('NameError', r'NameError: name [\'\"]([^\'\"]+)[\'\"] is not defined', 'The name `{}` was used before Python knew what it referred to.'), ('IndexError', r'IndexError: (.+)', 'Code tried to access a sequence position outside the available range.'), ('KeyError', r'KeyError: [\'\"]?([^\'\"\n]+)', 'A dictionary lookup requested a key that is not present.'), ('ZeroDivisionError', r'ZeroDivisionError: (.+)', 'A calculation attempted to divide by zero.'), ('FileNotFoundError', r'FileNotFoundError: (.+)', 'Python could not find the requested file or directory.'), ('TypeError', r'TypeError: (.+)', 'An operation received a value of an unexpected type.')],
        'JavaScript': [('TypeError', r'TypeError: Cannot read properties of (undefined|null) \(reading [\'\"]([^\'\"]+)', 'JavaScript tried to read `{}` from a missing value.'), ('ReferenceError', r'ReferenceError: (.+) is not defined', 'Code referenced `{}` before it was declared.'), ('SyntaxError', r'SyntaxError: (.+)', 'The JavaScript parser could not understand the code structure.')],
        'C++': [('std::out_of_range', r'std::out_of_range', 'A standard library access received an index outside the valid range.'), ('Segmentation fault', r'(?:segmentation fault|SIGSEGV)', 'The program accessed memory it is not allowed to access.'), ('Linker error', r'undefined reference to [`\']?([^\'\n]+)', 'The linker could not find an implementation for a referenced symbol.')],
        'Java': [('NullPointerException', r'NullPointerException', 'Java attempted to use an object reference whose value is null.'), ('ArrayIndexOutOfBoundsException', r'ArrayIndexOutOfBoundsException', 'Code accessed an array position outside its valid range.'), ('ClassNotFoundException', r'ClassNotFoundException: (.+)', 'The JVM could not find the requested class at runtime.')]
    }
    classification, explanation, signal = 'Unclassified runtime error', 'The trace does not match a built-in pattern yet. Start with the file and line number, then reproduce the failure in a small test.', error.splitlines()[-1][:240]
    for name, pattern, template in patterns.get(language, []):
        match = re.search(pattern, error, re.I)
        if match:
            classification = name
            explanation = template.format(match.group(1) if match.groups() else name)
            signal = match.group(0)
            break
    location = re.search(r'(?:File |at )?[\"\']?([^\"\'\s]+\.(?:py|js|jsx|ts|tsx|cpp|cc|c|java))[^\n]*?(?:line |:)(\d+)', error, re.I)
    evidence = [signal]
    if location: evidence.append(f'Location hint: {location.group(1)} at line {location.group(2)}')
    if context: evidence.append('User context supplied: reproduction details are available for verification.')
    causes = {
        'ModuleNotFoundError':['The dependency is not installed in the active environment.','A different interpreter or virtual environment is running the command.','The import name differs from the package name.'],
        'NameError':['A variable or function has a typo.','The declaration runs after the failing line.','The name is outside the current scope.'],
        'TypeError':['A value has a different shape or type than expected.','An API response is missing a field or is still loading.','A function received the wrong arguments.'],
        'IndexError':['The sequence is shorter than expected.','A loop has an off-by-one boundary.','The input collection is empty.'],
        'KeyError':['The key is optional or spelled differently.','The input schema changed.','The dictionary was built from incomplete data.'],
        'ZeroDivisionError':['The denominator can be zero for valid input.','A default value was not initialized.','A guard condition is missing or too late.'],
        'FileNotFoundError':['The relative path uses a different working directory.','The file is missing or named differently.','The runtime lacks the expected mounted directory.']
    }.get(classification, [f'The {language} runtime rejected an assumption made by the code.','Input data, environment, or dependency versions may differ from the expected setup.','The failing line may be a symptom of an earlier state change.'])
    loc = f'Open `{location.group(1)}` at line {location.group(2)} and inspect values immediately before the failing expression.' if location else 'Find the first file and line number in the trace, then inspect values immediately before the failing expression.'
    steps=[loc,'Reproduce the error with the smallest input that still fails.','Add a temporary log, print, or debugger breakpoint for the values involved.','Change one assumption at a time, rerun, and keep the check that confirms the cause.']
    if classification == 'ModuleNotFoundError': steps.insert(1,'Run `python -m pip show <module>` using the same interpreter that runs the program.')
    fixes={'ModuleNotFoundError':['Install the dependency in the active environment: `python -m pip install <package>`.','Add the dependency to `requirements.txt` and recreate the environment.'],'NameError':['Correct the spelling or move the declaration before use.','Pass the value explicitly instead of relying on a hidden global.'],'TypeError':['Validate the value before the operation.','Make the function contract explicit with a small input check or type annotation.'],'IndexError':['Guard the access with a length check or iterate directly.','Fix the loop boundary so it stops before the collection length.'],'KeyError':['Use `.get()` with a deliberate fallback when optional.','Validate the input schema and fail with a clearer message.'],'ZeroDivisionError':['Check the denominator before dividing.','Add a regression test for zero and near-zero inputs.'],'FileNotFoundError':['Build paths with `pathlib.Path` from a known project root.','Confirm the file exists in the runtime environment.']}.get(classification,['Reduce the failing case to a minimal reproduction.','Add a regression test once the cause is confirmed.'])
    report = f'# Bug: {classification} in {language}\n\n## Summary\n{explanation}\n\n## Error output\n```text\n{error}\n```\n\n## Context\n{context or "Not provided."}\n\n## Hypotheses to verify\n' + '\n'.join('- [ ] '+x for x in causes) + '\n\n## Debugging checklist\n' + '\n'.join(f'{i+1}. {x}' for i,x in enumerate(steps)) + '\n\n## Candidate fixes\n' + '\n'.join('- '+x for x in fixes) + '\n\n## Acceptance criteria\n- [ ] Root cause verified\n- [ ] Fix covered by a regression test\n- [ ] No secrets included'
    return {'classification':classification,'explanation':explanation,'evidence':evidence,'possible_causes':causes,'debug_steps':steps,'suggested_fixes':fixes,'github_report':report,'confidence':'high' if classification != 'Unclassified runtime error' else 'low'}
