#-----------------------------------------------------------
# imagefile
#
# References:
#  http://msdn2.microsoft.com/en-us/library/a329t4ed(VS\.80)\.aspx
#  CWDIllegalInDllSearch: http://support.microsoft.com/kb/2264107
#  http://carnal0wnage.attackresearch.com/2012/04/privilege-escalation-via-sticky-keys.html
#  'Auto' value - https://docs.microsoft.com/en-us/windows/desktop/debug/configuring-automatic-debugging
#  https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-R2-and-2012/dn408187(v=ws.11)
#
# Change history:
#  20200515 - updated date output format
#  20190829 - added check for AuditLevel value
#  20190511 - added search for 'auto' value
#  20131007 - added Carnal0wnage reference
#  20130425 - added alertMsg() functionality
#  20130410 - added Wow6432Node support
#  20100824 - added check for "CWDIllegalInDllSearch" value
#
# copyright 2019-2020 Quantum Analytics Research, LLC
# Author: H. Carvey, keydet89@yahoo.com
#-----------------------------------------------------------
package imagefile;
use strict;

my %config = (hive          => "Software",
              hasShortDescr => 1,
              hasDescr      => 0,
              hasRefs       => 0,
              osmask        => 22,
              category      => "persistence",
              version       => 20200515);

sub getConfig{return %config}
sub getShortDescr {
	return "Checks ImageFileExecutionOptions subkeys values";	
}
sub getDescr{}
sub getRefs {}
sub getHive {return $config{hive};}
sub getVersion {return $config{version};}

my $VERSION = getVersion();

sub pluginmain {
	my $class = shift;
	my $hive = shift;
	::logMsg("Launching imagefile v.".$VERSION);
	::rptMsg("imagefile v.".$VERSION); # banner
    ::rptMsg("(".getHive().") ".getShortDescr()."\n"); # banner
	my $reg = Parse::Win32Registry->new($hive);
	my $root_key = $reg->get_root_key;
	my @paths = ("Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options",
	             "Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options");
	
	foreach my $key_path (@paths) {
		my $key;
		if ($key = $root_key->get_subkey($key_path)) {
			::rptMsg($key_path);
#			::rptMsg("LastWrite Time ".gmtime($key->get_timestamp())." (UTC)");
#			::rptMsg("");
		
			my @subkeys = $key->get_list_of_subkeys();
			if (scalar(@subkeys) > 0) {
				my %debug;
				my $i = "Your Image File Name here without a path";
				foreach my $s (@subkeys) {
					my $name = $s->get_name();
					next if ($name =~ m/^$i/i);
					my $debugger;
					eval {
						$debugger = $s->get_value("Debugger")->get_data();
					};
# If the eval{} throws an error, it's b/c the Debugger value isn't
# found within the key, so we don't need to do anything w/ the error
					if ($debugger ne "") {
						$debug{$name}{debug} = $debugger;
						$debug{$name}{lastwrite} = $s->get_timestamp();
					}
			
					my $dllsearch = "";
					eval {
						$dllsearch = $s->get_value("CWDIllegalInDllSearch")->get_data();
					};
# 20190511 - added search for 'auto' value					
					eval {
						$debug{$name}{auto} = $s->get_value("Auto")->get_data();
					};
# 20190829 - added check for AuditLevel value
					eval {
						$debug{$name}{auditlevel} = $s->get_value("AuditLevel")->get_data();
					};
		
					if ($dllsearch ne "") {
						$debug{$name}{dllsearch} = sprintf "0x%x",$dllsearch;
						$debug{$name}{lastwrite} = $s->get_timestamp();
					}
				}
			
				if (scalar (keys %debug) > 0) {
					foreach my $d (keys %debug) {
						::rptMsg($d."  LastWrite: ".::getDateFromEpoch($debug{$d}{lastwrite})."Z");
						::rptMsg("  Debugger             : ".$debug{$d}{debug}) if (exists $debug{$d}{debug});
						::rptMsg("  Auto                 : ".$debug{$d}{auto}) if (exists $debug{$d}{auto});
						::rptMsg("  CWDIllegalInDllSearch: ".$debug{$d}{dllsearch}) if (exists $debug{$d}{dllsearch});
						::rptMsg("  AuditLevel           : ".$debug{$d}{auditlevel}) if (exists $debug{$d}{auditlevel});
					}
				}
				else {
					::rptMsg("No Debugger/CWDIllegalInDllSearch values found.");
				}
				::rptMsg("");
			}
			else {
				::rptMsg($key_path." has no subkeys.");
			}
		}
		else {
			::rptMsg($key_path." not found.");
		}
	}
}
1;