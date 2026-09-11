# Fabric Convention Tags

This fork of the fabric-convention-tags aims to extract the conventional tags used by mods and list them in a markdown file which is compatible with the modern fabric docs.

# Use

Drop the mod jar files you want to extract tags from into a `mods` subfolder and run the `collect_mod_tags.py` script.

This will update the tags.json file (incrementally, existing tags will not be removed). 

Then run `to_mediawiki.py` to generate the Mediawiki text for the wiki.
