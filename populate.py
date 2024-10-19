import os
from query.sequence_align import MLSType
from Hashing import generate_tsv
from submit import ask_for_password, get_loculus_authentication_token, get_submission_ids_from_tsv, generate_placeholder_fasta
import random
from submit import submit as submit_main
import tempfile
from datetime import datetime, timedelta


def random_date_within_last_six_months():
    today = datetime.today()
    six_months_ago = today - timedelta(days=6*30)
    random_date = six_months_ago + (today - six_months_ago) * random.random()
    return random_date.strftime('%Y-%m-%d')

def process_fasta_file(file_path):
    # Add your processing logic here
    print(f"Processing {file_path}")
    args = ["--refAllele", 'test/cgMLST_v2_ref.fasta', '--genome', file_path, "--unique_key", os.path.basename(file_path).split('.')[0]]
    mlst_type = MLSType(args) # -i/--genome, -r/--refAllele, -k/--unique_key
    with open('temp_mlst_type.txt', 'w') as temp_file:
        temp_file.write(mlst_type)
    countries = ['USA', 'UK', 'Germany', 'France', 'Italy', 'Spain', 'China', 'Japan', 'Australia']
    random_country = random.choice(countries)
    print(f"Selected country: {random_country}")

    collection_date = random_date_within_last_six_months()
    print(f"Selected collection date: {collection_date}")

    generate_tsv('temp_mlst_type.txt', 'output.tsv', os.path.basename(file_path).split('.')[0], collection_date, random_country)
    with open('output.tsv', 'r') as tsv_file:
        lines = tsv_file.readlines()
        if len(lines) > 1:
            second_line = lines[1].strip()
    return second_line

    


def main():
    folder_path = '/Users/nfareed/code/pathinder-client/sal_review'
    all_tsv_out = []
    if not os.path.exists('all_tsv_out.tsv') or True:
        for filename in os.listdir(folder_path):
            if filename.endswith('.fasta'):
                file_path = os.path.join(folder_path, filename)
                all_tsv_out.append(process_fasta_file(file_path))
                # write all_tsv_out to a file . headers are submissionId	collectionDate	location	profileHash 
                with open('all_tsv_out.tsv', 'w') as tsv_file:
                    tsv_file.write('submissionId\tcollectionDate\tlocation\tprofileHash\n')
                    for line in all_tsv_out:
                        tsv_file.write(line + '\n')
    password = ask_for_password()
    authentication_token = get_loculus_authentication_token('happykhan', password)
    submission_ids = get_submission_ids_from_tsv('all_tsv_out.tsv')
    placeholder_fasta_str = generate_placeholder_fasta(submission_ids)

    # Write the placeholder FASTA to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".fasta") as fasta_file:
        fasta_file.write(placeholder_fasta_str.encode('utf-8'))
        placeholder_tmp_path = fasta_file.name

    submit_main(authentication_token, 1, 'all_tsv_out.tsv', placeholder_tmp_path)



if __name__ == "__main__":
    main()