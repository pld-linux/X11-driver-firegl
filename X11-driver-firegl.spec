#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	incall		# include all sources in srpm
%bcond_with	grsec_kernel	# build for kernel-grsecurity

%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
%if %{without kernel}
%undefine with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		_min_eq_x11	1:6.9.0
%define		_max_x11	1:7.0.0
%define		x11ver		x690

%ifarch %{ix86}
%define		arch_sufix	""
%define		arch_dir	x86
%else
%define		arch_sufix	_64a
%define		arch_dir	x86_64
%endif

%define		_rel	57
%define		pname	X11-driver-firegl
Summary:	Linux Drivers for ATI graphics accelerators
Summary(pl):	Sterowniki do akceleratorów graficznych ATI
Name:		%{pname}%{_alt_kernel}
Version:	8.36.5
Release:	%{_rel}
License:	ATI Binary (parts are GPL)
Group:		X11
Source0:	http://www2.ati.com/drivers/linux/ati-driver-installer-%{version}-x86.x86_64.run
# Source0-md5:	bf056417ac6c57acdf5e5a6bb99a7dae
Patch0:		firegl-panel.patch
Patch1:		firegl-panel-ugliness.patch
Patch2:		%{pname}-kh.patch
Patch3:		%{pname}-viak8t.patch
# Patch4:		%{pname}-force-define-AGP.patch
URL:		http://ati.amd.com/support/drivers/linux/linux-radeon.html
#BuildRequires:	X11-devel >= %{_min_eq_x11}	# disabled for now
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.14}
%{?with_userspace:BuildRequires:	qt-devel}
BuildRequires:	rpmbuild(macros) >= 1.330
Requires:	X11-OpenGL-core >= %{_min_eq_x11}
Requires:	X11-Xserver
%{?with_kernel:Requires:	X11-driver-firegl(kernel)}
Requires:	X11-libs < %{_max_x11}
Requires:	X11-libs >= %{_min_eq_x11}
Requires:	X11-modules < %{_max_x11}
Requires:	X11-modules >= %{_min_eq_x11}
Provides:	X11-OpenGL-libGL
Provides:	XFree86-OpenGL-libGL
Obsoletes:	Mesa
Obsoletes:	X11-OpenGL-libGL
Obsoletes:	XFree86-OpenGL-libGL
Obsoletes:	XFree86-driver-firegl
ExclusiveArch:	i586 i686 athlon pentium3 pentium4 %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_ccver	%(rpm -q --qf "%{VERSION}" gcc | sed 's/\\..*//')

%define		_noautoreqdep	libGL.so.1

%define		_prefix		/usr/X11R6
%define		_mandir		%{_prefix}/man

%description
Display driver files for the ATI Radeon 8500, 9700, Mobility M9 and
the FireGL 8700/8800, E1, Z1/X1 graphics accelerators. This package
provides 2D display drivers and hardware accelerated OpenGL.

%description -l pl
Sterowniki do kart graficznych ATI Radeon 8500, 9700, Mobility M9 oraz
graficznych akceleratorów FireGL 8700/8800, E1, Z1/X1. Pakiet
dostarcza sterowniki obs³uguj±ce wy¶wietlanie 2D oraz sprzêtowo
akcelerowany OpenGL.

%package -n kernel%{_alt_kernel}-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL
Release:	%{_rel}@%{_kernel_ver_str}
License:	ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	X11-driver-firegl(kernel)

%description -n kernel%{_alt_kernel}-video-firegl
ATI kernel module for FireGL support.

%description -n kernel%{_alt_kernel}-video-firegl -l pl
Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL.

%package -n kernel%{_alt_kernel}-smp-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL
Release:	%{_rel}@%{_kernel_ver_str}
License:	ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	X11-driver-firegl(kernel)

%description -n kernel%{_alt_kernel}-smp-video-firegl
ATI kernel module for FireGL support.

%description -n kernel%{_alt_kernel}-smp-video-firegl -l pl
Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL.

%prep
%setup -q -c -T

sh %{SOURCE0} --extract .

cp arch/%{arch_dir}/lib/modules/fglrx/build_mod/* common/lib/modules/fglrx/build_mod

install -d panel_src
tar -xzf common/usr/src/ati/fglrx_panel_sources.tgz -C panel_src
%patch0 -p1
%patch1 -p1
cd common
%{?with_dist_kernel:%patch2 -p1}
%patch3 -p1
# %patch4 -p2
cd -

install -d common%{_prefix}/{%{_lib},bin}
cp -r %{x11ver}%{arch_sufix}%{_prefix}/%{_lib}/* common%{_prefix}/%{_lib}
cp -r %{x11ver}%{arch_sufix}%{_bindir}/* common%{_bindir}
cp -r arch/%{arch_dir}%{_prefix}/%{_lib}/* common%{_prefix}/%{_lib}
cp -r arch/%{arch_dir}%{_bindir}/* common%{_bindir}

%build
%if %{with kernel}
cd common/lib/modules/fglrx/build_mod
cp -f 2.6.x/Makefile .
%build_kernel_modules -m fglrx GCC_VER_MAJ=%{_ccver}
cd -
%endif

%if %{with userspace}
%{__make} -C panel_src \
	C="%{__cc}" \
	CC="%{__cxx}" \
	CCFLAGS="%{rpmcflags} -DFGLRX_USE_XEXTENSIONS" \
	MK_QTDIR=/usr \
	LIBQT_DYN=qt-mt
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m common/lib/modules/fglrx/build_mod/fglrx -d misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_includedir}/X11/extensions} \
	$RPM_BUILD_ROOT/usr/{%{_lib},include/GL}

install common%{_bindir}/{fgl_glxgears,fglrxinfo,aticonfig} \
	$RPM_BUILD_ROOT%{_bindir}
install panel_src/fireglcontrol.qt3.gcc%(gcc -dumpversion) \
	$RPM_BUILD_ROOT%{_bindir}/fireglcontrol
cp -r common%{_prefix}/%{_lib}/* $RPM_BUILD_ROOT%{_libdir}

ln -sf libGL.so.1 $RPM_BUILD_ROOT%{_libdir}/libGL.so

# OpenGL ABI for Linux compatibility
ln -sf %{_libdir}/libGL.so.1 $RPM_BUILD_ROOT/usr/%{_lib}/libGL.so.1
ln -sf %{_libdir}/libGL.so $RPM_BUILD_ROOT/usr/%{_lib}/libGL.so

install common/usr/include/GL/*.h $RPM_BUILD_ROOT/usr/include/GL
install common%{_includedir}/X11/extensions/*.h $RPM_BUILD_ROOT%{_includedir}/X11/extensions
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel%{_alt_kernel}-video-firegl
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-video-firegl
%depmod %{_kernel_ver}

%post	-n kernel%{_alt_kernel}-smp-video-firegl
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-video-firegl
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/libGL.so.*.*
%attr(755,root,root) %{_libdir}/libGL.so
%attr(755,root,root) %{_libdir}/libfglrx_dm.so.*.*
%attr(755,root,root) %{_libdir}/libfglrx_gamma.so.*.*
%attr(755,root,root) %{_libdir}/libfglrx_pp.so.*.*
%attr(755,root,root) %{_libdir}/libfglrx_tvout.so.*.*
# Linux OpenGL ABI compatibility symlinks
%attr(755,root,root) /usr/%{_lib}/libGL.so.1
%attr(755,root,root) /usr/%{_lib}/libGL.so

#%%attr(755,root,root) %{_libdir}/modules/dri/atiogl_a_dri.so
%attr(755,root,root) %{_libdir}/modules/glesx.so
%attr(755,root,root) %{_libdir}/modules/dri/fglrx_dri.so
%attr(755,root,root) %{_libdir}/modules/drivers/fglrx_drv.so
%attr(755,root,root) %{_libdir}/modules/linux/libfglrxdrm.so

%doc ATI_LICENSE.TXT common%{_docdir}/fglrx/*.html common%{_docdir}/fglrx/articles common%{_docdir}/fglrx/release-notes common%{_docdir}/fglrx/user-manual

# -devel
#%attr(755,root,root) %{_libdir}/libfglrx_gamma.so
#%{_includedir}/X11/include/libfglrx_gamma.h
#/usr/include/GL/glATI.h
#/usr/include/GL/glxATI.h

# -static
#%{_libdir}/libfglrx_gamma.a
#%{_libdir}/libfglrx_pp.a
#%{_libdir}/modules/esut.a
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif
