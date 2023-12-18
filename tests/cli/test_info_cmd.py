"""Unit tests for the info CLI command."""
# tests/cli/test_info_cmd.py

# Unit under test:
import dem.cli.main as main

# Test framework
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import io
from rich.console import Console
from rich.table import Table
from dem.core.tool_images import ToolImages

## Global test variables

# In order to test stdout and stderr separately, the stderr can't be mixed into the stdout.
runner = CliRunner(mix_stderr=False)

## Test helpers

def get_expected_table(expected_tools: list[list[str]]) ->str:
    expected_table = Table()
    expected_table.add_column("Type")
    expected_table.add_column("Image")
    expected_table.add_column("Status")
    for expected_tool in expected_tools:
        expected_table.add_row(*expected_tool)
    console = Console(file=io.StringIO())
    console.print(expected_table)
    return console.file.getvalue()

## Test cases

def test_info_local_dev_env_demo():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_dev_env = MagicMock()
    mock_dev_env.tools = [
        {
            "type": "build system",
            "image_name": "axemsolutions/make_gnu_arm",
            "image_version": "latest", 
        },
        {
            "type": "toolchain",
            "image_name": "axemsolutions/make_gnu_arm",
            "image_version": "latest", 
        },
        {
            "type": "debugger",
            "image_name": "axemsolutions/stlink_org",
            "image_version": "latest", 
        },
        {
            "type": "deployer",
            "image_name": "axemsolutions/stlink_org",
            "image_version": "latest", 
        },
        {
            "type": "test framework",
            "image_name": "axemsolutions/cpputest",
            "image_version": "latest" 
        },
    ]
    mock_platform.get_dev_env_by_name.return_value = mock_dev_env
    def stub_check_image_availability(*args, **kwargs):
        for tool in mock_dev_env.tools:
            tool["image_status"] = ToolImages.LOCAL_AND_REGISTRY
    mock_dev_env.check_image_availability.side_effect = stub_check_image_availability

    # Run unit under test
    test_dev_env_name = "demo"
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    mock_dev_env.check_image_availability.assert_called_once_with(mock_platform.tool_images)

    expected_tools = [
        ["build system", "axemsolutions/make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["toolchain", "axemsolutions/make_gnu_arm:latest", "Image is available locally and in the registry."],
        ["debugger", "axemsolutions/stlink_org:latest", "Image is available locally and in the registry."],
        ["deployer", "axemsolutions/stlink_org:latest", "Image is available locally and in the registry."],
        ["test framework", "axemsolutions/cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools)  == runner_result.stdout

def test_info_local_dev_env_nagy_cica_project():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    fake_dev_env = MagicMock()
    fake_dev_env.tools = [
        {
            "type": "build system",
            "image_name": "axemsolutions/bazel",
            "image_version": "latest", 
        },
        {
            "type": "toolchain",
            "image_name": "axemsolutions/gnu_arm",
            "image_version": "latest", 
        },
        {
            "type": "debugger",
            "image_name": "axemsolutions/jlink",
            "image_version": "latest", 
        },
        {
            "type": "deployer",
            "image_name": "axemsolutions/jlink",
            "image_version": "latest", 
        },
        {
            "type": "test framework",
            "image_name": "axemsolutions/cpputest",
            "image_version": "latest" 
        },
    ]
    mock_platform.get_dev_env_by_name.return_value = fake_dev_env
    def stub_check_image_availability(*args, **kwargs):
        fake_dev_env.tools[0]["image_status"] = ToolImages.NOT_AVAILABLE
        fake_dev_env.tools[1]["image_status"] = ToolImages.NOT_AVAILABLE
        fake_dev_env.tools[2]["image_status"] = ToolImages.LOCAL_ONLY
        fake_dev_env.tools[3]["image_status"] = ToolImages.LOCAL_ONLY
        fake_dev_env.tools[4]["image_status"] = ToolImages.LOCAL_AND_REGISTRY
    fake_dev_env.check_image_availability.side_effect = stub_check_image_availability

    # Run unit under test
    test_dev_env_name = "nagy_cica_project"
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    fake_dev_env.check_image_availability.assert_called_once_with(mock_platform.tool_images)

    expected_tools = [
        ["build system", "axemsolutions/bazel:latest", "[red]Error: Required image is not available![/]"],
        ["toolchain", "axemsolutions/gnu_arm:latest", "[red]Error: Required image is not available![/]"],
        ["debugger", "axemsolutions/jlink:latest", "Image is available locally."],
        ["deployer", "axemsolutions/jlink:latest", "Image is available locally."],
        ["test framework", "axemsolutions/cpputest:latest", "Image is available locally and in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout

def test_info_dev_env_invalid():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.get_dev_env_by_name.return_value = None
    mock_platform.dev_env_catalogs.catalogs = []

    # Run unit under test
    test_dev_env_name = "not_existing_environment"
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    console = Console(file=io.StringIO())
    console.print("[red]Error: Unknown Development Environment: not_existing_environment[/]")
    expected_output = console.file.getvalue()
    assert expected_output == runner_result.stderr

def test_info_org_dev_env():
    # Test setup
    mock_platform = MagicMock()
    main.platform = mock_platform

    mock_platform.get_dev_env_by_name.return_value = None

    mock_catalog = MagicMock()
    mock_platform.dev_env_catalogs.catalogs = [mock_catalog]
    fake_dev_env = MagicMock()
    fake_dev_env.tools = [
        {
            "type": "build system",
            "image_name": "axemsolutions/cmake",
            "image_version": "latest", 
        },
        {
            "type": "toolchain",
            "image_name": "axemsolutions/llvm",
            "image_version": "latest", 
        },
        {
            "type": "debugger",
            "image_name": "axemsolutions/pemicro",
            "image_version": "latest", 
        },
        {
            "type": "deployer",
            "image_name": "axemsolutions/pemicro",
            "image_version": "latest", 
        },
        {
            "type": "test framework",
            "image_name": "axemsolutions/unity",
            "image_version": "latest" 
        },
    ]
    mock_catalog.get_dev_env_by_name.return_value = fake_dev_env
    def stub_check_image_availability(*args, **kwargs):
        for tool in fake_dev_env.tools:
            tool["image_status"] = ToolImages.REGISTRY_ONLY
    fake_dev_env.check_image_availability.side_effect = stub_check_image_availability

    # Run unit under test
    test_dev_env_name = "org_only_env"
    runner_result = runner.invoke(main.typer_cli, ["info", test_dev_env_name], color=True)

    # Check expectations
    assert runner_result.exit_code == 0

    mock_platform.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)

    mock_catalog.get_dev_env_by_name.assert_called_once_with(test_dev_env_name)
    fake_dev_env.check_image_availability.assert_called_once_with(mock_platform.tool_images)

    expected_tools = [
        ["build system", "axemsolutions/cmake:latest", "Image is available in the registry."],
        ["toolchain", "axemsolutions/llvm:latest", "Image is available in the registry."],
        ["debugger", "axemsolutions/pemicro:latest", "Image is available in the registry."],
        ["deployer", "axemsolutions/pemicro:latest", "Image is available in the registry."],
        ["test framework", "axemsolutions/unity:latest", "Image is available in the registry."],
    ]
    assert get_expected_table(expected_tools) == runner_result.stdout