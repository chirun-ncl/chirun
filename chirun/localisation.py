from   babel.messages.mofile import write_mo
from   babel.messages.pofile import read_po
import json
from   pathlib import Path

def compile_for_theme(theme_path):
    print(theme_path)
    translations_dir = theme_path / 'translations'
    po_files = [p for p in translations_dir.iterdir() if p.suffix == '.po']
    for po in po_files:
        print(po)
        with open(po, 'rb') as f:
            catalog = read_po(f)

        with open(po.with_suffix('.mo'), 'wb') as f:
            write_mo(f, catalog)

        js_entries = [m for m in catalog if any(Path(n).suffix in ('.js', '.mjs') for n,_ in m.locations)]
        js_map = {m.id: m.string for m in js_entries}
        with open(po.with_suffix('.mjs'), 'w') as f:
            f.write(f'export default {json.dumps(js_map)}')

if __name__ == '__main__':
    themes = Path('themes')
    for d in themes.iterdir():
        if d.is_dir() and (d / 'translations').exists():
            compile_for_theme(d)
