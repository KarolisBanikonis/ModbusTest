# Third party imports
from colorama import Fore, Style

def print_with_colour(text, colour):
    """
    Adds specified colour tags to the provided text.

        Parameters:
            text (str): to what text colour tags should be added
            colour (str): what colour should be used, for example: "RED", "YELLOW"
        Returns:
            coloured_text (str): text with colour tags
    """
    coloured_text = f"{getattr(Fore, colour)}{text}{Style.RESET_ALL}"
    return coloured_text

def print_error(text, output_list, colour=None):
    """
    Prints error to terminal.

        Parameters:
            text (str): what error text should be printed
            output_list (reprint.reprint.output.SignalList): list required for printing to terminal
            colour (str): what colour should be used, for example: "RED", "YELLOW"
    """
    if(colour == None):
        output_list[7] = text
    else:
        output_list[7] = print_with_colour(text, colour)