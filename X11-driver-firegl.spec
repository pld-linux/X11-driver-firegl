# TODO:
# - kernel modules (SMP)
# - missing obsoletes/conflicts
Summary:	Linux Drivers for ATI FireGL Chips
Summary(pl):	Sterowniki do kart graficznych ATI FireGL
Name:		XFree86-driver-firegl
Version:	1.9.20
Release:	1
License:	ATI Binary
Vendor:		ATI
Group:		X11/XFree86
URL:		http://www.ati.com/support/drivers/firegl/linux/linuxfiregl4x4201920.html
Source0:	http://mirror2.ati.com/drivers/firegl/fgl23glibc22-X42-%{version}.tgz
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
ExclusiveArch:	%{ix86}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoreqdep	libGL.so.1.2

%define		_fontdir	/usr/share/fonts
%define		_prefix		/usr/X11R6
%define		_mandir		%{_prefix}/man
%define		_appnkldir	%{_datadir}/applnk

%description
Linux Drivers for ATI FireGL Chips.

%description -l pl
Sterowniki do kart graficznych ATI FireGL.

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
%setup -q -c
tar xfz fgl*.tgz && rm -f fgl*.tgz

%build
cp make.sh make.sh.org && rm -f make.sh
sed -e 's#gcc#%{kgcc}#g' -e 's#`id -u` -ne 0#`id -u` -ne `id -u`#g' make.sh.org > make.sh
chmod 755 make.sh
./make.sh

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_includedir}/X11/extensions
install -d $RPM_BUILD_ROOT%{_libdir}/modules/{drivers,extensions,dri}

install -D firegl23.o		$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/firegl23.o

install fgl_gamma.h		$RPM_BUILD_ROOT%{_includedir}/X11/extensions
install fgl_xgamma fgl_glxgears firegl23config fireglinfo $RPM_BUILD_ROOT%{_bindir}
install libfgl_gamma.a 		$RPM_BUILD_ROOT%{_libdir}
install *.so.*			$RPM_BUILD_ROOT%{_libdir}
install *_drv.o			$RPM_BUILD_ROOT%{_libdir}/modules/drivers
install *_dri.so		$RPM_BUILD_ROOT%{_libdir}/modules/dri

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
%doc readme.txt
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/lib*.so*
%attr(755,root,root) %{_libdir}/lib*.a
%attr(755,root,root) %{_libdir}/modules/dri/*.so
%attr(755,root,root) %{_libdir}/modules/drivers/*_drv.o
%{_includedir}/X11/extensions/*.h

%files -n kernel-video-firegl
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*.o
