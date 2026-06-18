---
title: Docker Image Build & Launch for MindSpore Transformers
category: workflows
sources: ["docker-installation.html"]
last_updated: 2026-05-17
confidence: high
---

Build a Docker image containing MindSpore Transformers with all dependencies pre-installed, using multi-stage build to minimize image size.

## Host Prerequisites

**Hardware:** NPU driver and firmware must be installed on the Docker host machine. The container mounts these at runtime; they are not included in the image.

**Software:** Docker 26.1.4 or later.

```bash
docker --version
```

**Network:** Stable internet connection to download CANN, MindSpore wheels, and MindFormers source from Huawei cloud.

## Build Image

### 1. Prepare Dockerfile

Create a directory and save the Dockerfile (available from [community issue](https://gitee.com/mindspore/mindformers/issues)):

```bash
mkdir -p mindformers-Dockerfiles
cd mindformers-Dockerfiles
# Save Dockerfile to this directory
```

### 2. Build Command

Template:
```bash
docker build -f Dockerfile \
  --build-arg PYTHON_VERSION="3.11.4" \
  --build-arg CANN_TOOLKIT_URL="<toolkit_url>" \
  --build-arg CANN_KERNELS_URL="<kernels_url>" \
  --build-arg MS_WHL_URL="<mindspore_wheel_url>" \
  --build-arg MINDFORMERS_GIT_REF="r1.8.0" \
  -t "mindformers:r1.8.0_ms2.7.2_cann8.5.0_py3.11" .
```

### 3. Build Arguments

| Argument | Example | Source |
|---|---|---|
| `PYTHON_VERSION` | 3.11.4 | [Python.org](https://www.python.org) |
| `CANN_TOOLKIT_URL` | https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/... | [Ascend Community](https://ascend.huawei.com/) |
| `CANN_KERNELS_URL` | https://ascend-repo.obs.cn-east-2.myhuaweicloud.com/CANN/... | Ascend Community |
| `MS_WHL_URL` | https://ms-release.obs.cn-north-4.myhuaweicloud.com/2.7.2/... | [MindSpore PyPI](https://pypi.org/project/mindspore) |
| `MINDFORMERS_GIT_REF` | r1.8.0 | [MindFormers Repository](https://gitee.com/mindspore/mindformers) |

### 4. Multi-Stage Build Strategy

The Dockerfile uses three stages:
- **Stage 1:** Install Python
- **Stage 2:** Install CANN toolkit and kernels
- **Stage 3:** Install MindSpore wheel and MindFormers source; combine all layers

This reduces final image size (~14 GB for r1.6.0 example) and improves build efficiency.

### 5. Build Duration

Expect 30 minutes to 1+ hour depending on network speed and hardware. Slow networks may significantly extend build time.

### 6. Verify Image

```bash
docker images | grep mindformers
```

Example output:
```
REPOSITORY    TAG                                IMAGE ID       CREATED        SIZE
mindformers   r1.8.0_ms2.7.2_cann8.5.0_py3.11  abc123def456   2 hours ago    14GB
```

## Launch Container

### Development Container

```bash
docker run -itd \
  --hostname $(hostname -I | awk '{print $1}' | tr '.' '-') \
  --ipc=host \
  --network=host \
  --device=/dev/davinci0:rwm \
  --device=/dev/davinci1:rwm \
  --device=/dev/davinci2:rwm \
  --device=/dev/davinci3:rwm \
  --device=/dev/davinci4:rwm \
  --device=/dev/davinci5:rwm \
  --device=/dev/davinci6:rwm \
  --device=/dev/davinci7:rwm \
  --device=/dev/davinci_manager:rwm \
  --device=/dev/devmm_svm:rwm \
  --device=/dev/hisi_hdc:rwm \
  -v /usr/local/dcmi:/usr/local/dcmi \
  -v /var/log/npu/:/usr/slog \
  -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
  -v /usr/bin/hccn_tool:/usr/bin/hccn_tool \
  -v /usr/local/Ascend/driver/lib64/common:/usr/local/Ascend/driver/lib64/common \
  -v /usr/local/Ascend/driver/lib64/driver:/usr/local/Ascend/driver/lib64/driver \
  -v /usr/local/Ascend/driver/version.info:/usr/local/Ascend/driver/version.info \
  -v /etc/ascend_install.info:/etc/ascend_install.info \
  -v /etc/hccn.conf:/etc/hccn.conf \
  -v /etc/localtime:/etc/localtime \
  --name my-mindformers \
  mindformers:r1.8.0_ms2.7.2_cann8.5.0_py3.11 \
  /bin/bash
```

### Key Mounts Explained

| Host Path | Container Path | Purpose |
|---|---|---|
| `/dev/davinci0-7` | Same | NPU device access (up to 8 NPUs) |
| `/dev/davinci_manager` | Same | NPU manager interface |
| `/dev/devmm_svm` | Same | Unified memory interface |
| `/dev/hisi_hdc` | Same | HDC debug/control interface |
| `/usr/local/Ascend/driver/` | Same | Host driver libraries (read-only) |
| `/var/log/npu/` | `/usr/slog` | NPU logs |
| `/etc/hccn.conf` | Same | HCCL collective communication config |

### Attach to Running Container

```bash
docker exec -it my-mindformers /bin/bash
```

## Security Risks (Production Hardening)

- **Root user:** Container runs as root by default. Create non-privileged user in production.
- **No resource limits:** Set `--cpus` and `--memory` flags to prevent resource exhaustion of host.
- **Broad device permissions:** `rwm` (read/write/mknod) on NPU devices. In security-sensitive environments, evaluate if read-only or restricted access suffices.

For production deployments, review and apply security best practices beyond the examples above.