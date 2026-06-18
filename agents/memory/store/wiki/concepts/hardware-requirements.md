---
title: Supported Hardware & System Requirements
category: concepts
sources: ["installation.html", "docker-installation.html"]
last_updated: 2026-05-17
confidence: high
---

Minimum and recommended hardware and software configurations for running MindSpore Transformers.

## Supported NPU Hardware

MindSpore Transformers 1.8.0 is certified on:

- **Atlas 800T A2** — Ascend 910B chips for training
- **Atlas 800I A2** — Ascend 910B chips for inference
- **Atlas 900 A3 SuperPoD** — Multi-NPU cluster for large-scale distributed training

All use Ascend NPU architecture (not NVIDIA CUDA).

## System Requirements

### Firmware & Driver

Version must match from [[config/version-compatibility]]. For MindFormers 1.8.0:

- **Firmware & Driver:** 25.5.0

Install at `/usr/local/Ascend/` following [Ascend official documentation](https://ascend.huawei.com/).

### CANN (Compute Architecture for Neural Networks)

Version must match compatibility table.

- **CANN 8.5.0** for MindFormers 1.8.0
- Includes CANN toolkit and CANN kernels (910B)

### MindSpore Framework

- **MindSpore 2.7.2** for MindFormers 1.8.0

### Python

- **Python 3.11.4** (officially supported for 1.8.0)
- Avoid other Python versions; may cause ABI incompatibilities

### Network (Docker Builds)

Stable internet access required to:
- Download CANN packages from Huawei cloud
- Download MindSpore wheels from PyPI
- Clone MindFormers source from Gitee

## Recommended Host Specifications (Bare Metal)

For single-node development with 1–2 NPUs:

- **CPU:** 16+ cores (Intel Xeon or ARM)
- **RAM:** 128 GB (for large model weights during training)
- **Storage:** 500 GB SSD (OS + CANN + MindSpore + code + model checkpoints)
- **Network:** 1 Gbps+ Ethernet

For multi-node clusters, refer to Ascend cluster documentation.

## Docker Host Requirements

When running in containers:

- **Host OS:** Linux (Ubuntu 24.04 recommended per Dockerfile)
- **Docker:** Version 26.1.4+
- **NPU drivers on host:** Must be installed; containers mount them at runtime
- **Storage:** Image size ~14 GB; add space for training data and logs

## Version Mismatch Pitfalls

**Common failure:** Installing MindSpore 2.7.1 with CANN 8.5.0 (mismatch on minor version).

**Result:** Runtime type errors, operator dispatch failures, or silent numerical divergence.

**Prevention:** Always verify all four versions (MindFormers, MindSpore, CANN, firmware) match the [[config/version-compatibility]] table before installation.