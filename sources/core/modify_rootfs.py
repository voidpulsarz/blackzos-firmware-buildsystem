import os
import sys



from utils.execute import run, run_command, run_command_live


def chroot(busybox_src_dir, rootfs_dir):
    
    print("Copying Qemu-File !. .. ..")
    run_command_live(
        ["sudo", "cp", "/usr/bin/qemu-aarch64-static", "rootfs/usr/bin/"]
    )
    
    print("Mounting FileSystem !!!. .. .")
    run_command_live(["sudo", "mount", "-t", "proc", "/proc", "rootfs/proc"])
    run_command_live(["sudo", "mount", "-t", "sysfs", "/sys", "rootfs/sys"])
    run_command_live(["sudo", "mount", "--bind", "/dev", "rootfs/dev"])
    run_command_live(["sudo", "mount", "--bind", "/dev/pts", "rootfs/dev/pts"])


    print("Entering CHROOT!... . .")
    run_command_live(
            ["sudo", "chroot", rootfs_dir, "/usr/bin/qemu-aarch64-static", "/bin/sh"],
            cwd=busybox_src_dir,
            desc="BusyBox oldconfig (non-interaktiv)"
        )


