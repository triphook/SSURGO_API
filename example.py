import ssurgo_api as s

# Activate a SSURGO object
ssurgo_path = r"T:\SSURGO"
ssurgo = s.SSURGO(ssurgo_path)

# Get all the soil textural classes present in Alabama (table: chtexturegrp, field: texdesc)
textures_by_horizon = ssurgo.al.chtexturegrp.texdesc
textures = set(textures_by_horizon.values())  # textures by horizon is indexed by chkey. Access unique values here
print("{} unique textures in Alabama including:\n {}\n".format(len(textures), ", ".join(list(textures)[:5])))
for horizon_id, texture in textures_by_horizon.items()[:5]:
    print("Horizon ID {} has texture {}".format(horizon_id, texture))

# Access all the fields in the texture group table
print("\n")
headings = ssurgo.al.chtexturegrp.headings
print("The table chtexturegrp contains the following headings:\n" + ", ".join(headings))

# Get the components for a random map unit in Iowa
print("\n")
random_map_unit = ssurgo.ia.map_units[77]
components = ssurgo.ia.components[random_map_unit]
print("Map unit {} contains the following components:".format(random_map_unit))
for component_id, pct_area in components:
    print("\t{} ({}% of map unit area)".format(component_id, pct_area))

# Loop through all the states for which SSURGO data is available, and count the number of map units
print("\n")
for state in ssurgo:
    n_map_units = len(state.map_units)
    n_components = len({component for map_unit in state.map_units for component in state.components[map_unit]})
    print("{} has {} unique map units".format(state.name, len(state.map_units)))