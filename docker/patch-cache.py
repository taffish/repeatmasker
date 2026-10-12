#!/usr/bin/python3
"""Asserted readonly-runtime compatibility patches; no search algorithm edits."""
from pathlib import Path
p = Path('/opt/RepeatMasker/RepeatMasker')
old = 'my @LIBPATH = ( $LIBDIR,\n                $ENV{\'HOME\'} . "/.RepeatMaskerCache" );'
new = 'my @LIBPATH = (); # TAFFISH: readonly install/HOME; use the job tempdir below.'
source = p.read_text()
assert source.count(old) == 1, 'upstream cache layout changed; review patch'
p.write_text(source.replace(old, new))

# ProcessRepeats reads config in BEGIN and does not resolve env overrides.
# A per-process computed config value also covers raw upstream helper commands.
p = Path('/opt/RepeatMasker/RepeatMaskerConfig.pm')
source = p.read_text()
assert source.rstrip().endswith('1;')
addition = "\n$RepeatMaskerConfig::configuration->{'FAMDB_DIR'}->{'value'} = "
addition += "exists $ENV{'FAMDB_DIR'} ? $ENV{'FAMDB_DIR'} : "
addition += "(-s '/opt/RepeatMasker/Libraries/famdb/taffish-famdb.ready' ? '/opt/FamDB' : '');\n"
p.write_text(source.rstrip()[:-2] + addition + '1;\n')

# The protein helper has a separate cache search without a /tmp fallback.
p = Path('/opt/RepeatMasker/RepeatProteinMask')
source = p.read_text()
old = 'my @prot_search_path = (\n  "$LIBDIR/$prot_cache_name",\n  "$ENV{HOME}/.RepeatMaskerCache/$prot_cache_name",\n);'
new = 'require File::Temp;\nmy $taf_prot_root = File::Temp::tempdir("taf-repeatmasker-protein-XXXXXXXX", TMPDIR => 1, CLEANUP => 1);\nmy @prot_search_path = ( "$taf_prot_root/$prot_cache_name" );'
assert source.count(old) == 1, 'upstream protein cache layout changed'
p.write_text(source.replace(old, new))

# Taxonomy previously captured the configuration at Perl module load time,
# before RepeatMasker applies documented FAMDB_DIR / -famdb_dir overrides.
p = Path('/opt/RepeatMasker/Taxonomy.pm')
source = p.read_text()
old = 'my $FAMDB = $RepeatMaskerConfig::configuration->{\'FAMDB_DIR\'}->{\'value\'} . "/famdb.py";'
new = 'my $FAMDB; # TAFFISH: resolve after command-line/environment overrides.'
assert source.count(old) == 1, 'upstream Taxonomy configuration changed'
source = source.replace(old, new)
old = 'sub new {\n  my $class = shift;'
new = old + '\n  $FAMDB = $RepeatMaskerConfig::configuration->{\'FAMDB_DIR\'}->{\'value\'} . "/famdb.py";'
assert source.count(old) == 1, 'upstream Taxonomy constructor changed'
p.write_text(source.replace(old, new))
