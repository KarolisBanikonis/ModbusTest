# Third party imports
import traceback
from reprint import output
from colorama import Fore, Style

class PrintModule:

    def __init__(self):
        """Initializes PrintModule object."""
        self.output = output(output_type="list", initial_len=8, interval=0)
        self.print_list = self.output.warped_obj

    def print_at_row(self, row, text):
        """
        Prints text to terminal at specified row.

            Parameters:
                row (int): at what row of terminal text should be printed
                text (str): what content should be printed
        """
        if(row < 0 or row > len(self.print_list)):
            self.warning(f"Text could not be printed at row: {row}!")
        else:
            self.print_list[row] = text

    def colour_text(self, text, colour):
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

    def error(self, text):
        """
        Prints error to terminal.

            Parameters:
                text (str): what error text should be printed
        """
        self.print_list[7] = self.colour_text(text, "RED")
        self.__reset_print_line()

    def warning(self, text):
        """
        Prints warning to terminal.

            Parameters:
                text (str): what error text should be printed
        """
        self.print_list[7] = self.colour_text(text, "YELLOW")

    def clear_warning(self):
        """Clears the row where warnings are printed."""
        self.print_list[7] = ""

    def __reset_print_line(self):
        """Sets a new line for printing new results."""
        self.output.__exit__("Error", "Critical", traceback)