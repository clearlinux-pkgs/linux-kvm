#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us top optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        4.5.4
Release:        164
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.5.4.tar.xz
Source1:        config
Source2:        cmdline

%define kversion %{version}-%{release}.kvm

BuildRequires:  bash >= 2.03
BuildRequires:  bc
# For bfd support in perf/trace
BuildRequires:  binutils-dev
BuildRequires:  elfutils
BuildRequires:  elfutils-dev
BuildRequires:  kmod
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison

# don't srip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

# Serie    00XX: mainline, CVE, bugfixes patches

# Serie    01XX: Clear Linux patches
#Patch0101: 0101-msleep-warning.patch
Patch0102: 0102-cpuidle-skip-synchronize_rcu-on-single-CPU-systems.patch
Patch0103: 0103-sysrq-skip-synchronize_rcu-if-there-is-no-old-op.patch
Patch0104: 0104-fbcon-enable-no-blink-by-default.patch
Patch0105: 0105-vmstats-wakeups.patch
Patch0106: 0106-pci-probe.patch
Patch0107: 0107-cgroup.patch
Patch0108: 0108-smpboot.patch
Patch0109: 0109-perf.patch
Patch0110: 0110-sched-fair-tweak-the-scheduler-to-favor-CPU-0.patch
Patch0111: 0111-pci-probe-identify-known-devices.patch
Patch0112: 0112-init-no-wait-for-the-known-devices.patch
Patch0113: 0113-fork-turn-mmput-into-an-async-function.patch
Patch0114: 0114-ksm-wakeups.patch
Patch0115: 0115-init-do_mounts-recreate-dev-root.patch
Patch0116: 0116-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
#Patch0117: 0117-KVM-x86-Add-hypercall-KVM_HC_RETURN_MEM.patch
#Patch0118: 0118-mm-shrink-caches.patch
#Patch0119: 0119-mm-page_alloc-return-memory-to-host.patch

# Serie    XYYY: Extra features modules
# AUFS
Patch1001: 1001-aufs-kbuild.patch
Patch1002: 1002-aufs-base.patch
Patch1003: 1003-aufs-mmap.patch
Patch1004: 1004-aufs-standalone.patch
Patch1005: 1005-aufs-driver-and-docs.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel kvm extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.5.4

# Serie    00XX: mainline, CVE, bugfixes patches

# Serie    01XX: Clear Linux patches
# Use when needed
# Added a warning to msleep (our local patch) to catch where it is used
# not all uses are bug
#%patch0101 -p1
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
%patch0113 -p1
%patch0114 -p1
%patch0115 -p1
%patch0116 -p1
#%patch0117 -p1
#%patch0118 -p1
#%patch0119 -p1

# Serie    XYYY: Extra features modules
# AUFS
%patch1001 -p1
%patch1002 -p1
%patch1003 -p1
%patch1004 -p1
%patch1005 -p1

cp %{SOURCE1} .

%build
BuildKernel() {
    MakeTarget=$1

    Arch=x86_64
    ExtraVer="-%{release}.kvm"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make -s mrproper
    cp config .config

    make -s ARCH=$Arch oldconfig > /dev/null
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch $MakeTarget %{?sparse_mflags}
    make -s CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} ARCH=$Arch modules %{?sparse_mflags} || exit 1
}

BuildKernel bzImage

%install

InstallKernel() {
    KernelImage=$1

    Arch=x86_64
    KernelVer=%{kversion}
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 .config    ${KernelDir}/config-${KernelVer}
    install -m 644 System.map ${KernelDir}/System.map-${KernelVer}
    install -m 644 %{SOURCE2} ${KernelDir}/cmdline-${KernelVer}
    cp  $KernelImage ${KernelDir}/org.clearlinux.kvm.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.kvm.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules/$KernelVer
    make -s ARCH=$Arch INSTALL_MOD_PATH=%{buildroot}/usr modules_install KERNELRELEASE=$KernelVer

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source

    # Erase some modules index
    for i in alias ccwmap dep ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols usbmap softdep devname
    do
        rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.${i}*
    done
    rm -f %{buildroot}/usr/lib/modules/${KernelVer}/modules.*.bin
}

InstallKernel arch/x86/boot/bzImage

rm -rf %{buildroot}/usr/lib/firmware

# Recreate modules indices
depmod -a -b %{buildroot}/usr %{kversion}

ln -s org.clearlinux.kvm.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-kvm

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.kvm.%{version}-%{release}
/usr/lib/kernel/default-kvm
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
