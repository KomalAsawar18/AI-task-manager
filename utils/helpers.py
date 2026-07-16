import sys

def format_table(headers, rows):
    """
    Prints a beautiful ASCII table with dynamic column widths.
    """
    if not headers:
        return ""
        
    # Convert all row elements to strings
    string_rows = [[str(item) for item in row] for row in rows]
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in string_rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(val))
                
    # Build lines
    horizontal_border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    lines = []
    lines.append(horizontal_border)
    
    # Header row
    header_line = "| " + " | ".join(headers[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
    lines.append(header_line)
    lines.append(horizontal_border)
    
    # Data rows
    for row in string_rows:
        # Pad row with empty strings if it has fewer elements than headers
        padded_row = row + [""] * (len(headers) - len(row))
        data_line = "| " + " | ".join(padded_row[i].ljust(col_widths[i]) for i in range(len(headers))) + " |"
        lines.append(data_line)
        
    lines.append(horizontal_border)
    return "\n".join(lines)


def get_non_empty_input(prompt):
    """
    Repeatedly prompts the user until a non-empty string is provided.
    """
    while True:
        try:
            val = input(prompt).strip()
            if val:
                return val
            print("Error: Input cannot be empty. Please try again.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)


def get_choice_input(prompt, valid_choices):
    """
    Repeatedly prompts user for input until it matches one of the valid choices (case-insensitive).
    Returns the matching valid choice.
    """
    choices_str = "/".join(valid_choices)
    formatted_prompt = f"{prompt} ({choices_str}): "
    
    while True:
        try:
            val = input(formatted_prompt).strip()
            # Case insensitive check
            matching = [c for c in valid_choices if c.lower() == val.lower()]
            if matching:
                return matching[0]
            print(f"Error: Invalid choice. Must be one of {choices_str}.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)


def get_int_input(prompt, allow_empty=False):
    """
    Repeatedly prompts user for an integer.
    """
    while True:
        try:
            val = input(prompt).strip()
            if not val and allow_empty:
                return None
            if val.isdigit():
                return int(val)
            print("Error: Please enter a valid positive integer.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)
