from __future__ import annotations

import importlib
import logging
import shutil
import subprocess
import sys
import unittest
from datetime import datetime, time
from pathlib import Path
from threading import Event
from unittest.mock import Mock, patch

import service


ATTENDANT = service.ScheduleEntry("atendente", time(9, 0), False)
REQUESTER = service.ScheduleEntry("solicitante", time(8, 0), True)


class ServiceImportTests(unittest.TestCase):
    def test_import_has_no_execution_side_effect(self) -> None:
        module = importlib.reload(service)
        self.assertTrue(callable(module.main))

    def test_import_in_subprocess_does_not_call_application(self) -> None:
        command = "import service; print('IMPORTED')"
        result = subprocess.run(
            [sys.executable, "-c", command],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "IMPORTED")


class ScheduleCalculationTests(unittest.TestCase):
    def test_before_time_uses_same_day(self) -> None:
        event = service.next_event(datetime(2026, 8, 13, 7, 0), [REQUESTER])
        self.assertEqual(event.scheduled_for, datetime(2026, 8, 13, 8, 0))

    def test_exact_time_is_eligible(self) -> None:
        event = service.next_event(datetime(2026, 8, 13, 8, 0), [REQUESTER])
        self.assertEqual(event.scheduled_for, datetime(2026, 8, 13, 8, 0))

    def test_after_time_uses_next_day(self) -> None:
        event = service.next_event(datetime(2026, 8, 13, 8, 1), [REQUESTER])
        self.assertEqual(event.scheduled_for, datetime(2026, 8, 14, 8, 0))

    def test_multiple_times_select_earliest_event(self) -> None:
        event = service.next_event(datetime(2026, 8, 13, 7, 0), [ATTENDANT, REQUESTER])
        self.assertEqual(event.entry, REQUESTER)

    def test_consumed_exact_event_selects_next_one(self) -> None:
        now = datetime(2026, 8, 13, 8, 0)
        event = service.next_event(now, [REQUESTER, ATTENDANT], {("solicitante", now)})
        self.assertEqual(event.entry, ATTENDANT)

    def test_load_schedule_validates_format(self) -> None:
        with self.assertRaisesRegex(ValueError, "HH:MM"):
            service.load_schedule({service.ATTENDANT_TIME_ENV: "25:00"})


class FlowDispatchTests(unittest.TestCase):
    def test_dispatches_attendant(self) -> None:
        runner = Mock(return_value=0)
        service.execute_event(service.ScheduledEvent(ATTENDANT, datetime(2026, 8, 13, 9)), runner)
        runner.assert_called_once_with(solicitante=False)

    def test_dispatches_requester(self) -> None:
        runner = Mock(return_value=0)
        service.execute_event(service.ScheduledEvent(REQUESTER, datetime(2026, 8, 13, 8)), runner)
        runner.assert_called_once_with(solicitante=True)


class SequentialExecutionTests(unittest.TestCase):
    def test_due_events_execute_without_overlap(self) -> None:
        order: list[str] = []
        running = False
        requester_at_same_time = service.ScheduleEntry("solicitante", time(9, 0), True)

        def runner(*, solicitante: bool) -> int:
            nonlocal running
            self.assertFalse(running)
            running = True
            name = "solicitante" if solicitante else "atendente"
            order.append(f"inicio {name}")
            order.append(f"fim {name}")
            running = False
            return 0

        service.process_due_events(
            datetime(2026, 8, 13, 9, 0), [requester_at_same_time, ATTENDANT], set(), runner
        )
        self.assertEqual(
            order,
            ["inicio atendente", "fim atendente", "inicio solicitante", "fim solicitante"],
        )


class ReturnCodeTests(unittest.TestCase):
    def test_logs_all_application_return_codes(self) -> None:
        event = service.ScheduledEvent(ATTENDANT, datetime(2026, 8, 13, 9))
        for code in (0, 1, 2):
            with self.subTest(code=code), self.assertLogs(service.LOGGER, level=logging.INFO) as logs:
                result = service.execute_event(event, Mock(return_value=code))
            self.assertEqual(result, code)
            self.assertIn(f"codigo={code}", " ".join(logs.output))
            self.assertIn("atendente", " ".join(logs.output))


class FailureRecoveryTests(unittest.TestCase):
    def test_exception_does_not_prevent_second_execution(self) -> None:
        runner = Mock(side_effect=[RuntimeError("falha"), 0])
        consumed: set[tuple[str, datetime]] = set()
        requester_at_same_time = service.ScheduleEntry("solicitante", time(9, 0), True)
        with self.assertLogs(service.LOGGER, level=logging.ERROR):
            service.process_due_events(
                datetime(2026, 8, 13, 9), [requester_at_same_time, ATTENDANT], consumed, runner
            )
        self.assertEqual(runner.call_count, 2)

    def test_error_return_does_not_prevent_second_execution(self) -> None:
        runner = Mock(side_effect=[1, 0])
        requester_at_same_time = service.ScheduleEntry("solicitante", time(9, 0), True)
        service.process_due_events(
            datetime(2026, 8, 13, 9), [requester_at_same_time, ATTENDANT], set(), runner
        )
        self.assertEqual(runner.call_count, 2)


class LateEventPolicyTests(unittest.TestCase):
    def test_five_minutes_late_executes_once(self) -> None:
        runner = Mock(return_value=0)
        consumed: set[tuple[str, datetime]] = set()
        now = datetime(2026, 8, 13, 8, 5)
        service.process_due_events(now, [REQUESTER], consumed, runner)
        service.process_due_events(now, [REQUESTER], consumed, runner)
        runner.assert_called_once_with(solicitante=True)

    def test_more_than_five_minutes_late_is_discarded(self) -> None:
        runner = Mock(return_value=0)
        consumed: set[tuple[str, datetime]] = set()
        with self.assertLogs(service.LOGGER, level=logging.WARNING) as logs:
            service.process_due_events(
                datetime(2026, 8, 13, 8, 6), [REQUESTER], consumed, runner
            )
        runner.assert_not_called()
        self.assertIn("descartado", " ".join(logs.output))
        upcoming = service.next_event(datetime(2026, 8, 13, 8, 6), [REQUESTER], consumed)
        self.assertEqual(upcoming.scheduled_for, datetime(2026, 8, 14, 8))


class InstanceLockTests(unittest.TestCase):
    def test_only_one_instance_can_hold_lock(self) -> None:
        directory = Path.cwd() / ".test-service-lock"
        directory.mkdir(exist_ok=False)
        try:
            path = directory / "service.lock"
            first = service.InstanceLock(path)
            second = service.InstanceLock(path)
            first.acquire()
            try:
                with self.assertRaises(service.InstanceAlreadyRunningError):
                    second.acquire()
            finally:
                first.release()
            second.acquire()
            second.release()
            self.assertFalse(path.exists())
        finally:
            shutil.rmtree(directory)

    def test_abrupt_process_exit_does_not_leave_blocking_lock(self) -> None:
        directory = Path.cwd() / ".test-service-abrupt-lock"
        directory.mkdir(exist_ok=False)
        try:
            path = directory / "service.lock"
            command = (
                "import os, service; from pathlib import Path; "
                f"lock = service.InstanceLock(Path({str(path)!r})); "
                "lock.acquire(); os._exit(0)"
            )
            result = subprocess.run(
                [sys.executable, "-c", command],
                cwd=Path(__file__).resolve().parent.parent,
                timeout=5,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(path.exists())

            replacement = service.InstanceLock(path)
            replacement.acquire()
            replacement.release()
            self.assertFalse(path.exists())
        finally:
            shutil.rmtree(directory)


class FakeStopEvent:
    def __init__(self, clock_values: list[datetime]) -> None:
        self.clock_values = clock_values
        self.stopped = False
        self.waits: list[float] = []

    def is_set(self) -> bool:
        return self.stopped

    def wait(self, timeout: float) -> bool:
        self.waits.append(timeout)
        self.stopped = True
        return True


class ControlledShutdownTests(unittest.TestCase):
    def test_already_stopped_loop_does_not_run(self) -> None:
        stopper = Event()
        stopper.set()
        runner = Mock()
        service.run_scheduler([REQUESTER], runner=runner, stop_event=stopper)
        runner.assert_not_called()

    def test_stop_during_wait_prevents_execution(self) -> None:
        now = datetime(2026, 8, 13, 7)
        stopper = FakeStopEvent([now])
        runner = Mock()
        service.run_scheduler([REQUESTER], runner=runner, clock=lambda: now, stop_event=stopper)
        runner.assert_not_called()
        self.assertEqual(stopper.waits, [3600.0])

    def test_keyboard_interrupt_releases_instance_lock(self) -> None:
        directory = Path.cwd() / ".test-service-shutdown-lock"
        directory.mkdir(exist_ok=False)
        try:
            path = directory / "service.lock"
            lock = service.InstanceLock(path)
            with (
                patch.object(service, "InstanceLock", return_value=lock),
                patch.object(service, "setup_logging"),
                patch.object(service, "run_scheduler", side_effect=KeyboardInterrupt),
                self.assertLogs(service.LOGGER, level=logging.INFO) as logs,
            ):
                result = service.main()
            self.assertEqual(result, 0)
            self.assertFalse(path.exists())
            self.assertIn("Encerramento solicitado", " ".join(logs.output))
        finally:
            shutil.rmtree(directory)


class SchedulerIntegrationTests(unittest.TestCase):
    def test_multiple_events_failures_delay_and_next_event(self) -> None:
        consumed: set[tuple[str, datetime]] = set()
        runner = Mock(side_effect=[0, RuntimeError("indisponivel"), 2])
        with self.assertLogs(service.LOGGER, level=logging.INFO) as logs:
            service.process_due_events(
                datetime(2026, 8, 13, 8, 0), [REQUESTER, ATTENDANT], consumed, runner
            )
            service.process_due_events(
                datetime(2026, 8, 13, 9, 0), [REQUESTER, ATTENDANT], consumed, runner
            )
            service.process_due_events(
                datetime(2026, 8, 14, 9, 0), [REQUESTER, ATTENDANT], consumed, runner
            )
        self.assertEqual(
            runner.call_args_list,
            [
                unittest.mock.call(solicitante=True),
                unittest.mock.call(solicitante=False),
                unittest.mock.call(solicitante=False),
            ],
        )
        output = " ".join(logs.output)
        self.assertIn("codigo=0", output)
        self.assertIn("continuara ativo", output)
        self.assertIn("codigo=2", output)
        self.assertIn(("solicitante", datetime(2026, 8, 14, 8)), consumed)
        upcoming = service.next_event(datetime(2026, 8, 14, 9), [REQUESTER, ATTENDANT], consumed)
        self.assertEqual(upcoming.scheduled_for, datetime(2026, 8, 15, 8))


if __name__ == "__main__":
    unittest.main()
