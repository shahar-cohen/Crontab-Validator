import re
import sys
import os
import shutil

def validate_cron_syntax(line):
    """
    Validates the cron syntax for a single crontab line.
    """
    cron_regex = r'^(\*|([0-9]|[1-5][0-9]))\s+(\*|([0-9]|[1-5][0-9]))\s+(\*|([1-9]|[1-2][0-9]|3[0-1]))\s+(\*|(1[0-2]|[1-9]))\s+(\*|([0-6]))\s+.+$'
    special_syntax_regex = r'^@(reboot|hourly|daily|weekly|monthly|yearly|annually)\s+.+$'
    return bool(re.match(cron_regex, line) or re.match(special_syntax_regex, line))

def extract_command(line):
    """
    Extracts the command or script path from a valid crontab line.
    """
    parts = line.split()
    if line.startswith('@'):
        return ' '.join(parts[1:])
    else:
        return ' '.join(parts[5:])

def is_unix_command(command):
    """
    Checks if the first part of the command is a valid Unix/Linux command.
    """
    executable = command.split()[0]
    return shutil.which(executable) is not None

def resolve_path(script_path, crontab_dir):
    """
    Resolves a script path relative to the crontab file's directory if it's a relative path.
    """
    if not os.path.isabs(script_path):
        return os.path.normpath(os.path.join(crontab_dir, script_path))
    return script_path

def validate_script_or_command(line_no, command, crontab_dir, errors):
    """
    Validates whether the script or command in the crontab line exists or is valid.
    Updates the errors list with relevant error messages if issues are found.
    """
    script_path = command.split()[0]
    resolved_path = resolve_path(script_path, crontab_dir)

    script_exists = os.path.exists(resolved_path)
    is_valid_command = is_unix_command(script_path) if not script_exists else False

    if not script_exists and not is_valid_command:
        errors.append(f"Non-existing script or invalid command on line {line_no}: {script_path} (resolved path: {resolved_path})")

    if not os.path.isabs(script_path):
        absolute_recommendation = os.path.abspath(resolved_path)
        errors.append(
            f"Recommendation: Use absolute file paths to avoid ambiguity. Replace '{script_path}' "
            f"with '{absolute_recommendation}' on line {line_no}."
        )

def validate_crontab_line(line, line_no, crontab_dir, check_scripts=False):
    """
    Validates a single crontab line for both syntax and script/command existence.
    Updates an errors list if any issues are found.
    """
    errors = []

    # Validate cron syntax
    if not validate_cron_syntax(line):
        errors.append(f"Syntax error on line {line_no}: {line}")
    elif check_scripts:
        command = extract_command(line)
        validate_script_or_command(line_no, command, crontab_dir, errors)

    return errors

def validate_crontab_file(file_path, check_scripts=False):
    """
    Reads and validates a crontab file.
    Optionally checks if the commands or scripts exist.
    Returns a tuple: (bool, str) -> (success, message).
    """
    crontab_dir = os.path.dirname(os.path.abspath(file_path))

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
        if not line or line.startswith('#'):
            continue

        # Validate each line using the modular function
        line_errors = validate_crontab_line(line, line_no, crontab_dir, check_scripts=check_scripts)
        errors.extend(line_errors)

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
    if "--help" in sys.argv:
        print_usage()

    if len(sys.argv) < 2:
        print("Error: Missing required <crontab_file_path> argument.\n")
        sys.exit(2)

    crontab_file_path = sys.argv[1]
    check_scripts = '--check-scripts' in sys.argv

    success, message = validate_crontab_file(crontab_file_path, check_scripts=check_scripts)

    print(message)
    sys.exit(0 if success else 3)
