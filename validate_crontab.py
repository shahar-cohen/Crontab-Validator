import re
import sys
import os
import shutil

def validate_crontab_line(line):
    """
    Validates a single crontab line for correct syntax.
    """
    # Regex for standard crontab syntax
    cron_regex = r'^(\*|([0-9]|[1-5][0-9]))\s+(\*|([0-9]|[1-5][0-9]))\s+(\*|([1-9]|[1-2][0-9]|3[0-1]))\s+(\*|(1[0-2]|[1-9]))\s+(\*|([0-6]))\s+.+$'
    
    # Regex for special syntax like @reboot, @daily, etc.
    special_syntax_regex = r'^@(reboot|hourly|daily|weekly|monthly|yearly|annually)\s+.+$'

    if re.match(cron_regex, line) or re.match(special_syntax_regex, line):
        return True
    return False

def extract_command(line):
    """
    Extracts the command or script path from a valid crontab line.
    """
    parts = line.split()
    if line.startswith('@'):
        # Special syntax: Skip the first part (e.g., "@daily")
        return ' '.join(parts[1:])
    else:
        # Standard syntax: Skip the first five parts (minute, hour, day, month, weekday)
        return ' '.join(parts[5:])

def is_unix_command(command):
    """
    Checks if the first part of the command is a valid Unix/Linux command.
    """
    executable = command.split()[0]  # Get the first part of the command
    return shutil.which(executable) is not None

def resolve_path(script_path, crontab_dir):
    """
    Resolves a script path relative to the crontab file's directory if it's a relative path.
    """
    if not os.path.isabs(script_path):
        # If the path is relative, resolve it against the crontab file's directory
        return os.path.normpath(os.path.join(crontab_dir, script_path))
    return script_path

def validate_crontab_file(file_path, check_scripts=False):
    """
    Reads and validates a crontab file.
    Optionally checks if the commands or scripts exist.
    Returns a tuple: (bool, str) -> (success, message).
    """
    crontab_dir = os.path.dirname(os.path.abspath(file_path))  # Get crontab file's directory

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return False, f"Error: File '{file_path}' not found."
    except PermissionError:
        return False, f"Error: Permission denied for file '{file_path}'."

    errors = []
    for line_no, line in enumerate(lines, start=1):
        line = line.strip()
        # Ignore blank lines and comments
        if not line or line.startswith('#'):
            continue

        # Validate line syntax
        if not validate_crontab_line(line):
            errors.append(f"Syntax error on line {line_no}: {line}")
            continue

        # Check script existence or command validity if enabled
        if check_scripts:
            command = extract_command(line)
            script_path = command.split()[0]
            resolved_path = resolve_path(script_path, crontab_dir)

            # Check if the script exists
            script_exists = os.path.exists(resolved_path)

            # Only check if it's a valid Unix/Linux command if the script doesn't exist
            is_valid_command = is_unix_command(script_path) if not script_exists else False

            # Unified error message for non-existing scripts and invalid commands
            if not script_exists and not is_valid_command:
                errors.append(f"Non-existing script or invalid command on line {line_no}: {script_path} (resolved path: {resolved_path})")

            # Recommend using absolute paths for relative paths
            if not os.path.isabs(script_path):
                absolute_recommendation = os.path.abspath(resolved_path)
                errors.append(
                    f"Recommendation: Use absolute file paths to avoid ambiguity. Replace '{script_path}' "
                    f"with '{absolute_recommendation}' on line {line_no}."
                )

    if errors:
        return False, "\n".join(errors)

    return True, "The crontab file is valid."

def print_usage():
    """
    Prints usage instructions for the script.
    """
    usage_message = """
Usage: python validate_crontab.py <crontab_file_path> [--check-scripts] [--help]

Arguments:
  <crontab_file_path>   Path to the crontab file to validate.
  --check-scripts       Enable checking if scripts exist or commands are valid Unix/Linux commands.
  --help                Show this help message and exit.
"""
    print(usage_message)
    sys.exit(0)

if __name__ == "__main__":
    # Handle CLI arguments
    if "--help" in sys.argv:
        print_usage()  # Display usage and exit with 0.

    if len(sys.argv) < 2:
        print("Error: Missing required <crontab_file_path> argument.\n")
        sys.exit(2)  # Exit with code 2 for invalid usage.

    # Parse arguments
    crontab_file_path = sys.argv[1]
    check_scripts = '--check-scripts' in sys.argv

    # Validate the crontab file
    success, message = validate_crontab_file(crontab_file_path, check_scripts=check_scripts)

    # Handle validation result
    print(message)
    if not success:
        sys.exit(3)  # Exit with code 3 for invalid crontab file.

    sys.exit(0)  # Exit with 0 for success.
