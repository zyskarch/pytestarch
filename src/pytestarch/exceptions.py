class ImproperlyConfigured(Exception):
    pass


class ParsingError(Exception):
    pass


class PumlParsingError(ParsingError):
    pass


class ImpossibleMatch(Exception):
    pass
