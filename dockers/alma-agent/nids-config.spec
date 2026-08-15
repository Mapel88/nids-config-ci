Name:           nids-config
Version:        1.0.0
Release:        1%{?dist}
Summary:        Configuration utility for NIDS network setup (IPv4/IPv6)

License:        MIT
URL:            https://github.com/Mapel88/nids-config-ci
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch

Requires:       python3 >= 3.8
Requires:       python3-pyyaml
Requires:       iproute

%description
This package installs the nids-config Python tool, a command-line utility
used to configure IPv4 and IPv6 protocol monitoring settings for Network
Intrusion Detection System (NIDS) environments on RHEL-family Linux systems.

Features:
 - Enable/disable IPv4 and IPv6 protocol monitoring
 - Auto-detect and configure network interfaces
 - Enable promiscuous mode for packet capture
 - Validate system environment for NIDS readiness
 - Persistent configuration in /etc/nids/config.yaml

%prep
%setup -q

%build
# Nothing to build for Python script

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sysconfdir}/nids
mkdir -p %{buildroot}%{_datadir}/doc/%{name}

install -m 755 nids-config.py %{buildroot}%{_bindir}/nids-config

cat > %{buildroot}%{_sysconfdir}/nids/config.yaml << EOF
ipv4_enabled: true
ipv6_enabled: true
interfaces: []
last_updated: null
EOF

if [ -f README.md ]; then
    install -m 644 README.md %{buildroot}%{_datadir}/doc/%{name}/README.md
fi

%files
%{_bindir}/nids-config
%dir %{_sysconfdir}/nids
%config(noreplace) %{_sysconfdir}/nids/config.yaml
%doc %{_datadir}/doc/%{name}/README.md

%post
mkdir -p /var/log/nids
chmod 755 /var/log/nids
chmod 755 %{_sysconfdir}/nids
chmod 644 %{_sysconfdir}/nids/config.yaml

echo "NIDS Configuration Tool installed successfully"
echo "Run 'sudo nids-config --validate' to check system readiness"

%preun
if [ $1 -eq 0 ]; then
    echo "Removing NIDS Configuration Tool"
fi

%postun
if [ $1 -eq 0 ]; then
    echo "NIDS Configuration Tool removed"
fi

%changelog
* Tue Nov 18 2025 Maayan Apelboim Garbash <maintainer@example.com> - 1.0.0-1
- Initial release of the NIDS configuration Python tool
- IPv4/IPv6 protocol monitoring configuration support
- Dynamic network interface detection
- Promiscuous mode configuration
- System validation functionality
