---
title: MindSpore Transformers Installation Procedure
category: workflows
sources: ["installation.html"]
last_updated: 2026-05-17
confidence: high
---

Step-by-step installation of MindSpore Transformers and its dependencies on Ascend hardware.

## Prerequisite: Version Selection

1. Choose target MindFormers version (see [[config/version-compatibility]]).
2. Obtain matching MindSpore, CANN, and firmware versions from the compatibility table.
3. **All four versions must match exactly.** Mismatches are a common installation failure cause.

## Step 1: Install Firmware & Driver

Download and install Ascend firmware and driver from the [[config/version-compatibility]] table.

```bash
# Reference: follow Ascend official documentation
# https://ascend.huawei.com/
# Install to /usr/local/Ascend/
```

**Hardware supported:** Atlas 800T A2, Atlas 800I A2, Atlas 900 A3 SuperPoD.

Verify:
```bash
npu-smi info
```

## Step 2: Install CANN

Download CANN toolkit and kernels from Ascend repository. Version must match table.

```bash
# Example for CANN 8.5.0:
# Download from Ascend community and install
# Installation creates /usr/local/Ascend/cann/
```

Verify:
```bash
# CANN binaries should be in PATH
which ccec_compiler
```

## Step 3: Install MindSpore

Install MindSpore Python wheel matching the version in compatibility table.

```bash
pip install mindspore==2.7.2  # Example for MindFormers 1.8.0
```

Verify:
```bash
python -c "import mindspore as ms; print(ms.__version__)"
```

## Step 4: Install Python 3.11.4

MindFormers 1.8.0 officially supports Python 3.11.4. Other versions may cause import or ABI incompatibilities.

```bash
# Install via your system package manager or pyenv
python --version  # Verify 3.11.4
```

## Step 5: Install MindSpore Transformers from Source

Clone and build:

```bash
git clone -b r1.8.0 https://gitee.com/mindspore/mindformers.git
cd mindformers
bash build.sh
```

This compiles and installs the MindFormers package. Build time depends on network speed and hardware (typically 10–30 minutes).

## Step 6: Verify Installation

```bash
python -c "import mindformers as mf; mf.run_check()"
```

Success output:
```
- INFO - All checks passed, used **** seconds, the environment is correctly set up!
```

If the check fails, verify each step's prerequisites and version compatibility.

## Common Failure Modes

| Error | Cause | Fix |
|---|---|---|
| Module not found: `mindformers` | Step 5 incomplete or build.sh failed | Re-run `bash build.sh` and check for errors |
| Version mismatch errors at runtime | MindSpore version ≠ CANN version | Check compatibility table; reinstall matching versions |
| `npu-smi` command not found | Firmware/driver not installed or not in PATH | Verify Step 1; check `/usr/local/Ascend/driver/` exists |
| Permission denied on `/usr/local/Ascend/` | Insufficient privileges during installation | Reinstall CANN and firmware with sudo |