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



Operations: 
    any edge
    edge
    neg edge
    neg any


Operation Markers:
    any         should import except, should only import except | should be except, should only be except
    edge        should import, should only import               | should be, should only be
    neg edge    should not import, should only import except    | should not be, should only be except
    neg any     should not import except, should only import    | should only be, should not be except

simplified:
    any         should except, should only except
    edge        should, should only
    neg edge    should not, should only except
    neg any     should not except, should only
