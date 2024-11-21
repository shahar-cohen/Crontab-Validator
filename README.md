# Crontab-Validator
A Python script to validate the syntax of Crontab files

## Function
Validates the cron syntax of each line in a Crontab file and prints out informative messages notifying the user of any invalid lines.
Optionally checks for the existance of the files (or validity of unix commands) to be triggered.
This script could either be used in CLI or in code.

## Usage:
python validate_crontab.py <crontab_file_path> [--check-scripts] [--help]

Arguments:
  <crontab_file_path>   Path to the crontab file to validate.
  --check-scripts       Enable checking if scripts exist or commands are valid Unix/Linux commands.
  --help                Show this help message and exit.
