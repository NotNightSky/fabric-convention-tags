from json import JSONDecodeError
from pathlib import Path
from sys import exit

from zipfile import ZipFile
import re
import json

from datastructures import *

build_dir = Path('build')

TAG_PATTERN = re.compile(
    r"^(?:assets/[^/]+/lang/en_us\.json|"
    r"data/c/tags/(item|block|fluid|entity_type|worldgen/biome|enchantment)/(.*)\.json)$"
)

def load_tags(mod_jar: ZipFile, source: TagSource, tags: TagContainer):
    matches = filter(None, (TAG_PATTERN.match(entry) for entry in mod_jar.namelist()))
    for match in matches:
        path = match.group(0)
        tag_json = json.loads(mod_jar.read(path))

        if path.startswith("assets/"):
            parts = path.split('/')
            namespace = parts[1]
            locale = parts[-1].replace('.json', '')
            tag_type = "language"
            tag_id = f"{namespace}:{locale}"

            tags.add_tag(tag_type, source, tag_id, {"values": [{"id": k, "translation": v} for k, v in tag_json.items() if k.split(".").count("c") == 1]})
            continue

        tag_type = match.group(1)
        tag_id = match.group(2)

        if '/' in tag_type:
            tag_type = tag_type.replace('/', '_')

        tags.add_tag(tag_type, source, tag_id, tag_json)


def pull_mod_tags(mod_path: Path, tags: TagContainer):
    print("Loading", mod_path)

    with ZipFile(str(mod_path)) as mod_jar:
        # Grab the fabric-mod.json to get the mod id
        try:
            fabric_mod_info = json.loads(mod_jar.read("fabric.mod.json"))
        except KeyError:
            print("Failed to find fabric.mod.json in", mod_path)
            return False
        except JSONDecodeError:
            print("Invalid fabric.mod.json file in", mod_path)
            return False

        mod_id = fabric_mod_info['id']
        try:
            mod_name = fabric_mod_info['name']
        except KeyError:
            mod_name = mod_id
        mod_version = fabric_mod_info['version']
        mod_url = fabric_mod_info.get('contact', {}).get('homepage', None)

        tag_source = TagSource(mod_id, mod_name, mod_version, mod_url)

        load_tags(mod_jar, tag_source, tags)

    return True


def gather_all_tags(mod_folder: Path, tags: TagContainer):
    """
    Gather all convention tags from configured mods.
    """
    for mod_path in mod_folder.glob("*.jar"):
        pull_mod_tags(mod_path, tags)

    return True


def run():
    if not build_dir.exists():
        build_dir.mkdir()

    mod_folder = Path('mods')

    if Path("tags.json").exists():
        with open('tags.json', 'rt') as fh:
            tags = TagContainer.from_json(json.load(fh))
    else:
        tags = TagContainer()

    if not gather_all_tags(mod_folder, tags):
        exit(-1)

    with open('tags.json', 'wt') as fh:
        json.dump(tags.to_json(), fh, indent=2)


if __name__ == '__main__':
    run()
