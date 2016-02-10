
def extract_grid(folder_path, outfolder, state):

    arcpy.env.workspace = folder_path

    # Save all tables
    for table in arcpy.ListTables():
        new_table = os.path.join(outfolder, table + ".csv")
        if not os.path.exists(new_table):
            arcpy.CopyRows_management(table, new_table)

    # Save raster grid
    for raster in arcpy.ListRasters():
        new_raster = os.path.join(outfolder, state)
        if not os.path.exists(new_raster):
            arcpy.Raster(raster).save(new_raster)


def customize_ssurgo(ssurgo_folder, folder_format, out_folder):

    ssurgo_map = map_ssurgo(ssurgo_folder, folder_format)
    for state, gdb in sorted(ssurgo_map.items()):
        state_folder = os.path.join(out_folder, state)
        if not os.path.exists(state_folder):
            os.makedirs(state_folder)
        print(state)
        start = time.time()
        extract_grid(gdb, state_folder, state)
        print("...completed in {} seconds".format(int(time.time() - start)))


def main():
    ssurgo_folder = r"T:\SSURGO"
    folder_format = "_(\D{2})_"
    out_folder = r"T:\CustomSSURGO"

    customize_ssurgo(ssurgo_folder, folder_format, out_folder)

sys.exit(main())