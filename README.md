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
