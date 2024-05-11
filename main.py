import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import pickle

from src.species import Species
from src.env import Env_Cell, Env_Var, Env_Def, Geography, Pop
import src.globals as glv

START_POS = (15, 15, 44)

FLOOR_SET = {
    (  0, 162, 232): "sand",
    (239, 228, 176): "clay",
    (255, 127,  39): "basalt",
    (127, 127, 127): "stone",
    (237,  28,  36): "vent",
}


def get_species():

    df = pd.read_csv('species/species.tsv', sep='\t')

    species_list = []
    for i, row in df.iterrows():
        print(i, row, type(row))
        species_list.append(Species(row))

    return species_list


def show_demography(demography_map_xy, demography_map_z, no = 0):

    for species in demography_map_xy.keys():

        xy_data = []
        z_data = []
        for i in range(100):
            y_data = []
            for j in range(100):
                if (i, j) in demography_map_xy[species].keys():
                    y_data.append(demography_map_xy[species][i, j])
                else:
                    y_data.append(0)
            xy_data.append(y_data)

            if i in demography_map_z[species].keys():
                z_data.append([demography_map_z[species][i]] * 10)
            else:
                z_data.append([1] * 10)
        df1 = pd.DataFrame(np.array(xy_data))
        df2 = pd.DataFrame(np.array(z_data))

        fig, ax = plt.subplots(ncols=2, figsize=(10, 4))
        im1 = ax[0].matshow(df1)
        im2 = ax[1].matshow(df2)
        fig.colorbar(im1, ax=ax[0])
        fig.colorbar(im2, ax=ax[1])
        plt.suptitle(species)

        plt.savefig(f'results/{species}_{no:03d}.png')


if __name__ == '__main__':


    world_file = input("Load the world from: ")
    set_world_again = False
    new_world = False
    world = dict()

    if os.path.isfile(world_file):
        with open(world_file, 'rb') as world_raw:
            world = pickle.load(world_raw)
            print(len(world.keys()), '/ 1000000 cells are loaded.')
        set_world_again = len(input("set world again? : ")) > 0
    else:
        set_world_again = True
        new_world = True
        print("No loading data is selected")
        glv.o2_evo = len(input("o2_evo: ")) > 0
        glv.temp_pos = float(input("set_temp: ") + '0') * 4
        glv.org_rain = len(input("org_rain: ")) > 0
        glv.clay_co2 = len(input("clay_co2: ")) > 0
        glv.ozone_set = len(input("ozone_set: ")) == 0

    cycle = 0
    while cycle < 1:
        cyc_text = input("Set cycle count: ")
        if len(cyc_text) > 0:
            cycle = int(cyc_text)
    new_world_file = input("Set the after-world to: ")

    input("Starting...")

    species_list = get_species()

    if set_world_again:
        geography = Geography()

        floor_image = Image.open("map_floor.bmp")
        depth_image = Image.open("map_depth.bmp")
        floor = np.array(floor_image)
        depth = np.array(depth_image)
        for i in range(100):
            for j in range(100):
                geography.floor[(i, j)] = FLOOR_SET[tuple(floor[i, j])]
                geography.depth[(i, j)] = min(105 - int(depth[i, j][0]/2.55), 99)
                # print(f"{geography.depth[(i, j)]:02d}", end="")
                if FLOOR_SET[tuple(floor[i, j])] == 'vent':
                    geography.vent_list.append((i, j, geography.depth[(i, j)]))
            # print()

        world = dict()

        for x in range(100):
            for y in range(100):
                for z in range(100):
                    world[x, y, z] = Env_Cell((x, y, z), geography.floor[(x, y)], geography.depth[(x, y)])

    if new_world:
        for species in species_list:
            species_id = species.species_id
            for x in range(100):
                for y in range(100):
                    for z in range(100):
                        if world[x, y, z].env_def.material in ('', 'sand2', 'clay2', 'clay3', 'clay4'):
                            continue
                        world[x, y, z].env_pop.append(Pop(species, species_id, 1, 1000000, 100000, 10000000))
    else:
        for x in range(100):
            for y in range(100):
                for z in range(100):
                    for i, pop in enumerate(world[x, y, z].env_pop):
                        for species in species_list:
                            if pop.species.species_id == species.species_id:
                                world[x, y, z].env_pop[i] = species

    for cyc in range(cycle):

        print(cyc+1, "step starting")
        mig_dict = dict()
        for x in range(100):
            print(f"\r{x+1}/100 eating", end='')
            for y in range(100):
                for z in range(100):
                    world[x, y, z].step_interaction()

                    pos_list = []
                    if x+1 < 100 and len(world[x+1, y, z].env_def.material) > 0:
                        pos_list.append(world[x+1, y, z].env_def)
                    if x-1 >= 0 and len(world[x-1, y, z].env_def.material) > 0:
                        pos_list.append(world[x-1, y, z].env_def)
                    if y+1 < 100 and len(world[x, y+1, z].env_def.material) > 0:
                        pos_list.append(world[x, y+1, z].env_def)
                    if y-1 >= 0 and len(world[x, y-1, z].env_def.material) > 0:
                        pos_list.append(world[x, y-1, z].env_def)
                    if z+1 < 100 and len(world[x, y, z+1].env_def.material) > 0:
                        pos_list.append(world[x, y, z+1].env_def)
                    if z-1 >= 0 and len(world[x, y, z-1].env_def.material) > 0:
                        pos_list.append(world[x, y, z-1].env_def)
                    mig_cell = world[x, y, z].get_migration(env_def_list=pos_list)

                    for key, item in mig_cell.items():
                        if key in mig_dict.keys():
                            mig_dict[key] += item
                        else:
                            mig_dict[key] = item

        print("- eating over")

        for x in range(100):
            for y in range(100):
                for z in range(100):
                    if (x, y, z) in mig_dict.keys():
                        world[x, y, z].step_migration(mig_dict[x, y, z])
        print("- migration over")

        print(cyc+1, "step complete")
        print()

        demography_map_xy = dict()
        demography_map_z = dict()
        for species in species_list:
            demography_map_xy[species.species_id] = dict()
            demography_map_z[species.species_id] = dict()

        for x in range(100):
            for y in range(100):
                for z in range(100):
                    for pop in world[x, y, z].env_pop:
                        if (x, y) in demography_map_xy[pop.species_id].keys():
                            demography_map_xy[pop.species_id][x, y] += pop.population
                        else:
                            demography_map_xy[pop.species_id][x, y] = pop.population
                        if z in demography_map_z[pop.species_id].keys():
                            demography_map_z[pop.species_id][z] += pop.population
                        else:
                            demography_map_z[pop.species_id][z] = pop.population

        # print(demography_map_xy)
        # print(demography_map_z)
        if cyc % 1 == 0:
            show_demography(demography_map_xy, demography_map_z, cyc+1)

    with open(new_world_file, 'wb') as world_raw:
        pickle.dump(world, world_raw)
