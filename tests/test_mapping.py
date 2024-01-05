import filecmp, hashlib, os.path, pytest, json
from types import SimpleNamespace
from VisioNomicon.main import save_mapping, rename_from_mapping

def test_mapping_save(asset_copy):
    og_filepaths = [str(asset_copy / '1.jpg'), str(asset_copy / '2.jpg')]
    new_filepaths = [str(asset_copy / 'blue.jpg'), str(asset_copy / 'green.jpg')]

    args = SimpleNamespace()
    args.files = og_filepaths
    args.output = str(asset_copy / 'mapping-test.json')

    save_mapping(args, new_filepaths)

    assert filecmp.cmp(args.output, asset_copy / 'mapping.json')

def test_rename_from_mapping(asset_copy):
    # test execution
    checksums = [sha256sum(asset_copy / "1.jpg"), sha256sum(asset_copy / "2.jpg")]
    rename_from_mapping(str(asset_copy / 'mapping.json'))

    assert os.path.isfile(asset_copy / "blue.jpg")
    assert os.path.isfile(asset_copy / "green.jpg")

    rename_sums = [sha256sum(asset_copy / "blue.jpg"), sha256sum(asset_copy / "green.jpg")]
    assert(checksums == rename_sums)

    # test undo
    rename_from_mapping(str(asset_copy / 'mapping.json'), True)
    checksums = [sha256sum(asset_copy / "1.jpg"), sha256sum(asset_copy / "2.jpg")]

    assert os.path.isfile(asset_copy / "1.jpg")
    assert os.path.isfile(asset_copy / "2.jpg")

    assert(checksums == rename_sums)
    
def sha256sum(filename):
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(filename, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()
    
