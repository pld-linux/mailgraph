Summary:	Simple mail statistics for Postfix
Summary(pl.UTF-8):	Proste statystyki dla Postfiksa
Name:		mailgraph
Version:	1.14
Release:	3
License:	GPL v2
Group:		Applications/Networking
Source0:	http://mailgraph.schweikert.ch/pub/%{name}-%{version}.tar.gz
# Source0-md5:	0f0ae91968ea7ae0c1d14985c560530b
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Source3:	%{name}-apache.conf
Source4:	lighttpd.conf
Source5:	http://oss.oetiker.ch/rrdtool/.pics/rrdtool.gif
# Source5-md5:	51ab9e952ecfffa45b2c65eacc93f3a2
Source6:	%{name}-httpd.conf
Patch0:		%{name}-paths.patch
Patch1:		%{name}-postfix_rbl.patch
Patch2:		clamd-enable.patch
Patch3:		rrdtool-url.patch
URL:		http://mailgraph.schweikert.ch/
BuildRequires:	perl-tools-pod
BuildRequires:	rpm-perlprov
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires(triggerpostun):	sed >= 4.0
Requires:	postfix
Requires:	rc-scripts
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

%package cgi
Summary:	CGI script for displaying mailgraph rrd data
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Requires:	webapps
Requires:	webserver
Requires:	webserver(cgi)
Conflicts:	apache-base < 2.4.0-1

%description cgi
CGI script for displaying mailgraph rrd data.

%prep
%setup	-q
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1

%build
pod2man mailgraph.pl > mailgraph.1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig},%{_sysconfdir},%{_sbindir},%{_mandir}/man1} \
	$RPM_BUILD_ROOT{%{_appdir},%{_pkglibdir}/img,/var/log}

install -p mailgraph.cgi $RPM_BUILD_ROOT%{_appdir}/index.cgi
install -p mailgraph.pl $RPM_BUILD_ROOT%{_sbindir}/mailgraph.pl
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -a mailgraph.1 $RPM_BUILD_ROOT%{_mandir}/man1
cp -a %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/mailgraph
touch $RPM_BUILD_ROOT/var/log/mailgraph.log

# cgi app
cp -a %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf
cp -a mailgraph.css $RPM_BUILD_ROOT%{_sysconfdir}/mailgraph.css
cp -a %{SOURCE5} $RPM_BUILD_ROOT%{_appdir}
ln -sf %{_sysconfdir}/mailgraph.css $RPM_BUILD_ROOT%{_appdir}/mailgraph.css

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
if [ ! -f /var/log/mailgraph.log ]; then
	touch /var/log/mailgraph.log
	chown http /var/log/mailgraph.log
fi

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%triggerin cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun cgi -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin cgi -- apache-base
%webapp_register httpd %{_webapp}

%triggerun cgi -- apache-base
%webapp_unregister httpd %{_webapp}

%triggerin cgi -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun cgi -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%triggerpostun -- %{name} < 1.14-2.1
chown http:http %{_pkglibdir}/*.rrd

%files
%defattr(644,root,root,755)
%doc README CHANGES
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mailgraph
%attr(754,root,root) /etc/rc.d/init.d/mailgraph
%attr(755,root,root) %{_sbindir}/mailgraph.pl
%{_mandir}/man1/mailgraph.1*
%attr(770,root,http) %dir %{_pkglibdir}
%ghost /var/log/mailgraph.log

%files cgi
%defattr(644,root,root,755)
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mailgraph.css
%dir %{_appdir}
%attr(755,root,root) %{_appdir}/index.cgi
%{_appdir}/mailgraph.css
%{_appdir}/rrdtool.gif
%attr(775,root,http) %dir %{_pkglibdir}/img
