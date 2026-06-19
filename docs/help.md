taf-repeatmasker 4.2.4-r1

RepeatMasker screens DNA FASTA sequences for interspersed repeats and
low-complexity DNA. This app defaults to upstream RepeatMasker through a small
entrypoint and includes RMBlast, TRF, HMMER, FamDB tools, UCSC helpers, and
RepeatMasker utilities.

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
  taf-repeatmasker -- --help
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
  taf-repeatmasker famdb.py --help
  taf-repeatmasker download_dfam.py --help

Common custom-library workflow:
  taf-repeatmasker -pa 8 -engine rmblast -lib repeats.fa -dir rm-out genome.fa

Common Dfam/FamDB workflow:
  taf-repeatmasker famdb.py -i /opt/RepeatMasker/Libraries/famdb info
  taf-repeatmasker -pa 8 -engine rmblast -species "Homo sapiens" genome.fa

Important data note:
  RepeatMasker 4.2.4 no longer bundles Dfam data. This app packages FamDB
  3.0.0 and configures FamDB itself to read Dfam component files from:
    /opt/RepeatMasker/Libraries/famdb

  Custom-library runs with -lib do not need Dfam data. To keep that mode
  working, the static RepeatMasker config leaves FamDB disabled when no .h5
  files are present. Species or clade runs with -species require Dfam 4.x
  FamDB component files; when mounted .h5 files exist, the default entrypoint
  enables FamDB before running RepeatMasker. The wrapper auto-mounts an
  existing local directory when one of these paths exists:
    TAFFISH_REPEATMASKER_FAMDB_PATH
    ~/.local/share/taffish/databases/repeatmasker/dfam4
    /usr/local/share/taffish/databases/repeatmasker/dfam4
    /opt/taffish/databases/repeatmasker/dfam4

  To prepare personal data, create and enter the database root, then run:
    mkdir -p ~/.local/share/taffish/databases/repeatmasker/dfam4
    cd ~/.local/share/taffish/databases/repeatmasker
    taf-repeatmasker download_dfam.py -o "$PWD/dfam4"

  RepBase is not included.

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
  RepeatMasker, taf-repeatmasker-entrypoint, ProcessRepeats,
  RepeatProteinMask, DupMasker, famdb.py, download_dfam.py, RM2Bed.py,
  rmOutToGFF3.pl, buildSummary.pl, calcDivergenceFromAlign.pl,
  createRepeatLandscape.pl, rmToTrackHub.pl, maskFile.pl,
  buildRMLibFromEMBL.pl, rmblastn, makeblastdb, trf, nhmmer, hmmsearch,
  twoBitInfo, bedToBigBed.

Outputs:
  Typical runs write .out repeat annotations, .masked FASTA, .tbl summaries,
  optional .align alignments, .cat files, and optional .gff output.

Help behavior:
  Upstream RepeatMasker normally uses a pager for help. This app sets PAGER=cat
  so RepeatMasker -help and --help print directly and exit in non-interactive
  TAFFISH, Docker, Podman, CI, and flow contexts.

Platform:
  Native platform is linux/amd64 only because this app uses the official
  RMBlast x64 Linux binary. Docker and Podman request --platform linux/amd64;
  arm64 hosts use amd64 emulation, not native arm64 execution.

License:
  TAFFISH app packaging: Apache-2.0.
  Upstream RepeatMasker: OSL-2.1.
  Packaged FamDB code and Dfam data notices: CC0.
  RMBlast/NCBI components, UCSC utilities, external Dfam components,
  RepBase, and user-provided resources keep their own license terms.

Boundaries:
  This app does not include Dfam component data, RepBase, cross_match, or
  ABBLAST. Dfam download is only performed when users explicitly run
  download_dfam.py. Utility network fetches such as UCSC chrom.sizes downloads
  and large genome-scale scientific validation are outside smoke tests.
