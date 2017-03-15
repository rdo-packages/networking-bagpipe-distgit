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
Source1:        %{servicename}.service

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-coverage
BuildRequires:  python-hacking
BuildRequires:  python-oslo-sphinx
BuildRequires:  python-oslotest
BuildRequires:  python-oslo-rootwrap
BuildRequires:  python-pbr
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  python-subunit
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools
BuildRequires:  python-pecan

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
Requires:       python-netaddr
Requires:       python-oslo-db >= 4.15.0
Requires:       python-oslo-config >= 2:3.9.0
Requires:       python-oslo-concurrency >= 3.8.0
Requires:       python-oslo-i18n >= 2.1.0
Requires:       python-oslo-log >= 3.11.0
Requires:       python-oslo-messaging >= 5.14.0
Requires:       python-oslo-service >= 1.10.0
Requires:       python-oslo-rootwrap
Requires:       python-pecan
Requires:       python-setuptools
Requires:       python-exabgp >= 4.0.1
Requires:       python-pyroute2
Requires:       python-stevedore
Requires:       python-six

%description -n python2-%{pypi_name}
BaGPipe BGP is a lightweight implementation of BGP VPNs (IP VPNs and E-VPNs),
targeting deployments on servers hosting VMs, in particular for Openstack/KVM
platforms.

%package -n python-%{pypi_name}-doc
Summary:        networking-bagpipe documentation

%description -n python-%{pypi_name}-doc
Documentation for networking-bagpipe

%package -n openstack-%{servicename}
Summary:    Networking-BaGPipe
Requires:   python-networking-bagpipe = %{version}-%{release}
Requires:   openstack-neutron-common

%description -n openstack-%{servicename}
Bagpipe-BGP service

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%py2_build
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install

# bagpipe _sysconfdir and conf files
install -p -D -m 0640 %{buildroot}/etc/%{servicename}/bgp.conf.template %{buildroot}%{_sysconfdir}/neutron/%{servicename}/bgp.conf
install -p -D -m 0640 %{buildroot}/etc/%{servicename}/rootwrap.conf %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.conf
install -p -D -m 0640 %{buildroot}/etc/%{servicename}/rootwrap.d/linux-vxlan.filters  %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.d/linux-vxlan.filters
install -p -D -m 0640 %{buildroot}/etc/%{servicename}/rootwrap.d/mpls-ovs-dataplane.filters  %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.d/mpls-ovs-dataplane.filters

# remove unneeded files
rm -rf %{buildroot}/etc/%{servicename}

# systemd service
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{servicename}.service

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
%{_bindir}/bagpipe-fakerr
%{_bindir}/bagpipe-impex2dot
%{_bindir}/bagpipe-looking-glass
%{_bindir}/bagpipe-rest-attach

%files -n python-%{pypi_name}-doc
%license LICENSE

%files -n openstack-%{servicename}
%license LICENSE
%{_unitdir}/%{servicename}.service
%{_bindir}/bagpipe-bgp
%{_bindir}/bagpipe-bgp-cleanup
%dir  %attr(0750, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/
%config(noreplace) %attr(0640, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/*.conf
%config(noreplace) %attr(0640, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/rootwrap.d/*.filters

%changelog

