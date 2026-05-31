# tests/test_foam_path_utils.py
# Pure pytest tests for addon/foam_path_utils.py
# No Blender or bpy imports needed — all functions are plain Python.

import os
import sys
import tempfile
import pytest

# Import foam_path_utils directly to avoid addon/__init__.py (which imports bpy)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'addon'))
import foam_path_utils


# ─────────────────── resolve_case_path ───────────────────


class TestResolveCasePath:
    """Tests for path normalization and symlink resolution."""

    def test_expanduser(self):
        """~ should expand to the user's home directory."""
        result = foam_path_utils.resolve_case_path("~/foam_cases/test")
        expected = os.path.realpath(os.path.expanduser("~/foam_cases/test"))
        assert result == expected

    def test_strips_trailing_slash(self):
        """Trailing slashes should be removed."""
        result = foam_path_utils.resolve_case_path("/tmp/test_case/")
        assert not result.endswith("/")

    def test_empty_string(self):
        """Empty input should return empty string."""
        assert foam_path_utils.resolve_case_path("") == ""

    def test_whitespace_only(self):
        """Whitespace-only input should return empty string."""
        assert foam_path_utils.resolve_case_path("   ") == ""

    def test_resolves_symlinks(self, tmp_path):
        """Symlinked paths should be resolved to their physical targets."""
        real_dir = tmp_path / "real_case"
        real_dir.mkdir()
        symlink = tmp_path / "link_to_case"
        symlink.symlink_to(real_dir)

        resolved = foam_path_utils.resolve_case_path(str(symlink))
        assert resolved == str(real_dir.resolve())


# ─────────────────── validate_case_path ───────────────────


class TestValidateCasePath:
    """Tests for path validation including FOAM_RUN containment."""

    def test_empty_path(self):
        """Empty path should be invalid."""
        result = foam_path_utils.validate_case_path("")
        assert result["valid"] is False
        assert any("empty" in w.lower() for w in result["warnings"])

    def test_nonexistent_but_writable_parent(self, tmp_path):
        """Non-existent path under a writable parent should be valid."""
        new_case = tmp_path / "does_not_exist_yet"
        result = foam_path_utils.validate_case_path(str(new_case))
        assert result["valid"] is True
        assert result["writable"] is True

    def test_path_is_file_not_dir(self, tmp_path):
        """Path pointing to a file should be invalid."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("hello")
        result = foam_path_utils.validate_case_path(str(file_path))
        assert result["valid"] is False
        assert any("file" in w.lower() for w in result["warnings"])

    def test_path_inside_foam_run(self, tmp_path):
        """Case path inside FOAM_RUN should set is_inside_foam_run = True."""
        foam_run = tmp_path / "run"
        foam_run.mkdir()
        case_dir = foam_run / "my_case"
        case_dir.mkdir()

        result = foam_path_utils.validate_case_path(
            str(case_dir), foam_run_dir=str(foam_run)
        )
        assert result["is_inside_foam_run"] is True
        assert not any("outside" in w.lower() for w in result["warnings"])

    def test_path_outside_foam_run(self, tmp_path):
        """Case path outside FOAM_RUN should warn but still be valid."""
        foam_run = tmp_path / "run"
        foam_run.mkdir()
        outside_case = tmp_path / "elsewhere" / "case"
        outside_case.mkdir(parents=True)

        result = foam_path_utils.validate_case_path(
            str(outside_case), foam_run_dir=str(foam_run)
        )
        assert result["valid"] is True
        assert result["is_inside_foam_run"] is False
        assert any("outside" in w.lower() for w in result["warnings"])

    def test_no_foam_run_set(self, tmp_path):
        """When FOAM_RUN is empty, skip containment check — no warning."""
        case_dir = tmp_path / "my_case"
        case_dir.mkdir()

        result = foam_path_utils.validate_case_path(str(case_dir), foam_run_dir="")
        assert result["is_inside_foam_run"] is True  # default: assume OK
        assert not any("outside" in w.lower() for w in result["warnings"])

    def test_symlinked_foam_run_containment(self, tmp_path):
        """Symlinked FOAM_RUN should resolve before containment check."""
        real_run = tmp_path / "real_run"
        real_run.mkdir()
        link_run = tmp_path / "link_run"
        link_run.symlink_to(real_run)

        case_dir = real_run / "my_case"
        case_dir.mkdir()

        # Pass the symlink as foam_run, real path as case_path
        result = foam_path_utils.validate_case_path(
            str(case_dir), foam_run_dir=str(link_run)
        )
        assert result["is_inside_foam_run"] is True


# ─────────────────── is_valid_openfoam_case ───────────────────


class TestIsValidOpenfoamCase:
    """Tests for OpenFOAM case structure validation."""

    def test_with_system_dir(self, tmp_path):
        """Directory with system/ subdirectory should be valid."""
        case = tmp_path / "valid_case"
        case.mkdir()
        (case / "system").mkdir()
        assert foam_path_utils.is_valid_openfoam_case(str(case)) is True

    def test_without_system_dir(self, tmp_path):
        """Directory without system/ subdirectory should be invalid."""
        case = tmp_path / "invalid_case"
        case.mkdir()
        assert foam_path_utils.is_valid_openfoam_case(str(case)) is False

    def test_empty_path(self):
        """Empty path should return False."""
        assert foam_path_utils.is_valid_openfoam_case("") is False
