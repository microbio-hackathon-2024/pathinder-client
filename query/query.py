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


def find(query: set[str], database: list[SequenceEntry], min_proportion_matched: float) -> list[(SequenceEntry, float)]:
    matched: list[(SequenceEntry, float)] = []
    for database_entry in database:
        proportion_matched = match(query, database_entry.profile_hash)
        if proportion_matched >= min_proportion_matched:
            matched.append((database_entry, proportion_matched))
    return matched


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


@click.command()
@click.option('--hash-file', required=True, help='Path to a file with a comma-separated list of hashes')
@click.option(
    '--min-proportion-matched',
    default=0.95,
    type=float,
    help='The minimal proportion of the queried hashes that match the entry in the database')
def main(hash_file: str, min_proportion_matched: float):
    print('Querying Patinder data with a minimal matching proportion of {:.2f}%'.format(min_proportion_matched * 100))
    query = read_hashes_from_file(hash_file)
    database = download_from_loculus()
    print('Total number of sequences in Patinder: {}'.format(len(database)))
    matched = find(query, database, min_proportion_matched)
    print('{} sequences match the request'.format(len(matched)))
    print_matched_entries(matched)


if __name__ == '__main__':
    main()
