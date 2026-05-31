# tests/test_tutorial_copy_sets_case_path.py
# Integration tests verifying that tutorial_manager.CLASSY_OT_copy_tutorial
# correctly sets scene.classy_mesh_props.case_path after a successful copy.
#
# Uses mocked bpy and shutil to avoid real filesystem or Blender dependencies.

import os
import sys
import types
import tempfile
import importlib
import pytest
from unittest import mock


# ─────────────────── bpy Mock Setup ───────────────────

def _build_mock_bpy():
    """
    Builds a minimal bpy mock with Scene, PropertyGroup-like attributes.
    All property constructors return None (annotation-only in class body).
    """
    bpy_mod = types.ModuleType("bpy")
    bpy_mod.types = types.ModuleType("bpy.types")
    bpy_mod.props = types.ModuleType("bpy.props")
    bpy_mod.utils = types.ModuleType("bpy.utils")
    bpy_mod.ops = mock.MagicMock()

    # Minimal stubs for Blender types
    bpy_mod.types.Operator = object
    bpy_mod.types.Panel = object
    bpy_mod.types.PropertyGroup = object
    bpy_mod.types.Scene = type("Scene", (), {})

    # Property stubs — return identity function (covers all prop types)
    _prop_stub = lambda **kw: None
    for prop_name in [
        "StringProperty", "EnumProperty", "BoolProperty",
        "IntProperty", "FloatProperty", "PointerProperty",
        "IntVectorProperty", "FloatVectorProperty",
    ]:
        setattr(bpy_mod.props, prop_name, _prop_stub)

    bpy_mod.utils.register_class = lambda cls: None
    bpy_mod.utils.unregister_class = lambda cls: None

    return bpy_mod


@pytest.fixture(autouse=True)
def mock_bpy_and_import():
    """Inject a mocked bpy module and import tutorial_manager directly."""
    bpy_mod = _build_mock_bpy()
    with mock.patch.dict(sys.modules, {"bpy": bpy_mod}):
        # Clear any cached addon modules
        for key in list(sys.modules.keys()):
            if "tutorial_manager" in key:
                del sys.modules[key]

        # Import tutorial_manager directly from the addon directory
        addon_dir = os.path.join(os.path.dirname(__file__), '..', 'addon')
        sys.path.insert(0, addon_dir)
        try:
            import tutorial_manager as tm
            importlib.reload(tm)  # Ensure fresh import with mock bpy
            yield tm
        finally:
            sys.path.remove(addon_dir)
            if "tutorial_manager" in sys.modules:
                del sys.modules["tutorial_manager"]


# ─────────────────── Tests ───────────────────


class TestTutorialCopySetsPath:
    """Verify that CLASSY_OT_copy_tutorial wires the copy destination
    back into the pipeline's case_path property."""

    def _make_context(self, foam_run_dir, foam_tut_dir, selected_tut, new_name):
        """Build a fake Blender context with the required scene attributes."""
        context = mock.MagicMock()
        scene = context.scene

        # foam_dirs
        scene.foam_dirs.foam_run_dir = foam_run_dir
        scene.foam_dirs.foam_tutorials_dir = foam_tut_dir

        # tutorial_manager props
        scene.tutorial_manager.available_tutorials = selected_tut
        scene.tutorial_manager.new_case_name = new_name

        # classy_mesh_props
        scene.classy_mesh_props.case_path = ""

        return context

    def test_copy_sets_case_path(self, tmp_path, mock_bpy_and_import):
        """After a successful copy, case_path should be set to dest_path."""
        tm = mock_bpy_and_import

        # Create source tutorial
        tut_dir = tmp_path / "tutorials" / "incompressible" / "icoFoam" / "cavity"
        (tut_dir / "system").mkdir(parents=True)
        (tut_dir / "system" / "controlDict").write_text("// test")

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        ctx = self._make_context(
            foam_run_dir=str(run_dir),
            foam_tut_dir=str(tmp_path / "tutorials"),
            selected_tut="incompressible/icoFoam/cavity",
            new_name="my_test_case",
        )

        op = tm.CLASSY_OT_copy_tutorial()
        op.report = mock.MagicMock()
        result = op.execute(ctx)

        expected_dest = os.path.join(str(run_dir), "my_test_case")
        assert result == {'FINISHED'}
        
        # Verify the popup operator was called with the correct dest_path
        import sys
        bpy = sys.modules["bpy"]
        bpy.ops.classy.confirm_case_path.assert_called_once_with('INVOKE_DEFAULT', dest_path=expected_dest)

        # Now simulate the user accepting the popup by running the confirm operator
        confirm_op = tm.CLASSY_OT_confirm_case_path()
        confirm_op.dest_path = expected_dest
        confirm_result = confirm_op.execute(ctx)

        assert confirm_result == {'FINISHED'}
        assert ctx.scene.classy_mesh_props.case_path == expected_dest

    def test_copy_failure_does_not_set_case_path(self, tmp_path, mock_bpy_and_import):
        """If copytree fails, case_path should remain unchanged."""
        tm = mock_bpy_and_import

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        ctx = self._make_context(
            foam_run_dir=str(run_dir),
            foam_tut_dir=str(tmp_path / "tutorials"),
            selected_tut="nonexistent/tutorial/path",
            new_name="my_failing_case",
        )

        op = tm.CLASSY_OT_copy_tutorial()
        op.report = mock.MagicMock()
        result = op.execute(ctx)

        # Should have failed — source doesn't exist
        assert result == {'CANCELLED'}
        assert ctx.scene.classy_mesh_props.case_path == ""

    def test_copy_refuses_existing_destination(self, tmp_path, mock_bpy_and_import):
        """If destination already exists, copy should be cancelled."""
        tm = mock_bpy_and_import

        tut_dir = tmp_path / "tutorials" / "basic" / "case1"
        (tut_dir / "system").mkdir(parents=True)

        run_dir = tmp_path / "run"
        run_dir.mkdir()

        # Pre-create the destination
        existing = run_dir / "already_exists"
        existing.mkdir()

        ctx = self._make_context(
            foam_run_dir=str(run_dir),
            foam_tut_dir=str(tmp_path / "tutorials"),
            selected_tut="basic/case1",
            new_name="already_exists",
        )

        op = tm.CLASSY_OT_copy_tutorial()
        op.report = mock.MagicMock()
        result = op.execute(ctx)

        assert result == {'CANCELLED'}
        assert ctx.scene.classy_mesh_props.case_path == ""

