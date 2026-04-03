import json
import random

import requests

def get_versions(min_version, max_version):
	versions_url = "https://meta.fabricmc.net/v2/versions/game"
	print(versions_url)
	versions = [v["version"] for v in reversed(json.loads(requests.get(versions_url).text)) if v["stable"]]
	return versions[versions.index(min_version) : versions.index(max_version) + 1]

def get_slug_set(facets):
	slugs = set()
	offset = 0
	search_url = f"https://api.modrinth.com/v3/search?limit=100&facets=[{facets}]&offset={offset}"
	print(search_url)
	hits = json.loads(requests.get(search_url).text)["hits"]
	while hits:
		slugs.update([(submission["slug"], submission["downloads"]) for submission in hits])
		offset += 100
		search_url = f"https://api.modrinth.com/v3/search?limit=100&facets=[{facets}]&offset={offset}"
		print(search_url)
		hits = json.loads(requests.get(search_url).text)["hits"]
	return slugs

def mods_without_datapacks(loaders, versions, date):
	version_filter = f"[{",".join([f"\"game_versions:{version}\"" for version in versions])}]"
	date_filter = f"[\"date_created{date}\"]"
	loader_filter = f"[{",".join([f"\"categories:{loader}\"" for loader in loaders])}]"
	projects = get_slug_set(f"[\"project_types:mod\"],{loader_filter},{version_filter},{date_filter}")
	datapacks = get_slug_set(f"[\"project_types:datapack\"],{version_filter},{date_filter}")
	mods = projects - datapacks
	return mods

def downloads(mods):
	return sum([mod[1] for mod in mods])

def measure_versions(loaders, versions, date):
	print(f"Pulling slugs for {len(versions)} versions: {versions}")
	mod_versions = {}
	for version in versions:
		mod_versions[version] = mods_without_datapacks(loaders, [version], date)
	print(f"Project counts published {date} for {", ".join(loaders)} on {len(versions)} versions from {versions[0]} to {versions[-1]}:")
	for version in versions:
		mods = mod_versions[version]
		minimum = mods
		for v in versions[:versions.index(version)]:
			minimum = minimum - mod_versions[v]
		maximum = mods
		for v in versions[versions.index(version)+1:]:
			maximum = maximum - mod_versions[v]
		unique = mods
		for v in [v for v in versions if v != version]:
			unique = unique - mod_versions[v]
		missing = set()
		for v in versions:
			missing = missing | mod_versions[v]
		missing = missing - mods
		print(f"{version} Mods: {format(len(mods), ",")}/{format(downloads(mods), ",")} Unique: {format(len(unique), ",")}/{format(downloads(unique), ",")} Missing: {format(len(missing), ",")}/{format(downloads(missing), ",")} Minimum: {format(len(minimum), ",")}/{format(downloads(minimum), ",")} Maximum: {format(len(maximum), ",")}/{format(downloads(maximum), ",")} e.g. https://modrinth.com/mod/{(random.choice(list(unique if unique else mods)) if mods else ("???", 0))[0]}")

if __name__ == "__main__":
	versions = get_versions("1.21.1", "1.21.11")
	# versions = ["1.16.5", "1.18.2", "1.19.2", "1.20.1", "1.21.1", "1.21.8"]
	measure_versions(["fabric"], versions, ">2005-03-18T00")
