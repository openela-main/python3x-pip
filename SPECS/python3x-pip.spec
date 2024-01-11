%bcond_with tests
# RHEL: docs disabled because they need python3-sphinx, which needs
# python3-packaging, which is shahowed by python39-packaging during the build
# of the python39 module
%bcond_with doc

%global srcname pip
%global base_version 20.2.4
%global upstream_version %{base_version}%{?prerel}
%global python_wheelname %{srcname}-%{upstream_version}-py2.py3-none-any.whl
%global python_wheeldir %{_datadir}/python%{python3_pkgversion}-wheels

%if %{with doc}
# Commit hash to use from the repo https://github.com/pypa/pypa-docs-theme
%global pypa_theme_commit_hash d2e63fbfc62af3b7050f619b2f5bb8658985b931
%endif

%global bashcompdir %(pkg-config --variable=completionsdir bash-completion 2>/dev/null)

Name:           python3x-%{srcname}
Version:        %{base_version}%{?prerel:~%{prerel}}
Release:        7%{?dist}
Summary:        A tool for installing and managing Python packages

# We bundle a lot of libraries with pip, which itself is under MIT license.
# Here is the list of the libraries with corresponding licenses:

# appdirs: MIT
# certifi: MPLv2.0
# chardet: LGPLv2
# colorama: BSD
# CacheControl: ASL 2.0
# contextlib2: Python
# distlib: Python
# distro: ASL 2.0
# html5lib: MIT
# idna: BSD
# ipaddress: Python
# msgpack: ASL 2.0
# packaging: ASL 2.0 or BSD
# pep517: MIT
# progress: ISC
# pyparsing: MIT
# requests: ASL 2.0
# resolvelib: ISC
# retrying: ASL 2.0
# setuptools: MIT
# six: MIT
# toml: MIT
# urllib3: MIT
# webencodings: BSD

License:        MIT and Python and ASL 2.0 and BSD and ISC and LGPLv2 and MPLv2.0 and (ASL 2.0 or BSD)
URL:            https://pip.pypa.io/
Source0:        https://github.com/pypa/pip/archive/%{upstream_version}/%{srcname}-%{upstream_version}.tar.gz

BuildArch:      noarch
# Exclude i686 arch. Due to a modularity issue it's being added to the
# x86_64 compose of CRB, but we don't want to ship it at all.
# See: https://projects.engineering.redhat.com/browse/RCM-72605
ExcludeArch:    i686

%if %{with tests}
BuildRequires:  /usr/bin/git
BuildRequires:  /usr/bin/hg
BuildRequires:  /usr/bin/bzr
BuildRequires:  /usr/bin/svn
BuildRequires:  python%{python3_pkgversion}-setuptools-wheel
BuildRequires:  python%{python3_pkgversion}-wheel-wheel
%endif

# Themes required to build the docs.
%if %{with doc}
Source1:        https://github.com/pypa/pypa-docs-theme/archive/%{pypa_theme_commit_hash}.tar.gz
Source2:        https://github.com/python/python-docs-theme/archive/2018.2.tar.gz
%endif

# Downstream only patch
# Emit a warning to the user if pip install is run with root privileges
# Issue upstream: https://github.com/pypa/pip/issues/4288
Patch1:         emit-a-warning-when-running-with-root-privileges.patch

# Add path to the doc themes to conf.py
Patch2:         html_theme_path.patch

# Prevent removing of the system packages installed under /usr/lib
# when pip install -U is executed.
# https://bugzilla.redhat.com/show_bug.cgi?id=1550368#c24
Patch3:         remove-existing-dist-only-if-path-conflicts.patch

# Use the system level root certificate instead of the one bundled in certifi
# https://bugzilla.redhat.com/show_bug.cgi?id=1655253
Patch4:         dummy-certifi.patch

# Don't warn the user about pip._internal.main() entrypoint
# In Fedora, we use that in ensurepip and users cannot do anything about it,
# this warning is juts moot. Also, the warning breaks CPython test suite.
Patch5:         nowarn-pip._internal.main.patch

# Patch for CVE-2021-3572 - pip incorrectly handled unicode separators in git references
# Upstream PR: https://github.com/pypa/pip/pull/9827
# Bugzilla: https://bugzilla.redhat.com/show_bug.cgi?id=1962856
Patch6:         CVE-2021-3572.patch

# CVE-2021-33503 Catastrophic backtracking in URL authority parser
# Tracking bug: https://bugzilla.redhat.com/show_bug.cgi?id=1968074
# Upstream fix: https://github.com/urllib3/urllib3/commit/2d4a3fee6de2fa45eb82169361918f759269b4ec
Patch7:         CVE-2021-33503.patch

# Downstream only patch
# Users might have local installations of pip from using
# `pip install --user --upgrade pip` on older/newer versions.
# If they do that and they run `pip` or  `pip3`, the one from /usr/bin is used.
# However that's the one from this RPM package and the import in there might
# fail (it tries to import from ~/.local, but older or newer pip is there with
# a bit different API).
# We add this patch as a dirty workaround to make /usr/bin/pip* work with
# both pip10+ (from this RPM) and older or newer (19.3+) pip (from whatever).
# A proper fix is to put ~/.local/bin in front of /usr/bin in the PATH,
# however others are against that and we cannot change it for existing
# installs/user homes anyway.
# https://bugzilla.redhat.com/show_bug.cgi?id=1569488
# https://bugzilla.redhat.com/show_bug.cgi?id=1571650
# https://bugzilla.redhat.com/show_bug.cgi?id=1767212
# WARNING: /usr/bin/pip* are entrypoints, this cannot be applied in %%prep!
# %%patch10 doesn't work outside of %%prep, so we add it as a source
# Note that since pip 20, old main() import paths are preserved for backwards
# compatibility: https://github.com/pypa/pip/issues/7498
# Meaning we don't need to update any of the older pips to support 20+
# We also don't need to update Pythons to use new import path in ensurepip
Source10:        pip-allow-different-versions.patch

%description
pip is a package management system used to install and manage software packages
written in Python. Many packages can be found in the Python Package Index
(PyPI). pip is a recursive acronym that can stand for either "Pip Installs
Packages" or "Pip Installs Python".



# Virtual provides for the packages bundled by pip.
# You can generate it with:
# %%{_rpmconfigdir}/pythonbundles.py --namespace 'python%%{1}dist' src/pip/_vendor/vendor.txt
%global bundled() %{expand:
Provides: bundled(python%{1}dist(appdirs)) = 1.4.4
Provides: bundled(python%{1}dist(cachecontrol)) = 0.12.6
Provides: bundled(python%{1}dist(certifi)) = 2020.6.20
Provides: bundled(python%{1}dist(chardet)) = 3.0.4
Provides: bundled(python%{1}dist(colorama)) = 0.4.3
Provides: bundled(python%{1}dist(contextlib2)) = 0.6^post1
Provides: bundled(python%{1}dist(distlib)) = 0.3.1
Provides: bundled(python%{1}dist(distro)) = 1.5
Provides: bundled(python%{1}dist(html5lib)) = 1.1
Provides: bundled(python%{1}dist(idna)) = 2.10
Provides: bundled(python%{1}dist(ipaddress)) = 1.0.23
Provides: bundled(python%{1}dist(msgpack)) = 1
Provides: bundled(python%{1}dist(packaging)) = 20.4
Provides: bundled(python%{1}dist(pep517)) = 0.8.2
Provides: bundled(python%{1}dist(progress)) = 1.5
Provides: bundled(python%{1}dist(pyparsing)) = 2.4.7
Provides: bundled(python%{1}dist(requests)) = 2.24
Provides: bundled(python%{1}dist(resolvelib)) = 0.4
Provides: bundled(python%{1}dist(retrying)) = 1.3.3
Provides: bundled(python%{1}dist(setuptools)) = 44
Provides: bundled(python%{1}dist(six)) = 1.15
Provides: bundled(python%{1}dist(toml)) = 0.10.1
Provides: bundled(python%{1}dist(urllib3)) = 1.25.9
Provides: bundled(python%{1}dist(webencodings)) = 0.5.1
}

# Some manylinux1 wheels need libcrypt.so.1.
# Manylinux1, a common (as of 2019) platform tag for binary wheels, relies
# on a glibc version that included ancient crypto functions, which were
# moved to libxcrypt and then removed in:
#  https://fedoraproject.org/wiki/Changes/FullyRemoveDeprecatedAndUnsafeFunctionsFromLibcrypt
# The manylinux1 standard assumed glibc would keep ABI compatibility,
# but that's only the case if libcrypt.so.1 (libxcrypt-compat) is around.
# This should be solved in the next manylinux standard (but it may be
# a long time until manylinux1 is phased out).
# See: https://github.com/pypa/manylinux/issues/305
# Note that manylinux is only applicable to x86 (both 32 and 64 bits)
%global crypt_compat_recommends() %{expand:
Recommends: (libcrypt.so.1()(64bit) if python%{1}(x86-64))
Recommends: (libcrypt.so.1 if python%{1}(x86-32))
}



%package -n python%{python3_pkgversion}-%{srcname}
Summary:        A tool for installing and managing Python3 packages

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-rpm-macros
# python3 bootstrap: this is rebuilt before the final build of python3, which
# adds the dependency on python3-rpm-generators, so we require it manually
# Note that the package prefix is always python3-, even if we build for 3.X
BuildRequires:  python3-rpm-generators
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  bash-completion
%if %{with tests}
BuildRequires:  python%{python3_pkgversion}-cryptography
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-pretend
BuildRequires:  python%{python3_pkgversion}-freezegun
BuildRequires:  python%{python3_pkgversion}-scripttest
BuildRequires:  python%{python3_pkgversion}-virtualenv
BuildRequires:  python%{python3_pkgversion}-werkzeug
BuildRequires:  python%{python3_pkgversion}-pyyaml
%endif
BuildRequires:  python%{python3_pkgversion}-wheel
BuildRequires:  ca-certificates
Requires:       ca-certificates

# This was previously required and we keep it recommended because a lot of
# sdists installed via pip will try to import setuptools.
# But pip doesn't actually require setuptools.
# It can install wheels without them and it can build wheels in isolation mode
# (using setuptools/flit/poetry/... installed from PyPI).
# Side note: pip bundles pkg_resources from setuptools for internal usage.
Recommends:     python%{python3_pkgversion}-setuptools

# Require alternatives version that implements the --keep-foreign flag
Requires(postun): alternatives >= 1.19.1-1
# python39 installs the alternatives master symlink to which we attach a slave
Requires: python%{python3_pkgversion}
Requires(post): python%{python3_pkgversion}
Requires(postun): python%{python3_pkgversion}

# Virtual provides for the packages bundled by pip:
%{bundled %{python3_version}}

%{crypt_compat_recommends %{python3_pkgversion}}

%description -n python%{python3_pkgversion}-%{srcname}
pip is a package management system used to install and manage software packages
written in Python. Many packages can be found in the Python Package Index
(PyPI). pip is a recursive acronym that can stand for either "Pip Installs
Packages" or "Pip Installs Python".

%if %{with doc}
%package -n python%{python3_pkgversion}-%{srcname}-doc
Summary:        A documentation for a tool for installing and managing Python packages

BuildRequires:  python3-sphinx

%description -n python%{python3_pkgversion}-%{srcname}-doc
A documentation for a tool for installing and managing Python packages

%endif

%package -n python%{python3_pkgversion}-%{srcname}-wheel
Summary:        The pip wheel
Requires:       ca-certificates

# Virtual provides for the packages bundled by pip:
%{bundled %{python3_version}}

%{crypt_compat_recommends %{python3_pkgversion}}

%description -n python%{python3_pkgversion}-%{srcname}-wheel
A Python wheel of pip to use with venv.

%prep
%setup -q -n %{srcname}-%{upstream_version}

%if %{with doc}
pushd docs/html
tar -xf %{SOURCE1}
mv pypa-docs-theme-%{pypa_theme_commit_hash} pypa
tar -xf %{SOURCE2}
mv python-docs-theme-2018.2 python-docs-theme
popd
%endif

%autopatch -p1

# this goes together with patch4
rm src/pip/_vendor/certifi/*.pem

# tests expect wheels in here
ln -s %{python_wheeldir} tests/data/common_wheels

# Upstream uses a Python 2/3 compatibility library for csv with Python 3 semantics in tests
# We only target Python 3 and csv23 is not (yet) packaged
# As of 20.1b1, this workaround was sufficient to get around the missing dependency
sed -i -e 's/csv23/csv/g' tests/lib/wheel.py

# Remove windows executable binaries
rm -v src/pip/_vendor/distlib/*.exe
sed -i '/\.exe/d' setup.py

%build
%py3_build_wheel

%if %{with doc}
export PYTHONPATH=./src/
# from tox.ini
sphinx-build-3 -b html docs/html docs/build/html
sphinx-build-3 -b man  docs/man  docs/build/man  -c docs/html
rm -rf docs/build/html/{.doctrees,.buildinfo}
%endif


%install
# The following is similar to %%py3_install_wheel, but we don't have
# /usr/bin/pip yet, so we install using the wheel directly.
# (This is not standard wheel usage, but the pip wheel supports it -- see
#  pip/__main__.py)
%{__python3} dist/%{python_wheelname}/pip install \
    --root %{buildroot} \
    --no-deps \
    --no-cache-dir \
    --no-index \
    --ignore-installed \
    --find-links dist \
    'pip==%{upstream_version}'

%if %{with doc}
pushd docs/build/man
install -d %{buildroot}%{_mandir}/man1
for MAN in *1; do
install -pm0644 $MAN %{buildroot}%{_mandir}/man1/${MAN/pip/pip%{python3_version}}
install -pm0644 $MAN %{buildroot}%{_mandir}/man1/${MAN/pip/pip-%{python3_version}}
done
popd
%endif

# before we ln -s anything, we apply Source10 patch to all pips:
for PIP in %{buildroot}%{_bindir}/pip*; do
  patch -p1 --no-backup-if-mismatch $PIP < %{SOURCE10}
done

mkdir -p %{buildroot}%{bashcompdir}
PYTHONPATH=%{buildroot}%{python3_sitelib} \
    %{buildroot}%{_bindir}/pip completion --bash \
    > %{buildroot}%{bashcompdir}/pip%{python3_version}

# Make bash completion apply to all the 5 symlinks we install
sed -i -e "s/^\\(complete.*\\) pip\$/\\1 pip{,-}%{python3_version}/" \
    -e s/_pip_completion/_pip%{python3_pkgversion}_completion/ \
    %{buildroot}%{bashcompdir}/pip%{python3_version}


# Provide symlinks to executables to comply with Fedora guidelines for Python
ln -s ./pip%{python3_version} %{buildroot}%{_bindir}/pip-%{python3_version}
ln -s ./pip-%{python3_version} %{buildroot}%{_bindir}/pip-3


# Make sure the INSTALLER is not pip, otherwise Patch2 won't work
# %%pyproject macros do this for all packages
echo rpm > %{buildroot}%{python3_sitelib}/pip-%{upstream_version}.dist-info/INSTALLER

mkdir -p %{buildroot}%{python_wheeldir}
install -p dist/%{python_wheelname} -t %{buildroot}%{python_wheeldir}

# RHEL8: Remove binaries conflicting with Python 3.6
rm %{buildroot}%{_bindir}/pip
rm %{buildroot}%{_bindir}/pip3
rm %{buildroot}%{_bindir}/pip-3

# All ghost files controlled by alternatives need to exist for the files
# section check to succeed
touch %{buildroot}%{_bindir}/pip3
touch %{buildroot}%{_bindir}/pip-3


%if %{with tests}
%check
# Upstream tests
# bash completion tests only work from installed package
# needs unaltered sys.path and we cannot do that in %%check
#     test_pep517_and_build_options
#     test_config_file_venv_option
# TODO investigate failures
#     test_uninstall_non_local_distutils
# Incompatible with the latest virtualenv
#     test_from_link_vcs_with_source_dir_obtains_commit_id
#     test_from_link_vcs_without_source_dir
#     test_should_cache_git_sha
pytest_k='not completion and
          not test_pep517_and_build_options and
          not test_config_file_venv_option and
          not test_uninstall_non_local_distutils and
          not test_from_link_vcs_with_source_dir_obtains_commit_id and
          not test_from_link_vcs_without_source_dir and
          not test_should_cache_git_sha'

# --deselect'ed tests are not compatible with the latest virtualenv
# These files contain almost 500 tests so we should enable them back
# as soon as pip will be compatible upstream
# https://github.com/pypa/pip/pull/8441
%pytest -m 'not network' -k "$(echo $pytest_k)" \
    --deselect tests/functional --deselect tests/lib/test_lib.py --deselect tests/unit/test_build_env.py
%endif


%post -n python%{python3_pkgversion}-%{srcname}
alternatives --add-slave python3 %{_bindir}/python%{python3_version} \
    %{_bindir}/pip3 \
    pip3 \
    %{_bindir}/pip%{python3_version}
alternatives --add-slave python3 %{_bindir}/python%{python3_version} \
    %{_bindir}/pip-3 \
    pip-3 \
    %{_bindir}/pip-%{python3_version}

%postun -n python%{python3_pkgversion}-%{srcname}
# Do this only during uninstall process (not during update)
if [ $1 -eq 0 ]; then
    # Only remove the slave links if the master link for python3 still exists.
    # Due to a possible bug in yum, python39 gets removed before python39-pip
    # even though we have declared Requires(postun): python39
    EXISTS=`alternatives --display python3 | \
          grep -c "^/usr/bin/python%{python3_version} - priority [0-9]*"`

    if [ $EXISTS -ne 0 ]; then
        alternatives --keep-foreign --remove-slave python3 %{_bindir}/python%{python3_version} \
            pip3
        alternatives --keep-foreign --remove-slave python3 %{_bindir}/python%{python3_version} \
            pip-3
    fi
fi


%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE.txt
%doc README.rst
%if %{with doc}
%{_mandir}/man1/pip%{python3_version}.*
%{_mandir}/man1/pip%{python3_version}-*.*
%{_mandir}/man1/pip-%{python3_version}.*
%{_mandir}/man1/pip-%{python3_version}-*.*
%endif
%{_bindir}/pip%{python3_version}
%{_bindir}/pip-%{python3_version}
%{python3_sitelib}/pip*
%dir %{bashcompdir}
%{bashcompdir}/pip%{python3_version}
%ghost %{_bindir}/pip3
%ghost %{_bindir}/pip-3

%if %{with doc}
%files -n python%{python3_pkgversion}-%{srcname}-doc
%license LICENSE.txt
%doc README.rst
%doc docs/build/html
%endif

%files -n python%{python3_pkgversion}-%{srcname}-wheel
%license LICENSE.txt
# we own the dir for simplicity
%dir %{python_wheeldir}/
%{python_wheeldir}/%{python_wheelname}

%changelog
* Thu Oct 14 2021 Charalampos Stratakis <cstratak@redhat.com> - 20.2.4-7
- Remove bundled windows executables
- Resolves: rhbz#2006790

* Thu Aug 05 2021 Tomas Orsava <torsava@redhat.com> - 20.2.4-6
- Adjusted the postun scriptlets to enable upgrading to RHEL 9
- Resolves: rhbz#1933055

* Wed Jun 30 2021 Lumír Balhar <lbalhar@redhat.com> - 20.2.4-5
- Fix for CVE-2021-33503 Catastrophic backtracking in URL authority parser
Resolves: rhbz#1968074

* Tue Jun 08 2021 Lumír Balhar <lbalhar@redhat.com> - 20.2.4-4
- Fix for CVE-2021-3572 - pip incorrectly handled unicode separators in git references
Resolves: rhbz#1962856

* Wed Jan 06 2021 Tomas Orsava <torsava@redhat.com> - 20.2.4-3
- Convert from Fedora to the python39 module in RHEL8
- Resolves: rhbz#1877430

* Fri Dec 04 2020 Miro Hrončok <mhroncok@redhat.com> - 20.2.4-2
- Disable tests and documentation in Fedora ELN (and RHEL)

* Mon Oct 19 2020 Lumír Balhar <lbalhar@redhat.com> - 20.2.4-1
- Update to 20.2.4 (#1889112)

* Wed Aug 05 2020 Tomas Orsava <torsava@redhat.com> - 20.2.2-1
- Update to 20.2.2 (#1838553)

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20.1.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 10 2020 Lumír Balhar <lbalhar@redhat.com> - 20.1.1-6
- Do not emit a warning about root privileges when --root is used

* Wed Jul 08 2020 Miro Hrončok <mhroncok@redhat.com> - 20.1.1-5
- Update bundled provides to match 20.1.1

* Tue Jun 16 2020 Lumír Balhar <lbalhar@redhat.com> - 20.1.1-4
- Deselect tests incompatible with the latest virtualenv

* Sun May 24 2020 Miro Hrončok <mhroncok@redhat.com> - 20.1.1-3
- Rebuilt for Python 3.9

* Thu May 21 2020 Miro Hrončok <mhroncok@redhat.com> - 20.1.1-2
- Bootstrap for Python 3.9

* Wed May 20 2020 Tomas Hrnciar <thrnciar@redhat.com> - 20.1.1-1
- Update to 20.1.1

* Wed Apr 29 2020 Tomas Hrnciar <thrnciar@redhat.com> - 20.1-1
- Update to 20.1

* Mon Apr 27 2020 Tomas Hrnciar <thrnciar@redhat.com> - 20.1~b1-1
- Update to 20.1~b1

* Wed Apr 15 2020 Miro Hrončok <mhroncok@redhat.com> - 20.0.2-4
- Only recommend setuptools, don't require them

* Fri Apr 10 2020 Miro Hrončok <mhroncok@redhat.com> - 20.0.2-3
- Allow setting $TMPDIR to $PWD/... during pip wheel (#1806625)

* Tue Mar 10 2020 Miro Hrončok <mhroncok@redhat.com> - 20.0.2-2
- Don't warn the user about pip._internal.main() entrypoint to fix ensurepip

* Mon Mar 02 2020 Miro Hrončok <mhroncok@redhat.com> - 20.0.2-1
- Update to 20.0.2 (#1793456)

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 19.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Nov 04 2019 Tomas Orsava <torsava@redhat.com> - 19.3.1-1
- Update to 19.3.1 (#1761508)
- Drop upstreamed patch that fixed expected output in test to not break with alpha/beta/rc Python versions

* Wed Oct 30 2019 Miro Hrončok <mhroncok@redhat.com> - 19.2.3-2
- Make /usr/bin/pip(3) work with user-installed pip 19.3+ (#1767212)

* Mon Sep 02 2019 Miro Hrončok <mhroncok@redhat.com> - 19.2.3-1
- Update to 19.2.3 (#1742230)
- Drop patch that should strip path prefixes from RECORD files, the paths are relative

* Wed Aug 21 2019 Petr Viktorin <pviktori@redhat.com> - 19.1.1-8
- Remove python2-pip
- Make pip bootstrap itself, rather than with an extra bootstrap RPM build

* Sat Aug 17 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1.1-7
- Rebuilt for Python 3.8

* Wed Aug 14 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1.1-6
- Bootstrap for Python 3.8

* Wed Aug 14 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1.1-5
- Bootstrap for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 19.1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jul 15 2019 Petr Viktorin <pviktori@redhat.com> - 19.1.1-3
- Recommend libcrypt.so.1 for manylinux1 compatibility
- Make /usr/bin/pip Python 3

* Mon Jun 10 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1.1-2
- Fix root warning when pip is invoked via python -m pip
- Remove a redundant second WARNING prefix form the abovementioned warning

* Wed May 15 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1.1-1
- Update to 19.1.1 (#1706995)

* Thu Apr 25 2019 Miro Hrončok <mhroncok@redhat.com> - 19.1-1
- Update to 19.1 (#1702525)

* Wed Mar 06 2019 Miro Hrončok <mhroncok@redhat.com> - 19.0.3-1
- Update to 19.0.3 (#1679277)

* Wed Feb 13 2019 Miro Hrončok <mhroncok@redhat.com> - 19.0.2-1
- Update to 19.0.2 (#1668492)

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 18.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Dec 03 2018 Miro Hrončok <mhroncok@redhat.com> - 18.1-2
- Use the system level root certificate instead of the one bundled in certifi

* Thu Nov 22 2018 Miro Hrončok <mhroncok@redhat.com> - 18.1-1
- Update to 18.1 (#1652089)

* Tue Sep 18 2018 Victor Stinner <vstinner@redhat.com> - 18.0-4
- Prevent removing of the system packages installed under /usr/lib
  when pip install -U is executed. Original patch by Michal Cyprian.
  Resolves: rhbz#1550368.

* Wed Aug 08 2018 Miro Hrončok <mhroncok@redhat.com> - 18.0-3
- Create python-pip-wheel package with the wheel

* Tue Jul 31 2018 Miro Hrončok <mhroncok@redhat.com> - 18.0-2
- Remove redundant "Unicode"" from License

* Mon Jul 23 2018 Marcel Plch <mplch@redhat.com> - 18.0-7
- Update to 18.0

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 9.0.3-5
- Rebuilt for Python 3.7

* Wed Jun 13 2018 Miro Hrončok <mhroncok@redhat.com> - 9.0.3-4
- Bootstrap for Python 3.7

* Wed Jun 13 2018 Miro Hrončok <mhroncok@redhat.com> - 9.0.3-3
- Bootstrap for Python 3.7

* Fri May 04 2018 Miro Hrončok <mhroncok@redhat.com> - 9.0.3-2
- Allow to import pip10's main from pip9's /usr/bin/pip
- Do not show the "new version of pip" warning outside of venv
Resolves: rhbz#1569488
Resolves: rhbz#1571650
Resolves: rhbz#1573755

* Thu Mar 29 2018 Charalampos Stratakis <cstratak@redhat.com> - 9.0.3-1
- Update to 9.0.3

* Wed Feb 21 2018 Lumír Balhar <lbalhar@redhat.com> - 9.0.1-16
- Include built HTML documentation (in the new -doc subpackage) and man page

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Dec 04 2017 Charalampos Stratakis <cstratak@redhat.com> - 9.0.1-14
- Reintroduce the ipaddress module in the python3 subpackage.

* Mon Nov 20 2017 Charalampos Stratakis <cstratak@redhat.com> - 9.0.1-13
- Add virtual provides for the bundled libraries. (rhbz#1096912)

* Tue Aug 29 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-12
- Switch macros to bcond's and make Python 2 optional to facilitate building
  the Python 2 and Python 3 modules

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 23 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-10
- Modernized package descriptions
Resolves: rhbz#1452568

* Tue Mar 21 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-9
- Fix typo in the sudo pip warning

* Fri Mar 03 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-8
- Patch 1 update: No sudo pip warning in venv or virtualenv

* Thu Feb 23 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-7
- Patch 1 update: Customize the warning with the proper version of the pip
  command

* Tue Feb 14 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-6
- Added patch 1: Emit a warning when running with root privileges

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 9.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 02 2017 Tomas Orsava <torsava@redhat.com> - 9.0.1-4
- Provide symlinks to executables to comply with Fedora guidelines for Python
Resolves: rhbz#1406922

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 9.0.1-3
- Rebuild for Python 3.6 with wheel

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 9.0.1-2
- Rebuild for Python 3.6 without wheel

* Fri Nov 18 2016 Orion Poplawski <orion@cora.nwra.com> - 9.0.1-1
- Update to 9.0.1

* Fri Nov 18 2016 Orion Poplawski <orion@cora.nwra.com> - 8.1.2-5
- Enable EPEL Python 3 builds
- Use new python macros
- Cleanup spec

* Fri Aug 05 2016 Tomas Orsava <torsava@redhat.com> - 8.1.2-4
- Updated the test sources

* Fri Aug 05 2016 Tomas Orsava <torsava@redhat.com> - 8.1.2-3
- Moved python-pip into the python2-pip subpackage
- Added the python_provide macro

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.2-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue May 17 2016 Tomas Orsava <torsava@redhat.com> - 8.1.2-1
- Update to 8.1.2
- Moved to a new PyPI URL format
- Updated the prefix-stripping patch because of upstream changes in pip/wheel.py

* Mon Feb 22 2016 Slavek Kabrda <bkabrda@redhat.com> - 8.0.2-1
- Update to 8.0.2

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 7.1.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Oct 14 2015 Robert Kuska <rkuska@redhat.com> - 7.1.0-3
- Rebuilt for Python3.5 rebuild
- With wheel set to 1

* Tue Oct 13 2015 Robert Kuska <rkuska@redhat.com> - 7.1.0-2
- Rebuilt for Python3.5 rebuild

* Wed Jul 01 2015 Slavek Kabrda <bkabrda@redhat.com> - 7.1.0-1
- Update to 7.1.0

* Tue Jun 30 2015 Ville Skyttä <ville.skytta@iki.fi> - 7.0.3-3
- Install bash completion
- Ship LICENSE.txt as %%license where available

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 7.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 04 2015 Matej Stuchlik <mstuchli@redhat.com> - 7.0.3-1
- Update to 7.0.3

* Fri Mar 06 2015 Matej Stuchlik <mstuchli@redhat.com> - 6.0.8-1
- Update to 6.0.8

* Thu Dec 18 2014 Slavek Kabrda <bkabrda@redhat.com> - 1.5.6-5
- Only enable tests on Fedora.

* Mon Dec 01 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.6-4
- Add tests
- Add patch skipping tests requiring Internet access

* Tue Nov 18 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.6-3
- Added patch for local dos with predictable temp dictionary names
  (http://seclists.org/oss-sec/2014/q4/655)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun May 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.6-1
- Update to 1.5.6

* Fri Apr 25 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.4-4
- Rebuild as wheel for Python 3.4

* Thu Apr 24 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.4-3
- Disable build_wheel

* Thu Apr 24 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.4-2
- Rebuild as wheel for Python 3.4

* Mon Apr 07 2014 Matej Stuchlik <mstuchli@redhat.com> - 1.5.4-1
- Updated to 1.5.4

* Mon Oct 14 2013 Tim Flink <tflink@fedoraproject.org> - 1.4.1-1
- Removed patch for CVE 2013-2099 as it has been included in the upstream 1.4.1 release
- Updated version to 1.4.1

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 16 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.3.1-4
- Fix for CVE 2013-2099

* Thu May 23 2013 Tim Flink <tflink@fedoraproject.org> - 1.3.1-3
- undo python2 executable rename to python-pip. fixes #958377
- fix summary to match upstream

* Mon May 06 2013 Kevin Kofler <Kevin@tigcc.ticalc.org> - 1.3.1-2
- Fix main package Summary, it's for Python 2, not 3 (#877401)

* Fri Apr 26 2013 Jon Ciesla <limburgher@gmail.com> - 1.3.1-1
- Update to 1.3.1, fix for CVE-2013-1888.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Oct 09 2012 Tim Flink <tflink@fedoraproject.org> - 1.2.1-2
- Fixing files for python3-pip

* Thu Oct 04 2012 Tim Flink <tflink@fedoraproject.org> - 1.2.1-1
- Update to upstream 1.2.1
- Change binary from pip-python to python-pip (RHBZ#855495)
- Add alias from python-pip to pip-python, to be removed at a later date

* Tue May 15 2012 Tim Flink <tflink@fedoraproject.org> - 1.1.0-1
- Update to upstream 1.1.0

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Oct 22 2011 Tim Flink <tflink@fedoraproject.org> - 1.0.2-1
- update to 1.0.2 and added python3 subpackage

* Wed Jun 22 2011 Tim Flink <tflink@fedoraproject.org> - 0.8.3-1
- update to 0.8.3 and project home page

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec 20 2010 Luke Macken <lmacken@redhat.com> - 0.8.2-1
- update to 0.8.2 of pip
* Mon Aug 30 2010 Peter Halliday <phalliday@excelsiorsystems.net> - 0.8-1
- update to 0.8 of pip
* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 0.7.2-5
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Wed Jul 7 2010 Peter Halliday <phalliday@excelsiorsystems.net> - 0.7.2-1
- update to 0.7.2 of pip
* Sun May 23 2010 Peter Halliday <phalliday@excelsiorsystems.net> - 0.7.1-1
- update to 0.7.1 of pip
* Fri Jan 1 2010 Peter Halliday <phalliday@excelsiorsystems.net> - 0.6.1.4
- fix dependency issue
* Fri Dec 18 2009 Peter Halliday <phalliday@excelsiorsystems.net> - 0.6.1-2
- fix spec file 
* Thu Dec 17 2009 Peter Halliday <phalliday@excelsiorsystems.net> - 0.6.1-1
- upgrade to 0.6.1 of pip
* Mon Aug 31 2009 Peter Halliday <phalliday@excelsiorsystems.net> - 0.4-1
- Initial package

