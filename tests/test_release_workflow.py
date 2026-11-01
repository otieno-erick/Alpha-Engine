from pathlib import Path


def test_release_workflow_builds_required_artifacts():
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release.yml"
    content = workflow.read_text(encoding="utf-8")

    assert '      - "v*"' in content
    assert "windows-latest" in content
    assert "macos-latest" in content
    assert "ubuntu-24.04" in content
    assert "build_mode: --onefile" in content
    assert "build_mode: --onedir" in content
    assert "AlphaEngine-windows-x64.exe" in content
    assert "AlphaEngine-macos.dmg" in content
    assert "AlphaEngine-linux-x86_64.AppImage" in content
    assert "alpha-engine_${version:-0.1.0}_amd64.deb" in content
    assert "Verify the packaged bundle has no node_modules" in content
    assert "dist/AlphaEngine.exe --smoke-test" in content
    assert "dist/AlphaEngine.app/Contents/MacOS/AlphaEngine --smoke-test" in content
    assert "dist/AlphaEngine/AlphaEngine --smoke-test" in content
    assert "https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-gtk/master/linuxdeploy-plugin-gtk.sh" in content
    assert "linuxdeploy-plugin-gtk/releases/download/continuous" not in content
    assert "softprops/action-gh-release" in content


def test_readme_documents_unsigned_build_warning():
    readme = Path(__file__).resolve().parents[1] / "README.md"
    content = readme.read_text(encoding="utf-8").lower()

    assert "unsigned" in content
    assert "operating system may warn" in content
