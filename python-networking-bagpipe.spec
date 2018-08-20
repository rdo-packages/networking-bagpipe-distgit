%global milestone .0rc1
%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%global servicename bagpipe-bgp
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global common_desc \
BaGPipe BGP is a lightweight implementation of BGP VPNs (IP VPNs and E-VPNs), \
targeting deployments on servers hosting VMs, in particular for Openstack/KVM \
platforms.

Name:           python-%{pypi_name}
Version:        9.0.0
Release:        0.1%{?milestone}%{?dist}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend

License:        ASL 2.0
URL:            https://github.com/openstack/networking-bagpipe
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#
# patches_base=9.0.0.0rc1
#

Source1:        %{servicename}.service

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-hacking
BuildRequires:  python2-oslotest
BuildRequires:  python2-oslo-rootwrap
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools
BuildRequires:  python2-subunit
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools
BuildRequires:  python2-pecan
BuildRequires:  systemd
%description
%{common_desc}

%package -n     python2-%{pypi_name}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend
%{?python_provide:%python_provide python2-%{pypi_name}}

Requires:       python2-pbr >= 2.0.0
Requires:       python2-babel >= 2.3.4
Requires:       python2-neutron-lib >= 1.18.0
Requires:       python2-netaddr
Requires:       python2-oslo-db >= 4.27.0
Requires:       python2-oslo-config >= 2:5.2.0
Requires:       python2-oslo-concurrency >= 3.25.0
Requires:       python2-oslo-i18n >= 3.15.3
Requires:       python2-oslo-log >= 3.36.0
Requires:       python2-oslo-messaging >= 5.29.0
Requires:       python2-oslo-serialization >= 2.18.0
Requires:       python2-oslo-service >= 1.24.0
Requires:       python2-oslo-rootwrap >= 5.8.0
Requires:       python2-pecan
Requires:       python2-setuptools
Requires:       python2-exabgp >= 4.0.1
Requires:       python2-pyroute2
Requires:       python2-stevedore
Requires:       python2-six
Requires:       python2-oslo-versionedobjects >= 1.31.2
# NOTE(jpena): bagpipe is a BR for bgpvpn, so this creates a dependency loop.
#              On top of that, it makes unit tests for bgpvpn fail due to
#              wrong permissions for /etc/neutron/networking_bgpvpn.conf
#Requires:       python2-networking-bgpvpn >= 8.0.0
Requires:       python2-networking-sfc >= 6.0.0
Requires:       openstack-neutron >= 1:13.0.0

%description -n python2-%{pypi_name}
%{common_desc}

%package -n python-%{pypi_name}-doc
Summary:        networking-bagpipe documentation

%description -n python-%{pypi_name}-doc
Documentation for networking-bagpipe

%package -n openstack-%{servicename}
Summary:    Networking-BaGPipe
Requires:   python-networking-bagpipe = %{version}-%{release}
Requires:   openstack-neutron-common
%{?systemd_requires}

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
* Mon Aug 20 2018 RDO <dev@lists.rdoproject.org> 9.0.0-0.1.0rc1
- Update to 9.0.0.0rc1


