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
Version:        XXX
Release:        XXX
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend

License:        ASL 2.0
URL:            https://github.com/openstack/networking-bagpipe
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        %{servicename}.service

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-hacking
BuildRequires:  python3-oslotest
BuildRequires:  python3-oslo-rootwrap
BuildRequires:  python3-pbr
BuildRequires:  python3-setuptools
BuildRequires:  python3-subunit
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools
BuildRequires:  python3-pecan
BuildRequires:  systemd
%description
%{common_desc}

%package -n     python3-%{pypi_name}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       python3-babel >= 2.3.4
Requires:       python3-neutron-lib >= 2.2.0
Requires:       python3-netaddr
Requires:       python3-oslo-db >= 4.37.0
Requires:       python3-oslo-config >= 2:5.2.0
Requires:       python3-oslo-concurrency >= 3.26.0
Requires:       python3-oslo-i18n >= 3.15.3
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-messaging >= 5.29.0
Requires:       python3-oslo-serialization >= 2.18.0
Requires:       python3-oslo-service >= 1.24.0
Requires:       python3-oslo-rootwrap >= 5.8.0
Requires:       python3-pecan
Requires:       python3-setuptools
Requires:       python3-exabgp >= 4.0.4
Requires:       python3-pyroute2
Requires:       python3-stevedore
Requires:       python3-six
Requires:       python3-oslo-versionedobjects >= 1.35.1
# NOTE(jpena): bagpipe is a BR for bgpvpn, so this creates a dependency loop.
#              On top of that, it makes unit tests for bgpvpn fail due to
#              wrong permissions for /etc/neutron/networking_bgpvpn.conf
#Requires:       python3-networking-bgpvpn >= 8.0.0
Requires:       python3-networking-sfc >= 10.0.0
Requires:       openstack-neutron >= 1:16.0.0

%description -n python3-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        networking-bagpipe documentation

BuildRequires: python3-openstackdocstheme
BuildRequires: python3-oslo-config
BuildRequires: python3-sphinx
BuildRequires: python3-sphinxcontrib-actdiag
BuildRequires: python3-sphinxcontrib-blockdiag
BuildRequires: python3-sphinxcontrib-seqdiag

%description doc
%{common_desc}

Documentation for networking-bagpipe
%endif

%package -n openstack-%{servicename}
Summary:    Networking-BaGPipe
Requires:   python3-networking-bagpipe = %{version}-%{release}
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
%{py3_build}

%if 0%{?with_doc}
# Build html documentation
sphinx-build-3 -b html doc/source doc/build/html
# Remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

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

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.rst
%{python3_sitelib}/%{sname}
%{python3_sitelib}/%{sname}-*.egg-info
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
# REMOVEME: error caused by commit http://git.openstack.org/cgit/openstack/networking-bagpipe/commit/?id=30b058ec04f4ccbbbca41c36b72f877634873352
