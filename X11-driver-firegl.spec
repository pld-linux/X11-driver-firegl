#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
#

%define		_min_xfree	4.3.0
%define		_gcc_ver	%(gcc -dumpversion)

Summary:	Linux Drivers for ATI graphics accelerators
Summary(pl):	Sterowniki do akceleratorów graficznych ATI
Name:		XFree86-driver-firegl
Version:	3.7.0
Release:	3
License:	ATI Binary (parts are GPL)
Vendor:		ATI
Group:		X11/XFree86
Source0:	http://www2.ati.com/drivers/linux/fglrx-glc22-%{_min_xfree}-%{version}.i386.rpm
# Source0-md5:	7dd12340a2b8525b3a9fa1f310e06141
Patch0:		firegl-panel.patch
Patch1:		XFree86-driver-firegl-kh.patch  
URL:		http://www.ati.com/support/drivers/linux/radeon-linux.html
BuildRequires:	cpio
%if %{with kernel} && %{with dist_kernel}
BuildRequires:         kernel-source >= 2.6.0
%endif
BuildRequires:	rpm-utils
BuildRequires:	rpmbuild(macros) >= 1.118
# not used at the moment (see commented make in panel_src)
#BuildRequires:	XFree86-OpenGL-devel
#BuildRequires:	qt-devel
Requires:	XFree86-Xserver
Requires:	XFree86-libs >= %{_min_xfree}
Requires:	XFree86-modules >= %{_min_xfree}
%{?with_dist_kernel:Requires:	kernel-video-firegl = %{version} }
Provides:	XFree86-OpenGL-core = %{_min_xfree}
Provides:	XFree86-OpenGL-libGL
Obsoletes:	Mesa
Obsoletes:	XFree86-OpenGL-libGL
ExclusiveArch:	i586 i686 athlon
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libGL.so.1.2

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

%package -n kernel-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL
Release:	%{release}@%{_kernel_ver_str}
License:	ATI
Vendor:		ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
PreReq:		modutils >= 2.3.18-2
Requires(post,postun):	/sbin/depmod

%description -n kernel-video-firegl
ATI kernel module for FireGL support.

%description -n kernel-video-firegl -l pl
Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL.

%package -n kernel-smp-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL
Release:	%{release}@%{_kernel_ver_str}
License:	ATI
Vendor:		ATI
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
PreReq:		modutils >= 2.3.18-2
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-video-firegl
ATI kernel module for FireGL support.

%description -n kernel-smp-video-firegl -l pl
Modu³ j±dra oferuj±cy wsparcie dla ATI FireGL.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -i -d
bzip2 -d -v usr/X11R6/bin/*.bz2
install -d panel_src
tar -xzf usr/src/ATI/fglrx_panel_sources.tgz -C panel_src
%patch0 -p1
%{?with_dist_kernel:%patch1 -p1}

%build
%if %{with kernel}
cd lib/modules/fglrx/build_mod

ln -sf %{_kernelsrcdir}/config-up .config
rm -rf include
install -d include/{linux,config}
ln -s %{_kernelsrcdir}/include/linux/autoconf.h include/linux/autoconf.h
ln -s %{_kernelsrcdir}/include/asm-%{_arch} include/asm
touch include/config/MARKER
cp 2.6.x/Makefile Makefile
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules

mv fglrx.ko fglrx.up

%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 mrproper

ln -sf %{_kernelsrcdir}/config-smp .config
rm -rf include
install -d include/{linux,config}
ln -s %{_kernelsrcdir}/include/linux/autoconf.h include/linux/autoconf.h
ln -s %{_kernelsrcdir}/include/asm-%{_arch} include/asm
touch include/config/MARKER
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules


%endif

%if %{with userspace}
#%{__make} -C panel_src \
#	MK_QTDIR=/usr \
#	LIBQT_DYN=qt-mt
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
install lib/modules/fglrx/build_mod/fglrx.up $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/fglrx.ko
install lib/modules/fglrx/build_mod/fglrx.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_includedir}/X11/extensions} \
	$RPM_BUILD_ROOT/usr/{%{_lib},include/GL}

install usr/X11R6/bin/{fgl_glxgears,fglrxconfig,fglrxinfo} $RPM_BUILD_ROOT%{_bindir}
#install panel_src/{fireglcontrol.qt3.gcc%{_gcc_ver},fireglcontrol} $RPM_BUILD_ROOT%{_bindir}
cp -r usr/X11R6/lib/* $RPM_BUILD_ROOT%{_libdir}

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

%files -n kernel-smp-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.ko*
%endif
