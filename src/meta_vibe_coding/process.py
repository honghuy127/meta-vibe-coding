"""Bounded subprocess exchange shared by the coding-agent wrappers."""

import asyncio
import os
import signal
import time

from .core import FlowError


class CliFailure(FlowError):
    """Keep bounded stdout available for native error classification, never display it."""

    def __init__(self, stdout: bytes):
        super().__init__("unavailable", "The agent process failed. Check its installation and account configuration.")
        self.stdout = stdout


async def run_cli(args: list[str], *, content: str, cwd: str, env: dict[str, str], timeout: float) -> bytes:
    """No shell; bound both output streams and stop the process group on failure."""
    if timeout <= 0:
        raise TimeoutError()
    started = time.perf_counter()
    # asyncio's subprocess transport closes/kills an in-progress spawn on cancellation.
    process = await asyncio.wait_for(asyncio.create_subprocess_exec(*args, cwd=cwd, env=env,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, start_new_session=True), timeout)

    async def read(stream, limit):
        output = bytearray()
        while chunk := await stream.read(min(65_536, limit + 1 - len(output))):
            output.extend(chunk)
            if len(output) > limit:
                raise FlowError("invalid_output", "The agent output exceeded the prototype limit.")
        return bytes(output)

    readers = []

    async def exchange():
        process.stdin.write(content.encode("utf-8"))
        await process.stdin.drain()
        process.stdin.close()
        readers.extend([asyncio.create_task(read(process.stdout, 1_000_000)),
                        asyncio.create_task(read(process.stderr, 128_000))])
        stdout, _stderr, _returncode = await asyncio.gather(*readers, process.wait())
        if process.returncode:
            raise CliFailure(stdout)
        return stdout

    try:
        return await asyncio.wait_for(exchange(), max(0, timeout - (time.perf_counter() - started)))
    finally:
        # Descendants must not survive a cancelled or timed-out request.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        await process.wait()
        for task in readers:
            task.cancel()
        await asyncio.gather(*readers, return_exceptions=True)
