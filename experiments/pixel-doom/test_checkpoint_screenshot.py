"""A hung/failed optional capture must not abort a successful checkpoint."""
import os
from pathlib import Path
import sys
import tempfile

from progressive import checkpoint_screenshot

with tempfile.TemporaryDirectory(prefix='pd-capture-test-') as directory:
    root=Path(directory);grim=root/'grim';image=root/'checkpoint.png'
    previous=os.environ['PATH'];os.environ['PATH']=str(root)+os.pathsep+previous
    try:
        def script(body):
            grim.write_text(f'#!{sys.executable}\nfrom pathlib import Path\nimport sys,time\n'+body)
            grim.chmod(0o700)
        script('Path(sys.argv[1]).write_bytes(b"partial")\ntime.sleep(5)\n')
        result=checkpoint_screenshot(image,timeout=.2)
        assert result['error_type']=='TimeoutExpired' and not image.exists(),result
        script('Path(sys.argv[1]).write_bytes(b"partial")\nsys.exit(1)\n')
        result=checkpoint_screenshot(image)
        assert result['error_type']=='CalledProcessError' and not image.exists(),result
        script('Path(sys.argv[1]).write_bytes(b"complete")\n')
        assert checkpoint_screenshot(image)['status']=='saved'
        assert image.read_bytes()==b'complete'
    finally:
        os.environ['PATH']=previous
print('PASS: timed-out/failed capture is nonfatal, partial files removed, later capture succeeds')
