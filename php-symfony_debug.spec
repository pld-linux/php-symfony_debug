#
# Conditional build:
%bcond_without	tests		# build without tests

%define		php_name	php%{?php_suffix}
%define		modname	symfony_debug
Summary:	Symfony Debug Extension
Name:		%{php_name}-%{modname}
Version:	2.7.3
Release:	1
License:	MIT
Group:		Development/Languages/PHP
Source0:	https://github.com/symfony/Debug/archive/v%{version}/Debug-%{version}.tar.gz
# Source0-md5:	74b1ec1c41ae362d48b39e424fc78232
Patch0:		tests.patch
URL:		https://github.com/symfony/Debug/tree/2.7/Resources/ext
%{?with_tests:BuildRequires:    %{php_name}-cli}
BuildRequires:	%{php_name}-devel >= 4:5.3
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-pcre
BuildRequires:	%{php_name}-spl
%endif
%{?requires_php_extension}
Provides:	php(symfony_debug) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This extension publishes several functions to help building powerful
debugging tools.

%prep
%setup -qc
mv Debug-%{version}/* .
%patch0 -p1

%build
cd Resources/ext
phpize
%configure
%{__make}

%if %{with tests}
# simple module load test
%{__php} -n -q \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

cat <<'EOF' > run-tests.sh
#!/bin/sh
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="pcre spl" \
	RUN_TESTS_SETTINGS="-q $*"
EOF

chmod +x run-tests.sh
./run-tests.sh -w failed.log
test -f failed.log -a ! -s failed.log
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C Resources/ext install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
