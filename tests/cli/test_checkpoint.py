import mock
from click.testing import CliRunner

from great_expectations.cli import cli
from tests.cli.utils import assert_no_logging_messages_or_tracebacks


def test_checkpoint_list(caplog, empty_context_with_checkpoint):
    context = empty_context_with_checkpoint
    root_dir = context.root_directory
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, f"checkpoint list -d {root_dir}", catch_exceptions=False,
    )
    stdout = result.stdout
    assert result.exit_code == 0
    assert "Found 1 checkpoint." in stdout
    assert "my_checkpoint" in stdout

    assert_no_logging_messages_or_tracebacks(caplog, result)


@mock.patch(
    "great_expectations.core.usage_statistics.usage_statistics.UsageStatisticsHandler.emit"
)
def test_checkpoint_run_raises_error_if_checkpoint_is_not_found(
    mock_emit, caplog, empty_data_context
):
    context = empty_data_context
    root_dir = context.root_directory

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, f"checkpoint run fake_checkpoint -d {root_dir}", catch_exceptions=False,
    )
    stdout = result.stdout
    print(stdout)

    assert "Could not find checkpoint `fake_checkpoint`." in stdout
    assert "Try running" in stdout
    assert result.exit_code == 1

    assert mock_emit.call_count == 2
    assert mock_emit.call_args_list == [
        mock.call(
            {"event_payload": {}, "event": "data_context.__init__", "success": True}
        ),
        mock.call(
            {"event": "cli.checkpoint.list", "event_payload": {}, "success": False}
        ),
    ]

    assert_no_logging_messages_or_tracebacks(caplog, result)


@mock.patch(
    "great_expectations.core.usage_statistics.usage_statistics.UsageStatisticsHandler.emit"
)
def test_checkpoint_run_on_bad_checkpoint(
    mock_emit, caplog, empty_context_with_checkpoint
):
    context = empty_context_with_checkpoint
    root_dir = context.root_directory

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        cli, f"checkpoint run not_a_checkpoint -d {root_dir}", catch_exceptions=False,
    )
    stdout = result.stdout
    print(stdout)
    assert result.exit_code == 1

    assert mock_emit.call_count == 2
    assert mock_emit.call_args_list == [
        mock.call(
            {"event_payload": {}, "event": "data_context.__init__", "success": True}
        ),
        mock.call(
            {"event": "cli.checkpoint.list", "event_payload": {}, "success": False}
        ),
    ]

    assert_no_logging_messages_or_tracebacks(caplog, result)
