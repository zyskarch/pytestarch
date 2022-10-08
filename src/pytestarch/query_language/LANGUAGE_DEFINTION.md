# PyTestArch Query Language

## Structure
SUBJECT VERB_MARKER_1 IMPORT_TYPE VERB_MARKER_2 OBJECT

VERB_MARKER_1:
    should
    should only
    should not

VERB_MARKER_2:
    except

IMPORT_TYPE:
    import_from
    be_imported_from

SUBJECT/OBJECT:
    sub_module_of
    name  # complete match
    anything (only object)


M1 should import_from M2
M1 should import_from except M2  # any import from M1 that isn't M2 (but M2 might be imported as well)
M1 should only import_from M2
M1 should only import_from except M2  # M2 cannot be imported by M1, min. 1 import needed
M1 should not import_from M2
M1 should not import_from except M2  # M1 does not have to import M2

M1 should be_imported_from M2
M1 should be_imported_from except M2  # any import of M1 that is not M2 (but M2 might import as well)
M1 should only be_imported_from M2
M1 should only be_imported_from except M2  # M2 cannot import M1, but min other module is importing M1
M1 should not be_imported_from M2
M1 should not be_imported_from except M2  # M1 does not have to be imported


not all combinations are possible with anything:
M1 should import anything                       x
M1 should import except anything                x
M1 should only import anything                  x
M1 should only import except anything           x
M1 should not import anything                   o
M1 should not import except anything            x
M1 should be_imported by anything               x
M1 should be_imported by except anything        x
M1 should only be_imported by anything          x
M1 should only be_imported except by anything   x
M1 should not be_imported by anything           o
M1 should not be_imported except by anything    x



## Semantics
M1 should import M2                 -> edge from M1 to M2
M1 should only import M2            -> -"-, neg(any edge from M1 to non-M2)
M1 should not import M2             -> neg(edge from M1 to M2)
M1 should import except M2          -> any edge from M1 to non-M2
M1 should only import except M2     -> any edge from M1 to non-M2, neg(edge from M1 to M2)
M1 should not import except M2      -> neg(any edge from M1 to non-M2)


M1 should be_imported_from M2               -> edge from M2 to M1
M1 should only be_imported_from M2          -> -"-, neg(any edge from non-M2 to M1)
M1 should not be_imported_from M2           -> neg(edge from M2 to M1)
M1 should be_imported_from except M2        -> any edge from non-M2 to M1
M1 should only be_imported_from except M2   -> any edge from non-M2 to M1, neg(edge from M2 to M1)
M1 should not be_imported_from except M2    -> neg(any edge from non-M2 to M1)

M1 should not import anything               -> neg(any edge from M1 to ?)
M1 should not be_imported by anything       -> neg(any edge from ? to M1)


If M2 contains multiple modules, they can be treated separately for "edge", but need to be considered jointly for 
"any edge".


Aliases:
M1 should not import anything -> M1 should not import anything except itself
M1 should not be imported by anything -> M1 should not be imported by anything except itself



Operations: 
    any edge
    edge
    neg edge
    neg any


Operation Markers:
    any         should import except, should only import except             | should be except, should only be except
    edge        should import, should only import                           | should be, should only be
    neg edge    should not import, should only import except                | should not be, should only be except
    neg any     should not import except, should only import                | should only be, should not be except

simplified:
    any         should except, should only except
    edge        should, should only
    neg edge    should not, should only except
    neg any     should not except, should only


# Rule Violation Messages
### One M2
| type                                        | message                                                                                                  | note                   |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------|------------------------|
| should import                               | M1 does not import M2                                                                                    | -                      |
| should only import -- forbidden             | Violator1 imports Violator2. Subviolator1 imports Violator3                                              | (submodule of M1)      |
| should only import -- no import             | M1 does not import M2                                                                                    | -                      |
| should only import -- both                  | Violator1 imports Violator2. Subviolator1 imports Violator3. M1 does not import M2                       | (submodule of M1)      |
| should not import                           | Violator1 imports Violator2. Subviolator1 imports Subviolator2.                                          | (submodules of M1, M2) |
| should import except                        | M1 does not import any that is not M2                                                                    | -                      |
| should only import except -- forbidden      | Violator1 imports Violator2. Subviolator1 imports Subviolator2.                                          | (submodules of M1, M2) |
| should only import except -- no import      | M1 does not import any that is not M2                                                                    | -                      |
| should only import except -- both           | Violator1 imports Violator2. Subviolator1 imports Subviolator2. M1 does not import any that is not M2    | (submodules of M1, M2) |
| should not import except                    | Violator1 imports Violator2. Subviolator1 imports Violator3.                                             | (submodule of M1)      |
| should be imported                          | M1 is not imported by M2                                                                                 | -                      |
| should only be imported -- forbidden        | Violator2 imports Violator1. Violator3 imports Subviolator1                                              | (submodule of M1)      |
| should only be imported -- no import        | M1 is not imported by M2                                                                                 | -                      |
| should only be imported -- both             | Violator2 imports Violator1. Violator3 imports Subviolator1. M1 is not imported by M2                    | (submodule of M1)      |
| should not be imported                      | Violator2 imports Violator1. Violator 3 imports Subviolator1.                                            | (submodules of M1, M2) |
| should be imported except                   | M1 is not imported by any that is not M2                                                                 | -                      |
| should only be imported except -- forbidden | Violator2 imports Violator1. Subviolator2 imports Subviolator1.                                          | (submodules of M1, M2) |
| should only be imported except -- no import | M1 is not imported by any that is not M2                                                                 | -                      |
| should only be imported except -- both      | Violator2 imports Violator1. Subviolator2 imports Subviolator1. M1 is not imported by any that is not M2 | (submodules of M1, M2) |
| should not be imported except               | Violator2 imports Violator1. Violator3 imports Subviolator1.                                             | (submodule of M1)      |


### Multiple M2s
| type                                        | message                                                                                                                                      | note                                                | diff to One M2 |
|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|---------------|
| should import                               | M1 does not import M2, M3                                                                                                                    | concatentation with ","                             | list all M2s  |
| should only import -- forbidden             | Violator1 imports Violator2. Subviolator1 imports Violator3.                                                                                 | (submodule of M1)                                   | -             |
| should only import -- no import             | M1 does not import M2(, M3)                                                                                                                  | concatentation with ","                             | -             |
| should only import -- both                  | Violator1 imports Violator2. Subviolator1 imports Violator3. M1 does not import M2(, M3)                                                     | (submodule of M1); concatentation with ","          | -             |
| should not import                           | Violator1 imports Violator2. Subviolator1 imports Subviolator2. Subviolator1 imports Subviolator2. Subviolator1 imports Violator3            | (submodules of M1, M2, M3); concatentation with "," | -             |
| should import except                        | M1 does not import any that is not M2, M3                                                                                                    | concatentation with ","                             | list all M2s  |
| should only import except -- forbidden      | Violator1 imports Violator2. Subviolator1 imports Subviolator2. Subviolator1 imports Violator3                                               | (submodules of M1, M2, M3); concatentation with "," | -             ||
| should only import except -- no import      | M1 does not import any that is not M2, M3                                                                                                    | concatentation with ","                             | list all M2s  |
| should only import except -- both           | Violator1 imports Violator2. Subviolator1 imports Subviolator2. Subviolator1 imports Violator3 . M1 does not import any that is not M2, M3   | (submodules of M1, M2, M3); concatentation with "," | list all M2s  |
| should not import except                    | Violator1 imports Violator2. Subviolator1 imports Subviolator2. Subviolator1 imports Violator3                                               | (submodule of M1)                                   | -             |
| should be imported                          | M1 is not imported by M2, M3                                                                                                                 | concatentation with ","                             | list all M2s  |
| should only be imported -- forbidden        | Violator2 imports Violator1. Violator2 imports Subviolator1                                                                                  | (submodule of M1)                                   | -             |
| should only be imported -- no import        | M1 is not imported by M2, M3                                                                                                                 | concatentation with ","                             | -             |
| should not be imported                      | Violator2 imports Violator1. Violator3 imports Subviolator1.                                                                                 | (submodules of M1, M2, M3)                          | -             |
| should be imported except                   | M1 is not imported by any that is not M2, M3                                                                                                 | concatentation with ","                             | list all M2s  |
| should only be imported except -- forbidden | Violator2 imports Violator1. Subviolator2 imports Subviolator1. Violator3 imports Subviolator1.                                              | (submodules of M1, M2, M3)                          | -             |
| should only be imported except -- no import | M1 is not imported by any that is not M2, M3                                                                                                 | concatentation with ","                             | list all M2s  |
| should only be imported except -- both      | Violator2 imports Violator1. Subviolator2 imports Subviolator1. Violator3 imports Subviolator1. M1 is not imported by any that is not M2, M3 | (submodules of M1, M2, M3); concatentation with "," | list all M2s  |
| should not be imported except               | Violator2 imports Violator1. Violator3 imports Subviolator1                                                                                  | (submodule of M1)                                   | -             |
