from pathlib import Path
from utils.load import load_config
from utils.download import download_file, extract_tarball
from utils.execute import run_command_live, run_command
import os
import multiprocessing

DEFAULT_PATCH = {
    "CONFIG_TC": "n",           # TC deaktivieren
    "CONFIG_STATIC": "y",       # Optional: statisches Binary
}


def set_config_option(cfg_file: Path, key: str, value: str):
    """Setzt oder ersetzt eine Option in der .config"""
    lines = cfg_file.read_text().splitlines()
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            break
    else:
        lines.append(f"{key}={value}")
    cfg_file.write_text("\n".join(lines) + "\n")


def patch_config(busybox_src_dir: Path, patch_options: dict):
    """Patched die .config Datei mit den gegebenen Optionen"""
    cfg_file = busybox_src_dir / ".config"
    if not cfg_file.exists():
        raise FileNotFoundError(f".config nicht gefunden in {busybox_src_dir}")

    for key, val in patch_options.items():
        set_config_option(cfg_file, key, val)
    print(f"Console > .config gepatcht: {list(patch_options.keys())}")


def build_busybox(work_dir: Path, downloads_dir: Path, rootfs_dir: Path, args):
    """Lädt, entpackt, patcht, kompiliert und installiert BusyBox"""
    
    # Config laden
    config = load_config(Path("configs") / args.config)
    version = config["version"]
    url = config["url"]
    cross_compile = config.get("cross_compile", {})
    extra_cfg = config.get("extra_config", {})
    

    # Architektur anpassen
    if args.arch:
        cross_compile["arch"] = args.arch
        if args.arch == "x86_64":
            cross_compile["compiler_prefix"] = ""
        elif args.arch == "arm64":
            cross_compile["compiler_prefix"] = "aarch64-linux-gnu-"

    # Pfade
    downloads_dir.mkdir(parents=True, exist_ok=True)
    rootfs_dir.mkdir(parents=True, exist_ok=True)

    # Download & Extraktion
    print(f"Console > Lade BusyBox {version} herunter...")
    tarball = download_file(url, downloads_dir)

    print(f"Console > Entpacke BusyBox {version}...")
    extracted_dir = extract_tarball(tarball, work_dir)

    # Quelle ermitteln
    subdirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
    src_dir = subdirs[0] if len(subdirs) == 1 else extracted_dir
    busybox_src_dir = work_dir / f"busybox-{version}"
    print(f"Console > BusyBox Quellverzeichnis: {busybox_src_dir}")

    # Umgebungsvariablen für Cross-Compile
    env = os.environ.copy()
    arch = cross_compile.get("arch", "arm64")
    env["ARCH"] = arch
    if arch != "x86_64":
        env["CROSS_COMPILE"] = cross_compile.get("compiler_prefix", "")
    env["CFLAGS"] = cross_compile.get("cflags", "")
    env["LDFLAGS"] = cross_compile.get("ldflags", "")

    # 1️⃣ defconfig erstellen
    run_command_live(["make", "defconfig"], cwd=busybox_src_dir, env=env, desc="BusyBox defconfig erstellen")

    # 2️⃣ .config patchen (TC deaktivieren + optional extra_cfg)
    patch_config(busybox_src_dir, {**DEFAULT_PATCH, **extra_cfg})

    # 3️⃣ oldconfig non-interaktiv
    # run_command_live(["make", "oldconfig"], cwd=busybox_src_dir, env=env, desc="BusyBox oldconfig (non-interaktiv)", input="/dev/null")
    run_command_live(
        ["make", "oldconfig", "KCONFIG_ALLCONFIG=/dev/null"],
        cwd=busybox_src_dir,
        env=env,
        desc="BusyBox oldconfig (non-interaktiv)"
    )


    # 4️⃣ Kompilieren mit allen Cores
    num_cores = multiprocessing.cpu_count()
    print(f"Console > Kompiliere BusyBox mit {num_cores} Cores...")
    run_command_live(["make", f"-j{num_cores}"], cwd=busybox_src_dir, env=env, desc="BusyBox kompilieren")

    # 5️⃣ Installation ins RootFS
    run_command_live(["make", f"CONFIG_PREFIX={rootfs_dir}", "install"], cwd=busybox_src_dir, env=env, desc="BusyBox installieren")

    print(f"✅ BusyBox {version} erfolgreich installiert in {rootfs_dir}")
    
    
    
