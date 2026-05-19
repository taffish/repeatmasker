ARG REPEATMASKER_VERSION=4.2.3
ARG REPEATMASKER_ARCHIVE=RepeatMasker-4.2.3.tar.gz
ARG REPEATMASKER_SHA256=832e2b22aef6763ef7d5dd2771eef22f7dd8b9738bea0e1d81295aa511b61e6a
ARG RMBLAST_VERSION=2.17.1
ARG RMBLAST_IMAGE=ghcr.io/taffish/rmblast:2.17.1-r1
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
ARG DEBIAN_SECURITY_MIRROR=http://deb.debian.org/debian-security

FROM debian:12-slim AS fetcher

ARG REPEATMASKER_ARCHIVE
ARG REPEATMASKER_SHA256
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
      "https://www.repeatmasker.org/RepeatMasker/${REPEATMASKER_ARCHIVE}|${REPEATMASKER_ARCHIVE}|${REPEATMASKER_SHA256}"; do \
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
    test -r /opt/RepeatMasker/LICENSE

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
COPY --from=rmblast /opt/rmblast /opt/rmblast
COPY --from=fetcher /opt/ucsc /opt/ucsc

ENV PATH=/opt/RepeatMasker:/opt/RepeatMasker/util:/opt/rmblast/bin:/opt/ucsc/bin:${PATH}
ENV BLAST_USAGE_REPORT=false
ENV REPEATMASKER_LIB_DIR=/opt/RepeatMasker/Libraries

RUN set -eux; \
    cd /opt/RepeatMasker; \
    TERM=dumb perl ./configure \
      -trf_prgm /usr/bin/trf \
      -rmblast_dir /opt/rmblast/bin \
      -hmmer_dir /usr/bin \
      -default_search_engine rmblast; \
    RepeatMasker -v 2>&1 | grep -F "RepeatMasker version ${REPEATMASKER_VERSION}" >/dev/null; \
    rmblastn -version 2>&1 | grep -F "rmblastn: ${RMBLAST_VERSION}+" >/dev/null; \
    trf -v 2>&1 | grep -F "Tandem Repeats Finder, Version 4.09" >/dev/null; \
    nhmmer -h 2>&1 | grep -F "HMMER" >/dev/null; \
    twoBitInfo 2>&1 | grep -F "twoBitInfo" >/dev/null; \
    bedToBigBed 2>&1 | grep -F "bedToBigBed" >/dev/null; \
    famdb.py -i /opt/RepeatMasker/Libraries/famdb info 2>&1 | grep -F "Database: Dfam" >/dev/null; \
    famdb.py -i /opt/RepeatMasker/Libraries/famdb info 2>&1 | grep -F "Version : 3.9" >/dev/null; \
    mkdir -p /tmp/repeatmasker-check/out; \
    cd /tmp/repeatmasker-check; \
    printf '>ToyRepeat#DNA/Toy\nACGTTGCATGTCAGTACGATCGTACGATGCTAGCTAGGATCCGATCGT\n' > repeats.fa; \
    printf '>seq1\nNNNNNACGTTGCATGTCAGTACGATCGTACGATGCTAGCTAGGATCCGATCGTNNNNN\n' > input.fa; \
    RepeatMasker -pa 1 -engine rmblast -lib repeats.fa -dir out input.fa >/tmp/repeatmasker-check/run.log 2>&1; \
    test -s out/input.fa.out; \
    test -s out/input.fa.masked; \
    grep -F "ToyRepeat" out/input.fa.out >/dev/null; \
    grep -F "seq1" out/input.fa.masked >/dev/null; \
    rm -rf /tmp/repeatmasker-check

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=repeatmasker
