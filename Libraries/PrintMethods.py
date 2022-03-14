# Third party imports
from colorama import Fore, Style

def print_with_colour(text, colour):
    coloured_text = f"{getattr(Fore, colour)}{text}{Style.RESET_ALL}"
    return coloured_text

def print_error(text, output_list, colour=None):
    if(colour == None):
        output_list[7] = text
    else:
        output_list[7] = print_with_colour(text, colour)