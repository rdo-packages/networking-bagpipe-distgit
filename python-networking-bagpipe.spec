# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %{expand:%{python%{pyver}_sitelib}}
%global pyver_install %{expand:%{py%{pyver}_install}}
%global pyver_build %{expand:%{py%{pyver}_build}}
# End of macros for py2/py3 compatibility
%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%global servicename bagpipe-bgp
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global with_doc 1
%global common_desc \
BaGPipe BGP is a lightweight implementation of BGP VPNs (IP VPNs and E-VPNs), \
targeting deployments on servers hosting VMs, in particular for Openstack/KVM \
platforms.

Name:           python-%{pypi_name}
Version:        11.0.2
Release:        1%{?dist}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend

License:        ASL 2.0
URL:            https://github.com/openstack/networking-bagpipe
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#

Source1:        %{servicename}.service

BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-oslo-rootwrap
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools
BuildRequires:  python%{pyver}-pecan
BuildRequires:  systemd
%description
%{common_desc}

%package -n     python%{pyver}-%{pypi_name}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:       python%{pyver}-pbr >= 2.0.0
Requires:       python%{pyver}-babel >= 2.3.4
Requires:       python%{pyver}-neutron-lib >= 1.18.0
Requires:       python%{pyver}-netaddr
Requires:       python%{pyver}-oslo-db >= 4.27.0
Requires:       python%{pyver}-oslo-config >= 2:5.2.0
Requires:       python%{pyver}-oslo-concurrency >= 3.26.0
Requires:       python%{pyver}-oslo-i18n >= 3.15.3
Requires:       python%{pyver}-oslo-log >= 3.36.0
Requires:       python%{pyver}-oslo-messaging >= 5.29.0
Requires:       python%{pyver}-oslo-serialization >= 2.18.0
Requires:       python%{pyver}-oslo-service >= 1.24.0
Requires:       python%{pyver}-oslo-rootwrap >= 5.8.0
Requires:       python%{pyver}-pecan
Requires:       python%{pyver}-setuptools
Requires:       python%{pyver}-exabgp >= 4.0.4
Requires:       python%{pyver}-pyroute2
Requires:       python%{pyver}-stevedore
Requires:       python%{pyver}-six
Requires:       python%{pyver}-oslo-versionedobjects >= 1.31.2
# NOTE(jpena): bagpipe is a BR for bgpvpn, so this creates a dependency loop.
#              On top of that, it makes unit tests for bgpvpn fail due to
#              wrong permissions for /etc/neutron/networking_bgpvpn.conf
#Requires:       python%{pyver}-networking-bgpvpn >= 8.0.0
Requires:       python%{pyver}-networking-sfc >= 8.0.0
Requires:       openstack-neutron >= 1:13.0.0

%description -n python%{pyver}-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        networking-bagpipe documentation

BuildRequires: python%{pyver}-openstackdocstheme
BuildRequires: python%{pyver}-oslo-config
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-sphinxcontrib-actdiag
BuildRequires: python%{pyver}-sphinxcontrib-blockdiag
BuildRequires: python%{pyver}-sphinxcontrib-seqdiag

%description doc
%{common_desc}

Documentation for networking-bagpipe
%endif

%package -n openstack-%{servicename}
Summary:    Networking-BaGPipe
Requires:   python%{pyver}-networking-bagpipe = %{version}-%{release}
Requires:   openstack-neutron-common
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description -n openstack-%{servicename}
Bagpipe-BGP service

%prep
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%build
%{pyver_build}

%if 0%{?with_doc}
# Build html documentation
sphinx-build-%{pyver} -b html doc/source doc/build/html
# Remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

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

%files -n python%{pyver}-%{pypi_name}
%license LICENSE
%doc README.rst
%{pyver_sitelib}/%{sname}
%{pyver_sitelib}/%{sname}-*.egg-info
%{_bindir}/bagpipe-fakerr
%{_bindir}/bagpipe-impex2dot
%{_bindir}/bagpipe-looking-glass
%{_bindir}/bagpipe-rest-attach

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%license LICENSE
%endif

%files -n openstack-%{servicename}
%license LICENSE
%{_unitdir}/%{servicename}.service
%{_bindir}/bagpipe-bgp
%{_bindir}/bagpipe-bgp-cleanup
%dir  %attr(0750, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/
%config(noreplace) %attr(0640, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/*.conf
%config(noreplace) %attr(0640, neutron, neutron) %{_sysconfdir}/neutron/%{servicename}/rootwrap.d/*.filters

%changelog
* Mon Feb 01 2021 RDO <dev@lists.rdoproject.org> 11.0.2-1
- Update to 11.0.2

* Tue Feb 18 2020 RDO <dev@lists.rdoproject.org> 11.0.1-1
- Update to 11.0.1

* Wed Oct 16 2019 RDO <dev@lists.rdoproject.org> 11.0.0-1
- Update to 11.0.0

* Fri Oct 04 2019 RDO <dev@lists.rdoproject.org> 11.0.0-0.1.0rc1
- Update to 11.0.0.0rc1

