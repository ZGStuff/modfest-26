import os
import shutil
import subprocess

from scripts import common

# Copy world into specified folder from backup
# Run this script twice and validate for errors - delete any MCASelector "failed to delete" stuff (usually poi)

def trim_world():
	# Event-Specific Data
	folder_name  = "ModFest Toybox Showcase"
	level_name = "ModFest: Toybox Showcase World"
	spawn = [54, 222, 85]
	dim_borders = { # chunk coordinates to keep, inclusive-inclusive.
		"": [0, 0, 31, 31], # Overworld
	}
	dim_time_prune = { # min time inhabited to keep chunks. good for natural gen areas where you want to keep booth-only
		# Must always define these 3 because they're not in dimension
		"": "30 seconds",
		"DIM-1": "1 minute",
		"DIM1": "1 minute",
	}
	remove = [ # files to ditch from the save entirely
		# player data - note shard collections are kept for their stats.
		"playerdata",
		"player-mod-data",
		"stats",
		"advancements",
		# junk
		"level.dat_old",
		"session.lock",
		# unused dimensions
		"DIM1",
		"DIM-1",
		"dimensions/fantasy"
	]

	# directories
	repo_root = common.get_repo_root()
	world_dir = repo_root / "pack" / "saves" / folder_name
	selector_jar = repo_root / "scripts" / "libs" / "mcaselector.jar"
	unbted_jar = repo_root / "scripts" / "libs" / "unbted.jar"

	if os.path.exists(f"{world_dir}/dimensions"):
		for namespace in os.listdir(f"{world_dir}/dimensions"):
			for path in os.listdir(f"{world_dir}/dimensions/{namespace}"):
				dim = f"dimensions/{namespace}/{path}"
				if f"dimensions/{namespace}" not in remove and dim not in remove:
					if path.startswith("workspace_") or "region" not in os.listdir(f"{world_dir}/{dim}"):
						remove.append(dim)
					elif dim not in dim_time_prune.keys():
						dim_time_prune[dim] = "10 seconds"

	shutil.copyfile(repo_root / "pack" / "server-icon.png", world_dir / "icon.png")

	for file in remove:
		path = f"{world_dir}/{file}"
		if os.path.exists(path):
			print(f"removing {path}")
			if os.path.isdir(path):
				shutil.rmtree(path)
			else:
				os.remove(path)

	for dim, time in dim_time_prune.items():
		dim_path = f"{world_dir}/{dim}" if dim else world_dir
		print("---")
		print(f"Pruning chunks from {dim_path} that are empty, inhabited less than {time}{', or outside border' if dim in dim_borders else ''}")
		border_exp = f"OR xPos < {dim_borders[dim][0]} OR zPos < {dim_borders[dim][1]} OR xPos > {dim_borders[dim][2]} OR zPos > {dim_borders[dim][3]}" if dim in dim_borders else ""
		query = f"\"Palette = \"air\" OR InhabitedTime < \\\"{time}\\\" {border_exp}\""
		command = f"java -jar \"{selector_jar}\" --mode delete --world \"{dim_path}\" --query {query}"
		print(command)
		subprocess.run(command)

	print("---")

	for path, dirs, files in list(os.walk(world_dir))[1:]:
		found = False
		for file in files:
			file_path = f"{path}/{file}"
			if file.endswith(".mca") and os.path.getsize(file_path) == 0:
				if not found:
					found = True
					print(f"Removing empty .mca files from {path}")
				os.remove(file_path)

	print(f"Cleaning up empty folders")
	for path, dirs, files in list(os.walk(world_dir))[1:]:
		if not files and not dirs:
			os.removedirs(path)

	# todo maybe a system where you can target folders (e.g. worldcomment, surveyor) that should match whether regions exist in the actual region folder?

	print(f"Tweaking level.dat for world \"{level_name}\"")
	subprocess.run(f"java -jar \"{unbted_jar}\" \"{world_dir}/level.dat\"", input=f"""
        set Data/allowCommands true
        set Data/GameType 2
        set Data/GameRules/spawnRadius 0
        set Data/BorderWarningBlocks 0
        del Data/Player -r
        mkdir Data/Player
        set Data/Player/Pos --list
        set Data/Player/Pos[0] --double -- {spawn[0] + 0.5} 
        set Data/Player/Pos[1] --double -- {spawn[1]}
        set Data/Player/Pos[2] --double -- {spawn[2] + 0.5} 
        set Data/LevelName \"{level_name}\"
        save
    """.encode('ascii'))


if __name__ == "__main__":
	trim_world()
