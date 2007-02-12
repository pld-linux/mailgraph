%include	/usr/lib/rpm/macros.perl
Summary:	Simple mail statistics for Postfix
Summary(pl.UTF-8):   Proste statystyki dla Postfiksa
Name:		mailgraph
Version:	1.12
Release:	7
License:	GPL v2
Group:		Applications/Networking
Source0:	http://people.ee.ethz.ch/~dws/software/mailgraph/pub/%{name}-%{version}.tar.gz
# Source0-md5:	e3c88ee9ff6e423942ff8ce7038449c4
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}.conf
Patch0:		%{name}-paths.patch
Patch1:		%{name}-postfix_rbl.patch
URL:		http://people.ee.ethz.ch/~dws/software/mailgraph/
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(triggerpostun):	sed >= 4.0
Requires:	apache(mod_cgi)
Requires:	apache(mod_expires)
Requires:	postfix
Requires:	rc-scripts
Requires:	webapps
Requires:	webserver = apache
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_prefix}/lib/cgi-bin/%{_webapp}
%define		_pkglibdir	/var/lib/%{name}

%description
Mailgraph is a very simple mail statistics RRDtool frontend for
Postfix that produces daily, weekly, monthly and yearly graphs of
received/sent and bounced/rejected mail.

%description -l pl.UTF-8
Mailgraph to prosty frontend na RRDtool do statystyk pocztowych dla
Postfiksa. Produkuje wykresy dzienne, tygodniowe, miesięczne i roczne
poczty wysłanej/odebranej i odbitej/odrzuconej.

%prep
%setup	-q
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_sysconfdir},%{_sbindir}} \
	$RPM_BUILD_ROOT{%{_appdir},%{_pkglibdir}/img,/var/log}

install mailgraph.cgi $RPM_BUILD_ROOT%{_appdir}/index.cgi
install mailgraph.pl $RPM_BUILD_ROOT%{_sbindir}/mailgraph.pl
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/mailgraph
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
touch $RPM_BUILD_ROOT/var/log/mailgraph.log

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- syslog >= 1.4.1-19
m=$(%addusertogroup stats syslog)
if [ -n "$m" ]; then
	echo >&2 "$m"
	%service %{name} restart
fi

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
if [ ! -f /var/log/mailgraph.log ]; then
	touch /var/log/mailgraph.log
	chown stats /var/log/mailgraph.log
fi

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%triggerin -- apache1 < 1.3.37-3, apache1-base
m=$(%addusertogroup http stats)
if [ -n "$m" ]; then
	echo >&2 "$m"
	%service apache restart
fi
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
m=$(%addusertogroup http stats)
if [ -n "$m" ]; then
	echo >&2 "$m"
	%service httpd restart
fi
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name} < 1.12-2.2
# nuke very-old config location (this mostly for Ra)
if [ -f /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}.conf/d" /etc/httpd/httpd.conf
fi

# migrate from httpd (apache2) config dir
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	cp -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/httpd.conf
	sed -i -e 's,/usr/share/mailgraph,%{_appdir},' %{_sysconfdir}/httpd.conf
fi

rm -f /etc/httpd/conf.d/99_mailgraph.conf
/usr/sbin/webapp register httpd %{_webapp}
%service -q httpd reload

%triggerpostun -- %{name} < 1.12-6
chown stats:stats %{_pkglibdir}/*.rrd

%files
%defattr(644,root,root,755)
%doc README CHANGES
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(755,root,root) %{_sbindir}/mailgraph.pl
%attr(754,root,root) /etc/rc.d/init.d/mailgraph
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mailgraph
%dir %{_appdir}
%attr(755,root,root) %{_appdir}/index.cgi
%attr(770,root,stats) %dir %{_pkglibdir}
%attr(775,root,http) %dir %{_pkglibdir}/img
%ghost /var/log/mailgraph.log
