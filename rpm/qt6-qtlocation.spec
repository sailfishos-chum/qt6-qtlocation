
%global qt_version 6.7.2
%global qt_module qtlocation


Summary: Qt6 - Location Libraries
Name:    qt6-%{qt_module}
Version: 6.7.2
Release: 2%{?dist}

# Rest of the licenses are for Qt code in src/location and src/plugins
License: LGPL-3.0-only OR GPL-3.0-only WITH Qt-GPL-exception-1.0
Url:     http://www.qt.io

%if 0%{?unstable}
Source0: https://download.qt.io/development_releases/qt/%{majmin}/%{qt_version}/submodules/%{qt_module}-everywhere-src-%{qt_version}-%{prerelease}.tar.xz
%else
Source0: https://download.qt.io/official_releases/qt/%{majmin}/%{version}/submodules/%{qt_module}-everywhere-src-%{version}.tar.xz
%endif

# filter plugin/qml provides
%global __provides_exclude_from ^(%{_qt6_archdatadir}/qml/.*\\.so|%{_qt6_plugindir}/.*\\.so)$

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: ninja
BuildRequires: qt6-rpm-macros
BuildRequires: qt6-qtbase-devel >= %{qt_version}
BuildRequires: qt6-qtbase-private-devel
%{?_qt6:Requires: %{_qt6}%{?_isa} = %{_qt6_version}}
BuildRequires: qt6-qtdeclarative-devel >= %{qt_version}
BuildRequires: qt6-qtpositioning-devel >= %{qt_version}
BuildRequires: qt6-qtshadertools-devel >= %{qt_version}
BuildRequires: pkgconfig(xkbcommon) >= 0.5.0


%description
The Qt Location API helps you create viable mapping solutions using
the data available from some of the popular location services.

%package devel
Summary: Development files for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: qt6-qtbase-devel%{?_isa}
Requires: qt6-qtdeclarative-devel%{?_isa}
Requires: qt6-qtpositioning-devel%{?_isa}
%description devel
%{summary}.

%if 0%{?examples}
%package examples
Summary: Programming examples for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
%description examples
%{summary}.
%endif

%prep
%autosetup -n %{qt_module}-everywhere-src-%{qt_version}%{?unstable:-%{prerelease}} -p1


%build
# QT is known not to work properly with LTO at this point.  Some of the issues
# are being worked on upstream and disabling LTO should be re-evaluated as
# we update this change.  Until such time...
# Disable LTO
%global _lto_cflags %{nil}

%cmake_qt6 \
  -DQT_BUILD_EXAMPLES:BOOL=%{?examples:ON}%{!?examples:OFF} \
  -DQT_INSTALL_EXAMPLES_SOURCES=%{?examples:ON}%{!?examples:OFF}

%cmake_build


%install
%cmake_install

## .prl/.la file love
# nuke .prl reference(s) to %%buildroot, excessive (.la-like) libs
pushd %{buildroot}%{_qt6_libdir}
for prl_file in libQt6*.prl ; do
  sed -i -e "/^QMAKE_PRL_BUILD_DIR/d" ${prl_file}
  if [ -f "$(basename ${prl_file} .prl).so" ]; then
    rm -fv "$(basename ${prl_file} .prl).la"
    sed -i -e "/^QMAKE_PRL_LIBS/d" ${prl_file}
  fi
done
popd


%files
%license LICENSES/GPL* LICENSES/LGPL*
%{_qt6_libdir}/libQt6Location.so.6*
%dir %{_qt6_archdatadir}/qml/QtLocation
%{_qt6_archdatadir}/qml/QtLocation/*
%{_qt6_plugindir}/geoservices/

%files devel
%dir %{_qt6_headerdir}/QtLocation
%{_qt6_headerdir}/QtLocation/*
%{_qt6_libdir}/libQt6Location.so
%{_qt6_libdir}/libQt6Location.prl
%dir %{_qt6_libdir}/cmake/Qt6Location
%{_qt6_libdir}/cmake/Qt6BuildInternals/StandaloneTests/QtLocationTestsConfig.cmake
%{_qt6_libdir}/cmake/Qt6Location/*.cmake
%{_qt6_libdir}/cmake/Qt6Qml/QmlPlugins/*.cmake
%{_qt6_archdatadir}/mkspecs/modules/qt_lib_location*.pri
%{_qt6_libdir}/qt6/metatypes/qt6*_metatypes.json
%{_qt6_libdir}/qt6/modules/*.json
%{_qt6_libdir}/pkgconfig/*.pc

%if 0%{?examples}
%files examples
%{_qt6_examplesdir}/
%endif
