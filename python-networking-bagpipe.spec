%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%global servicename bagpipe-bgp
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pypi_name}
Version:        XXX
Release:        XXX
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend

License:        ASL 2.0
URL:            https://github.com/openstack/networking-bagpipe
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-coverage
BuildRequires:  python-hacking
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-oslotest
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-subunit
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python2-devel

%description
BaGPipe BGP is a lightweight implementation of BGP VPNs (IP VPNs and E-VPNs),
targeting deployments on servers hosting VMs, in particular for Openstack/KVM
platforms.

%package -n     python2-%{pypi_name}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python-pbr >= 1.8
Requires:       python-babel >= 2.3.4
Requires:       python-neutron-lib >= 1.1.0
Requires:       python-oslo-db >= 4.15.0
Requires:       python-oslo-config >= 2:3.9.0
Requires:       python-oslo-concurrency >= 3.8.0
Requires:       python-oslo-i18n >= 2.1.0
Requires:       python-oslo-log >= 3.11.0
Requires:       python-oslo-messaging >= 5.14.0
Requires:       python-oslo-service >= 1.10.0
Requires:       python-setuptools

%description -n python2-%{pypi_name}
BaGPipe BGP is a lightweight implementation of BGP VPNs (IP VPNs and E-VPNs),
targeting deployments on servers hosting VMs, in particular for Openstack/KVM
platforms.

%package -n python-%{pypi_name}-doc
Summary:        networking-bagpipe documentation
%description -n python-%{pypi_name}-doc
Documentation for networking-bagpipe

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install
cp %{buildroot}/%{_bindir}/neutron-bagpipe-linuxbridge-agent %{buildroot}/%{_bindir}/neutron-bagpipe-linuxbridge-agent-2
ln -sf %{_bindir}/neutron-bagpipe-linuxbridge-agent-2 %{buildroot}/%{_bindir}/neutron-bagpipe-linuxbridge-agent-%{python2_version}

%package -n openstack-%{servicename}
Summary:    Networking-BGP

%description -n openstack-%{servicename}
Networking-BGP


%post -n openstack-%{servicename}
%systemd_post %{servicename}.service

%preun -n openstack-%{servicename}
%systemd_preun %{servicename}.service

%postun -n openstack-%{servicename}
%systemd_postun_with_restart %{servicename}.service

%files -n python2-%{pypi_name}
%license LICENSE
%doc README.rst
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%{_bindir}/neutron-bagpipe-linuxbridge-agent
%{_bindir}/neutron-bagpipe-linuxbridge-agent-2
%{_bindir}/neutron-bagpipe-linuxbridge-agent-%{python2_version}
%{_bindir}/bagpipe-bgp
%{_bindir}/bagpipe-bgp-cleanup
%{_bindir}/bagpipe-fakerr
%{_bindir}/bagpipe-impex2dot
%{_bindir}/bagpipe-looking-glass
%{_bindir}/bagpipe-rest-attach
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/bagpipe-bgp/*.conf
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/bagpipe-bgp/rootwrap.d/*.filters
%config(noreplace) %attr(0640, root, neutron) %{_sysconfdir}/bagpipe-bgp/*.template

%files -n python-%{pypi_name}-doc
%license LICENSE

%changelog
* Wed Mar 15 2017 Luke Hinds <lhinds@redhat.com> - 6.0.0
- Initial package.
- Added new file directives from bagpipe-bgp merge into networking-bagpipe
