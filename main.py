import argparse
import csv
import logging
import sys
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Pseudonymize a column in a CSV file using Faker.')
    parser.add_argument('input_file', help='Path to the input CSV file.')
    parser.add_argument('output_file', help='Path to the output CSV file.')
    parser.add_argument('column_name', help='Name of the column to pseudonymize.')
    parser.add_argument('--locale', default='en_US', help='Locale for Faker (default: en_US).')
    parser.add_argument('--seed', type=int, help='Seed for Faker\'s random number generator for reproducibility.')
    return parser

def pseudonymize_column(input_file, output_file, column_name, locale='en_US', seed=None):
    """
    Replaces values in a specified column of a CSV file with pseudonyms.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to the output CSV file.
        column_name (str): Name of the column to pseudonymize.
        locale (str, optional): Locale for Faker. Defaults to 'en_US'.
        seed (int, optional): Seed for Faker's random number generator. Defaults to None.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If the specified column name is not found in the CSV file.
        Exception: For other unhandled errors during file processing or pseudonym generation.
    """
    try:
        # Initialize Faker with locale and seed
        fake = Faker(locale)
        if seed:
            Faker.seed(seed)

        # Open input and output CSV files
        with open(input_file, 'r', newline='') as infile, \
             open(output_file, 'w', newline='') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Read header row
            header = next(reader)
            writer.writerow(header)

            # Find the column index
            try:
                column_index = header.index(column_name)
            except ValueError:
                raise ValueError(f"Column '{column_name}' not found in the CSV file.")

            # Process each row
            for row in reader:
                # Pseudonymize the specified column
                try:
                    original_value = row[column_index]
                    # Attempt to infer the data type and generate a suitable pseudonym
                    # Basic type inference and generation - can be extended for more types
                    if original_value.isdigit(): # Integer
                        row[column_index] = str(fake.random_int())
                    elif original_value.replace('.', '', 1).isdigit():  # Float
                        row[column_index] = str(fake.pyfloat())
                    else: # String
                        row[column_index] = fake.name() # Default pseudonymization to name
                except IndexError:
                     logging.warning(f"Row is shorter than expected. Skipping pseudonymization for this row.")
                
                writer.writerow(row)
        logging.info(f"Successfully pseudonymized column '{column_name}' in '{input_file}' and saved to '{output_file}'.")


    except FileNotFoundError:
        logging.error(f"Input file '{input_file}' not found.")
        raise
    except ValueError as e:
        logging.error(str(e))
        raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise

def main():
    """
    Main function to execute the pseudonymization process.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    try:
        pseudonymize_column(args.input_file, args.output_file, args.column_name, args.locale, args.seed)
    except (FileNotFoundError, ValueError) as e:
        logging.error(str(e))
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    
    print("Data pseudonymization completed successfully.")

if __name__ == "__main__":
    # Example usage
    # python main.py input.csv output.csv sensitive_column --locale fr_FR --seed 42

    # Create a dummy input.csv for demonstration
    # echo "name,age,city" > input.csv
    # echo "Alice,30,New York" >> input.csv
    # echo "Bob,25,London" >> input.csv

    main()