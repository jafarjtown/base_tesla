from pathlib import Path as Pa

from .collections import Collection

BASE_DIR = Pa(__file__).resolve().parent

abs_path = BASE_DIR

collections_manage = Collection({})

def register_collections(*model):
    for m in model:
        collections_manage.add(m)