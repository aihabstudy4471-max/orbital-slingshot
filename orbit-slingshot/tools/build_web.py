"""Builds the web version from ONLY the files the game needs.

    python orbit-slingshot/tools/build_web.py          # make build/web.zip for itch.io
    python orbit-slingshot/tools/build_web.py --test   # play it locally at http://localhost:8000

(Works from any folder.) It copies the game files into a clean folder and runs pygbag there,
so notes, READMEs and tools are NOT included in the upload.
"""
import os
import shutil
import subprocess
import sys

GAME_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
STAGE_ROOT = os.path.join(GAME_DIR, 'build', 'web-src')
STAGE = os.path.join(STAGE_ROOT, 'orbit-slingshot')    # folder name = name pygbag gives the game

GAME_FILES = ['main.py', 'classes.py', 'levels.py', 'level_select.py']
ASSET_EXTS = ('.png', '.jpg', '.jpeg', '.ogg', '.wav', '.mp3', '.ttf', '.otf')


def copy_game():
    if os.path.isdir(STAGE_ROOT):
        shutil.rmtree(STAGE_ROOT)
    os.makedirs(STAGE)
    for name in GAME_FILES:
        shutil.copy2(os.path.join(GAME_DIR, name), STAGE)
    count = len(GAME_FILES)
    src_assets = os.path.join(GAME_DIR, 'assets')
    for folder, _, files in os.walk(src_assets):
        for f in files:
            if not f.lower().endswith(ASSET_EXTS) or '-pygbag.' in f:
                continue        # skip READMEs and pygbag's leftover copies
            rel = os.path.relpath(os.path.join(folder, f), src_assets)
            dest = os.path.join(STAGE, 'assets', rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(os.path.join(folder, f), dest)
            count += 1
    print('Copied %d game files into %s' % (count, STAGE))


def main():
    copy_game()
    pygbag = [sys.executable, '-m', 'pygbag']
    if '--test' in sys.argv:
        print('Starting test server - open http://localhost:8000  (Ctrl+C to stop)')
        subprocess.call(pygbag + [STAGE])
        return
    result = subprocess.call(pygbag + ['--archive', STAGE])
    built = os.path.join(STAGE, 'build', 'web.zip')
    if result != 0 or not os.path.isfile(built):
        sys.exit('Build failed - see the messages above.')
    final = os.path.join(GAME_DIR, 'build', 'web.zip')
    shutil.copy2(built, final)
    print('\nDone! Upload this file to itch.io:\n    %s' % final)


if __name__ == '__main__':
    main()
