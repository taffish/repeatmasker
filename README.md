# repeatmasker

`repeatmasker` packages [RepeatMasker](https://github.com/Dfam-consortium/RepeatMasker/releases/tag/v4.2.5) for TAFFISH.

Package identity: tool `repeatmasker`, command `taf-repeatmasker`, version
`4.2.5-r1`, image `ghcr.io/taffish/repeatmasker:4.2.5-r1`.
Packaging license: Apache-2.0; upstream components keep their own licenses.

## What This App Packages

RepeatMasker 4.2.5 masks interspersed repeats and low-complexity DNA. It keeps
upstream command mode and uses RMBlast 2.17.1+ by default. This release supports
both RMBlast 2.x and 3.x; the app deliberately retains the tested 2.x engine.
Source commit: `68f04286b0c68eec386b5fff7a4bee5ba170bb73`.
Source SHA256: `2a863a62c01d631f733ee0e9d01278241a96dfc168dc8eb974c43a44bcf1d570`.

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
`RepeatMasker` and legacy `taf-repeatmasker-entrypoint` share one environment
initializer; it enables FamDB only after prepared-root verification. It never
runs `configure` or writes an installation marker at runtime. The raw upstream
executable remains at `/opt/RepeatMasker/RepeatMasker` for advanced usage.

Asserted packaging patches make nucleotide libraries use the upstream per-job
temporary directory and protein libraries use a private auto-cleaned `/tmp`
directory, rather than the installation tree or `$HOME`.
This trades cross-job cache reuse for read-only SIF compatibility; scientific
search/join algorithms are unchanged. A second asserted patch defers Taxonomy's
FamDB path lookup until object creation, after upstream applies its documented
environment/command-line overrides (the original module captured the empty static
value too early). The generated config also computes the prepared FamDB path at
module load for ProcessRepeats and other helpers that read it before resolving
environment options. Python bytecode and BLAST telemetry are
disabled; `PAGER=cat` keeps help non-interactive.

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
be much larger. `list` and `install --dry-run` show exact IDs, sizes, URLs and
official MD5 values. Selection is the user's scientific decision; there is no
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
incomplete root fails closed; it does not search another root for missing species.
Symlinks resolve to the physical root, which must be engine-visible. Paths
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

### Previous candidate evidence (2026-10-06/07)

The counts and image size in this subsection describe the candidate before the
UCSC frozen-source repair. They are retained as historical evidence, not as tests
of the replacement binaries; the source-repair results are recorded separately below.

Build-time checks are identity/imports and one tiny custom-library masking path.
Runtime smoke adds help, resource dry-run/negative paths, GFF/BED/divergence/HTML
generation and engine probes. Production resources are not fetched during smoke.
On native amd64 Linux, the final image passed 195 exact fresh/offline probes:
Docker and Podman normal/read-only roots plus the same-OCI read-only Apptainer SIF.
The real built wrapper passed 107 checks across the three backends, plus nine
isolated personal-discovery/override/disable checks. Coverage includes custom
masking, GFF/BED/divergence, offline/online HTML generation, Dfam species masking, a
protein-search no-hit path, space/symlink resource paths, manual mounts, ordinary
UID output, full verification and actual read-only write rejection. Docker also
tested a second ordinary UID reading the same prepared data without write access.
Nine additional GUI-generation calls used two real tiny repeat classes across
Docker/Podman/Apptainer, including an otherwise unknown class; one short Docker
`taf run` call also passed. Nine final host-side wrapper help/version/compile
checks match the final 89-line help. Independent parser/escaping tests cover
malformed input, non-finite values, duplicate classes/bins and HTML/JSON escaping.
The viewer keeps all input counts; raw class summaries and bin totals are checked
against the generated upstream divergence summary, not a hand-drawn chart.
The visual repair adds 23 deterministic source/JavaScript/DOM-model checks
(`node tests/test-landscape-logic.cjs`): fixed-scale filtering, readable tick
formatting, zero/tiny values, long names, multi-class colors and CSV/SVG contents.
These tests do not launch a browser or validate actual fonts/CSS/native downloads.
Four English-only synthetic display fixtures supplement the real masking report;
a separate Unicode fixture verifies that input titles/class names are preserved,
not translated. The native class selector retains keyboard/focus behavior, with
a decorative inset arrow and matching control spacing; forced-colors mode uses
the native system arrow. Browser inspection was still pending at that stage;
the 2026-10-12 browser acceptance below closes that gate for the current candidate.

The official Dfam 4.0 root and curated.consensus.0 were downloaded and verified;
eight resource checks cover invalid selection, incomplete/corrupt roots, locking,
cache corruption and real download resume through a wrapper. The helper/catalog
bytes are unchanged from those download tests; final-image idempotent reuse and
full verification passed on all three backends. Actual root-owned installation
under `/usr/local/share` or `/opt/taffish` was not performed: only the shared-root
mechanism/permissions were tested in a private directory. Other large Dfam/HMM
partitions and production-scale protein/genome analyses were not validated.

AluY annotation and masked FASTA matched an unmodified official source/configure
reference byte-for-byte on the same input and dependencies. The final image is
999,707,898 bytes; Python bytecode/apt caches were removed in the installation
layer. The 625 MiB RMBlast executable suite is retained for upstream compatibility.
No compiler/sysroot was added; runtime data, examples, POD and licenses are retained.

`taf check`, docs checks, read-only hubctl and remote-checked publish dry-run pass;
Action is a byte-identical copy of the fresh canonical template. Native ARM,
ARM-host emulation and full-genome scientific accuracy are not claimed.
No backend exception is needed. The approved offline helper and alignment asset
fix are implemented; generated artifacts, data integrity and JS syntax pass.
The reported overlapping Y-axis title/ticks was a defect in the TAFFISH-added
viewer, not in upstream annotation results. The title is now horizontal above the
plot, with compact ticks; responsive layout, long text and SVG context were also
reworked. Maintainer review found the overall layout acceptable before the final
select-arrow polish. The automation browser used at that stage disallowed local
file URLs, so those checks did not establish browser acceptance. The separate
2026-10-12 native Chrome acceptance below supersedes that pending status.

### Frozen UCSC source repair (2026-10-12)

The unpublished `4.2.5-r1` candidate now uses the official frozen v479 tools.
An app-root native amd64 build with `--no-cache` fetched and verified the fixed
materials successfully; after correcting a new test's join-track coordinate
assumption, the final image was rebuilt and all current tests rerun. The first
failed test receipts are retained separately, not counted as passes.

The final OCI image is `sha256:db1b3572ba6f67f79e159382349206d483ff170140f56746c30f3442b59d45e9`
(989,121,373 bytes). It passed 200 fresh/offline probes: combined exist, 31
individual exist checks and eight independent tests on Docker/Podman normal and
read-only roots, and a read-only Apptainer SIF made from that same OCI image.
The new `ucsc` test checks real 2bit lengths (58 total, 48 non-N), the upstream
landscape `-twoBit` path, and `rmToTrackHub.pl` output in both `bed9+5` and
`bed3+14` formats. It decodes each bigBed record and checks it against the verified
source TSV, distinguishing join-display bounds from actual alignment coordinates.
A deliberately failing converter was rejected even though upstream does not
propagate its exit status.

All three real wrappers passed 113 checks in total, including persistent track-hub
output, custom-library and representative Dfam masking, repeat-protein searches,
prepared-root verification, read-only binds, ordinary-user permissions and
space/symlink paths. The fixed Dfam root plus curated.consensus.0 was installed in
the private test directory; no complete Dfam family or system-wide install was
performed. Ten report-generation/development calls and five display-fixture
generation checks also passed. These are not browser interaction or visual tests.
The wrapper, help, report code, upstream identity and canonical Action remain
unchanged from the task-start candidate. This source-repair run alone did not
establish browser acceptance; the separate acceptance below closes that gate.
Independent comparison found all 54 comparable annotation, masked-FASTA,
divergence and HTML outputs byte-identical to the previous candidate. Final
wrapper metadata checks, docs checks, 23 viewer logic tests and remote-checked
publish dry-run passed. Generated targets were archived, leaving only `.gitkeep`;
the private remote test directory was removed after receipt checksum verification.

### Browser acceptance and final recheck (2026-10-12)

Native Chrome 154.0.8037.98 on macOS opened the current image-generated files
directly with `file://`. The final native selector, mouse and keyboard filtering,
fixed-scale chart/table updates, bar details and keyboard focus passed. Actual CSV
and SVG downloads were saved and independently checked against the embedded data:
the filtered report's CSV retains both classes and all 71 bins (142 data rows),
while its SVG contains only the selected class with complete source provenance.
A 24-class SVG preserves all classes, 426 nonzero bars, long names and its footer;
the downloaded SVG also rendered correctly when opened as a separate local file.

Desktop and 390-by-844 CSS-pixel layouts were inspected, including keyboard
horizontal scrolling to bin 70, readable focus/details, long titles, Unicode,
tiny nonzero percentages and zero coverage. Alignment HTML passed individual HSP
expansion plus open-all/close-all. DevTools Offline reload loaded only the local
HTML document; filtering and keyboard interactions worked with an empty console.
An initial DevTools-opening session reported a same-file unique-origin diagnostic;
it did not recur after reload or during those offline interactions. No security
setting was weakened. This is Chrome acceptance, not cross-browser certification,
forced-colors visual acceptance or a new claim about the upstream online viewer.

The unchanged OCI image above passed a fresh 200-probe backend matrix and a
42-check real-wrapper subset (14 per backend); 23 viewer logic tests also passed.
Fifteen representative output files match the previous run byte-for-byte.
The earlier 113-check wrapper and resource evidence remains applicable to identical
code; it is not represented as a full rerun. Fresh canonical Action comparison and
RepeatMasker-only read-only upstream checks passed. No backend exception is needed.
The existing native-platform, external-resource and scientific-validation limits
remain in effect; local readiness does not mean publication or a passing future
GitHub build/Hub Index run.

## License and Citation

TAFFISH packaging is Apache-2.0. RepeatMasker's root license is OSL-2.1;
individual utilities retain their notices (including GPL notices in landscape code).
FamDB code and Dfam data are CC0; RMBlast/NCBI retain their distribution notices.
The two UCSC CLI utilities follow the Kent CLI MIT terms; its full license boundary
is retained in `/opt/ucsc/LICENSE`. Debian notices remain under `/usr/share/doc`.

Cite Smit, Hubley and Green's RepeatMasker, the Dfam Consortium, and BLAST+:
Camacho et al. 2009, DOI `10.1186/1471-2105-10-421`, PMID `20003500`.
