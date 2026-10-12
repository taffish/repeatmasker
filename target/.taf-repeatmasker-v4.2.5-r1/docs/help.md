repeatmasker 4.2.5-r1

Purpose:
  Mask repeats in DNA FASTA using a custom library or prepared Dfam partitions.

Usage:
  taf-repeatmasker [RepeatMasker options] genome.fa
  taf-repeatmasker COMMAND [arguments]
  taf-repeatmasker --help                 TAFFISH usage
  taf-repeatmasker --version              Package version
  taf-repeatmasker -- --help              Upstream options
  taf-repeatmasker -- -v                  Upstream version
  taf-repeatmasker --compile [arguments]  Show generated shell command

Custom library (no Dfam download needed):
  mkdir -p rm-out
  taf-repeatmasker -pa 8 -engine rmblast -lib repeats.fa -a -gff \
    -dir rm-out genome.fa
  Use headers like >repeat_name#class/subclass in repeats.fa.

Common options:
  -pa N          Parallel jobs
  -lib FILE      Custom repeat consensus FASTA
  -species NAME  Species/clade in prepared Dfam data
  -dir DIR       Writable output directory; prefer a new one for each run
  -a -gff -html  Also produce alignments, GFF and offline alignment HTML
  -xsmall        Soft-mask to lowercase
  -nolow -norna  Skip low-complexity/small-RNA masking, respectively

Outputs and utilities:
  .out annotations, .masked FASTA, .tbl summary, optional .align and .out.gff.
  taf-repeatmasker RM2Bed.py rm-out/genome.fa.out rm-out/repeats.bed
  taf-repeatmasker rmOutToGFF3.pl rm-out/genome.fa.out > rm-out/repeats.gff3
  taf-repeatmasker calcDivergenceFromAlign.pl -s genome.divsum rm-out/genome.fa.align
  taf-repeatmasker taf-repeatmasker-landscape --div genome.divsum \
    --genome-size 3000000 --output landscape.html --title "'My repeat landscape'"
  Open landscape.html or rm-out/genome.fa.out.html locally; no network is needed.
  Alignment repeat-name links open the upstream website; HSP viewing stays offline.
  Landscape: class filter, bar details, CSV (all data), SVG (current chart/legend).
  Use your actual genome-size denominator; existing HTML needs explicit --force.
  Original createRepeatLandscape.pl remains available but requires Google/network.

Prepare Dfam 4.0 (online, explicitly selected members):
  mkdir -p "$HOME/.local/share/taffish/databases/repeatmasker"
  cd "$HOME/.local/share/taffish/databases/repeatmasker"
  export TAFFISH_REPEATMASKER_AUTO_MOUNT=0
  taf-repeatmasker taf-repeatmasker-dfam list
  taf-repeatmasker taf-repeatmasker-dfam install --db-root "$PWD/dfam4" \
    --part curated.consensus.0 --dry-run
  Repeat without --dry-run to install; add --part for additional members.
  unset TAFFISH_REPEATMASKER_AUTO_MOUNT
  taf-repeatmasker taf-repeatmasker-dfam verify --db-root /opt/RepeatMasker/Libraries/famdb
  taf-repeatmasker famdb.py info
  taf-repeatmasker -species human -dir rm-out genome.fa
  The root + example member download is about 89 MB; other partitions are larger.

Shared data:
  Admins can install once under /usr/local/share/taffish/databases/repeatmasker/dfam4
  or /opt/taffish/databases/repeatmasker/dfam4, using the same installer.
  Users need read/traverse access; ordinary users do not run the installer again.
  Discovery: TAFFISH_REPEATMASKER_FAMDB_PATH, personal path, /usr/local/share, /opt/taffish.
  Invalid/high-priority roots fail; set the override to another prepared root.
  TAFFISH_REPEATMASKER_AUTO_MOUNT=0 disables discovery, useful for custom -lib.
  Old loose .h5 folders need a new prepared root; keep the old files until migration.

Backend selection (same CLI/data/report commands):
  TAFFISH_CONTAINER_BACKEND=docker taf-repeatmasker -- -v
  TAFFISH_CONTAINER_BACKEND=podman taf-repeatmasker -- -v
  TAFFISH_CONTAINER_BACKEND=apptainer taf-repeatmasker -- -v
  Apptainer needs native amd64 Linux. Docker/Podman request amd64 automatically;
  ARM hosts need working amd64 emulation, not native ARM support.

Manual read-only DB mount (DB is an engine-visible prepared root):
  export TAFFISH_REPEATMASKER_AUTO_MOUNT=0
  DB=/absolute/path/dfam4
  TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="-v $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
  TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="-v $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
  TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
  unset TAFFISH_REPEATMASKER_AUTO_MOUNT

Troubleshooting:
  Annotation is offline: missing Dfam members are not automatically downloaded.
  Keep analysis FASTA paths free of spaces/shell-special characters (upstream limit).
  For helper paths with spaces, preserve literal quotes, e.g.
    --db-root "'/absolute/resource path/dfam4'" or --output "'report folder/view.html'"
  Use a single-word species alias, or preserve quotes: -species "'Homo sapiens'".
  Missing species: inspect famdb.py info, prepare required partitions in a new root.
  Interrupted install: retry the identical command; corrupt caches fail with a path.
  RepBase requires your own authorization and is not bundled. See README for details.
