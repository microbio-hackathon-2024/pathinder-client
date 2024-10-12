import click
import requests
import getpass
import tempfile
import csv


KEYCLOAK_TOKEN_URL = "https://authentication-microbioinfo-hackathon.loculus.org/realms/loculus/protocol/openid-connect/token"
SUBMISSION_URL = "https://backend-microbioinfo-hackathon.loculus.org/salmonella/submit?groupId={group_id}&dataUseTermsType=OPEN"


def generate_placeholder_fasta(submission_ids: list[str]) -> str:
    """
    Generates a placeholder FASTA file for each submission ID with "NNN" as the sequence.
    """
    fasta_entries = []
    for submission_id in submission_ids:
        fasta_entries.append(f">{submission_id}")
        fasta_entries.append("NNN")  # Placeholder sequence
    return "\n".join(fasta_entries)


def get_submission_ids_from_tsv(file_path: str) -> list[str]:
    """
    Reads a TSV file and extracts submission IDs by parsing the "submissionId" column.
    """
    submission_ids = []
    with open(file_path, 'r') as tsv_file:
        reader = csv.DictReader(tsv_file, delimiter='\t')

        # Check if "submissionId" exists in the header
        if 'submissionId' not in reader.fieldnames:
            raise ValueError('Error: "submissionId" column not found in the TSV file.')

        # Extract submission IDs from the "submissionId" column
        for row in reader:
            submission_ids.append(row['submissionId'])

    return submission_ids


def ask_for_password() -> str:
    """
    Prompt the user for a password securely (without echoing the input).
    """
    return getpass.getpass(prompt="Enter your password: ")


def get_loculus_authentication_token(username: str, password: str) -> str:
    """
    Sends a request to the Keycloak authentication server to obtain a token.
    """
    response = requests.post(
        KEYCLOAK_TOKEN_URL,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'username': username,
            'password': password,
            'grant_type': 'password',
            'client_id': 'backend-client'
        }
    )

    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        raise Exception(f"Error: Unable to authenticate. Status code: {response.status_code}, Response: {response.text}")


def submit(authentication_token: str, group_id: int, tsv_path: str, fasta_path: str) -> None:
    """
    Submits the metadata and sequence files to Loculus via a POST request.
    """
    submission_url = SUBMISSION_URL.format(group_id=group_id)

    with open(tsv_path, 'rb') as tsv_file, open(fasta_path, 'rb') as fasta_file:
        response = requests.post(
            submission_url,
            headers={
                'Authorization': f'Bearer {authentication_token}',
                'accept': 'application/json'
            },
            files={
                'metadataFile': tsv_file,
                'sequenceFile': fasta_file
            }
        )

    if response.status_code == 200:
        print("Upload successful.")
        print("You can approve the upload for release at:\n\nhttps://microbioinfo-hackathon.loculus.org/salmonella/submission/1/review")
    else:
        raise Exception(f"Error: Unable to submit. Status code: {response.status_code}, Response: {response.text}")


@click.command()
@click.option('--input', required=True, help='Path to the input TSV file')
@click.option('--group-id', required=True, type=int, help='The ID of the group for which you are submitting')
@click.option('--username', required=True, help='Your username')
def main(input: str, group_id: int, username: str):
    password = ask_for_password()
    authentication_token = get_loculus_authentication_token(username, password)
    submission_ids = get_submission_ids_from_tsv(input)
    placeholder_fasta_str = generate_placeholder_fasta(submission_ids)

    # Write the placeholder FASTA to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as fasta_file:
        fasta_file.write(placeholder_fasta_str.encode('utf-8'))
        placeholder_tmp_path = fasta_file.name

    submit(authentication_token, group_id, input, placeholder_tmp_path)


if __name__ == "__main__":
    main()
