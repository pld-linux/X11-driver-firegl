#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
%bcond_without	incall		# include all sources in srpm

%define		_min_x11	6.8.0

%if %{without kernel}
%undefine with_dist_kernel
%endif

%ifarch %{ix86}
%define		need_x86	1
%else
%define		need_x86	0%{?with_incall:1}
%endif
%ifarch %{x8664}
%define		need_amd64	1
%else
%define		need_amd64	0%{?with_incall:1}
%endif

Summary:	Linux Drivers for ATI graphics accelerators
Summary(pl):	Sterowniki do akcelerator�w graficznych ATI
Name:		X11-driver-firegl
Version:	8.14.13
%define		_rel	1
Release:	%{_rel}
License:	ATI Binary (parts are GPL)
Vendor:		ATI
Group:		X11/XFree86
%if %{need_x86}
Source0:	http://www2.ati.com/drivers/linux/fglrx_6_8_0-%{version}-1.i386.rpm
# Source0-md5:	5187698cee2edf3dee89bc3eee5729c1
%endif
%if %{need_amd64}
Source1:	http://www2.ati.com/drivers/linux/64bit/fglrx64_6_8_0-%{version}-1.x86_64.rpm
# Source1-md5:	fc6c39cdf856955359c6f7087a78581c
%endif
Patch0:		firegl-panel.patch
Patch1:		firegl-panel-ugliness.patch
Patch2:		%{name}-kh.patch
Patch3:		%{name}-viak8t.patch
# needed to compile with linux kernel 2.6.12 or newer
# NOTE: You have to uncommented these in %%prep (I thinks these may brake build on < 2.6.12)
Patch4:		%{name}-pci_name.patch
Patch5:		%{name}-inter_module_get.patch
URL:		http://www.ati.com/support/drivers/linux/radeon-linux.html
BuildRequires:	cpio
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.213
%{?with_userspace:BuildRequires:	qt-devel}
#BuildRequires:	X11-devel >= %{_min_x11}	# disabled for now
Requires:	X11-OpenGL-core >= %{_min_x11}
Requires:	X11-Xserver
%{?with_kernel:Requires:	X11-driver-firegl(kernel)}
Requires:	X11-libs >= %{_min_x11}
Requires:	X11-modules >= %{_min_x11}
Provides:	X11-OpenGL-libGL
Provides:	XFree86-OpenGL-libGL
Obsoletes:	Mesa
Obsoletes:	X11-OpenGL-libGL
Obsoletes:	XFree86-OpenGL-libGL
Obsoletes:	XFree86-driver-firegl
ExclusiveArch:	i586 i686 athlon pentium3 pentium4 %{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libGL.so.1

%define		_prefix		/usr/X11R6
%define		_mandir		%{_prefix}/man

%description
Display driver files for the ATI Radeon 8500, 9700, Mobility M9 and
the FireGL 8700/8800, E1, Z1/X1 graphics accelerators. This package
provides 2D display drivers and hardware accelerated OpenGL.

%description -l pl
Sterowniki do kart graficznych ATI Radeon 8500, 9700, Mobility M9 oraz
graficznych akcelerator�w FireGL 8700/8800, E1, Z1/X1. Pakiet
dostarcza sterowniki obs�uguj�ce wy�wietlanie 2D oraz sprz�towo
akcelerowany OpenGL.

%package -n kernel-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu� j�dra oferuj�cy wsparcie dla ATI FireGL
Release:	%{_rel}@%{_kernel_ver_str}
License:	ATI
Vendor:		ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	X11-driver-firegl(kernel)

%description -n kernel-video-firegl
ATI kernel module for FireGL support.

%description -n kernel-video-firegl -l pl
Modu� j�dra oferuj�cy wsparcie dla ATI FireGL.

%package -n kernel-smp-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu� j�dra oferuj�cy wsparcie dla ATI FireGL
Release:	%{_rel}@%{_kernel_ver_str}
License:	ATI
Vendor:		ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	X11-driver-firegl(kernel)

%description -n kernel-smp-video-firegl
ATI kernel module for FireGL support.

%description -n kernel-smp-video-firegl -l pl
Modu� j�dra oferuj�cy wsparcie dla ATI FireGL.

%prep
%setup -q -c -T
%ifarch %{x8664}
rpm2cpio %{SOURCE1} | cpio -i -d
%else
rpm2cpio %{SOURCE0} | cpio -i -d
%endif
install -d panel_src
tar -xzf usr/src/ATI/fglrx_panel_sources.tgz -C panel_src

%patch0 -p1
%patch1 -p1
%{?with_dist_kernel:%patch2 -p1}
%patch3 -p1
#%patch4 -p1
#%patch5 -p1

%build
%if %{with kernel}
cd lib/modules/fglrx/build_mod
cp -f 2.6.x/Makefile .
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
%if %{without dist_kernel}
	ln -sf %{_kernelsrcdir}/scripts
%endif
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv fglrx{,-$cfg}.ko
done
cd -
%endif

%if %{with userspace}
%{__make} -C panel_src \
	CCFLAGS="%{rpmcflags} -DFGLRX_USE_XEXTENSIONS" \
	MK_QTDIR=/usr \
	LIBQT_DYN=qt-mt
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
cd lib/modules/fglrx/build_mod
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc

install fglrx-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/fglrx.ko
%if %{with smp} && %{with dist_kernel}
install fglrx-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/fglrx.ko
%endif
cd -
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_includedir}/X11/extensions} \
	$RPM_BUILD_ROOT/usr/{%{_lib},include/GL}

install usr/X11R6/bin/{fgl_glxgears,fglrxconfig,fglrxinfo} \
	$RPM_BUILD_ROOT%{_bindir}
install panel_src/fireglcontrol.qt3.gcc%(gcc -dumpversion) \
	$RPM_BUILD_ROOT%{_bindir}/fireglcontrol
cp -r usr/X11R6/%{_lib}/* $RPM_BUILD_ROOT%{_libdir}

ln -sf libGL.so.1 $RPM_BUILD_ROOT%{_libdir}/libGL.so

# OpenGL ABI for Linux compatibility
ln -sf %{_libdir}/libGL.so.1 $RPM_BUILD_ROOT/usr/%{_lib}/libGL.so.1
ln -sf %{_libdir}/libGL.so $RPM_BUILD_ROOT/usr/%{_lib}/libGL.so

install usr/include/GL/*.h $RPM_BUILD_ROOT/usr/include/GL
install usr/X11R6/include/X11/extensions/*.h $RPM_BUILD_ROOT%{_includedir}/X11/extensions
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel-video-firegl
%depmod %{_kernel_ver}

%postun -n kernel-video-firegl
%depmod %{_kernel_ver}

%post	-n kernel-smp-video-firegl
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-video-firegl
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/libGL.so.*.*
%attr(755,root,root) %{_libdir}/libGL.so
%attr(755,root,root) %{_libdir}/libfglrx_gamma.so.*.*
# Linux OpenGL ABI compatibility symlinks
%attr(755,root,root) /usr/%{_lib}/libGL.so.1
%attr(755,root,root) /usr/%{_lib}/libGL.so

%attr(755,root,root) %{_libdir}/modules/dri/fglrx_dri.so
%attr(755,root,root) %{_libdir}/modules/drivers/fglrx_drv.o
%{_libdir}/modules/linux/libfglrxdrm.a

# -devel
#%attr(755,root,root) %{_libdir}/libfglrx_gamma.so
#%{_includedir}/X11/include/libfglrx_gamma.h
#/usr/include/GL/glxATI.h

# -static
#%{_libdir}/libfglrx_gamma.a
%endif

%if %{with kernel}
%files -n kernel-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
%endif
