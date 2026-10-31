# Origen: primer-proyecto-tdc/src/automatas/errors.py, commit 750243e.
# Adaptación: únicamente imports automatas.x a .x; sin cambios de lógica.
class AutomataError(ValueError):
    pass


class RegexSyntaxError(AutomataError):
    pass


class AutomataValidationError(AutomataError):
    pass


class InputFormatError(AutomataError):
    pass


class VisualizationError(AutomataError):
    pass
