%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%global servicename bagpipe-bgp
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# NOTE(jpena): to build docs, we would need to add networking_bagpipe as a BR,
# creating the same dependency loop we have in runtime requirements
%global with_doc 0
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
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
BuildRequires:  openstack-macros
%endif

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
Requires:       python3-neutron-lib >= 2.19.0
Requires:       python3-netaddr >= 0.7.18
Requires:       python3-oslo-db >= 4.37.0
Requires:       python3-oslo-config >= 2:5.2.0
Requires:       python3-oslo-concurrency >= 3.26.0
Requires:       python3-oslo-i18n >= 3.15.3
Requires:       python3-oslo-log >= 3.36.0
Requires:       python3-oslo-messaging >= 5.29.0
Requires:       python3-oslo-serialization >= 2.18.0
Requires:       python3-oslo-service >= 1.24.0
Requires:       python3-oslo-rootwrap >= 5.8.0
Requires:       python3-pecan >= 1.3.2
Requires:       python3-exabgp >= 4.0.4
Requires:       python3-pyroute2 >= 0.5.7
Requires:       python3-stevedore >= 1.20.0
Requires:       python3-oslo-versionedobjects >= 1.35.1
Requires:       python3-oslo-privsep >= 2.3.0
# NOTE(jpena): bagpipe is a BR for bgpvpn, so this creates a dependency loop.
#              On top of that, it makes unit tests for bgpvpn fail due to
#              wrong permissions for /etc/neutron/networking_bgpvpn.conf
#Requires:       python3-networking-bgpvpn >= 8.0.0
Requires:       python3-networking-sfc >= 10.0.0
Requires:       openstack-neutron-common >= 1:16.0.0

%description -n python3-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        networking-bagpipe documentation

BuildRequires: openstack-neutron
BuildRequires: python3-exabgp
BuildRequires: python3-networking-bgpvpn
BuildRequires: python3-openstackdocstheme
BuildRequires: python3-oslo-concurrency
BuildRequires: python3-oslo-config
BuildRequires: python3-oslo-log
BuildRequires: python3-oslo-service
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
Requires:   openstack-neutron-common >= 16.0.0
%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description -n openstack-%{servicename}
Bagpipe-BGP service

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info
# Let RPM handle the dependencies
rm -f {,test-}requirements.txt

%build
%{py3_build}

%if 0%{?with_doc}
# Build html documentation
export PBR_VERSION=%{version}
export PYTHONPATH=.
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
