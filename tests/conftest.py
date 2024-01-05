import pytest, shutil, json
from pathlib import Path

@pytest.fixture
def asset_copy(tmp_path):
    # Create a subdirectory for our assets.
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()

    # Your original assets directory.
    original_assets_dir = Path("assets/test")  # Convert string to Path

    # Copy your assets into the temporary directory before each test.
    for item in original_assets_dir.iterdir():
        if item.is_dir():
            shutil.copytree(item, assets_dir / item.name)
        else:
            shutil.copy(item, assets_dir / item.name)

    # Create mapping
    mapping = {
        str(assets_dir / "1.jpg"): str(assets_dir / "blue.jpg"),
        str(assets_dir / "2.jpg"): str(assets_dir / "green.jpg")
    }
    mapping_file = assets_dir / 'mapping.json'
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=4)
    
    return assets_dir
