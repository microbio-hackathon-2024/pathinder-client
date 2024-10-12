import argparse
from Bio import SeqIO
import hashlib
import re
import pandas as pd

# Function to compute MD5 hash for a given sequence
def md5_hash(sequence):
    return hashlib.md5(sequence.encode()).hexdigest()

# Function to normalize the DNA sequence
def normalize_sequence(sequence):
    # Convert to lowercase
    sequence = sequence.lower()
    # Replace non-ACGT characters with 'n'
    sequence = re.sub(r'[^acgt]', 'n', sequence)
    return sequence

# Function to process FASTA file and generate the desired TSV output
def generate_tsv(input_fasta, output_tsv, submission_id, collection_date, location):
    # List to store all computed hashes
    hashes = []
    # Read the FASTA file and compute the hash for each gene/sequence
    with open(input_fasta, "r") as fasta_file:
        for line in fasta_file:
            if not line.startswith(">"):
                sequence = line.strip()
                normalized_sequence = normalize_sequence(sequence)  # Normalize the sequence
                hash_value = md5_hash(normalized_sequence)  # Compute MD5 hash
                hashes.append(hash_value)  # Store the hash

    # Combine all hashes into a single string separated by commas
    profile_hash = ",".join(hashes)

    # Create a DataFrame for the output
    data = {
        "submissionId": [submission_id],
        "collectionDate": [collection_date],
        "location": [location],
        "profileHash": [profile_hash]
    }

    df = pd.DataFrame(data)

    # Write the DataFrame to a TSV file
    df.to_csv(output_tsv, sep="\t", index=False)
    print(f"Output written to: {output_tsv}")

# Main function to handle command-line arguments and call the generate_tsv function
def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Generate TSV output with MD5 hashes from a FASTA file.")

    # Define command-line arguments
    parser.add_argument("-i", "--input", required=True, help="Path to the input FASTA file.")
    parser.add_argument("-o", "--output", required=True, help="Path to the output TSV file.")
    parser.add_argument("-n", "--submission_id", required=True, help="Submission ID for the sequences.")
    parser.add_argument("-d", "--date", required=True, help="Collection date in ISO format (YYYY-MM-DD).")
    parser.add_argument("-l", "--location", required=True, help="Location where the sequences were collected.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Call the generate_tsv function with parsed arguments
    generate_tsv(args.input, args.output, args.submission_id, args.date, args.location)

# If this script is run directly, execute the main function
if __name__ == "__main__":
    main()