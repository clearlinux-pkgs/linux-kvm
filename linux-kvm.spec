#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us to optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        4.15.3
Release:        253
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.15.3.tar.xz
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


Patch0201: 0001-ima-Use-i_version-only-when-filesystem-supports-it.patch
Patch0202: 0002-lustre-don-t-set-f_version-in-ll_readdir.patch
Patch0203: 0003-ntfs-remove-i_version-handling.patch
Patch0204: 0004-fs-new-API-for-handling-inode-i_version.patch
Patch0205: 0005-fs-don-t-take-the-i_lock-in-inode_inc_iversion.patch
Patch0206: 0006-fat-convert-to-new-i_version-API.patch
Patch0207: 0007-affs-convert-to-new-i_version-API.patch
Patch0208: 0008-afs-convert-to-new-i_version-API.patch
Patch0209: 0009-btrfs-convert-to-new-i_version-API.patch
Patch0210: 0010-exofs-switch-to-new-i_version-API.patch
Patch0211: 0011-ext2-convert-to-new-i_version-API.patch
Patch0212: 0012-ext4-convert-to-new-i_version-API.patch
Patch0213: 0013-nfs-convert-to-new-i_version-API.patch
Patch0214: 0014-nfsd-convert-to-new-i_version-API.patch
Patch0215: 0015-ocfs2-convert-to-new-i_version-API.patch
Patch0216: 0016-ufs-use-new-i_version-API.patch
Patch0217: 0017-xfs-convert-to-new-i_version-API.patch
Patch0218: 0018-IMA-switch-IMA-over-to-new-i_version-API.patch
Patch0219: 0019-fs-only-set-S_VERSION-when-updating-times-if-necessa.patch
Patch0220: 0020-xfs-avoid-setting-XFS_ILOG_CORE-if-i_version-doesn-t.patch
Patch0221: 0021-btrfs-only-dirty-the-inode-in-btrfs_update_time-if-s.patch
Patch0222: 0022-fs-handle-inode-i_version-more-efficiently.patch
patch0223: kvm-retpoline.patch


Patch0500: zero-regs.patch

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
%setup -q -n linux-4.15.3

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

# upstream backports
%patch0201 -p1
%patch0202 -p1
%patch0203 -p1
%patch0204 -p1
%patch0205 -p1
%patch0206 -p1
%patch0207 -p1
%patch0208 -p1
%patch0209 -p1
%patch0210 -p1
%patch0211 -p1
%patch0212 -p1
%patch0213 -p1
%patch0214 -p1
%patch0215 -p1
%patch0216 -p1
%patch0217 -p1
%patch0218 -p1
%patch0219 -p1
%patch0220 -p1
%patch0221 -p1
%patch0222 -p1
%patch0223 -p1

%patch0500 -p1

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
