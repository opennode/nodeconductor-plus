Name: nodeconductor-plus
Summary: Extension of NodeConductor with extra features
Group: Development/Libraries
Version: 0.1.0
Release: 1.el7
License: Copyright 2015 OpenNode LLC.  All rights reserved.
Url: http://nodeconductor.com
Source0: %{name}-%{version}.tar.gz

Requires: nodeconductor >= 0.7.0
Requires: python-digitalocean >= 1.5
Requires: python-django-cors-headers
Requires: python-gitlab >= 0.9

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
NodeConductor Plus is an extension of NodeConductor with extra features.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --single-version-externally-managed -O1 --root=%{buildroot} --record=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Wed Jul 15 2015 Juri Hudolejev <juri@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package
