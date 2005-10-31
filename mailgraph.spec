#
# TODO:
# - IMPORTANT: don't make temporary files in /tmp that are picked by apache
#
%include	/usr/lib/rpm/macros.perl
Summary:	Simple mail statistics for Postfix
Summary(pl):	Proste statystyki dla Postfiksa
Name:		mailgraph
Version:	1.12
Release:	1
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
BuildRequires:	rpmbuild(macros) >= 1.176
PreReq:		rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun):	grep
Requires(preun):	fileutils
Requires:	apache-mod_expires
Requires:	postfix
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}
%define		_httpappsdir		%{_datadir}/%{name}

%description
Mailgraph is a very simple mail statistics RRDtool frontend for
Postfix that produces daily, weekly, monthly and yearly graphs of
received/sent and bounced/rejected mail.

%description -l pl
Mailgraph to prosty frontend na RRDtool do statystyk pocztowych dla
Postfiksa. Produkuje wykresy dzienne, tygodniowe, miesiêczne i roczne
poczty wys³anej/odebranej i odbitej/odrzuconej.

%prep
%setup	-q
%patch0 -p1
%patch1 -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d/init.d,sysconfig,httpd},%{_bindir}} \
	$RPM_BUILD_ROOT{%{_httpappsdir},%{_pkglibdir}}

install mailgraph.cgi $RPM_BUILD_ROOT%{_httpappsdir}/index.cgi
install mailgraph.pl $RPM_BUILD_ROOT%{_bindir}/mailgraph.pl

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/mailgraph
install %{SOURCE3} $RPM_BUILD_ROOT/etc/httpd/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*/%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
elif [ -d /etc/httpd/httpd.conf ]; then
	ln -sf /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi
if [ -f /var/lock/subsys/%{name} ]; then
	/etc/rc.d/init.d/%{name} restart 1>&2
else
	%banner %{name} -e <<EOF
Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon.
EOF
fi

%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			/etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
	fi
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
	if [ -f /var/lock/subsys/%{name} ]; then
		/etc/rc.d/init.d/%{name} stop 1>&2
	fi
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc README CHANGES
%attr(755,root,root) %{_bindir}/mailgraph.pl
%attr(754,root,root) /etc/rc.d/init.d/mailgraph
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/sysconfig/mailgraph
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) /etc/httpd/mailgraph.conf
%dir %{_httpappsdir}
%attr(755,root,root) %{_httpappsdir}/index.cgi
%attr(771,root,stats) %dir %{_pkglibdir}
