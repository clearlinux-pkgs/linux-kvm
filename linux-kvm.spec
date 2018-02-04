#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        4.15.1
Release:        253
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.15.1.tar.xz
Source1:        config
Source2:        cmdline

%define ktarget  kvm
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  bash >= 2.03
BuildRequires:  bc
BuildRequires:  binutils-dev
BuildRequires:  elfutils-dev
BuildRequires:  make >= 3.78
BuildRequires:  openssl-dev
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  kmod

Requires: systemd-console

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#    000X: cve, bugfixes patches

#    00XY: Mainline patches, upstream backports

# Serie    01XX: Clear Linux patches
Patch0101: 0101-cpuidle-skip-synchronize_rcu-on-single-CPU-systems.patch
Patch0102: 0102-sysrq-skip-synchronize_rcu-if-there-is-no-old-op.patch
Patch0103: 0103-fbcon-enable-no-blink-by-default.patch
Patch0104: 0104-mm-reduce-vmstat-wakeups.patch
Patch0105: 0105-pci-probe.patch
Patch0106: 0106-cgroup-delayed-work.patch
Patch0107: 0107-smpboot-reuse-timer-calibration.patch
Patch0108: 0108-perf.patch
Patch0109: 0109-pci-probe-identify-known-devices.patch
Patch0110: 0110-init-no-wait-for-the-known-devices.patch
Patch0111: 0111-ksm-wakeups.patch
Patch0112: 0112-init-do_mounts-recreate-dev-root.patch
Patch0113: 0113-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0114: 0114-cirrus-set-ioremap_cache.patch

# Clear Linux KVM Memory Optimization
Patch0151: 0151-mm-Export-do_madvise.patch
Patch0152: 0152-x86-kvm-Notify-host-to-release-pages.patch
Patch0153: 0153-x86-Return-memory-from-guest-to-host-kernel.patch
Patch0154: 0154-sysctl-vm-Fine-grained-cache-shrinking.patch

# nospec
Patch0401: 0401-Documentation-document-array_ptr.patch
Patch0402: 0402-asm-nospec-array_ptr-sanitize-speculative-array-de-r.patch
Patch0403: 0403-x86-implement-array_ptr_mask.patch
Patch0404: 0404-x86-introduce-__uaccess_begin_nospec-and-ifence.patch
Patch0405: 0405-x86-__get_user-use-__uaccess_begin_nospec.patch
Patch0406: 0406-x86-get_user-use-pointer-masking-to-limit-speculatio.patch
Patch0407: 0407-x86-narrow-out-of-bounds-syscalls-to-sys_read-under-.patch
Patch0408: 0408-vfs-fdtable-prevent-bounds-check-bypass-via-speculat.patch
Patch0409: 0409-kvm-x86-update-spectre-v1-mitigation.patch
Patch0410: 0410-nl80211-sanitize-array-index-in-parse_txq_params.patch

# Serie    XYYY: Extra features modules

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel kvm extra files
Group:          kernel

%description extra
Linux kernel extra files

%prep
%setup -q -n linux-4.15.1

#     000X  cve, bugfixes patches

#     00XY  Mainline patches, upstream backports

#     01XX  Clear Linux patches
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
%patch0113 -p1
%patch0114 -p1

# Clear Linux KVM Memory Optimization
%patch0151 -p1
%patch0152 -p1
%patch0153 -p1
%patch0154 -p1

# nospec
%patch0401 -p1
%patch0402 -p1
%patch0403 -p1
%patch0404 -p1
%patch0405 -p1
%patch0406 -p1
%patch0407 -p1
%patch0408 -p1
%patch0409 -p1
%patch0410 -p1

# Serie    XYYY: Extra features modules

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
