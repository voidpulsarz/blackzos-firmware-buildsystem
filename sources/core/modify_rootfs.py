import os
from pathlib import Path
from utils.execute import run_command_live

def cpy(qemu_bin_name, rootfs_dir):
    target = Path(rootfs_dir) / "usr/bin" / qemu_bin_name
    print(f"Copying {qemu_bin_name} to {target}")
    run_command_live(["sudo", "cp", f"/usr/bin/{qemu_bin_name}", str(target)])

def chroot(busybox_src_dir, rootfs_dir, arch: str):
    qemu_map = {
        "arm64": "qemu-aarch64-static",
        "arm": "qemu-arm-static",
        "x86_64": "qemu-x86_64-static",
        "i386": "qemu-i386-static",
    }

    qemu_bin_name = qemu_map.get(arch)
    if qemu_bin_name:
        cpy(qemu_bin_name, rootfs_dir)
    else:
        print(f"[WARN] Keine QEMU-Binärdatei für Architektur {arch} gefunden.")

    # Mount FileSystems
    for src, target, fstype, opts in [
        ("/proc", "proc", "proc", None),
        ("/sys", "sys", "sysfs", None),
        ("/dev", "dev", None, "--bind"),
        ("/dev/pts", "dev/pts", None, "--bind"),
    ]:
        mount_target = Path(rootfs_dir) / target
        cmd = ["sudo", "mount"]
        if opts:
            cmd.append(opts)
        if fstype:
            cmd += ["-t", fstype]
        cmd += [src, str(mount_target)]
        run_command_live(cmd)

    # Chroot
    chroot_cmd = ["sudo", "chroot", rootfs_dir]
    if qemu_bin_name:
        chroot_cmd.append(f"/usr/bin/{qemu_bin_name}")
    chroot_cmd.append("/bin/sh")

    run_command_live(
        chroot_cmd,
        cwd=busybox_src_dir,
        desc="BusyBox oldconfig (non-interaktiv)"
    )
