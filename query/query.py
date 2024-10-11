import click
import requests
import csv
from dataclasses import dataclass

loculus_host = 'https://lapis-microbioinfo-hackathon.loculus.org/salmonella'

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
    query_url = loculus_host + ('/sample/details?dataFormat=tsv'
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


def find(query: set[str], database: list[SequenceEntry], min_proportion_matched: float) -> list[SequenceEntry]:
    matched: list[SequenceEntry] = []
    for database_entry in database:
        if match(query, database_entry.profile_hash, min_proportion_matched):
            matched.append(database_entry)
    return matched


def match(query: set[str], database_entry_hashes: set[str], min_proportion_matched: float) -> bool:
    matched_hashes = query.intersection(database_entry_hashes)
    number_matched = len(matched_hashes)
    proportion_matched = number_matched / len(query)
    return proportion_matched >= min_proportion_matched


@click.command()
@click.option('--hash-file', required=True, help='Path to a file with a comma-separated list of hashes')
@click.option(
    '--min-proportion-matched',
    default=0.95,
    type=float,
    help='The minimal proportion of the queried hashes that match the entry in the database')
def main(hash_file: str, min_proportion_matched: float):
    print(min_proportion_matched)
    query = read_hashes_from_file(hash_file)
    database = download_from_loculus()
    matched = find(query, database, min_proportion_matched)
    print(len(database))
    for entry in matched:
        print(entry.submission_id)


if __name__ == '__main__':
    main()
