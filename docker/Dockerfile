ARG DEBIAN_IMAGE=debian:12-slim@sha256:a4672c0cb26fbdde88e38fa2dfb6c681942306680e41e4378b28770b6e79ee91
ARG RMBLAST_IMAGE=ghcr.io/taffish/rmblast:2.17.1-r1@sha256:3f39ff327be4108bc35611f6c620208d4155bf6058650e94f18478f353d0b4c1
# 构建来源维护：两个 image digest 固定身份，不保证 registry 永久保留；拉取失败先核对 amd64 与仓库。
# 不去掉 digest 或偷偷改用新镜像；实际材料变更须在候选中重验，已发布身份通过后继 release 修复。
FROM ${DEBIAN_IMAGE} AS fetcher
ARG TARGETARCH
# fetcher/final 的 APT 仍依赖活动 Debian 仓库；镜像 digest 不锁定后续包，重试不能恢复已下架材料。
RUN test "${TARGETARCH}" = amd64 && apt-get -o Acquire::Retries=3 update \
 && apt-get -o Acquire::Retries=3 install -y --no-install-recommends ca-certificates curl gzip tar \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /tmp/build
# RepeatMasker/FamDB tag 归档有固定 SHA256；404/不匹配先检查官方来源、文件类型及下载完整性。
# UCSC 两个工具采用官方一次性冻结的 linux.x86_64.v479，不使用无版本滚动目录。
# 冻结说明：https://groups.google.com/a/soe.ucsc.edu/g/genome-mirror/c/7knco87cYd8
# URL 固定版本，SHA256 固定字节；这不保证上游永久托管，也不代表整套 APT 依赖已锁定。
# 404/校验失败先核对官方来源与完整下载；不得退回 rolling、删校验或仅重算哈希。
# 旧材料不可得须如实记录；更换官方冻结版本或固定 Kent commit 源码构建后，重验
# twoBitInfo -noNs 和 rmToTrackHub 的两类 bigBed；已发布身份通过后继 release 修复。
RUN set -eu; \
    curl -fL --retry 3 --retry-all-errors https://codeload.github.com/Dfam-consortium/RepeatMasker/tar.gz/refs/tags/v4.2.5 -o repeatmasker.tar.gz; \
    echo '2a863a62c01d631f733ee0e9d01278241a96dfc168dc8eb974c43a44bcf1d570  repeatmasker.tar.gz' | sha256sum -c -; \
    curl -fL --retry 3 --retry-all-errors https://codeload.github.com/Dfam-consortium/FamDB/tar.gz/refs/tags/3.0.0 -o famdb.tar.gz; \
    echo 'cad4652696cbd6b3444ef1ea008764e4807eba503410bf24357c4505a5ddb8d4  famdb.tar.gz' | sha256sum -c -; \
    mkdir -p /opt/RepeatMasker/Libraries/famdb /opt/FamDB /opt/ucsc/bin; \
    tar -xzf repeatmasker.tar.gz -C /opt/RepeatMasker --strip-components=1; \
    tar -xzf famdb.tar.gz -C /opt/FamDB --strip-components=1; \
    sed -i 's|# FAMDB_DATA_DIR = /path/to/famdb/directory|FAMDB_DATA_DIR = /opt/RepeatMasker/Libraries/famdb|' /opt/FamDB/famdb.conf; \
    curl -fL --retry 3 --retry-all-errors https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.v479/twoBitInfo -o /opt/ucsc/bin/twoBitInfo; \
    echo '406001e3f150f2caecf4846a1fd287341bda0303113641a3a6f5719bab435996  /opt/ucsc/bin/twoBitInfo' | sha256sum -c -; \
    curl -fL --retry 3 --retry-all-errors https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64.v479/bedToBigBed -o /opt/ucsc/bin/bedToBigBed; \
    echo 'aa42073701d102b7eb5f7e6fe3c8f8057e5f983fb9967a9e501f044eb14c99f0  /opt/ucsc/bin/bedToBigBed' | sha256sum -c -; \
    chmod 0755 /opt/ucsc/bin/*; chmod -R a+rX /opt/RepeatMasker /opt/FamDB
FROM ${RMBLAST_IMAGE} AS rmblast
FROM ${DEBIAN_IMAGE}
LABEL maintainer="taffish@163.com"
ENV DEBIAN_FRONTEND=noninteractive
# hmmer/trf/Perl/Python 等运行依赖未完整锁定；debian-packages.tsv 是事后清单，不是安装输入 lock。
# 缺包先核对仓库分支/包身份；换用同版本可信材料或核验快照，若升级则重验 RepeatMasker 各引擎与离线路径。
RUN apt-get -o Acquire::Retries=3 update \
 && apt-get -o Acquire::Retries=3 install -y --no-install-recommends \
    ca-certificates curl gzip hmmer libbz2-1.0 libgomp1 libsqlite3-0 libstdc++6 \
    libzstd1 perl perl-doc python3 python3-h5py python3-pandas tar trf zlib1g \
 && mkdir -p /usr/share/taffish-repeatmasker \
 && dpkg-query -W > /usr/share/taffish-repeatmasker/debian-packages.tsv \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && find /usr/lib/python3 /usr/lib/python3.11 -type d -name __pycache__ -prune -exec rm -rf '{}' +
COPY --from=fetcher /opt/RepeatMasker /opt/RepeatMasker
COPY --from=fetcher /opt/FamDB /opt/FamDB
COPY --from=fetcher /opt/ucsc /opt/ucsc
COPY --from=rmblast /opt/rmblast /opt/rmblast
COPY docker/kent-LICENSE /opt/ucsc/LICENSE
COPY docker/dfam-4.0.catalog.json /opt/taffish-repeatmasker/dfam-4.0.catalog.json
COPY docker/patch-cache.py /opt/taffish-repeatmasker/patch-cache.py
COPY docker/patch-html.py /opt/taffish-repeatmasker/patch-html.py
COPY docker/landscape.html /opt/taffish-repeatmasker/landscape.html
COPY docker/taf-repeatmasker-landscape.py /usr/local/bin/taf-repeatmasker-landscape
COPY docker/taf-repeatmasker-dfam.py /usr/local/bin/taf-repeatmasker-dfam
COPY docker/RepeatMasker /usr/local/bin/RepeatMasker
COPY docker/taf-repeatmasker-smoke /usr/local/bin/taf-repeatmasker-smoke
ENV PATH=/usr/local/bin:/opt/RepeatMasker:/opt/RepeatMasker/util:/opt/FamDB:/opt/FamDB/utils:/opt/rmblast/bin:/opt/ucsc/bin:${PATH} \
    BLAST_USAGE_REPORT=false PAGER=cat PYTHONDONTWRITEBYTECODE=1 \
    REPEATMASKER_LIB_DIR=/opt/RepeatMasker/Libraries
RUN set -eu; \
    chmod 0755 /usr/local/bin/RepeatMasker /usr/local/bin/taf-repeatmasker-dfam /usr/local/bin/taf-repeatmasker-smoke /usr/local/bin/taf-repeatmasker-landscape; \
    ln -s RepeatMasker /usr/local/bin/taf-repeatmasker-entrypoint; \
    cd /opt/RepeatMasker; \
    TERM=dumb perl ./configure -trf_prgm /usr/bin/trf -rmblast_dir /opt/rmblast/bin -hmmer_dir /usr/bin -default_search_engine rmblast; \
    python3 /opt/taffish-repeatmasker/patch-cache.py; \
    python3 /opt/taffish-repeatmasker/patch-html.py; \
    python3 -c 'import h5py, pandas'; \
    taf-repeatmasker-smoke identity; taf-repeatmasker-smoke tiny
# Keep upstream examples, runtime data, Perl POD and all license notices.
# Debian-generated bytecode was removed in its installation layer above.
WORKDIR /tmp
ENV TAFFISH_ENV=TAFFISH TAFFISH_NAME=repeatmasker
