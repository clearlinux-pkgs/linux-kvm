#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        5.3.8
Release:        397
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.3.8.tar.xz
Source1:        config
Source2:        cmdline

%define ktarget  kvm
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  buildreq-kernel

Requires: systemd-bin
Requires: linux-kvm-license = %{version}-%{release}

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#cve.start cve patches from 0001 to 050
Patch0001: CVE-2019-12379.patch
#cve.end

#mainline: Mainline patches, upstream backport and fixes from 0051 to 0099
Patch0051: 0051-x86-reboot-Avoid-EFI-reboot-when-not-running-on-EFI.patch
#mainline.end

#Serie.clr 01XX: Clear Linux patches
Patch0101: 0101-do-accept-in-LIFO-order-for-cache-efficiency.patch
Patch0102: 0102-give-rdrand-some-credit.patch
Patch0103: 0103-init-wait-for-partition-and-retry-scan.patch
Patch0104: 0104-ksm-wakeups.patch
Patch0105: 0105-locking-rwsem-spin-faster.patch
Patch0106: 0106-Migrate-some-systemd-defaults-to-the-kernel-defaults.patch
Patch0107: 0107-smpboot-reuse-timer-calibration.patch
Patch0108: 0108-use-lfence-instead-of-rep-and-nop.patch
Patch0109: 0109-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0110: 0110-zero-extra-registers.patch
Patch0111: 0111-Compile-in-evged-always.patch
Patch0112: 0112-overload-on-wakeup.patch
#Serie.end

# Clear Linux KVM Memory Optimization
#Patch0151: 0151-mm-Export-do_madvise.patch
#Patch0152: 0152-x86-kvm-Notify-host-to-release-pages.patch
#Patch0153: 0153-x86-Return-memory-from-guest-to-host-kernel.patch
#Patch0154: 0154-sysctl-vm-Fine-grained-cache-shrinking.patch

#Serie1.name WireGuard
#Serie1.git  https://git.zx2c4.com/WireGuard
#Serie1.cmt  7bf34f50d41e8b60e01846baa2eb304697fab89c
#Serie1.tag  0.0.20190913
Patch1001: 1001-WireGuard-fast-modern-secure-kernel-VPN-tunnel.patch
#Serie1.end

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel kvm extra files
Group:          kernel
Requires:       linux-kvm-license = %{version}-%{release}

%description extra
Linux kernel extra files

%package license
Summary: license components for the linux package.
Group: Default

%description license
license components for the linux package.

%prep
%setup -q -n linux-5.3.8

#cve.patch.start cve patches
%patch0001 -p1
#cve.patch.end

#mainline.patch.start Mainline patches, upstream backport and fixes
%patch0051 -p1
#mainline.patch.end

#Serie.patch.start Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
#Serie.patch.end

# Clear Linux KVM Memory Optimization
#%patch0151 -p1
#%patch0152 -p1
#%patch0153 -p1
#%patch0154 -p1

#Serie1.patch.start
%patch1001 -p1
#Serie1.patch.end

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

    # Kernel default target link
    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget} %{kversion}

rm -rf %{buildroot}/usr/lib/firmware

mkdir -p %{buildroot}/usr/share/package-licenses/linux-kvm
cp COPYING %{buildroot}/usr/share/package-licenses/linux-kvm/COPYING
cp -a LICENSES/* %{buildroot}/usr/share/package-licenses/linux-kvm

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

%files license
%defattr(0644,root,root,0755)
/usr/share/package-licenses/linux-kvm
