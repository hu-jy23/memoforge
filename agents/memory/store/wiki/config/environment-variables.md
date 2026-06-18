---
title: MindSpore Transformers Environment Variables
category: config
sources: ["env_variables.html"]
last_updated: 2026-05-17
confidence: high
---

Environment variables that control runtime behaviour, logging, debugging, and device management in MindSpore Transformers.

## Debug & Determinism

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `HCCL_DETERMINISTIC` | false | true/false | Enable deterministic AllReduce/ReduceScatter/Reduce operations. **Trade-off:** eliminates multi-device ordering randomness but degrades performance. Use only when reproducibility required. |
| `LCCL_DETERMINISTIC` | 0 | 1/0 | Enable LCCL deterministic AllReduce. Effective only when rankSize ≤ 8. |
| `ASCEND_LAUNCH_BLOCKING` | 0 | 1/0 | Force synchronous operator execution (sync mode). Set to 1 during debugging to capture correct stack traces; set to 0 for production. |
| `TE_PARALLEL_COMPILER` | 8 | 1–32 | Operator parallel compilation processes. Max ≤ `cpu_cores * 80% / npu_count`. Set to 1 for sequential compilation during debug. |

## Matrix & Memory Optimization

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `CUSTOM_MATMUL_SHUFFLE` | on | on/off | Enable matmul shuffle for specific matrix sizes. Disable if matrix dimensions don't match tuned sizes. |
| `MS_MEMORY_STATISTIC` | 0 | 1/0 | Enable memory usage statistics for memory profiling. |
| `MS_ALLOC_CONF` | — | key:value pairs | Memory allocation strategy: `enable_vmm`, `vmm_align_size`, `memory_tracker`, `acl_allocator`, `somas_whole_block`. |

## Device & NPU

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `DEVICE_ID` | 0 | 0–N | Logical ID of NPU to use. Multi-machine setups repeat DEVICE_ID; use `RANK_ID` instead. |
| `RANK_ID` | — | integer | Unique process rank across cluster. Formula: `RANK_ID = SERVER_ID * DEVICE_NUM + DEVICE_ID` for multi-machine. |
| `RANK_SIZE` | — | >1 | Total number of NPUs across all machines. |
| `MS_NODE_ID` | — | integer | Process rank for dynamic networking startup. |
| `DEVICE_NUM_PER_NODE` | 8 | integer | Number of NPUs per server. |
| `MS_WORKER_NUM` | — | integer | Count of MS_WORKER processes for distributed training. |

## Logging & Paths

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `GLOG_v` | 3 | 0–4 | MindSpore log level: 0=DEBUG, 1=INFO, 2=WARN, 3=ERROR, 4=CRITICAL. |
| `ASCEND_GLOBAL_LOG_LEVEL` | 3 | 0–4 | CANN log level: 0=DEBUG, 1=INFO, 2=WARN, 3=ERROR, 4=NONE. |
| `ASCEND_SLOG_PRINT_TO_STDOUT` | 0 | 1/0 | Print logs to stdout instead of log files. |
| `LOCAL_DEFAULT_PATH` | ./output | path | Default directory for logs and artifacts. |
| `LOG_MF_PATH` | ./output/log | path | MindFormers-specific log directory. |
| `MF_LOG_SUFFIX` | — | string | Append suffix to log folders to isolate per-job logs. |
| `PLOG_REDIRECT_TO_OUTPUT` | False | True/False | Redirect plog output to ./output directory. |

## Communication Timeouts

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `HCCL_EXEC_TIMEOUT` | 1836 | (0, 17340] seconds | Timeout for device-to-device sync during AllReduce; increase for slow networks. |
| `HCCL_CONNECT_TIMEOUT` | 120 | [120, 7200] seconds | Timeout for socket setup between devices in distributed training/inference. |

## Model & Framework Control

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `RUN_MODE` | predict | predict/finetune/train/eval | Execution mode. |
| `USE_ROPE_SELF_DEFINE` | true | true/false | Use fused RoPE operator for efficiency. Keep true unless debugging. |
| `MS_ENABLE_INTERNAL_BOOST` | on | on/off | Enable MindSpore internal acceleration. Keep on for production; disable to isolate optimization effects during profiling. |
| `ENFORCE_EAGER` | False | False/True | Disable JIT compilation (eager execution only). False=JIT on (faster); True=JIT off (debugging). |
| `MS_ENABLE_FA_FLATTEN` | on | on/off | Enable FlashAttention flatten optimization. Disable for models not yet adapted. |

## Data & Cache

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `TRANSFORMERS_OFFLINE` | 0 | 1/on/true/yes or else | Force read-only offline local files; disallow network download. Set 1 in air-gapped environments. |
| `MDS_ENDPOINT` | https://modelers.cn | URL | openMind Hub endpoint. |
| `OM_MODULES_CACHE` | ~/.cache/openmind/modules | path | openMind modules cache directory. |
| `OPENMIND_CACHE` | ~/.cache/openmind/hub | path | openMind Hub cache directory. |

## Experimental & Deprecated

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `EXPERIMENTAL_KERNEL_LAUNCH_GROUP` | — | thread_num:N,kernel_group_num:M | **Experimental:** Enable parallel kernel launch. Supports DeepSeek inference; may regress on other models. |
| `MS_ENABLE_TFT` | — | {TTP:1,UCE:1,...} | Enable Training Fault Tolerance features. |
| `MS_INTERNAL_DISABLE_CUSTOM_KERNEL_LIST` | PagedAttention | string | Disable custom operators by name. Experimental; ignore unless instructed. |
| `ENABLE_LAZY_INLINE` | 1 | 1/0 | **Deprecated:** Will be removed next version. |
| `ENABLE_LAZY_INLINE_NO_PIPELINE` | 0 | 1/0 | **Deprecated:** Will be removed next version. |

## Fault Detection (Experimental)

| Variable | Default | Values | Purpose |
|---|---|---|---|
| `NPU_ASD_ENABLE` | 0 | 0–3 | Enable anomaly detection: 0=off, 1=log only, 2=log+throw, 3=log all (normal + anomaly). |
| `MS_SDC_DETECT_ENABLE` | 0 | 1/0 | Enable CheckSum detection of silent data corruption. |