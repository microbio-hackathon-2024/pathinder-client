import click
import requests
import csv
from dataclasses import dataclass


loculus_website = 'https://microbioinfo-hackathon.loculus.org'
loculus_lapis = 'https://lapis-microbioinfo-hackathon.loculus.org/salmonella'


@dataclass
class SequenceEntry:
    submission_id: str
    group_name: str
    group_id: str
    collection_date: str
    location: str
    profile_hash: set[str]


def read_hashes_from_file(file_path: str) -> set[str]:
    with open(file_path, 'r') as file:
        hashes = file.read().strip().split(',')
    return set(hashes)


def download_from_loculus() -> list[SequenceEntry]:
    query_url = loculus_lapis + ('/sample/details?dataFormat=tsv'
                                '&fields=submissionId,groupName,groupId,collectionDate,location,profileHash')
    response = requests.get(query_url)

    if response.status_code == 200:
        tsv_data = response.text
        sequence_entries = []

        reader = csv.DictReader(tsv_data.splitlines(), delimiter='\t')
        for row in reader:
            entry = SequenceEntry(
                submission_id=row['submissionId'],
                group_name=row['groupName'],
                group_id=row['groupId'],
                collection_date=row['collectionDate'],
                location=row['location'],
                profile_hash=set(row['profileHash'].split(','))
            )
            sequence_entries.append(entry)

        return sequence_entries
    else:
        print(f"Error: Unable to download data from loculus. Status code {response.status_code}")
        return []


def find(query: set[str], database: list[SequenceEntry], min_proportion_matched: float, comparison_method) -> list[(SequenceEntry, float)]:
    matched: list[(SequenceEntry, float)] = []
    for database_entry in database:
        proportion_matched = comparison_method(query, database_entry.profile_hash)
        if proportion_matched >= min_proportion_matched:
            matched.append((database_entry, proportion_matched))
    return matched


def jacquard_similarity(query: set[str], database_entry_hashes: set[str]) -> float:
    union = query.union(database_entry_hashes)
    intersection = query.intersection(database_entry_hashes)
    return len(intersection) / len(union)

def match(query: set[str], database_entry_hashes: set[str]) -> float:
    matched_hashes = query.intersection(database_entry_hashes)
    number_matched = len(matched_hashes)
    return number_matched / len(query)


def print_matched_entries(matched: list[(SequenceEntry, float)]):
    matched_sorted = sorted(matched, key=lambda x: x[1], reverse=True)
    for entry, proportion_match in matched_sorted:
        print('{} ({}, {}), matched {:.2f}%, submitted by {} ({}/group/{})'.format(
            entry.submission_id,
            entry.collection_date,
            entry.location,
            proportion_match * 100,
            entry.group_name,
            loculus_website,
            entry.group_id
        ))


def write_distance_matrix_to_tsv(query: set[str], database: list[SequenceEntry], comparison_method, output_file: str,
                                 query_name: str):
    # Combine the query with the database into a single list for all-vs-all comparison
    full_set = [(query_name, query)] + [(entry.submission_id, entry.profile_hash) for entry in database]

    # Create a distance matrix for all-vs-all comparison
    num_entries = len(full_set)
    matrix = [[0.0 for _ in range(num_entries)] for _ in range(num_entries)]

    # Fill the matrix with distances
    for i in range(num_entries):
        for j in range(i, num_entries):  # Symmetric matrix, so no need to compute j < i
            if i == j:
                matrix[i][j] = 0.0  # Distance from a sequence to itself is 0
            else:
                similarity = comparison_method(full_set[i][1], full_set[j][1])
                distance = 1 - similarity  # Convert similarity to distance
                matrix[i][j] = distance
                matrix[j][i] = distance  # Symmetric

    # Open a TSV file for writing
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')

        # Write the header (including the query as the first name)
        header = [name for name, _ in full_set]
        writer.writerow([''] + header)  # Empty first cell for alignment

        # Write the matrix row by row
        for i, (name, _) in enumerate(full_set):
            row = [name] + ["{:.4f}".format(matrix[i][j]) for j in range(num_entries)]
            writer.writerow(row)

    print(f"All-vs-all distance matrix written to {output_file}")


@click.command()
@click.option('--hash-file', required=True, help='Path to a file with a comma-separated list of hashes')
@click.option(
    '--min-proportion-matched',
    default=0.95,
    type=float,
    help='The minimal proportion of the queried hashes that match the entry in the database')
@click.option(
    '--comparison-method',
    default='default',
    type=str,
    help='Comparison method [default, jacquard]')
@click.option(
    '--matrix-output',
    default=None,
    type=str,
    help='Path to the output TSV file for the distance matrix')

@click.option(
    '-n', '--query-name',
    default='QUERY',
    type=str,
    help='Name for the query isolate in the matrix outputs')

def main(hash_file: str, min_proportion_matched: float, comparison_method: str, matrix_output: str, query_name: str):
    print('Querying Patinder data with a minimal matching proportion of {:.2f}%'.format(min_proportion_matched * 100))
    query = read_hashes_from_file(hash_file)
    database = download_from_loculus()
    print('Total number of sequences in Patinder: {}'.format(len(database)))
    if comparison_method == 'jaccard':
        matched = find(query, database, min_proportion_matched, jacquard_similarity)
    else:   
        matched = find(query, database, min_proportion_matched, match)

    if matrix_output:
        if comparison_method == 'jaccard':
            write_distance_matrix_to_tsv(query, database, jacquard_similarity, matrix_output,query_name)
        else:
            write_distance_matrix_to_tsv(query, database, match, matrix_output,query_name)

    print('{} sequences match the request'.format(len(matched)))
    print_matched_entries(matched)


if __name__ == '__main__':
    main()
