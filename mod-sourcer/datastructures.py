from typing import Dict, List


class TagSource:
    """
    Describes a potential source for tags, which is almost always a Mod or Vanilla Minecraft.
    """
    mod_id: str
    mod_name: str
    mod_version: str
    mod_url: str

    def __init__(self, mod_id, mod_name, mod_version, mod_url):
        self.mod_id = mod_id
        self.mod_name = mod_name
        self.mod_version = mod_version
        self.mod_url = mod_url

    def to_json(self):
        return {
            'id': self.mod_id,
            'name': self.mod_name,
            'version': self.mod_version,
            'url': self.mod_url
        }

    @classmethod
    def from_json(cls, json):
        return TagSource(json['id'], json['name'], json['version'], json['url'])


class TagEntry:
    value: str
    sources: List[TagSource]

    def __init__(self, value: str, sources: List[TagSource]) -> None:
        super().__init__()
        self.value = value
        self.sources = sources

    def add_source(self, source: TagSource):
        if source not in self.sources:
            self.sources.append(source)
            self.sources.sort(key=lambda x: x.mod_id)

    def to_json(self):
        return {
            'value': self.value,
            'sources': [s.mod_id for s in self.sources]
        }

    @classmethod
    def from_json(cls, json, sources):
        resolved_sources = [sources[x] for x in json['sources']]
        return TagEntry(json['value'], resolved_sources)


class Tag:
    id: str
    # Tag sources that will replace this tag fully
    replaced_by: List[TagSource]
    content: List[TagEntry]
    sources: List[TagSource]

    def __init__(self, id: str) -> None:
        super().__init__()
        self.id = id
        self.replaced_by = []
        self.content = []
        self.sources = []

    def add_source(self, source: TagSource, tag_json: Dict):
        if tag_json.get("replace", False):
            if source not in self.replaced_by:
                self.replaced_by.append(source)
        if source not in self.sources:
            self.sources.append(source)
        entries = tag_json.get("values", [])
        for entry in entries:
            found = False
            for existing_entry in self.content:
                if existing_entry.value == entry:
                    existing_entry.add_source(source)
                    found = True
            if not found:
                self.content.append(TagEntry(entry, [source]))

    def to_json(self):
        return {
            'id': self.id,
            'replaced_by': [s.mod_id for s in self.replaced_by],
            'sources': [s.mod_id for s in self.sources],
            'content': [c.to_json() for c in self.content]
        }

    @classmethod
    def from_json(cls, json, sources: Dict):
        tag = Tag(json['id'])
        tag.sources = [sources[x] for x in json['sources']]
        tag.replaced_by = [sources[x] for x in json['replaced_by']]
        tag.content = [TagEntry.from_json(x, sources) for x in json.get('content', [])]
        return tag


class TagContainer:
    sources: List[TagSource]
    item: Dict[str, Tag]
    block: Dict[str, Tag]
    fluid: Dict[str, Tag]
    entity_type: Dict[str, Tag]
    worldgen_biome: Dict[str, Tag]
    enchantment: Dict[str, Tag]
    language: Dict[str, Tag]

    def __init__(self) -> None:
        super().__init__()
        self.sources = []
        self.item = {}
        self.block = {}
        self.fluid = {}
        self.entity_type = {}
        self.worldgen_biome = {}
        self.enchantment = {}
        self.language = {}

    def add_tag(self, tag_type: str, source: TagSource, tag_id: str, tag_json: Dict):
        if source not in self.sources:
            self.sources.append(source)
            self.sources.sort(key=lambda x: x.mod_id)

        tag_dict: Dict[str, Tag] = self.__getattribute__(tag_type)

        if tag_id not in tag_dict:
            tag_dict[tag_id] = Tag(tag_id)

        tag_dict[tag_id].add_source(source, tag_json)

    def to_json(self) -> Dict:
        return {
            'sources': {source.mod_id: source.to_json() for source in self.sources},
            'item': [x.to_json() for x in self.item.values()],
            'block': [x.to_json() for x in self.block.values()],
            'fluid': [x.to_json() for x in self.fluid.values()],
            'entity_type': [x.to_json() for x in self.entity_type.values()],
            'worldgen_biome': [x.to_json() for x in self.worldgen_biome.values()],
            'enchantment': [x.to_json() for x in self.enchantment.values()],
            'language': [x.to_json() for x in self.language.values()]
        }

    @classmethod
    def from_json(cls, json):
        tags = TagContainer()
    
        json_sources = {}
        if('sources' in json):
            json_sources = json['sources']

        tags.sources = [TagSource.from_json(x) for x in json_sources.values()]
        sources = {s.mod_id: s for s in tags.sources}

        def load_tags(key):
            if key not in json:
                json[key] = []
            tag_list = [Tag.from_json(x, sources) for x in json[key]]
            return {t.id: t for t in tag_list}

        tags.item = load_tags('item')
        tags.block = load_tags('block')
        tags.fluid = load_tags('fluid')
        tags.entity_type = load_tags('entity_type')
        tags.worldgen_biome = load_tags('worldgen_biome')
        tags.enchantment = load_tags('enchantment')
        tags.language = load_tags('language')
        return tags
