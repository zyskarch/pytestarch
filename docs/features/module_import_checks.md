# Checking dependencies between modules

## General Structure

The query language that can be used to define architectural rules follows this structure: 

RULE_SUBJECT - VERB_MARKER_1 - IMPORT_TYPE - VERB_MARKER_2 - RULE_OBJECT

The meaning of these structural markers is described in the table below.

| Marker       | Description                                            | Example                            |
|--------------|--------------------------------------------------------|------------------------------------|
| RULE_SUBJECT | module(s) to be checked                                | modules that are named 'B'         |
| RULE_OBJECT  | module(s) to check against                             | modules that are submodules of 'A' |
| IMPORT_TYPE | expected type of import relationship | be imported by                     |
| VERB_MARKER_1 | defines the expected behavior, part I                  | should not                         |
| VERB_MARKER_2 | defines the expected behavior, part II                 | except                             |

The examples given in the table above combined form the rule `modules that are named 'B' (RULE_SUBJECT) should not (VERB_MARKER_1) be imported by (IMPORT_TYPE) modules except (VERB_MARKER_2) modules that are submodules of "A" (RULE_OBJECT)`.

Looking at the diagram in the section Complex Example, we can see that this rule holds - the only module importing 
from the "B" module is "fileA11", which is a submodule of "A".


## Features

Currently, the following markers are supported by PyTestArch:

### RULE_SUBJECT
* are_named("X"): applies to module named "X" (and also considers its submodules, as submodules are considered to be part of their parent module)
* are_submodules_of("Y"): applies to submodules of module named "Y", but not "Y" itself
* have_name_matching(regex): applies to module with names that match the given regex. 

⚠ When using the `have_name_matching` functionality, the regex should ideally only directly match the module one wants to test, not
also its submodules. For example, if a module named src.moduleA should be matched, the regex should not also match 
src.moduleA.submoduleAA, as this can increase the runtime of the rule assertion check. This has no effect on the 
result of the check itself, as submodules are considered to be part of their parent module - for example, if the parent
module has to import from module X, this condition is fulfilled if at least one of its submodules imports X.

⚠ Regex expressions that want to apply a predicate on a module, but not its submodules are not currently supported. 
This often happens with regex expressions that contain negations.
Consider the following example:
```
foo/
    bar_test.py (imports from util_test.py)
    util_test.py
```
We want to express that no production code (not ending with _test) may import from test code (ending in _test).
A rule with a negation in a regex could look like this:
`Rule().modules_that().have_name_matching(r"^((?!test$).)*$").should_not().import_modules_that().have_name_matching(r".*test$")`
PyTestArch calculates which modules match the first regex - which in this case, is only "foo". The second expression matches the two
test files. The rule then gets converted to 
```Rule().modules_that().are_named("foo").should_not().import_modules_that().have_name_matching(["foo.bar_test", "util_test"])```
"Foo" itself does not import any of the other files. However, the string "foo" matches not only "foo" itself, but also its
submodules, as these are considered to be part of their parent module. In this case, "foo.bar_test" is then checked for imports
of any test files - and bar_test does import util_test: The rule is marked as violated.

Rules like this can usually be expressed without negations, often even by using the general API: An equivalent rule would be
```Rule().modules_that().have_name_matching(".*test$").should_not().be_imported_by_modules_except_modules_that().have_name_matching(".*test$")```

Note: If a regex resolves to multiple rule subjects, this is equivalent to specifying the rule independently for both.

### RULE_OBJECT
same as RULE_SUBJECT, with an additional

anything: can only be used in combination with should_not()

In order to reduce the number of possible API component combinations, this rule object has been combined with two
verbs into: `import_anything()` and `be_imported_by_anything()`. 


Both RULE_SUBJECTs and RULE_OBJECTs can be specified in batch, i.e. via a list of values. If multiple rule subjects are
specified, this has the same effect as defining a rule per rule subject.
For example, the rule
```
modules_that() \
    .are_named(["1", "2"]) \
    .should_only() \
    .be_imported_by_modules_that() \
    .are_named(["3", "4"])
```
is fulfilled, it the modules "1" and "2" both are not imported by any module other than "3" and "4", and if both "3" and "4" do import "1" and "2".


### VERB_MARKER_1
* should()
* should_only()
* should_not()

### IMPORT_TYPE + VERB_MARKER_2
* import_modules_that()
* import_modules_except_modules_that()
* be_imported_by_modules_that()
* be_imported_by_modules_except_modules_that()

VERB_MARKER_2 and IMPORT_TYPE have been conflated into one expression to improve readability.

Markers from each category can be combined freely with all markers of all other categories. Example rules could be <br>
```
modules_that() \
    .are_sub_modules_of("A") \
    .should_only() \
    .be_imported_by_modules_that() \
    .are_sub_modules_of("B") \
```
(True in the above example)

or <br>
```
modules_that() \
    .are_named("C") \
    .should_only() \
    .be_imported_by_modules_that() \
    .are_named("A2") \
```
(False, also imported by module "A")


Most rules are so close to the English language that a detailed explanation seems unnecessary. An exception might be the
VERB_MARKER_2 "except". A combination of this VERB_MARKER_2 and every type of VERB_MARKER_1 and IMPORT_TYPE is given below
as reference (M1, M2 are used as RULE_SUBJECT and RULE_OBJECT respectively; pseudo-code for brevity):

| Rule | Explanation |
| ---- | ----------- |
| M1 should import except M2 | M1 should import at least one module that isn't M2, but can also import M2|
| M1 should only import except M2| M1 should import at least one module that isn't M2 and should not import M2 |
| M1 should not import except M2| M1 should not import any module other than M2, but does not have to import M2 |
| M1 should be imported except by M2 | at least one module that isn't M2 should import M1 (M2 can import M1 as well) |
| M1 should only be imported except by M2 | at least one module that isn't M2 should import M1, and M2 cannot import M1 |
| M1 should not be imported except by M2 | no module other than M2 should import M1, but M2 does not have to import M1 |


There are two aliases to make rules easier:

* 'M1 should not import anything' is equivalent to: 'M1 should not import anything except itself' (e.g. imports between its submodules are allowed, but no other imports)
* 'M1 should not be imported by anything' is equivalent to: 'M1 should not be imported by anything except itself' (dito)