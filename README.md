# repeatmasker

TAFFISH app for [RepeatMasker](https://www.repeatmasker.org/), a widely used
tool for screening DNA sequences for interspersed repeats and low-complexity
DNA.

## Package Identity

- name: `repeatmasker`
- command: `taf-repeatmasker`
- version: `4.2.3-r3`
- kind: `tool`
- image: `ghcr.io/taffish/repeatmasker:4.2.3-r3`
- upstream: RepeatMasker `4.2.3`
- runtime version: `RepeatMasker version 4.2.3`
- default command: `RepeatMasker`
- default search engine: `rmblast`
- native platform: `linux/amd64`

The image is configured non-interactively with RMBlast, TRF, HMMER, and small
UCSC helper tools used by RepeatMasker utilities. `PAGER=cat` is set so
upstream RepeatMasker help prints and exits instead of entering `more`. The app
is intended for offline custom-library runs and for Dfam/FamDB runs when users
provide the required database partitions.

## Install

```sh
taf install repeatmasker
```

## Usage

TAFFISH wrapper help:

```sh
taf-repeatmasker --help
taf-repeatmasker --version
taf-repeatmasker --compile
```

Upstream RepeatMasker help and version:

```sh
taf-repeatmasker -- -help
taf-repeatmasker -- --help
taf-repeatmasker -- -v
taf-repeatmasker RepeatMasker -v
```

Run with a custom repeat library:

```sh
taf-repeatmasker -pa 8 -engine rmblast -lib repeats.fa -dir rm-out genome.fa
```

Run bundled utility commands through command mode:

```sh
taf-repeatmasker famdb.py -i /opt/RepeatMasker/Libraries/famdb info
taf-repeatmasker rmOutToGFF3.pl genome.fa.out > genome.fa.out.gff
taf-repeatmasker buildSummary.pl genome.fa.out > genome.fa.tbl
taf-repeatmasker rmToTrackHub.pl -out genome.fa.out -genome hg38
taf-repeatmasker rmblastn -version
taf-repeatmasker trf -v
```

## Wrapper Semantics

`taf-repeatmasker` defaults to the upstream `RepeatMasker` command. Because
RepeatMasker uses single-dash options such as `-pa`, `-lib`, `-species`, and
`-dir`, normal option-led calls are passed directly to RepeatMasker.

Command mode remains enabled. If the first argument is another executable name,
TAFFISH runs that command in the same configured container:

```sh
taf-repeatmasker famdb.py --help
taf-repeatmasker ProcessRepeats -help
taf-repeatmasker rmblastn -version
```

## Runtime Contents

The image installs the official `RepeatMasker-4.2.3.tar.gz` release, copies
RMBlast from the `ghcr.io/taffish/rmblast:2.17.1-r1` app image, and installs
pinned UCSC command-line helper binaries needed by RepeatMasker utility
scripts. The Dockerfile verifies the RepeatMasker and UCSC helper checksums:

```text
RepeatMasker-4.2.3.tar.gz
832e2b22aef6763ef7d5dd2771eef22f7dd8b9738bea0e1d81295aa511b61e6a

twoBitInfo
fca5427e1aedd00be0d32117420010c9162d442562c83305b2d3e3c8e6cebe71

bedToBigBed
73e10feef3a685304d71c840058ae9a5113bdc4e134f161d3913cfebc5a2ec24
```

The RMBlast source checksum is enforced by the separate `rmblast` taf-app:

```text
rmblast-2.17.1+-x64-linux.tar.gz
9ddf0ffdc01f3dd7bf62bbcb01516757b1e732e54674e81d93a7c143157aa527
```

Packaged RepeatMasker commands and utilities include:

- `RepeatMasker`
- `ProcessRepeats`
- `RepeatProteinMask`
- `DupMasker`
- `famdb.py`
- `RM2Bed.py`
- `rmOutToGFF3.pl`
- `buildSummary.pl`
- `calcDivergenceFromAlign.pl`
- `createRepeatLandscape.pl`
- `rmToTrackHub.pl`
- `maskFile.pl`
- `buildRMLibFromEMBL.pl`

Search/runtime tools include:

- RMBlast `2.17.1+` (`rmblastn`, `makeblastdb`, and companion BLAST+ tools)
- TRF `4.09.1` from Debian
- HMMER `3.3.2` from Debian
- UCSC `twoBitInfo` and `bedToBigBed` helper binaries
- Perl, Python 3, Python h5py, curl, gzip, tar, and required shared libraries

`BLAST_USAGE_REPORT=false` is set by default so RMBlast does not report usage
statistics during local TAFFISH runs. `PAGER=cat` is set by default so
RepeatMasker help remains non-interactive and works predictably in terminals,
pipelines, CI, and TAFFISH flow contexts.

## Libraries And Data

The official RepeatMasker `4.2.3` tarball includes the Dfam `3.9` root FamDB
partition:

```text
/opt/RepeatMasker/Libraries/famdb/dfam39_full.0.h5
```

This root partition is required metadata and contains a small set of root-level
families. It is not the full Dfam database. Full species or clade coverage
requires adding matching Dfam `3.9` FamDB partitions under
`/opt/RepeatMasker/Libraries/famdb`, or using `-lib` with a custom FASTA repeat
library.

RepBase is not included. RepBase RepeatMasker Edition and later RepBase data
must be obtained by users under their own authorization and used according to
their license terms.

## Platform

This app is native `linux/amd64` only because it uses the official RMBlast x64
Linux binary. `src/main.taf` asks Docker and Podman to run with
`--platform linux/amd64`. On arm64 hosts this is amd64 emulation, not native
arm64 support. Apptainer behavior depends on the host's ability to run amd64
containers.

## Boundaries

This core image does not include:

- full Dfam partitions beyond the root partition included upstream
- RepBase
- `cross_match`
- ABBLAST/WUBlast
- a from-source RMBlast build inside this Dockerfile; it depends on the
  `ghcr.io/taffish/rmblast:2.17.1-r1` app image at build time
- Entrez Direct or online database download workflows, except utility scripts
  such as `rmToTrackHub.pl` can still use `curl` to fetch UCSC chromosome sizes
  when users request those workflows

The smoke tests validate the configured program stack and small offline
functional runs. They do not substitute for full biological validation on large
genomes or species-specific repeat libraries.

## License Boundary

The TAFFISH app packaging files are licensed under Apache-2.0. The packaged upstream RepeatMasker software is covered by: OSL-2.1 with bundled Dfam/FamDB CC0 code/data notices, RMBlast/NCBI components, and UCSC command-line utilities. Bundled third-party components, datasets, models, and external resources keep their own license terms.

## License And Citation

RepeatMasker open-4.0 and later are distributed under the Open Software License
v2.1. The bundled FamDB code is documented by upstream as CC0. RMBlast and NCBI
BLAST+ notices are included through the RMBlast distribution. UCSC
`twoBitInfo` and `bedToBigBed` are included as command-line utilities for
RepeatMasker helper-script compatibility; consult the UCSC Genome Browser/Kent
source terms for those tools.

Please refer to:

- Smit, AFA, Hubley, R. & Green, P. `RepeatMasker` at
  <https://www.repeatmasker.org/>
- Dfam Consortium for Dfam/FamDB data
- Camacho et al. 2009 for BLAST+. DOI: `10.1186/1471-2105-10-421`;
  PMID: `20003500`

## Smoke Coverage

Smoke tests cover:

- RepeatMasker, RMBlast, TRF, HMMER, and usage-reporting version/state checks.
- RepeatMasker non-interactive `--help` and ProcessRepeats help.
- FamDB info for the included Dfam 3.9 root partition.
- RepeatMasker configuration paths for RMBlast, TRF, HMMER, and default engine.
- A tiny offline `RepeatMasker -lib` run producing `.out` and `.masked`.
- A tiny offline `RepeatMasker -gff -lib` run producing `.out.gff`.
- Utility conversion/summary scripts on a tiny real RepeatMasker `.out` file,
  including the UCSC `twoBitInfo` helper required by `buildSummary.pl`.
