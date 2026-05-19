taf-repeatmasker 4.2.3-r1

RepeatMasker screens DNA FASTA sequences for interspersed repeats and
low-complexity DNA. This app defaults to upstream RepeatMasker and includes
RMBlast, TRF, HMMER, FamDB tools, UCSC helpers, and RepeatMasker utilities.

Usage:
  taf-repeatmasker [-h | --help]
  taf-repeatmasker [-v | --version]
  taf-repeatmasker [REPEATMASKER_OPTIONS...] <seq.fa>
  taf-repeatmasker -- [REPEATMASKER_ARGS...]
  taf-repeatmasker COMMAND [ARGS...]
  taf-repeatmasker --compile [ARGS...]

Wrapper options:
  -h, --help       Show this TAFFISH app help
  -v, --version    Show TAFFISH package version
  --compile        Print generated shell code instead of running it
  --               Stop wrapper option parsing and pass following args to
                   RepeatMasker

Default upstream command:
  taf-repeatmasker -- -help
  taf-repeatmasker -- -v
  taf-repeatmasker -pa 4 -engine rmblast -lib repeats.fa genome.fa

Command mode:
  taf-repeatmasker RepeatMasker -v
  taf-repeatmasker famdb.py -i /opt/RepeatMasker/Libraries/famdb info
  taf-repeatmasker rmOutToGFF3.pl genome.fa.out > genome.fa.out.gff
  taf-repeatmasker buildSummary.pl genome.fa.out > genome.fa.tbl
  taf-repeatmasker rmToTrackHub.pl -out genome.fa.out -genome hg38
  taf-repeatmasker rmblastn -version
  taf-repeatmasker trf -v

Common custom-library workflow:
  taf-repeatmasker -pa 8 -engine rmblast -lib repeats.fa -dir rm-out genome.fa

Common Dfam/FamDB workflow:
  taf-repeatmasker famdb.py -i /opt/RepeatMasker/Libraries/famdb info
  taf-repeatmasker -pa 8 -engine rmblast -species "Homo sapiens" genome.fa

Important data note:
  The official RepeatMasker 4.2.3 package includes the Dfam 3.9 root partition
  only. That root partition is required metadata and contains a small number of
  root-level families. Full species/clade coverage requires adding matching
  Dfam FamDB partitions under /opt/RepeatMasker/Libraries/famdb or using a
  custom FASTA library with -lib. RepBase is not included.

Common options:
  -pa INT            Parallel batch jobs
  -engine NAME       rmblast, hmmer, crossmatch, wublast, abblast, or ncbi
  -lib FILE          Use a custom repeat library FASTA
  -species NAME      Use installed Dfam/RepBase libraries for a species/clade
  -dir DIR           Write output files to DIR
  -gff               Also write GFF output
  -xsmall            Soft-mask repeats to lowercase
  -nolow             Do not mask simple repeats/low complexity
  -norna             Do not mask small RNA genes
  -e VALUE           Search e-value cutoff

Packaged commands:
  RepeatMasker, ProcessRepeats, RepeatProteinMask, DupMasker, famdb.py,
  RM2Bed.py, rmOutToGFF3.pl, buildSummary.pl, calcDivergenceFromAlign.pl,
  createRepeatLandscape.pl, rmToTrackHub.pl, maskFile.pl,
  buildRMLibFromEMBL.pl, rmblastn, makeblastdb, trf, nhmmer, hmmsearch,
  twoBitInfo, bedToBigBed.

Outputs:
  Typical runs write .out repeat annotations, .masked FASTA, .tbl summaries,
  optional .align alignments, .cat files, and optional .gff output.

Platform:
  Native platform is linux/amd64 only because this app uses the official
  RMBlast x64 Linux binary. Docker and Podman request --platform linux/amd64;
  arm64 hosts use amd64 emulation, not native arm64 execution.

Boundaries:
  This app does not include full Dfam partitions, RepBase, cross_match, or
  ABBLAST. Utility network fetches such as UCSC chrom.sizes downloads and
  large genome-scale scientific validation are outside smoke tests.
