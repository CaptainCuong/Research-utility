#!/usr/bin/env python3
import argparse
import os
import shlex
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import psutil
from rich.text import Text

# NVML (NVIDIA Management Library)
try:
    import pynvml as nvml
except Exception as e:
    raise SystemExit("pynvml is required. Install with: pip install pynvml") from e

# Textual TUI
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Input, Label
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.timer import Timer
from textual import events

@dataclass
class ProcInfo:
    pid: int
    gpu_index: int
    gpu_mem_mb: int
    username: str
    cmd: str

@dataclass
class GPUInfo:
    index: int
    name: str
    util_pct: int
    mem_used_mb: int
    mem_total_mb: int
    temp_c: int
    processes: List[ProcInfo]

def human_mb(v: int) -> str:
    return f"{v:,} MB"

def get_username(pid: int) -> str:
    try:
        return psutil.Process(pid).username()
    except Exception:
        return "?"

def get_cmdline(pid: int) -> str:
    try:
        p = psutil.Process(pid)
        cmd = p.cmdline()
        if not cmd:
            return p.name()
        # compact long commands
        s = " ".join(shlex.quote(x) for x in cmd)
        return (s[:120] + "…") if len(s) > 120 else s
    except Exception:
        return "?"

def collect_gpu_info() -> List[GPUInfo]:
    gpus: List[GPUInfo] = []
    device_count = nvml.nvmlDeviceGetCount()
    for i in range(device_count):
        h = nvml.nvmlDeviceGetHandleByIndex(i)
        name = nvml.nvmlDeviceGetName(h).decode() if isinstance(nvml.nvmlDeviceGetName(h), bytes) else nvml.nvmlDeviceGetName(h)
        util = nvml.nvmlDeviceGetUtilizationRates(h)
        mem = nvml.nvmlDeviceGetMemoryInfo(h)
        temp = 0
        try:
            temp = nvml.nvmlDeviceGetTemperature(h, nvml.NVML_TEMPERATURE_GPU)
        except nvml.NVMLError:
            temp = 0

        procs: List[ProcInfo] = []
        # Prefer compute procs; fall back to graphics if needed
        pid_lists = []
        try:
            pid_lists.append(nvml.nvmlDeviceGetComputeRunningProcesses_v3(h))
        except Exception:
            try:
                pid_lists.append(nvml.nvmlDeviceGetComputeRunningProcesses(h))
            except Exception:
                pid_lists = []
        try:
            pid_lists.append(nvml.nvmlDeviceGetGraphicsRunningProcesses_v3(h))
        except Exception:
            try:
                pid_lists.append(nvml.nvmlDeviceGetGraphicsRunningProcesses(h))
            except Exception:
                pass

        for plist in pid_lists:
            for p in plist:
                pid = int(p.pid)
                mem_mb = int(p.usedGpuMemory // (1024 * 1024)) if hasattr(p, "usedGpuMemory") else 0
                procs.append(
                    ProcInfo(
                        pid=pid,
                        gpu_index=i,
                        gpu_mem_mb=mem_mb,
                        username=get_username(pid),
                        cmd=get_cmdline(pid),
                    )
                )

        gpus.append(
            GPUInfo(
                index=i,
                name=name,
                util_pct=int(util.gpu) if hasattr(util, "gpu") else 0,
                mem_used_mb=int(mem.used // (1024 * 1024)),
                mem_total_mb=int(mem.total // (1024 * 1024)),
                temp_c=int(temp),
                processes=procs,
            )
        )
    return gpus

class GPUSummary(Static):
    gpu: reactive[Optional[GPUInfo]] = reactive(None)

    def watch_gpu(self, gpu: Optional[GPUInfo]) -> None:
        if gpu is None:
            self.update("No GPU data")
            return
        # Build a neat summary box with bars
        util_bar = self._bar(gpu.util_pct, 100, label=f"Util {gpu.util_pct}%")
        mem_pct = int(100 * gpu.mem_used_mb / max(1, gpu.mem_total_mb))
        mem_bar = self._bar(mem_pct, 100, label=f"Mem {gpu.mem_used_mb}/{gpu.mem_total_mb} MB")
        temp = f"{gpu.temp_c}°C" if gpu.temp_c else "n/a"

        header = Text.assemble(
            (f"GPU {gpu.index} • ", "bold"),
            (gpu.name, "bold"),
            "\n",
        )
        stats = Text.assemble(
            ("Temp: ", "dim"), (temp, "bold"),
            ("   Procs: ", "dim"), (str(len(gpu.processes)), "bold"),
            "\n",
        )
        self.update(Text.from_markup(f"{header}") + util_bar + "\n" + mem_bar + "\n" + stats)

    def _bar(self, value: int, total: int, width: int = 30, label: str = "") -> str:
        value = max(0, min(value, total))
        filled = int((value / total) * width)
        empty = width - filled
        return f"[{'#' * filled}{'-' * empty}] {label}"

class GPUApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    #body {
        height: 1fr;
    }
    #left {
        width: 40%;
        border: panel;
    }
    #right {
        width: 60%;
        border: panel;
    }
    .gpu-card {
        padding: 1 2;
        border: round;
        margin: 1 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_now", "Refresh"),
        ("f", "focus_filter", "Filter User"),
        ("c", "clear_filter", "Clear Filter"),
    ]

    interval: reactive[float] = reactive(1.0)
    user_filter: reactive[str] = reactive("")
    _timer: Optional[Timer] = None

    def __init__(self, interval: float = 1.0, filter_user: str = ""):
        super().__init__()
        self.interval = interval
        self.user_filter = filter_user
        self._gpu_cards: Dict[int, GPUSummary] = {}
        self._table: Optional[DataTable] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with VerticalScroll(id="left"):
                # dynamic GPU cards will be inserted here
                pass
            with Vertical(id="right"):
                yield Label("Process List (press F to filter by user)", id="table_label")
                table = DataTable(id="proc_table", zebra_stripes=True)
                table.add_columns("GPU", "PID", "User", "GPU Mem (MB)", "Command")
                yield table
                yield Input(placeholder="Type username then Enter…", id="filter_input")
        yield Footer()

    async def on_mount(self) -> None:
        # init NVML
        try:
            nvml.nvmlInit()
        except Exception as e:
            self.exit(message=f"Failed to initialize NVML: {e}")
            return

        # create GPU cards
        left = self.query_one("#left")
        try:
            for i in range(nvml.nvmlDeviceGetCount()):
                card = GPUSummary(classes="gpu-card")
                self._gpu_cards[i] = card
                left.mount(card)
        except Exception:
            pass

        self._table = self.query_one("#proc_table", DataTable)
        self._filter_input = self.query_one("#filter_input", Input)
        self._filter_input.display = False
        self._refresh()
        self._timer = self.set_interval(self.interval, self._refresh)

    def action_refresh_now(self) -> None:
        self._refresh()

    def action_focus_filter(self) -> None:
        self._filter_input.display = True
        self._filter_input.value = self.user_filter
        self.set_focus(self._filter_input)

    def action_clear_filter(self) -> None:
        self.user_filter = ""
        self._filter_input.display = False
        self._refresh()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "filter_input":
            self.user_filter = event.value.strip()
            self._filter_input.display = False
            self._refresh()

    def on_key(self, event: events.Key) -> None:
        # allow ESC to close filter box quickly
        if event.key == "escape" and self._filter_input.display:
            self._filter_input.display = False
            self._refresh()

    def _refresh(self) -> None:
        try:
            gpus = collect_gpu_info()
        except Exception as e:
            self.bell()
            return

        # Update cards
        for gpu in gpus:
            self._gpu_cards.get(gpu.index, GPUSummary()).gpu = gpu

        # Update table
        if self._table is None:
            return
        self._table.clear()
        rows = []
        for gpu in gpus:
            for p in gpu.processes:
                if self.user_filter and p.username and self.user_filter.lower() not in p.username.lower():
                    continue
                rows.append((
                    str(gpu.index),
                    str(p.pid),
                    p.username,
                    str(p.gpu_mem_mb),
                    p.cmd,
                ))
        # sort by GPU then pid
        rows.sort(key=lambda r: (int(r[0]), int(r[1])))
        for r in rows:
            style = "bold" if r[2] and r[2] == os.getenv("USER", "") else ""
            self._table.add_row(*r, style=style)

    async def on_unmount(self) -> None:
        try:
            nvml.nvmlShutdown()
        except Exception:
            pass

def main():
    parser = argparse.ArgumentParser(description="GPU Monitor TUI (Textual)")
    parser.add_argument("--interval", type=float, default=1.0, help="Refresh interval in seconds")
    parser.add_argument("--filter", type=str, default="", help="Filter processes by username")
    args = parser.parse_args()

    app = GPUApp(interval=args.interval, filter_user=args.filter)
    app.run()

if __name__ == "__main__":
    main()
