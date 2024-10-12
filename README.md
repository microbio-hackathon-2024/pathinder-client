# pathinder-client

pathinder (pathogen-tinder) is a matchmaking software for researchers to find others who have genomes similar to theirs. It is a project started during the [Microbiome Bioinformatics Hackathon 2024](https://github.com/microbio-hackathon-2024/).

The process is to take a assembled genome, extract seqeunces for a fixed set of marker genes and use a hashing function to covert  it into a vector of short strings. This string is then compared to other strings in a database to find similar genomes. The similarity is based on the Jaccard index (or hamming distance) of the query profile.

In principle, the marker gene set can be flexible, but for bacterial pathogens, cgMLST has proven to be an effective approach for developing such sets. cgMLST schemes are built around a community-agreed set of gene loci shared across all strains of a species. For each locus, a database of validated allele sequences is maintained, with a unique code assigned to each allele. A distinct "ST" (sequence type) code is then generated based on the unique combination of alleles. The cgMLST schemes supported by Pathogenwatch are provided by PubMLST, the Pasteur Institute, Enterobase, and the cgMLST.org Nomenclature Server.

Similar software:

*  https://github.com/lskatz/hashest
*  https://github.com/davideyre/hash-cgmlst 


## Website and Backend (Loculus)

The website of Patinder is at https://microbioinfo-hackathon.loculus.org/.

We use the [Loculus software](https://loculus.org) to build the website and backend. The config can be found at https://github.com/loculus-project/loculus/pull/2989.

## Upload

The steps to generate and upload a hash profile are:

1. Go to https://microbioinfo-hackathon.loculus.org/ and create an account and a submitting group (if you haven't yet).
2. Call the alleles
3. Generate the hash profile
4. Submit

### Allele caller 

Allele caller is MLSTType from EToki. It is a simple script that takes a fasta file and a reference fasta file and aligns the sequences to the reference. It then extracts the allele number from the reference and writes it to a file. 

[Etoki](https://github.com/zheminzhou/EToKi) is all the methods from EnteroBase. It uses blast and usearch for retriving the allele  sequences. 

```
python query/sequence_align.py -i test/SAL_QD2830AA_AS.result.fasta -r test/cgMLST_v2_ref.fasta -k SAL_QD2830AA_AS -o test/TEST.OUT
``` 

### Hash profile generation

Use the [Hashing.py](./Hashing.py) script to generate the hash profile:

```
python Hashing.py \
  --input test/TEST.OUT \
  --out test/TEST.tsv \
  --submission_id <an ID for your entry> \
  --date <collection date> \
  --location <collection location>
```

### Submit

Use the [submit.py](./submit.py) script to submit your data to Pathinder:

```
python submit.py \
  --input test/TEST.tsv \
  --group-id <your submitting group ID> \
  --username <your username>
```

This script will upload the data. Afterward, you have an opportunity to check the upload and approve it. You can find the review page at:

https://microbioinfo-hackathon.loculus.org/salmonella/submission/


## TODO

* Client to have a list of mirrored servers to query. 
* Client can fetch assemblies from all servers to compare them locally.
* Client can upload profiles/assemblies to servers.
* Automatic updating of the "public" server that has SRA/ENA data.
* League table of user submissions 
* 


## Worked example - a query.

Allele calling:

```
python query/sequence_align.py -i  some/SAL_BA2933AA_AS.scaffold.fasta  -r test/cgMLST_v2_ref.fasta -k SAL_BA2933AA_AS -o some_test
```

Hashing the alleles:

```
python Hashing.py -i some_test  -n some_test -d 2024 -l here  -o some_test_hash                 
Output written to: some_test_hash
```

Doing a query 

```
python query/query.py --hash-file some_test_hash 
Querying Patinder data with a minimal matching proportion of 95.00%
Total number of sequences in Patinder: 114
3 sequences match the request
SAL_BA2933AA_AS (2024-06-30, Spain), matched 99.97%, submitted by ASM-Hackathon (https://microbioinfo-hackathon.loculus.org/group/1)
SAL_BA3624AA_AS (2024-05-01, USA), matched 96.15%, submitted by ASM-Hackathon (https://microbioinfo-hackathon.loculus.org/group/1)
SAL_BA5451AA_AS (2024-05-09, Spain), matched 96.08%, submitted by ASM-Hackathon (https://microbioinfo-hackathon.loculus.org/group/1)```

