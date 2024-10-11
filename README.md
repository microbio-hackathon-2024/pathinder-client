# pathinder-client

pathinder (pathogen-tinder) is a matchmaking software for researchers to find others who have genomes similar to theirs. It is a project started during the [Microbiome Bioinformatics Hackathon 2024](https://github.com/microbio-hackathon-2024/).

The process is to take a assembled genome, extract seqeunces for a fixed set of marker genes and use a hashing function to covert  it into a vector of short strings. This string is then compared to other strings in a database to find similar genomes. The similarity is based on the Jaccard index (or hamming distance) of the query profile.

Similar software see https://github.com/lskatz/hashest


## Website and Backend (Loculus)

The website of Patinder is at https://microbioinfo-hackathon.loculus.org/.

We use the [Loculus software](https://loculus.org) to build the website and backend. The config can be found at https://github.com/loculus-project/loculus/pull/2989.
