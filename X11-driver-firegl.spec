# TODO:
# - kernel modules (SMP)
Summary:	Linux Drivers for ATI FireGL Chips
Summary(pl):	Sterowniki do kart graficznych ATI FireGL
Name:		XFree86-driver-firegl
Version:	2.5.1
Release:	1
License:	ATI Binary
Vendor:		ATI
Group:		X11/XFree86
URL:		http://www.ati.com/support/drivers/linux/radeon-linux.html
Source0:	http://pdownload.mii.instacontent.net/ati/drivers/fglrx-glc22-4.2.0-%{version}.i586.rpm
Conflicts:	XFree86-OpenGL-devel <= 4.2.0-3
Obsoletes:	Mesa
Obsoletes:	XFree86-OpenGL-core
PreReq:		/sbin/depmod
PreReq:		modutils >= 2.3.18-2
Provides:	XFree86-OpenGL-core
Requires:	XFree86-Xserver
Requires:	XFree86-libs >= 4.2.0
Requires:	XFree86-modules >= 4.2.0
Requires:	kernel-video-firegl = %{version}
%{!?_without_dist_kernel:BuildRequires:         kernel-headers >= 2.2.0 }
BuildRequires:	rpm-utils
BuildRequires:	bzip2
BuildRequires:	cpio
ExclusiveArch:	i586 i686 athlon
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libGL.so.1.2

%define		_fontdir	/usr/share/fonts
%define		_prefix		/usr/X11R6
%define		_mandir		%{_prefix}/man
%define		_appnkldir	%{_datadir}/applnk

%description
Display driver files for the ATI Radeon 8500, 9700, Mobility M9 and
the FireGL 8700/8800, E1, Z1/X1 graphics accelerators. This package
provides 2D display drivers and hardware accelerated OpenGL.

%description -l pl
Sterowniki do kart graficznych ATI Radeon 8500, 9700, Mobility M9 oraz
graficznych akaceleratorów FireGL 8700/8800, E1, Z1/X1. Pakiet
dostarcza sterowniki obs³uguj±ce wy¶wietlanie 2D oraz sprzêtowo
akacelerowany OpenGL.

%package -n kernel-video-firegl
Summary:	ATI kernel module for FireGL support
Summary(pl):	Modu³ kernela oferuj±cy wsparcie dla ATI FireGL
Release:	%{release}@%{_kernel_ver_str}
License:	ATI
Vendor:		ATI
Group:		Base/Kernel
%{!?_without_dist_kernel:%requires_releq_kernel_up}

%description -n kernel-video-firegl
ATI kernel module for FireGL support.

%description -n kernel-video-firegl -l pl
Modu³ kernela oferuj±cy wsparcie dla ATI FireGL.

%prep
%setup -q -c -T
rpm2cpio %{SOURCE0} | cpio -i -d
bzip2 -d -v usr/X11R6/bin/*.bz2

%build
cd lib/modules/fglrx/build_mod/
cp make.sh make.sh.org && rm -f make.sh
sed -e 's#gcc#%{kgcc}#g' -e 's#`id -u` -ne 0#`id -u` -ne `id -u`#g' make.sh.org > make.sh
chmod 755 make.sh
./make.sh

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_includedir}/X11/extensions
install -d $RPM_BUILD_ROOT%{_libdir}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/

install lib/modules/fglrx/build_mod/fglrx.o		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/

install usr/X11R6/bin/{fgl_glxgears,fglrxconfig,fglrxinfo,fireglcontrol.qt2} $RPM_BUILD_ROOT%{_bindir}
cp -r usr/X11R6/lib/* $RPM_BUILD_ROOT%{_libdir}/

cd $RPM_BUILD_ROOT%{_libdir}
ln -s libGL.so.* libGL.so

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post -n kernel-video-firegl
/sbin/depmod -a

%postun -n kernel-video-firegl
/sbin/depmod -a

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so*
%attr(755,root,root) %{_libdir}/modules/*/*.so
%attr(755,root,root) %{_libdir}/modules/*/*.o
%attr(644,root,root) %{_libdir}/modules/*/*.a

%files -n kernel-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.o*
