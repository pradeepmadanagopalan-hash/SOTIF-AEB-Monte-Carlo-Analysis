def load_catalogue(path):
    import yaml

    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return raw["triggering_conditions"]

def get_catalogue_snapshots(catalogue):
    cat_v10 = [t for t in catalogue if t["version_added"] in ("v1.0",)]
    cat_v11 = [t for t in catalogue if t["version_added"] in ("v1.0", "v1.1")]
    cat_v12 = catalogue

    return cat_v10, cat_v11, cat_v12


