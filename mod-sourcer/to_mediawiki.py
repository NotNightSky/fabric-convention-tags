import json
from operator import itemgetter
from typing import Dict, List

with open('tags.json', 'r') as fh:
    root = json.load(fh)

def generate_resources_link() -> str :
    resource_lines = []
    for source in root['sources'].values():
        if source['url'] is not None:
            resource_lines.append(f"    - {source['url']}")
    return "\n".join(resource_lines)

FRONTMATTER: str = (
"""---
title: Conventional Tags
description: List of conventional tags commonly used
resources:
%s
---""" % generate_resources_link()
)

ITEM_TAGS: str = "Item Tags {#item-tags}"
BLOCK_TAGS: str = "Block Tags {#block-tags}"
FLUID_TAGS: str = "Fluid Tags {#fluid-tags}"
ENTITY_TYPE_TAGS: str = "Entity Type Tags {#entity-type-tags}"
BIOME_TAGS: str = "Biome Tags {#biome-tags}"
ENCHANTMENT_TAGS: str = "Enchantment Tags {#enchantment-tags}"

def generate_page(sources, tags: List[Dict], out):
    # Sort tags by depth first
    tags.sort(key=lambda x: x['id'].count('/'))
    tags.sort(key=itemgetter('id'))

    print("| Tag ID | Contained IDs | Defined by |", file=out)
    print("|---|---|---|", file=out)
    for tag in tags:
        for content in tag['content']:
            val = content['value']
            tag_value = val['id'] if isinstance(val, dict) else str(val)

            print("|", 'c:' + tag['id'], file=out, end='')
            print("|", tag_value, file=out, end='')
            print("|", ", ".join(content['sources']), file=out, end='')
            print(" |", file=out)


with open('tags.md', 'wt') as out:
    generate_resources_link()
    print(FRONTMATTER, file=out)

    print(file=out)
    print(ITEM_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['item'], out)

    print(file=out)
    print(BLOCK_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['block'], out)

    print(file=out)
    print(FLUID_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['fluid'], out)

    print(file=out)
    print(ENTITY_TYPE_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['entity_type'], out)

    print(file=out)
    print(BIOME_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['worldgen_biome'], out)
    
    print(file=out)
    print(ENCHANTMENT_TAGS, file=out)
    print(file=out)
    generate_page(root['sources'], root['enchantment'], out)

    # print(file=out)
    # print('===== Sources =====', file=out)
    # print(file=out)
    # print("^ Mod ID ^ Name ^ Version ^ URL ^", file=out)
    #
    # for source in root['sources'].values():
    #     print("|", source['id'], "|", source["name"], "|", source["version"], "|", source["url"], "|", file=out)
