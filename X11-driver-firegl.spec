#
# Conditional build:
# _without_dist_kernel
#

%define		_min_xfree	4.3.0

Summary:	Linux Drivers for ATI graphics accelerators
Summary(pl):	Sterowniki do akceleratorów graficznych ATI
Name:		XFree86-driver-firegl
Version:	3.2.8
Release:	1.5
License:	ATI Binary
Vendor:		ATI
Group:		X11/XFree86
Source0:	http://www2.ati.com/drivers/firegl/fglrx-glc22-%{_min_xfree}-%{version}.i586.rpm
# Source0-md5:	824aaaafd4b4867c2456860ea5eff5ec
Patch0:		firegl-panel.patch
Patch1:		XFree86-driver-firegl-kh.patch  
URL:		http://www.ati.com/support/drivers/linux/radeon-linux.html
BuildRequires:	cpio
%{!?_without_dist_kernel:BuildRequires:         kernel-headers >= 2.2.0 }
BuildRequires:	rpm-utils
Requires:	XFree86-Xserver
Requires:	XFree86-libs >= %{_min_xfree}
Requires:	XFree86-modules >= %{_min_xfree}
%{!?_without_dist_kernel:Requires:	kernel-video-firegl = %{version} }
Provides:	XFree86-OpenGL-core = %{_min_xfree}
Obsoletes:	Mesa
Obsoletes:	XFree86-OpenGL-libGL
Provides:	XFree86-OpenGL-libGL
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
%{!?_without_dist_kernel:%requires_releq_kernel_up}
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
%{!?_without_dist_kernel:%requires_releq_kernel_smp}
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
mkdir panel_src
tar -xzf usr/src/ATI/fglrx_panel_sources.tgz -C panel_src
%patch0 -p1
%{!?_without_dist_kernel:%patch1 -p1}

%build
cd lib/modules/fglrx/build_mod/
cp make.sh make.sh.org && rm -f make.sh
sed -e 's#gcc#%{kgcc}#g' -e 's#`id -u` -ne 0#`id -u` -ne `id -u`#g' make.sh.org > make.sh
chmod 755 make.sh
./make.sh \
	SMP=1
mv fglrx.o fglrx-smp.o
./make.sh clean
./make.sh
cd ../../../../panel_src

%{__make} \
	MK_QTDIR=/usr \
	LIBQT_DYN=qt-mt

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir},%{_includedir}/X11/extensions} \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc/

install lib/modules/fglrx/build_mod/fglrx.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc
install lib/modules/fglrx/build_mod/fglrx-smp.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc

install usr/X11R6/bin/{fgl_glxgears,fglrxconfig,fglrxinfo} $RPM_BUILD_ROOT%{_bindir}
install panel_src/{fireglcontrol.qt3.gcc3.3.1,fireglcontrol} $RPM_BUILD_ROOT%{_bindir}
cp -r usr/X11R6/lib/* $RPM_BUILD_ROOT%{_libdir}/

cd $RPM_BUILD_ROOT%{_libdir}
ln -s libGL.so.* libGL.so

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	-n kernel-video-firegl
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver} }%{_kernel_ver}

%postun -n kernel-video-firegl
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver} }%{_kernel_ver}

%post	-n kernel-smp-video-firegl
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver}smp }%{_kernel_ver}smp

%postun -n kernel-smp-video-firegl
/sbin/depmod -a %{!?_without_dist_kernel:-F /boot/System.map-%{_kernel_ver}smp }%{_kernel_ver}smp

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so*
%attr(755,root,root) %{_libdir}/modules/*/*.so
%attr(755,root,root) %{_libdir}/modules/*/*.o
%attr(644,root,root) %{_libdir}/modules/*/*.a
%attr(755,root,root) /usr/X11R6/lib/libfglrx_gamma.a

%files -n kernel-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.o*

%files -n kernel-smp-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*.o*
