%include	/usr/lib/rpm/macros.perl
Summary:	Simple mail statistics for Postfix
Summary(pl):	Proste statystyki dla Postfiksa
Name:		mailgraph
Version:	0.22
Release:	1
License:	GPL
Group:		Applications/Networking
Source0:	http://people.ee.ethz.ch/~dws/software/mailgraph/pub/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-paths.patch
URL:		http://people.ee.ethz.ch/~dws/software/mailgraph/
Prereq:		/sbin/chkconfig
Prereq:		rc-scripts
Prereq:		grep
Requires:	postfix
Requires:	apache-mod_expires
Provides:	%{name}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}

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

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_pkglibdir},/etc/rc.d/init.d,/etc/httpd,\
	/home/services/httpd/html/mailgraph/imgs,%{_bindir}}

install mailgraph.cgi $RPM_BUILD_ROOT/home/services/httpd/html/mailgraph/mailgraph.cgi
install mailgraph.pl $RPM_BUILD_ROOT%{_bindir}/mailgraph.pl

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf

%post
/sbin/chkconfig --add %{name}
if [ -f %{_sysconfdir}/httpd/httpd.conf ] && \
        ! grep -q "^Include.*/%{name}.conf" %{_sysconfdir}/httpd/httpd.conf; then
                echo "Include %{_sysconfdir}/httpd/%{name}.conf" >> %{_sysconfdir}/httpd/httpd.conf
        if [ -f /var/lock/subsys/httpd ]; then
                /etc/rc.d/init.d/httpd restart 1>&2
        fi
fi
if [ -f /var/lock/subsys/%{name} ]; then
        /etc/rc.d/init.d/%{name} restart 1>&2
else
        echo "Run \"/etc/rc.d/init.d/%{name} start\" to start %{name} daemon."
fi

%preun
if [ "$1" = "0" ]; then
	grep -E -v "^Include.*%{name}.conf" %{_sysconfdir}/httpd/httpd.conf > \
		%{_sysconfdir}/httpd/httpd.conf.tmp
	mv -f %{_sysconfdir}/httpd/httpd.conf.tmp %{_sysconfdir}/httpd/httpd.conf
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
	if [ -f /var/lock/subsys/%{name} ]; then
        	/etc/rc.d/init.d/%{name} stop 1>&2
    	fi
	/sbin/chkconfig --del %{name}
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/mailgraph.pl
%attr(755,root,root) /home/services/httpd/html/mailgraph/mailgraph.cgi
%attr(754,root,root) /etc/rc.d/init.d/mailgraph
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/mailgraph.conf
%dir %{_pkglibdir}
%attr(771,root,http) %dir /home/services/httpd/html/mailgraph/imgs
%doc README CHANGES
