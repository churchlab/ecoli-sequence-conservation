# Ecoli Sequence Conservation
*Developing representation for per-nucleotide conservation across strains of E.
coli.*

## Strategy

1. Download a bunch of E. coli sources. This paper provides a good starting
point: <http://www.ncbi.nlm.nih.gov/pubmed/20623278>.  Specifically [Table
1](http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2974192/table/Tab1/). We use
BioPython to do this.

2. Gather the sequences the files with valid sequences (for now we ignore those
   that don't, for example the records that are the master record from a shotgun
   sequencing run and don't actually contain sequence data).

3. Run `progressiveMauve`.
