from __future__ import annotations

import logging
import os
import hashlib
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from threading import Event
from typing import Callable, Iterable, Protocol

from app.infra.fs import PROJECT_ROOT
from app.infra.logging_setup import setup_logging


LOGGER = logging.getLogger(__name__)
ATTENDANT_TIME_ENV = "FRANK_BOT_ATTENDANT_TIME"
REQUESTER_TIME_ENV = "FRANK_BOT_REQUESTER_TIME"
DEFAULT_ATTENDANT_TIME = "09:00"
DEFAULT_REQUESTER_TIME = "08:00"
MAX_LATE_DELAY = timedelta(minutes=5)
DEFAULT_LOCK_PATH = PROJECT_ROOT / "frank_bot_service.lock"


class Runner(Protocol):
    def __call__(self, *, solicitante: bool) -> int: ...


@dataclass(frozen=True)
class ScheduleEntry:
    name: str
    at: time
    solicitante: bool


@dataclass(frozen=True)
class ScheduledEvent:
    entry: ScheduleEntry
    scheduled_for: datetime

    @property
    def key(self) -> tuple[str, datetime]:
        return self.entry.name, self.scheduled_for


class InstanceAlreadyRunningError(RuntimeError):
    pass


class InstanceLock:
    def __init__(self, path: Path = DEFAULT_LOCK_PATH) -> None:
        self.path = path
        self._acquired = False
        self._mutex_handle: int | None = None

    def _mutex_name(self) -> str:
        normalized_path = str(self.path.resolve()).casefold().encode("utf-8")
        digest = hashlib.sha256(normalized_path).hexdigest()
        return f"Local\\FrankBotService_{digest}"

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.CreateMutexW(None, True, self._mutex_name())
        if not handle:
            raise OSError(ctypes.get_last_error(), "Nao foi possivel criar mutex do scheduler")
        if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
            kernel32.CloseHandle(handle)
            raise InstanceAlreadyRunningError(
                f"Scheduler ja esta ativo: {self.path}"
            )
        try:
            self.path.write_text(str(os.getpid()), encoding="ascii")
        except Exception:
            kernel32.ReleaseMutex(handle)
            kernel32.CloseHandle(handle)
            raise
        self._mutex_handle = handle
        self._acquired = True

    def release(self) -> None:
        if not self._acquired:
            return
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.ReleaseMutex.argtypes = (wintypes.HANDLE,)
            kernel32.ReleaseMutex.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
            kernel32.CloseHandle.restype = wintypes.BOOL
            if self._mutex_handle is not None:
                kernel32.ReleaseMutex(self._mutex_handle)
                kernel32.CloseHandle(self._mutex_handle)
            try:
                if self.path.read_text(encoding="ascii").strip() == str(os.getpid()):
                    self.path.unlink(missing_ok=True)
            except FileNotFoundError:
                pass
        finally:
            self._mutex_handle = None
            self._acquired = False

    def __enter__(self) -> "InstanceLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()


def parse_daily_time(value: str, variable_name: str) -> time:
    try:
        parsed = datetime.strptime(value.strip(), "%H:%M").time()
    except ValueError as error:
        raise ValueError(f"{variable_name} deve usar o formato HH:MM: {value!r}") from error
    return parsed


def load_schedule(environ: dict[str, str] | None = None) -> tuple[ScheduleEntry, ...]:
    values = os.environ if environ is None else environ
    attendant_time = parse_daily_time(
        values.get(ATTENDANT_TIME_ENV, DEFAULT_ATTENDANT_TIME), ATTENDANT_TIME_ENV
    )
    requester_time = parse_daily_time(
        values.get(REQUESTER_TIME_ENV, DEFAULT_REQUESTER_TIME), REQUESTER_TIME_ENV
    )
    return (
        ScheduleEntry("solicitante", requester_time, True),
        ScheduleEntry("atendente", attendant_time, False),
    )


def _event_on(entry: ScheduleEntry, day: date) -> ScheduledEvent:
    return ScheduledEvent(entry, datetime.combine(day, entry.at))


def next_event(
    now: datetime,
    entries: Iterable[ScheduleEntry],
    consumed: set[tuple[str, datetime]] | None = None,
) -> ScheduledEvent:
    consumed_keys = consumed if consumed is not None else set()
    candidates: list[ScheduledEvent] = []
    entries_tuple = tuple(entries)
    if not entries_tuple:
        raise ValueError("Ao menos um horario deve ser configurado")
    for day_offset in (0, 1):
        day = now.date() + timedelta(days=day_offset)
        for entry in entries_tuple:
            event = _event_on(entry, day)
            if event.scheduled_for >= now and event.key not in consumed_keys:
                candidates.append(event)
        if candidates:
            break
    return min(candidates, key=lambda event: (event.scheduled_for, event.entry.name))


def due_events(
    now: datetime,
    entries: Iterable[ScheduleEntry],
    consumed: set[tuple[str, datetime]],
) -> list[ScheduledEvent]:
    events = (_event_on(entry, now.date()) for entry in entries)
    return sorted(
        (
            event
            for event in events
            if event.scheduled_for <= now and event.key not in consumed
        ),
        key=lambda event: (event.scheduled_for, event.entry.name),
    )


def _application_run(*, solicitante: bool) -> int:
    from app.main import run

    return run(solicitante=solicitante)


def execute_event(event: ScheduledEvent, runner: Runner | None = None) -> int:
    selected_runner = runner if runner is not None else _application_run
    code = selected_runner(solicitante=event.entry.solicitante)
    if code == 0:
        level = logging.INFO
        meaning = "sucesso"
    elif code == 1:
        level = logging.ERROR
        meaning = "falha geral"
    elif code == 2:
        level = logging.ERROR
        meaning = "falha de configuracao"
    else:
        level = logging.ERROR
        meaning = "codigo desconhecido"
    LOGGER.log(level, "Fluxo %s finalizado: codigo=%s (%s)", event.entry.name, code, meaning)
    return code


def process_due_events(
    now: datetime,
    entries: Iterable[ScheduleEntry],
    consumed: set[tuple[str, datetime]],
    runner: Runner | None = None,
    stop_event: Event | None = None,
) -> None:
    for event in due_events(now, entries, consumed):
        consumed.add(event.key)
        delay = now - event.scheduled_for
        if delay > MAX_LATE_DELAY:
            LOGGER.warning(
                "Evento %s descartado por atraso: agendado=%s atraso=%s",
                event.entry.name,
                event.scheduled_for.isoformat(),
                delay,
            )
            continue
        if stop_event is not None and stop_event.is_set():
            return
        try:
            execute_event(event, runner=runner)
        except Exception:
            LOGGER.exception("Falha inesperada no fluxo %s; scheduler continuara ativo", event.entry.name)


def run_scheduler(
    entries: Iterable[ScheduleEntry] | None = None,
    *,
    runner: Runner | None = None,
    clock: Callable[[], datetime] = datetime.now,
    stop_event: Event | None = None,
) -> None:
    schedule = tuple(entries if entries is not None else load_schedule())
    stopper = stop_event if stop_event is not None else Event()
    consumed: set[tuple[str, datetime]] = set()
    while not stopper.is_set():
        now = clock()
        process_due_events(now, schedule, consumed, runner=runner, stop_event=stopper)
        if stopper.is_set():
            break
        upcoming = next_event(clock(), schedule, consumed)
        wait_seconds = max(0.0, (upcoming.scheduled_for - clock()).total_seconds())
        LOGGER.info(
            "Proxima execucao: fluxo=%s horario=%s",
            upcoming.entry.name,
            upcoming.scheduled_for.isoformat(),
        )
        stopper.wait(wait_seconds)


def main() -> int:
    setup_logging()
    try:
        schedule = load_schedule()
        with InstanceLock():
            LOGGER.info("Scheduler iniciado")
            try:
                run_scheduler(schedule)
            except KeyboardInterrupt:
                LOGGER.info("Encerramento solicitado")
            LOGGER.info("Scheduler encerrado")
        return 0
    except (ValueError, InstanceAlreadyRunningError) as error:
        LOGGER.error("Nao foi possivel iniciar o scheduler: %s", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
