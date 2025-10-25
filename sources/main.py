import argparse
import multiprocessing
import os
import json 

from pathlib import Path
from utils.create import (
    create_directories,
    create_etc_files,
    create_busybox_init,
    create_dev_nodes,
    create_symlinks,
    set_rootfs_permissions,
    copy_qemu_user_static
)
from utils.load import load_config

from core.busybox import build_busybox
from core.modify_rootfs import chroot

# ---------------------------
# Projektverzeichnisse
# ---------------------------
app_dir = Path(__file__).parent.resolve()
work_dir = app_dir / "work"
downloads_dir = work_dir / "downloads"
build_dir = work_dir / "build"
output_dir = work_dir / "output"
rootfs_dir = build_dir / "rootfs"
bootfs_dir = build_dir / "bootfs"




# ---------------------------
# RootFS erstellen
# ---------------------------
def create_rootfs(args):
    create_directories()
    create_etc_files()
    create_dev_nodes()
    create_busybox_init()
    create_symlinks()
    copy_qemu_user_static(arch=args.arch)
    set_rootfs_permissions()
    

# ---------------------------
# Main
# ---------------------------
def main():
    
    parser = argparse.ArgumentParser(description="BusyBox Build System")
    parser.add_argument("--config", type=str, default="busybox.json", help="Pfad zur BusyBox JSON Konfig")
    parser.add_argument("--arch", type=str, help="Überschreibe die Zielarchitektur (z.B. arm64, x86_64)")
    args = parser.parse_args()
    
    
    config = load_config(Path("configs") / args.config)
    version = config["version"]
    url = config["url"]
    cross_compile = config.get("cross_compile", {})
    extra_cfg = config.get("extra_config", {})
    
    
    
    print("[*] Starte RootFS-Erstellung...")
    create_rootfs(args=args)

    print("[*] Starte BusyBox-Build...")
    build_busybox(
        work_dir=work_dir,
        downloads_dir=downloads_dir,
        rootfs_dir=rootfs_dir,
        args=args
    )
    
    

    print("[+] Fertig! RootFS und BusyBox sind erstellt.")
    
    
    print("Chroote jetzt in das System!... .. .")
    
    busybox_src_dir = work_dir / f"busybox-{version}"
    chroot(busybox_src_dir=busybox_src_dir, rootfs_dir=rootfs_dir)


if __name__ == "__main__":
    main()
