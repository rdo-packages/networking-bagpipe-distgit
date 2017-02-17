%global pypi_name networking-bagpipe
%global sname networking_bagpipe
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           python-%{pypi_name}
Version:        6.0.0
Release:        1%{?dist}
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
# generate html docs
#%{__python2} setup.py build_sphinx
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

%install
%py2_install


%files -n python2-%{pypi_name}
%license LICENSE
%doc README.rst
%{python2_sitelib}/%{sname}
%{python2_sitelib}/%{sname}-*.egg-info
%{_bindir}/neutron-bagpipe-linuxbridge-agent

%files -n python-%{pypi_name}-doc
#%doc html
%license LICENSE

%changelog
* Fri Feb 17 2017 Alfredo Moralejo <amoralej@redhat.com> 6.0.0-1
- Update to 6.0.0

* Fri Nov 11 2016 Luke Hinds <lhinds@redhat.com> - 4.0.0-2
- Initial package.
