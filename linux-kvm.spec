#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        4.18.16
Release:        297
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.18.16.tar.xz
Source1:        config
Source2:        cmdline

%define ktarget  kvm
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  buildreq-kernel

Requires: systemd-bin

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#    000X: cve, bugfixes patches

#    00XY: Mainline patches, upstream backports

# Serie    01XX: Clear Linux patches
Patch0101: 0101-smpboot-reuse-timer-calibration.patch
Patch0102: 0102-ksm-wakeups.patch
Patch0103: 0103-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0104: 0104-give-rdrand-some-credit.patch
Patch0105: 0105-overload-on-wakeup.patch
Patch0106: 0106-Compile-in-evged-always.patch

# Clear Linux KVM Memory Optimization
#Patch0151: 0151-mm-Export-do_madvise.patch
#Patch0152: 0152-x86-kvm-Notify-host-to-release-pages.patch
#Patch0153: 0153-x86-Return-memory-from-guest-to-host-kernel.patch
#Patch0154: 0154-sysctl-vm-Fine-grained-cache-shrinking.patch

#
# Small tweaks
#
Patch0500: 0500-zero-extra-registers.patch

# Serie    XYYY: Extra features modules

#
#   400X: Wireguard
#
Patch4001: 4001-WireGuard-fast-modern-secure-kernel-VPN-tunnel.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel kvm extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.18.16

#     000X  cve, bugfixes patches

#     00XY  Mainline patches, upstream backports

#     01XX  Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1

# Clear Linux KVM Memory Optimization
#%patch0151 -p1
#%patch0152 -p1
#%patch0153 -p1
#%patch0154 -p1

#
# Small tweaks
#
%patch0500 -p1

# Serie    XYYY: Extra features modules

#
#   400X: Wireguard
#
%patch4001 -p1


cp %{SOURCE1} .

%build
BuildKernel() {

    Target=$1
    Arch=x86_64
    ExtraVer="-%{release}.${Target}"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make O=${Target} -s mrproper
    cp config ${Target}/.config

    make O=${Target} -s ARCH=${Arch} olddefconfig
    make O=${Target} -s ARCH=${Arch} CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} %{?sparse_mflags}
}

BuildKernel %{ktarget}

%install

InstallKernel() {

    Target=$1
    Kversion=$2
    Arch=x86_64
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 ${Target}/.config    ${KernelDir}/config-${Kversion}
    install -m 644 ${Target}/System.map ${KernelDir}/System.map-${Kversion}
    install -m 644 ${Target}/vmlinux    ${KernelDir}/vmlinux-${Kversion}
    install -m 644 %{SOURCE2}           ${KernelDir}/cmdline-${Kversion}
    cp  ${Target}/arch/x86/boot/bzImage ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules
    make O=${Target} -s ARCH=${Arch} INSTALL_MOD_PATH=%{buildroot}/usr modules_install

    rm -f %{buildroot}/usr/lib/modules/${Kversion}/build
    rm -f %{buildroot}/usr/lib/modules/${Kversion}/source

    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget}  %{kversion}

rm -rf %{buildroot}/usr/lib/firmware

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.%{ktarget}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget}
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
/usr/lib/kernel/vmlinux-%{kversion}
