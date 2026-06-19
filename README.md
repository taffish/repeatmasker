# repeatmasker

TAFFISH app for [RepeatMasker](https://www.repeatmasker.org/), a widely used
tool for screening DNA sequences for interspersed repeats and low-complexity
DNA.

## Package Identity

- name: `repeatmasker`
- command: `taf-repeatmasker`
- version: `4.2.4-r1`
- kind: `tool`
- image: `ghcr.io/taffish/repeatmasker:4.2.4-r1`
- upstream: RepeatMasker `4.2.4`
- runtime version: `RepeatMasker version 4.2.4`
- default command: `RepeatMasker` through `taf-repeatmasker-entrypoint`
- default search engine: `rmblast`
- native platform: `linux/amd64`

The image is configured non-interactively with RMBlast, TRF, HMMER, and small
UCSC helper tools used by RepeatMasker utilities. It also packages FamDB 3.0.0.
`PAGER=cat` is set so upstream RepeatMasker help prints and exits instead of
entering `more`. The app is intended for offline custom-library runs and for
Dfam/FamDB runs when users provide the required Dfam component files.

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
taf-repeatmasker famdb.py --help
taf-repeatmasker download_dfam.py --help
```

## Wrapper Semantics

`taf-repeatmasker` defaults to a small TAFFISH entrypoint that runs upstream
`RepeatMasker`. Because RepeatMasker uses single-dash options such as `-pa`,
`-lib`, `-species`, and `-dir`, normal option-led calls are passed directly to
that default entrypoint.

RepeatMasker 4.2.4 fails early if FamDB is configured but no Dfam `.h5` files
are present. To keep custom-library `-lib` runs working without Dfam data, the
image leaves FamDB out of the static RepeatMasker config. The entrypoint
auto-enables FamDB only when mounted `.h5` component files are found at runtime.

Command mode remains enabled. If the first argument is another executable name,
TAFFISH runs that command in the same configured container:

```sh
taf-repeatmasker famdb.py --help
taf-repeatmasker ProcessRepeats -help
taf-repeatmasker rmblastn -version
```

## Runtime Contents

The image installs the official `RepeatMasker-4.2.4.tar.gz` release, installs
FamDB `3.0.0`, copies RMBlast from the
`ghcr.io/taffish/rmblast:2.17.1-r1` app image, and installs pinned UCSC
command-line helper binaries needed by RepeatMasker utility scripts. The
Dockerfile verifies the RepeatMasker, FamDB, and UCSC helper checksums:

```text
RepeatMasker-4.2.4.tar.gz
7407b42909c64b7ae080efb737f3f725327be81ace1ec0cd9dc13c4a503885d7

FamDB-3.0.0.tar.gz
cad4652696cbd6b3444ef1ea008764e4807eba503410bf24357c4505a5ddb8d4

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
- `taf-repeatmasker-entrypoint`
- `ProcessRepeats`
- `RepeatProteinMask`
- `DupMasker`
- `famdb.py`
- `download_dfam.py`
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
- FamDB `3.0.0` with Python h5py/numpy support
- UCSC `twoBitInfo` and `bedToBigBed` helper binaries
- Perl, Python 3, Python h5py, curl, gzip, tar, and required shared libraries

`BLAST_USAGE_REPORT=false` is set by default so RMBlast does not report usage
statistics during local TAFFISH runs. `PAGER=cat` is set by default so
RepeatMasker help remains non-interactive and works predictably in terminals,
pipelines, CI, and TAFFISH flow contexts.

## Libraries And Data

RepeatMasker `4.2.4` no longer bundles a local Dfam root partition. Upstream
now treats FamDB as a separate optional package and Dfam `4.0` as external
component data. This image includes the FamDB `3.0.0` program and configures
FamDB itself to look for data in:

```text
/opt/RepeatMasker/Libraries/famdb
```

Custom-library runs with `-lib` do not need FamDB data. Species or clade
queries with `-species` require Dfam component files. When `.h5` component
files are mounted at the path above, the default TAFFISH entrypoint configures
RepeatMasker with `/opt/FamDB` before running the command. For most
RepeatMasker use cases, upstream FamDB recommends downloading the root
component plus curated consensus files; curated HMM files add sensitivity. A
complete Dfam 4.0 download is very large and is not bundled.

The wrapper automatically mounts an existing local Dfam/FamDB directory to
`/opt/RepeatMasker/Libraries/famdb` when one of these paths exists, and the
entrypoint then enables FamDB for RepeatMasker:

```text
TAFFISH_REPEATMASKER_FAMDB_PATH
~/.local/share/taffish/databases/repeatmasker/dfam4
/usr/local/share/taffish/databases/repeatmasker/dfam4
/opt/taffish/databases/repeatmasker/dfam4
```

Personal setup example:

```sh
mkdir -p ~/.local/share/taffish/databases/repeatmasker/dfam4
cd ~/.local/share/taffish/databases/repeatmasker
taf-repeatmasker download_dfam.py -o "$PWD/dfam4"
taf-repeatmasker famdb.py -i "$PWD/dfam4" info
```

Administrator setup can use `/usr/local/share/taffish/databases/repeatmasker`
with the same `dfam4` directory name, then make the files readable by users.
For one-off data elsewhere, set:

```sh
TAFFISH_REPEATMASKER_FAMDB_PATH=/abs/path/dfam4 \
taf-repeatmasker -pa 8 -engine rmblast -species "Homo sapiens" genome.fa
```

To disable auto-mount and provide backend args manually:

```sh
TAFFISH_REPEATMASKER_AUTO_MOUNT=0 \
TAFFISH_DOCKER_RUN_ARGS="-v /abs/path/dfam4:/opt/RepeatMasker/Libraries/famdb:ro" \
taf-repeatmasker -pa 8 -engine rmblast -species "Homo sapiens" genome.fa
```

Use `TAFFISH_PODMAN_RUN_ARGS` for Podman. Symlinks are resolved to their
physical target before auto-mounting, so the target must be readable and
visible to the selected container backend.

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

- full Dfam component data
- RepBase
- `cross_match`
- ABBLAST/WUBlast
- a from-source RMBlast build inside this Dockerfile; it depends on the
  `ghcr.io/taffish/rmblast:2.17.1-r1` app image at build time
- Entrez Direct. The upstream `download_dfam.py` utility is packaged for
  explicit user-initiated Dfam downloads, and utility scripts such as
  `rmToTrackHub.pl` can still use `curl` to fetch UCSC chromosome sizes when
  users request those workflows.

The smoke tests validate the configured program stack and small offline
functional runs. They do not download Dfam data and do not substitute for full
biological validation on large genomes or species-specific repeat libraries.

## License Boundary

The TAFFISH app packaging files are licensed under Apache-2.0. The packaged
upstream RepeatMasker software is covered by OSL-2.1. Packaged FamDB code and
Dfam data notices are CC0, while RMBlast/NCBI components and UCSC command-line
utilities keep their own terms. External Dfam component files, RepBase data,
models, and other user-provided resources keep their own license terms.

## License And Citation

RepeatMasker open-4.0 and later are distributed under the Open Software License
v2.1. The packaged FamDB code is documented by upstream as CC0. RMBlast and NCBI
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
- FamDB 3.0.0 help, Dfam downloader help, and missing-Dfam-data boundary.
- RepeatMasker configuration paths for RMBlast, TRF, HMMER, and default engine.
- A tiny offline default-entrypoint `-lib` run producing `.out` and `.masked`.
- A tiny offline default-entrypoint `-gff -lib` run producing `.out.gff`.
- Utility conversion/summary scripts on a tiny real RepeatMasker `.out` file,
  including the UCSC `twoBitInfo` helper required by `buildSummary.pl`.
