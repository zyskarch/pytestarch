# PytestArch Query Language

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


# Error Messages
should not be imported except
X is imported by Y

should only be imported except
1) X are not imported by any module that is not Y
2) X are imported by Y

should be imported except
X are not imported any that is not by Y

should not be imported
X are imported by Y

should only be imported
X are imported by Y

should be imported
X are not imported by Y

should not import except
X import Y

should only import except
1) X do not import any module that is not Y
2) X import Y

should import except
X do not import any module that are not Y

should not import
X import Y

should only import
X also imports Y

should import
X do not import Y


----------------------------
Grouped together:

X is imported by [LAX / AS DEFINED / AS DEFINED / LAX]        
        should not except [LAX]
            lax not
        should only be except - forbidden import [AS DEFINED]
            lax required & strict not
        should not be [AS DEFINED]
            strict not
        should only be [LAX]
            strict required & lax not

X is not imported by any that is not [AS DEFINED]
        should only be except - no import
            lax required & strict not
        should be except
            lax required (lax not False, strict req False, strict not False)

X is not imported by [AS DEFINED]
        should be imported
            strict required (lax req False, strict not False, lax not False)
 
X imports [LAX / AS DEFINED / AS DEFINED / LAX]
        should not except [LAX]
            lax not
        should only except - forbidden import [AS DEFINED]
            lax required & strict not
        should not [AS DEFINED]
            strict not
        should only [LAX]
            strict required & lax not

X does not import any that is not [AS DEFINED]
        should only except - no import
            lax required & strict not
        should except
            lax required

X does not import [AS DEFINED]
        should
            strict required