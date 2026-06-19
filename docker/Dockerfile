ARG REPEATMASKER_VERSION=4.2.4
ARG REPEATMASKER_ARCHIVE=RepeatMasker-4.2.4.tar.gz
ARG REPEATMASKER_SHA256=7407b42909c64b7ae080efb737f3f725327be81ace1ec0cd9dc13c4a503885d7
ARG FAMDB_VERSION=3.0.0
ARG FAMDB_ARCHIVE=FamDB-3.0.0.tar.gz
ARG FAMDB_SHA256=cad4652696cbd6b3444ef1ea008764e4807eba503410bf24357c4505a5ddb8d4
ARG RMBLAST_VERSION=2.17.1
ARG RMBLAST_IMAGE=ghcr.io/taffish/rmblast:2.17.1-r1
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
ARG DEBIAN_SECURITY_MIRROR=http://deb.debian.org/debian-security

FROM debian:12-slim AS fetcher

ARG REPEATMASKER_ARCHIVE
ARG REPEATMASKER_SHA256
ARG FAMDB_VERSION
ARG FAMDB_ARCHIVE
ARG FAMDB_SHA256
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR
ARG TARGETARCH=amd64

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    case "${TARGETARCH}" in \
      amd64|"") ;; \
      *) echo "RepeatMasker app uses the official x86_64 RMBlast binary; unsupported TARGETARCH=${TARGETARCH}" >&2; exit 1 ;; \
    esac; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3 4 5 6; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            ca-certificates \
            curl \
            gzip \
            tar; then \
        break; \
      fi; \
      if [ "$attempt" = "6" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/build

RUN set -eux; \
    for item in \
      "https://www.repeatmasker.org/RepeatMasker/${REPEATMASKER_ARCHIVE}|${REPEATMASKER_ARCHIVE}|${REPEATMASKER_SHA256}" \
      "https://github.com/Dfam-consortium/FamDB/archive/refs/tags/${FAMDB_VERSION}.tar.gz|${FAMDB_ARCHIVE}|${FAMDB_SHA256}"; do \
      url="$(printf '%s' "$item" | cut -d '|' -f 1)"; \
      archive="$(printf '%s' "$item" | cut -d '|' -f 2)"; \
      sha256="$(printf '%s' "$item" | cut -d '|' -f 3)"; \
      for attempt in 1 2 3 4 5 6; do \
        if curl \
            --fail \
            --location \
            --show-error \
            --connect-timeout 30 \
            --retry 3 \
            --retry-delay 5 \
            --retry-all-errors \
            -o "$archive" \
            "$url"; then \
          break; \
        fi; \
        if [ "$attempt" = "6" ]; then exit 1; fi; \
        sleep 10; \
      done; \
      echo "${sha256}  ${archive}" | sha256sum -c -; \
    done; \
    mkdir -p /opt/RepeatMasker; \
    tar -xzf "${REPEATMASKER_ARCHIVE}" -C /opt/RepeatMasker --strip-components=1; \
    test -x /opt/RepeatMasker/RepeatMasker; \
    test -x /opt/RepeatMasker/configure; \
    test -r /opt/RepeatMasker/LICENSE; \
    mkdir -p /opt/FamDB /opt/RepeatMasker/Libraries/famdb; \
    tar -xzf "${FAMDB_ARCHIVE}" -C /opt/FamDB --strip-components=1; \
    sed -i 's|# FAMDB_DATA_DIR = /path/to/famdb/directory|FAMDB_DATA_DIR = /opt/RepeatMasker/Libraries/famdb|' /opt/FamDB/famdb.conf; \
    chmod -R a+rX /opt/FamDB; \
    test -x /opt/FamDB/famdb.py; \
    test -x /opt/FamDB/utils/download_dfam.py; \
    grep -F "FAMDB_DATA_DIR = /opt/RepeatMasker/Libraries/famdb" /opt/FamDB/famdb.conf >/dev/null

ARG UCSC_TOOLS_BASE=http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64
ARG TWOBITINFO_SHA256=fca5427e1aedd00be0d32117420010c9162d442562c83305b2d3e3c8e6cebe71
ARG BEDTOBIGBED_SHA256=73e10feef3a685304d71c840058ae9a5113bdc4e134f161d3913cfebc5a2ec24

RUN set -eux; \
    mkdir -p /opt/ucsc/bin; \
    for item in \
      "${UCSC_TOOLS_BASE}/twoBitInfo|twoBitInfo|${TWOBITINFO_SHA256}" \
      "${UCSC_TOOLS_BASE}/bedToBigBed|bedToBigBed|${BEDTOBIGBED_SHA256}"; do \
      url="$(printf '%s' "$item" | cut -d '|' -f 1)"; \
      tool="$(printf '%s' "$item" | cut -d '|' -f 2)"; \
      sha256="$(printf '%s' "$item" | cut -d '|' -f 3)"; \
      for attempt in 1 2 3 4 5 6; do \
        if curl \
            --fail \
            --location \
            --show-error \
            --connect-timeout 30 \
            --retry 3 \
            --retry-delay 5 \
            --retry-all-errors \
            -o "$tool" \
            "$url"; then \
          break; \
        fi; \
        if [ "$attempt" = "6" ]; then exit 1; fi; \
        sleep 10; \
      done; \
      echo "${sha256}  ${tool}" | sha256sum -c -; \
      install -m 0755 "$tool" "/opt/ucsc/bin/$tool"; \
    done; \
    test -x /opt/ucsc/bin/twoBitInfo; \
    test -x /opt/ucsc/bin/bedToBigBed

FROM ${RMBLAST_IMAGE} AS rmblast

FROM debian:12-slim

LABEL maintainer="taffish@163.com"

ARG REPEATMASKER_VERSION
ARG FAMDB_VERSION
ARG RMBLAST_VERSION
ARG DEBIAN_MIRROR
ARG DEBIAN_SECURITY_MIRROR

ENV DEBIAN_FRONTEND=noninteractive

RUN set -eux; \
    sed -i \
      -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
      -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
      /etc/apt/sources.list.d/debian.sources; \
    for attempt in 1 2 3 4 5 6; do \
      if apt-get -o Acquire::Retries=3 update \
       && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
            ca-certificates \
            curl \
            gzip \
            hmmer \
            libbz2-1.0 \
            libgomp1 \
            libsqlite3-0 \
            libstdc++6 \
            libzstd1 \
            perl \
            perl-doc \
            python3 \
            python3-h5py \
            tar \
            trf \
            zlib1g; then \
        break; \
      fi; \
      if [ "$attempt" = "6" ]; then exit 1; fi; \
      apt-get clean; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

COPY --from=fetcher /opt/RepeatMasker /opt/RepeatMasker
COPY --from=fetcher /opt/FamDB /opt/FamDB
COPY --from=rmblast /opt/rmblast /opt/rmblast
COPY --from=fetcher /opt/ucsc /opt/ucsc

ENV PATH=/opt/RepeatMasker:/opt/RepeatMasker/util:/opt/FamDB:/opt/FamDB/utils:/opt/rmblast/bin:/opt/ucsc/bin:${PATH}
ENV BLAST_USAGE_REPORT=false
ENV PAGER=cat
ENV REPEATMASKER_LIB_DIR=/opt/RepeatMasker/Libraries

RUN set -eux; \
    printf '%s\n' \
      '#!/bin/sh' \
      'set -eu' \
      'taf_famdb_data_dir=/opt/RepeatMasker/Libraries/famdb' \
      'taf_famdb_configured=/opt/RepeatMasker/.taf-famdb-configured' \
      'taf_has_famdb=0' \
      'for taf_h5 in "$taf_famdb_data_dir"/*.h5; do' \
      '  if [ -e "$taf_h5" ]; then taf_has_famdb=1; break; fi' \
      'done' \
      'if [ "$taf_has_famdb" = 1 ] && [ ! -e "$taf_famdb_configured" ]; then' \
      '  cd /opt/RepeatMasker' \
      '  TERM=dumb perl ./configure -trf_prgm /usr/bin/trf -rmblast_dir /opt/rmblast/bin -hmmer_dir /usr/bin -famdb_dir /opt/FamDB -default_search_engine rmblast >/tmp/taf-repeatmasker-configure.log 2>&1 || { cat /tmp/taf-repeatmasker-configure.log >&2; exit 1; }' \
      '  touch "$taf_famdb_configured"' \
      'fi' \
      'exec RepeatMasker "$@"' \
      > /usr/local/bin/taf-repeatmasker-entrypoint; \
    chmod 0755 /usr/local/bin/taf-repeatmasker-entrypoint

RUN set -eux; \
    cd /opt/RepeatMasker; \
    TERM=dumb perl ./configure \
      -trf_prgm /usr/bin/trf \
      -rmblast_dir /opt/rmblast/bin \
      -hmmer_dir /usr/bin \
      -default_search_engine rmblast; \
    RepeatMasker -v 2>&1 | grep -F "RepeatMasker version ${REPEATMASKER_VERSION}" >/dev/null; \
    taf-repeatmasker-entrypoint -v 2>&1 | grep -F "RepeatMasker version ${REPEATMASKER_VERSION}" >/dev/null; \
    RepeatMasker --help >/tmp/repeatmasker.help 2>&1; \
    grep -F "RepeatMasker is a program that screens DNA sequences" /tmp/repeatmasker.help >/dev/null; \
    rm -f /tmp/repeatmasker.help; \
    rmblastn -version 2>&1 | grep -F "rmblastn: ${RMBLAST_VERSION}+" >/dev/null; \
    trf -v 2>&1 | grep -F "Tandem Repeats Finder, Version 4.09" >/dev/null; \
    nhmmer -h 2>&1 | grep -F "HMMER" >/dev/null; \
    twoBitInfo 2>&1 | grep -F "twoBitInfo" >/dev/null; \
    bedToBigBed 2>&1 | grep -F "bedToBigBed" >/dev/null; \
    famdb.py --help 2>&1 | grep -F "This is famdb.py version ${FAMDB_VERSION}" >/dev/null; \
    download_dfam.py --help 2>&1 | grep -F "Download, verify, and decompress FamDB component files from Dfam" >/dev/null; \
    if famdb.py -i /opt/RepeatMasker/Libraries/famdb info >/tmp/famdb-empty.log 2>&1; then exit 1; fi; \
    grep -F "No .h5 files found" /tmp/famdb-empty.log >/dev/null; \
    grep -F "FAMDB_DATA_DIR = /opt/RepeatMasker/Libraries/famdb" /opt/FamDB/famdb.conf >/dev/null; \
    grep -F "'FAMDB_DIR'" /opt/RepeatMasker/RepeatMaskerConfig.pm >/dev/null; \
    if grep -F "/opt/FamDB" /opt/RepeatMasker/RepeatMaskerConfig.pm >/dev/null; then exit 1; fi; \
    mkdir -p /tmp/repeatmasker-check/out; \
    cd /tmp/repeatmasker-check; \
    printf '>ToyRepeat#DNA/Toy\nACGTTGCATGTCAGTACGATCGTACGATGCTAGCTAGGATCCGATCGT\n' > repeats.fa; \
    printf '>seq1\nNNNNNACGTTGCATGTCAGTACGATCGTACGATGCTAGCTAGGATCCGATCGTNNNNN\n' > input.fa; \
    taf-repeatmasker-entrypoint -pa 1 -engine rmblast -lib repeats.fa -dir out input.fa >/tmp/repeatmasker-check/run.log 2>&1 || { cat /tmp/repeatmasker-check/run.log; exit 1; }; \
    test -s out/input.fa.out; \
    test -s out/input.fa.masked; \
    grep -F "ToyRepeat" out/input.fa.out >/dev/null; \
    grep -F "seq1" out/input.fa.masked >/dev/null; \
    rm -rf /tmp/repeatmasker-check

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=repeatmasker
