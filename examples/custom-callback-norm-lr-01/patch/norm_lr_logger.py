"""
norm_lr_logger.py
-----------------
MindFormers custom callback that writes global_norm and learning_rate
to a JSONL file every ``log_interval`` training steps.

Registration
~~~~~~~~~~~~
The class is registered under ``MindFormerModuleType.CALLBACK`` so it
can be instantiated directly from a YAML ``callbacks`` section:

    callbacks:
      - type: NormLRLogger
        log_file: ./output/norm_lr.jsonl
        log_interval: 100

Prerequisites
~~~~~~~~~~~~~
- Import this module **before** the MindFormers Trainer reads the YAML
  config so that ``NormLRLogger`` is present in the callback registry.
- Set ``runner_wrapper.use_clip_grad: true`` in the training YAML to
  get real ``global_norm`` values.  When clip-grad is disabled,
  ``global_norm`` is ``None`` and will be recorded as JSON ``null``.

MFTrainOneStepCell output layout (confirmed from wiki api/training_callbacks):
    [0] loss
    [1] overflow flag
    [2] loss_scale
    [3] learning_rate   ← primary LR source
    [4] global_norm     ← None when use_clip_grad=False
"""

import json
import os
import warnings
from datetime import datetime, timezone

from mindspore.train import Callback
from mindformers.tools import MindFormerRegister, MindFormerModuleType


@MindFormerRegister.register(MindFormerModuleType.CALLBACK)
class NormLRLogger(Callback):
    """Log ``learning_rate`` and ``global_norm`` to a JSONL file at regular step intervals.

    Each line written to *log_file* is a JSON object with the fields:

    .. code-block:: json

        {
            "step": 100,
            "learning_rate": 9.8e-05,
            "global_norm": 0.432,
            "timestamp": "2026-05-17T08:00:00Z"
        }

    ``global_norm`` is ``null`` when gradient clipping is disabled
    (``runner_wrapper.use_clip_grad: false``) or when the value cannot
    be extracted.

    The file is opened in **append** mode, so training can be resumed
    from a checkpoint without overwriting previously logged data.

    Args:
        log_file (str): Path to the output JSONL file.  Parent directories
            are created automatically if they do not yet exist.
        log_interval (int): Write one record every *log_interval* steps.
            Must be >= 1.  Default is 100.
    """

    def __init__(self, log_file: str, log_interval: int = 100):
        super().__init__()
        if not log_file:
            raise ValueError("NormLRLogger: log_file must be a non-empty string.")
        if log_interval < 1:
            raise ValueError("NormLRLogger: log_interval must be >= 1.")

        self.log_file = log_file
        self.log_interval = log_interval

        # Create parent directory at construction time so the file path
        # is valid before the first write (avoids silent errors mid-run).
        log_dir = os.path.dirname(os.path.abspath(log_file))
        os.makedirs(log_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # MindSpore Callback interface
    # ------------------------------------------------------------------

    def step_end(self, run_context):
        """Called by MindSpore at the end of every training step.

        Writes one JSON line to *log_file* every *log_interval* steps.
        Never raises — extraction failures are silently recorded as
        ``null`` so training is never interrupted by logging errors.
        """
        cb_params = run_context.original_args()
        step = int(cb_params.cur_step_num)

        if step == 0:
            return
        if step % self.log_interval != 0:
            return

        record = {
            "step": step,
            "learning_rate": self._extract_lr(cb_params),
            "global_norm": self._extract_global_norm(cb_params),
            "timestamp": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Append mode: safe for checkpoint-and-resume workflows.
        try:
            with open(self.log_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            warnings.warn(
                f"NormLRLogger: failed to write to {self.log_file!r} at step {step}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )

    # ------------------------------------------------------------------
    # Private extraction helpers — all return None on any failure
    # ------------------------------------------------------------------

    def _extract_lr(self, cb_params):
        """Extract current learning rate.

        Primary path
        ~~~~~~~~~~~~
        ``cb_params.net_outputs[3]`` — the LR tensor emitted directly by
        ``MFTrainOneStepCell``.  This is the most accurate value because it
        reflects the LR that was **actually used** for the current step,
        including any warm-up or decay scheduling already applied on-device.

        Fallback path
        ~~~~~~~~~~~~~
        ``cb_params.optimizer.get_lr()`` — used when ``net_outputs`` is
        absent or shorter than 4 elements (e.g. bare ``TrainOneStepCell``
        without MindFormers wrapper).  Note: ``get_lr()`` returns the
        *scheduled* LR for the **next** step in some scheduler
        implementations, so there can be a one-step lag.

        Returns:
            float on success, ``None`` on failure.
        """
        # Primary: net_outputs[3]
        try:
            net_outputs = getattr(cb_params, "net_outputs", None)
            if isinstance(net_outputs, (tuple, list)) and len(net_outputs) >= 4:
                lr_tensor = net_outputs[3]
                return float(lr_tensor.asnumpy())
        except Exception:  # pylint: disable=broad-except
            pass

        # Fallback: optimizer.get_lr()
        try:
            optimizer = getattr(cb_params, "optimizer", None)
            if optimizer is not None:
                lr = optimizer.get_lr()
                if hasattr(lr, "asnumpy"):
                    return float(lr.asnumpy())
                return float(lr)
        except Exception:  # pylint: disable=broad-except
            pass

        return None

    def _extract_global_norm(self, cb_params):
        """Extract gradient global norm.

        Source: ``cb_params.net_outputs[4]``.

        MFTrainOneStepCell emits ``global_norm`` at index 4 only when
        ``runner_wrapper.use_clip_grad: true`` is set in the training
        config.  When clip-grad is disabled the value at index 4 is
        ``None``; when the output tuple is shorter than 5 elements the
        wrapper variant in use does not expose global_norm at all.

        Returns:
            float when a valid norm tensor is present,
            ``None`` otherwise (recorded as JSON ``null``).
        """
        try:
            net_outputs = getattr(cb_params, "net_outputs", None)
            if not isinstance(net_outputs, (tuple, list)):
                return None
            if len(net_outputs) < 5:
                return None
            gn = net_outputs[4]
            if gn is None:
                return None
            return float(gn.asnumpy())
        except Exception:  # pylint: disable=broad-except
            return None
