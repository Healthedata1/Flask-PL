from pathlib import Path

key_order = {'Bundle': (
                'id',
                'meta',
                'implicitRules',
                'language',
                'identifier',
                'type',
                'timestamp',
                'total',
                'link',
                'entry',
                'signature',
                ),}

# validate by writing to ig examples file and then as separate step running the IG Build:
def write_out(out_path,f_name,my_file):
    p = Path(out_path) / 'test_output' / f_name
    p.write_text(my_file)

# validate by writing to ig examples file and then as separate step running the IG Build:
def read_in(in_path,f_name):
    p = Path(in_path) / 'test_output' / f_name
    return p.read_text()

# delete ig examples file when go to home:
def clear_dir(out_path, f_name):
    try:
        p = Path(out_path) / 'test_output'/ f_name
        p.unlink()
    except TypeError:
        pass

# sort resources keys:
def sort_r(r):
    #try:
        keyorder = key_order[r['resourceType']]
        listofTuples = sorted(r.items(), key=lambda x: keyorder.index(x[0]))
        return dict(listofTuples)
