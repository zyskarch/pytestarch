from __future__ import annotations


def is_submodule_of(module: str, parent_module_name: str) -> bool:
    """Determines whether a module is one of the given parent module's submodules.

    The prefix must end on a dot boundary: a plain startswith would also match
    modules that merely share the parent's name prefix, such as 'appstart' and
    'appweb' for a parent module 'app'.
    """
    return module.startswith(f"{parent_module_name}.")


def is_internal_module(module: str, internal_module_name: str) -> bool:
    """Determines whether a module is the given internal module itself or one of its submodules."""
    return module == internal_module_name or is_submodule_of(
        module, internal_module_name
    )
