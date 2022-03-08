# Third party imports
from colorama import Fore, Style

def print_with_colour(text, colour):
    coloured_text = f"{getattr(Fore, colour)}{text}{Style.RESET_ALL}"
    return coloured_text