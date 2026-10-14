# repeatmasker

`repeatmasker` packages [RepeatMasker](https://github.com/Dfam-consortium/RepeatMasker/releases/tag/v4.2.6) for TAFFISH.

Package identity: tool `repeatmasker`, command `taf-repeatmasker`, version
`4.2.6-r1`, image `ghcr.io/taffish/repeatmasker:4.2.6-r1`.
Packaging license: Apache-2.0; upstream components keep their own licenses.

## What This App Packages

RepeatMasker 4.2.6 masks interspersed repeats and low-complexity DNA. It keeps
upstream command mode and uses RMBlast 2.17.1+ by default. This release supports
both RMBlast 2.x and 3.x; the app deliberately retains the tested 2.x engine.
Source commit: `74d2b41c9f2378773e7d42c7f7aac88f7f8df840`.
Source SHA256: `05e1ac50a8918de9b7dea6a298ca08702d518ec399489e7ae32d6b10addec1cf`.

## Scope

Supported surfaces are custom-library masking, prepared Dfam/FamDB species
queries, repeat-protein searches, TRF/HMMER, annotation conversion, summaries,
divergence summaries, offline landscape/alignment HTML, original upstream online
landscape HTML and UCSC track generation.
Production-scale biological accuracy is not established by packaging smoke.
RepBase, cross_match, ABBLAST/WUBlast and Entrez Direct are not bundled.
No model/GPU service or desktop/noVNC session is needed by these CLI surfaces.

## Container Contents

- RepeatMasker, ProcessRepeats, RepeatProteinMask, DupMasker and upstream utilities.
- FamDB 3.0.0, h5py/numpy, and pandas for `RM2Bed.py`.
- RMBlast 2.17.1+ including `rmblastn`, `makeblastdb` and `blastx`.
- Debian TRF 4.09.1 and HMMER 3.3.2; Perl/POD help, Python, curl and gzip.
- UCSC `twoBitInfo` and `bedToBigBed` from the official frozen v479 Linux x86_64
  distribution, downloaded over HTTPS and individually SHA256-checked.
- `taf-repeatmasker-dfam`: explicit, pinned selective Dfam installer/verifier.
- `taf-repeatmasker-landscape`: independent standalone offline HTML viewer.

The Dockerfile fixes source/binary checksums and Debian/RMBlast platform image
digests. Debian package versions are recorded in
`/usr/share/taffish-repeatmasker/debian-packages.tsv`; apt repositories are not
snapshot-pinned. UCSC tools use the official
[one-time frozen v479 distribution](https://groups.google.com/a/soe.ucsc.edu/g/genome-mirror/c/7knco87cYd8)
at `https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.v479/`, not the rolling
`linux.x86_64/` directory. These are deliberately fixed compatibility helpers,
not a claim to package the newest UCSC tools or recover the previous rolling bytes.
SHA256: `twoBitInfo` = `406001e3f150f2caecf4846a1fd287341bda0303113641a3a6f5719bab435996`;
`bedToBigBed` = `aa42073701d102b7eb5f7e6fe3c8f8057e5f983fb9967a9e501f044eb14c99f0`.
Changed bytes fail closed; missing downloads never fall back to a rolling URL.
This reduces source drift, not a promise of permanent upstream hosting or a fully
locked Debian build. `docker/kent-LICENSE` is from the official `v479_base` source
commit `864846249d1323e9d51366ea37d6b3684b0abc9b`.

## Usage

```sh
taf install repeatmasker
taf-repeatmasker --help
taf-repeatmasker -- --help
taf-repeatmasker -- -v
mkdir -p rm-out
taf-repeatmasker -pa 8 -engine rmblast -lib repeats.fa -a -gff -dir rm-out genome.fa
taf-repeatmasker RM2Bed.py rm-out/genome.fa.out rm-out/repeats.bed
taf-repeatmasker rmOutToGFF3.pl rm-out/genome.fa.out > rm-out/repeats.gff3
```

## Command Mode

Option-leading arguments go to RepeatMasker. Wrapper `--help`, `--version`
and `--compile` belong to TAFFISH; use `-- -v` for upstream version. Explicit
executables remain available, for example `taf-repeatmasker famdb.py info`.
`RepeatMasker`, `RepeatProteinMask`, `ProcessRepeats` and the legacy
`taf-repeatmasker-entrypoint` share one environment initializer; it enables FamDB only after prepared-root verification. It never
runs `configure` or writes an installation marker at runtime. The raw upstream
executable remains at `/opt/RepeatMasker/RepeatMasker` for advanced usage.

Upstream 4.2.6 supplies the cache and FamDB configuration interfaces previously
handled by packaging patches. Those patches have been removed: the scientific
Perl programs and Taxonomy module are unchanged upstream files. The environment
initializer sets `REPEATMASKER_CACHE_DIR` to a private per-invocation temporary
directory and removes it after its child exits. It never writes the image tree or
database. Python bytecode and BLAST telemetry are disabled; `PAGER=cat` keeps help
non-interactive.

For optional persistent cache reuse, create a writable directory under the
working directory and pass `-cache_dir cache` to RepeatMasker. This overrides
the temporary default; its files remain yours to manage. Do not use a read-only
shared database as the cache directory. The upstream `-famdb_dir /opt/FamDB
-famdb_data_dir PATH` pair is also available for advanced, explicitly mounted
data; automatic discovery remains the recommended prepared-root path.
Environment variables set on the host are not implicitly forwarded into every
container backend.

## Inputs and Output Notes

Input is DNA FASTA plus a custom consensus FASTA (`-lib`) or a prepared Dfam
root and explicit `-species`. Classification in custom FASTA headers is
`>name#class/subclass`. Typical outputs are `.out`, `.masked`, `.tbl`, `.cat`,
optional `.align` (`-a`) and `.out.gff` (`-gff`). Use a fresh writable output
directory; upstream may replace files when names are reused. Upstream rejects
FASTA paths containing spaces or shell-special characters. Keep analysis paths
simple. Dfam helper paths are a separate interface and accept spaces; with the
current TAFFISH argument boundary, explicitly preserve literal quotes, e.g.
`--db-root "'/absolute/resource path/dfam4'"`. Automatic discovery through the
environment override handles a space-containing root without this CLI workaround.

## Resources, Databases, and Platform

Dfam is a selectable external family, not bundled data. The fixed Dfam 4.0
FamDB catalog is in `/opt/taffish-repeatmasker/dfam-4.0.catalog.json`. The root
member is always required (60,708,386 compressed bytes); example member
`curated.consensus.0` adds 28,260,067 bytes. Other consensus/HMM partitions can
be much larger. `list` and `install --dry-run` show exact IDs, sizes, URLs,
official MD5 values and the resource license. The plan also identifies the fixed
catalog by SHA256 and does not create an install root or lock. Selection is the user's scientific decision; there is no
default whole-family download. HMMER searches require appropriate HMM members.

Personal installation (choose required partitions, repeat `--part` as needed):

```sh
mkdir -p "$HOME/.local/share/taffish/databases/repeatmasker"
cd "$HOME/.local/share/taffish/databases/repeatmasker"
TAFFISH_REPEATMASKER_AUTO_MOUNT=0 taf-repeatmasker taf-repeatmasker-dfam list
TAFFISH_REPEATMASKER_AUTO_MOUNT=0 taf-repeatmasker taf-repeatmasker-dfam install \
  --db-root "$PWD/dfam4" --part curated.consensus.0 --dry-run
TAFFISH_REPEATMASKER_AUTO_MOUNT=0 taf-repeatmasker taf-repeatmasker-dfam install \
  --db-root "$PWD/dfam4" --part curated.consensus.0
taf-repeatmasker taf-repeatmasker-dfam verify --db-root /opt/RepeatMasker/Libraries/famdb
taf-repeatmasker famdb.py info
taf-repeatmasker -species human -dir rm-out genome.fa
```

The same commands work with `TAFFISH_CONTAINER_BACKEND=docker`, `podman`, or
`apptainer` on native amd64 Linux. Work inside the resource parent so TAFFISH's
working-directory bind exposes the writable installation destination. Preparation
is explicitly online; annotation never downloads a missing database.

An administrator may instead prepare `dfam4` under
`/usr/local/share/taffish/databases/repeatmasker` or
`/opt/taffish/databases/repeatmasker`, once for all users. Use the same installer
with the chosen parent mounted writable; no ordinary user needs sudo or a
second download. Successful directories are 0755 and files 0644; all ancestors
must be traversable. Administrative installation and Docker access remain site
policy; this app never changes parent ownership or global permissions.
Ordinary users reuse the shared read-only database without installation writes.
The Dfam resource license is CC0, separately from the software licenses below.

Discovery priority: `TAFFISH_REPEATMASKER_FAMDB_PATH`, then the personal path,
then `/usr/local/share`, then `/opt/taffish`. A higher-priority invalid or
incomplete root, including a dangling symlink, fails closed; it does not silently
fall back to a lower-priority root or search another root for missing species.
Valid symlinks resolve to the physical root, which must be engine-visible. Paths
containing `:` or `,` cannot be auto-bound. Disable discovery using
`TAFFISH_REPEATMASKER_AUTO_MOUNT=0` (also false/no/off).

Installation uses a persistent sibling advisory lock, private resumable download
cache, bounded curl retries, official compressed MD5/size verification, SHA256 of
unpacked data, a member inventory and private staging followed by atomic rename.
An identical complete install is fully verified and reused. Different partitions,
corrupt caches and untracked/partial roots fail closed. There is no `--force`:
prepare a new root and select it explicitly instead of mutating a shared database.
The conservative initial free-space estimate is 4x compressed size plus 64 MiB;
decompression also checks remaining space. Actual expansion is data-dependent.
After verified success, the owner may remove the exact sibling `.dfam4.downloads`
cache when no installer is running; do not remove the persistent lock inode.
INT/TERM/HUP exit without resuming installation, reap the owned downloader/parser,
and remove only this attempt's staging directory. The packaging runtime records
signals during process/directory creation until ownership is registered, then
exits with 130/143/129. Repeated signals do not interrupt cleanup; a child that
ignores TERM is killed after a five-second grace period. The same protection
covers the annotation launcher's private cache and owned process session.
Before atomic promotion, no new
root is exposed; after promotion, a fully verified root remains and retry is
idempotent. Existing nonempty roots are never replaced. SIGKILL/power loss may
leave a private stage/cache: inspect it before removing that exact stage, and do
not delete another installer's lock or a previously prepared root.

Automatic use validates inventory/ready checksums and file sizes; `verify`
performs full SHA256 rehashing. Re-run full verification after transfers or suspected
corruption. These checks detect damage, not a malicious administrator replacing
both data and receipts. Old loose `.h5` directories are not implicitly trusted:
preserve them, prepare a new root, then switch the override. Raw `download_dfam.py`
and `famdb.py -i PATH` remain upstream advanced interfaces; their output is not
automatically an installer-managed root.

Custom `-lib` inputs are project-specific and need no download/share helper.
RepBase is separate licensed data: obtain it under your authorization, do not
assume Dfam's CC0 license applies. Small upstream runtime libraries stay in the image.

## Backend Usage and Capability Matrix

| Capability | Docker | Podman | Apptainer | Boundary |
| --- | --- | --- | --- | --- |
| Masking/utility CLI | same wrapper | same wrapper | same wrapper | Native linux/amd64 only |
| Dfam discovery | automatic RO volume | automatic RO volume | automatic RO bind | Verified root, never runtime configure |
| Resource preparation | current-directory RW bind | current-directory RW bind | current-directory RW bind | Explicit online install; caller permissions |
| ARM host | amd64 emulation if installed | amd64 emulation if installed | not supported by this image | Use native amd64 Linux; no native arm64 claim |
| Landscape/alignment HTML | offline file | offline file | offline file | New helper/native -html; original landscape command remains online |

The app embeds Docker/Podman `--platform linux/amd64`. It does not install
emulators. For manual mounting, set `DB` to an engine-visible prepared root:

```sh
export TAFFISH_REPEATMASKER_AUTO_MOUNT=0
DB=/absolute/path/dfam4
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_DOCKER_RUN_ARGS="-v $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_PODMAN_RUN_ARGS="-v $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_APPTAINER_RUN_ARGS="--bind $DB:/opt/RepeatMasker/Libraries/famdb:ro" taf-repeatmasker famdb.py info
unset TAFFISH_REPEATMASKER_AUTO_MOUNT
```

## Browser Reports and Boundaries

`calcDivergenceFromAlign.pl -s genome.divsum genome.fa.align` creates a divergence
summary. The separate `taf-repeatmasker-landscape` helper produces one offline HTML:

```sh
taf-repeatmasker calcDivergenceFromAlign.pl -s genome.divsum rm-out/genome.fa.align
taf-repeatmasker taf-repeatmasker-landscape --div genome.divsum \
  --genome-size 3000000 --title "'My repeat landscape'" --output landscape.html
# Existing output is rejected unless you explicitly add --force.
# For a pre-existing folder with spaces: --output "'report folder/view.html'"
```

Use the same commands with `TAFFISH_CONTAINER_BACKEND=docker`, `podman`, or
`apptainer`; open the generated file on your own computer using `file://`.
No HTTP server, port, authentication or long-running session is involved.
The Python standard-library helper adds offline SVG, class filtering, exact-value
tooltips, a raw-class table and CSV/SVG downloads without adding a browser runtime
to the image. It keeps every raw class and divergence bin, including unknown
classes and bins above 50: it does **not** apply the upstream landscape utility's
class remapping, fixed display-class list or 0–50 display cutoff.
Each bar is the upstream bin count / explicit genome denominator ×100. The table
separately sums family absLen and bin coverage; it does not infer uniquely masked
or unmasked bases. Record whether the supplied genome denominator includes Ns.
This is a distinct viewer, not a claim of identical upstream chart semantics.
The vertical axis uses compact readable ticks and keeps the same scale across
class filters. Narrow screens scroll inside the chart and table rather than
shrinking their text. Long titles/class names wrap; a zero-coverage selection is
explicitly identified. Hover, keyboard-focus or tap a bar for its count and
percentage. The CSV always includes all original classes/bins without display
rounding. SVG export follows the current filter and includes the report title,
legend, denominator, method note and input checksum; it is not a screenshot of
the entire HTML page. The displayed tick rounding never changes the underlying
coverage values.
Inputs and the source SHA256 are embedded; sample/repeat names may be sensitive.
No external scripts, fonts, telemetry or network requests are needed.

The original `createRepeatLandscape.pl -div genome.divsum -g GENOME_BP` remains
byte-for-byte upstream and writes HTML to stdout. It loads Google's visualization
API: use the new helper for offline viewing. Upstream `RepeatMasker -html -a ...`
produces `.out.html` with expandable alignment HSPs. Its otherwise unchanged
template embeds the bundled `bluegrad.jpg` as a data URI, fixing the upstream
output's missing relative asset without altering annotations or interaction code.
Repeat-name hyperlinks still open the upstream RepeatMasker website only when
clicked; custom-library names may not exist there. They are not rendering dependencies.
Only open reports generated from trusted inputs; the original alignment renderer
is not a general-purpose sanitizer for untrusted FASTA identifiers.
Upstream output-overwrite semantics still apply; use a fresh annotation directory.

For a local source checkout, `taf build` creates the versioned target wrapper;
short `taf run -b docker -- taf-repeatmasker-landscape ...` is also a generation
path (not installation). Installed users use the examples above.

`rmToTrackHub.pl`
produces UCSC track assets; it can fetch chromosome sizes online, and a compatible
external UCSC Genome Browser/track host is required for viewing. We do not bundle
the independent UCSC browser service or claim it passed this app's GUI tests.

## Troubleshooting

- Missing species: inspect `famdb.py info` and the selected partition inventory;
  prepare the required members in a new root, then select that root explicitly.
- Invalid old root: disable auto-mount for custom `-lib`, or use the pinned installer.
- Read-only failure: make the working/output directory writable, not `/opt` or the DB.
- Interrupted install: retry the identical command; completed archives are verified,
  partial archives resume when the server supports ranges. Corrupt cache errors name
  the exact file to inspect; there is no silent checksum bypass.
- Blank legacy landscape: use the new offline helper or permit Google's runtime
  for the original upstream command; see browser boundaries.

## Testing

Build-time checks are exact identity, imports and one tiny custom-library path.
Runtime smoke adds helpers, resource planning/negative paths, real masking,
GFF/BED/divergence/HTML, engine probes and UCSC bigBed records. Each manifest probe
runs fresh/offline; production databases are not downloaded during smoke.

The 4.2.6-r1 successor passed a native amd64 no-cache build from the canonical
app-root context. Docker/Podman normal and read-only roots plus the same-OCI
read-only Apptainer SIF passed 200 fresh/offline probes (40 per configuration).
All three real wrappers passed 113 checks; 75 resource checks cover actual
representative installation, full verification, idempotency, old-root protection,
locking and controlled INT/TERM at validation and atomic-promotion boundaries.
Another 45 checks cover persistent cache reuse, explicit FamDB data paths,
personal discovery, override/disable, isolated site-prefix priority, actual
official download range resume and corrupt-cache rejection. The site-prefix
checks execute the actual discovery expression with private test paths; they do
not claim administrative deployment. Final wrapper metadata/runtime adds 12 checks.

Additional repair regressions cover early child/directory creation, repeated
signals, TERM-resistant children, dangling-resource discovery and consistency
between dry-run, catalog and completion-manifest licenses. Controlled timing
fixtures invoke the installed production functions through real wrappers; their
tiny synthetic members do not substitute for actual FamDB parsing. Separate
unmodified installer CLI tests interrupt a real curl transfer, then repeat the
same command for recovery and idempotency. Apptainer's outer shell can exit just
before its helper completes cleanup: tests require no owned downloader or stage
within ten seconds (the observed real-download cleanup lag was about 0.06 seconds).

The final OCI image is 989,148,407 bytes. RMBlast accounts for about 625 MiB and
is retained for complete search-engine functionality. Apt caches and Python
bytecode are removed in the installation layer; fetch archives do not enter the
final stage. Runtime data, examples, POD and license notices remain available.
Native ARM and ARM-host emulation are not claimed. No backend exception is needed.

The offline landscape viewer is unchanged from its accepted predecessor. Its
23 source/JavaScript/DOM-model checks cover filtering, scale, extreme values,
long names, CSV and SVG semantics; these are not actual browser interaction tests.
Current image-generated report data matches the upstream divergence summary.
Native Chrome opened the current offline landscape and alignment files: filtering,
axis/layout, HSP expansion/collapse and actual CSV/SVG downloads passed. Exported
counts and provenance were independently checked. The unchanged viewer's previous
narrow-window, multi-class and long-text browser acceptance is retained as such,
not described as a fresh complete cross-browser run.

Only the fixed Dfam 4.0 root and curated.consensus.0 representative member are
used for integration tests. Controlled synthetic members exercise transaction
interruption without pretending to be a scientific database. A private shared
root demonstrates ordinary-user/read-only reuse, not actual root-owned deployment
under /usr/local/share or /opt/taffish. Other Dfam partitions, full-genome accuracy,
and production-scale protein searches are outside this packaging validation.

An initial online Apptainer test incorrectly disabled the host resolver bind with
an extra diagnostic `--no-mount bind-paths` option. Normal online wrapper settings
passed after removing that test-only restriction; offline smoke retains network
isolation. No app networking bypass or system change was needed. `taf check`, docs,
read-only upstream checks and remote-checked publish dry-run passed. Readiness is
not actual publication or a guarantee of future upstream hosting/CI availability.

## License and Citation

TAFFISH packaging is Apache-2.0. RepeatMasker's root license is OSL-2.1;
individual utilities retain their notices (including GPL notices in landscape code).
FamDB code and Dfam data are CC0; RMBlast/NCBI retain their distribution notices.
The two UCSC CLI utilities follow the Kent CLI MIT terms; its full license boundary
is retained in `/opt/ucsc/LICENSE`. Debian notices remain under `/usr/share/doc`.

Cite Smit, Hubley and Green's RepeatMasker, the Dfam Consortium, and BLAST+:
Camacho et al. 2009, DOI `10.1186/1471-2105-10-421`, PMID `20003500`.
