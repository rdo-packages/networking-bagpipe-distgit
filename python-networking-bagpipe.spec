%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%global servicename bagpipe-bgp
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some runtime reqs from automatic generator
%global excluded_reqs networking-bgpvpn horizon

# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order isort pylint networking-bgpvpn
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

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

License:        Apache-2.0
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
BuildRequires:  pyproject-rpm-macros
BuildRequires:  systemd
%description
%{common_desc}

%package -n     python3-%{pypi_name}
Summary:        Mechanism driver for Neutron ML2 plugin using BGP E-VPNs/IP VPNs as a backend

# NOTE(jpena): bagpipe is a BR for bgpvpn, so this creates a dependency loop.
Requires:       openstack-neutron-common >= 1:16.0.0

%description -n python3-%{pypi_name}
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:        networking-bagpipe documentation

%description doc
%{common_desc}

Documentation for networking-bagpipe
%endif

%package -n openstack-%{servicename}
Summary:    Networking-BaGPipe
Requires:   openstack-neutron-common >= 16.0.0
Requires:   python3-networking-bagpipe = %{version}-%{release}

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
%autosetup -n %{pypi_name}-%{upstream_version} -S git

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs};do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
# Exclude some bad-known runtime reqs
for pkg in %{excluded_reqs}; do
  sed -i /^${pkg}.*/d requirements.txt
done

%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
%tox -e docs
# Remove the sphinx-build leftovers
rm -rf doc/build/html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

# bagpipe _sysconfdir and conf files
install -p -D -m 0640 %{buildroot}/%{python3_sitelib}/etc/%{servicename}/bgp.conf.template %{buildroot}%{_sysconfdir}/neutron/%{servicename}/bgp.conf
install -p -D -m 0640 %{buildroot}/%{python3_sitelib}/etc/%{servicename}/rootwrap.conf %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.conf
install -p -D -m 0640 %{buildroot}/%{python3_sitelib}/etc/%{servicename}/rootwrap.d/linux-vxlan.filters  %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.d/linux-vxlan.filters
install -p -D -m 0640 %{buildroot}/%{python3_sitelib}/etc/%{servicename}/rootwrap.d/mpls-ovs-dataplane.filters  %{buildroot}%{_sysconfdir}/neutron/%{servicename}/rootwrap.d/mpls-ovs-dataplane.filters

# remove unneeded files
rm -rf %{buildroot}/%{python3_sitelib}/etc/%{servicename}

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
%{python3_sitelib}/%{sname}-*.dist-info
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
