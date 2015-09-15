#
# This is a special configuration of the Linux kernel, aimed exclusively
# for running inside a KVM virtual machine
# This specialization allows us top optimize memory footprint and boot time.
#

Name:           linux-kvm
Version:        4.2.0
Release:        115
License:        GPL-2.0
Summary:        The Linux kernel optimized for running inside KVM
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://www.kernel.org/pub/linux/kernel/v4.x/linux-4.2.tar.xz
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
BuildRequires:  openssl
BuildRequires:  flex
BuildRequires:  bison
# For EFI Stub kernel
BuildRequires:  systemd-boot

# don't srip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

Patch1:  0001-msleep.patch
patch2:  0002-Skip-synchronize_rcu-on-single-CPU-systems.patch
patch3:  0003-sysrq-Skip-synchronize_rcu-if-there-is-no-old-op.patch
patch4:  0004-enable-no-blink-by-default.patch
patch5:  0005-wakeups.patch
patch6:  0006-probe.patch
patch7:  0007-cgroup.patch
patch8:  0008-smpboot.patch
patch9:  0009-perf.patch
patch10: 0010-tweak-the-scheduler-to-favor-CPU-0.patch
patch11: 0011-probe2.patch
patch12: 0012-No-wait-for-the-known-devices.patch

patch13: 0013-Turn-mmput-into-an-async-function.patch
Patch14: 0014-ptdamage.patch

Patch701: 701-kdbus.patch

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel
Group:          kernel

%description extra
Linux kernel extra file

%prep
%setup -q -n linux-4.2

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1

%patch13 -p1
%patch14 -p1

%patch701 -p1


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
    install -m 644 .config    ${KernelDir}/config-$KernelVer
    install -m 644 System.map ${KernelDir}/System.map-$KernelVer
    install -m 644 %{SOURCE2} ${KernelDir}/cmdline-$KernelVer
    cp  $KernelImage ${KernelDir}/org.clearlinux.kvm.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.kvm.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules/$KernelVer
    make -s ARCH=$Arch INSTALL_MOD_PATH=%{buildroot}/usr modules_install KERNELRELEASE=$KernelVer

    rm -f %{buildroot}/usr/lib/modules/$KernelVer/build
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/source

    # Erase some modules dictionaries
    for i in alias ccwmap dep ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols usbmap softdep devname
    do
        rm -f %{buildroot}/usr/lib/modules/$KernelVer/modules.${i}*
    done
    rm -f %{buildroot}/usr/lib/modules/$KernelVer/modules.*.bin
}

createEFIStub() {

   BZIMAGE=$1
   CMDLINE=%{SOURCE2}

   cp /usr/lib/os-release /tmp/os-release
   OS_RELEASE=/tmp/os-release
   sed -i 's/_ID=1/_ID=%{release}.kvm/'  $OS_RELEASE

   EFISTUB=org.clearlinux.kvm.%{version}-%{release}.efi

   kernel-efi-stub -r $OS_RELEASE -b $BZIMAGE -c $CMDLINE \
       -o %{buildroot}/usr/lib/kernel/$EFISTUB
}

InstallKernel arch/x86/boot/bzImage
createEFIStub arch/x86/boot/bzImage

rm -rf %{buildroot}/usr/lib/firmware

# Recreate modules indices
depmod -a -b %{buildroot}/usr %{kversion}

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/org.clearlinux.kvm.%{version}-%{release}.efi
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/org.clearlinux.kvm.%{version}-%{release}
/usr/lib/kernel/System.map-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
