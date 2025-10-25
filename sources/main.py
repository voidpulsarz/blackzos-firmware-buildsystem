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
work_dir = Path("work")
downloads_dir = work_dir / "downloads"
build_dir = work_dir / "build"
output_dir = work_dir / "output"
rootfs_dir = build_dir / "rootfs"
bootfs_dir = build_dir / "bootfs"



def parse():
    parser = argparse.ArgumentParser(description="BusyBox Build System")
    parser.add_argument("--config", type=str, default="busybox.json", help="Pfad zur BusyBox JSON Konfig")
    parser.add_argument("--arch", type=str, help="Überschreibe die Zielarchitektur (z.B. arm64, x86_64)")
    args = parser.parse_args()
    return args



def configs(args):
    print("Console > Configuring BuildSystem ::::...:.. . :: .--. .")
    config = load_config(Path("configs") / args.config)
    version = config["version"]
    url = config["url"]
    cross_compile = config.get("cross_compile", {})
    extra_cfg = config.get("extra_config", {})
    config_patches = config.get("config_patch", [])
    busybox_src_dir = work_dir / f"busybox-{version}"
    return version, url, cross_compile, extra_cfg, config_patches, busybox_src_dir



# ---------------------------
# RootFS erstellen
# ---------------------------
def create_rootfs(args):
    print("[*] Starte RootFS-Erstellung...")
    create_directories()
    create_etc_files()
    create_dev_nodes()
    create_busybox_init()
    create_symlinks()
    copy_qemu_user_static(arch=args.arch)
    set_rootfs_permissions()
    

    
    
def busybox(args):
    print("[*] Starte BusyBox-Build...")
    build_busybox(
        work_dir=work_dir,
        downloads_dir=downloads_dir,
        rootfs_dir=rootfs_dir,
        args=args
    )
    print("[+] Fertig! RootFS und BusyBox sind erstellt.")




# ---------------------------
# Main
# ---------------------------
def main():
    # Get User's CommandLine Arguments
    args = parse()
    # Load the configs from the json
    version, url, cross_compile, extra_cfg, config_patches, busybox_src_dir = configs(args=args)
    # Creates the Workenviroment and the Target RootFS
    create_rootfs(args=args)
    # Downloads, Extracts, Configures, Compiles & Finnaly Installs Busybox into the RootFS
    busybox(args=args)
    
    chroot(busybox_src_dir=busybox_src_dir, rootfs_dir=rootfs_dir, arch=args.arch)


if __name__ == "__main__":
    main()
