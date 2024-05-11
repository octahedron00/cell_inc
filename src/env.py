from src.species import Species
import src.globals as glv

Z = 0.00000001

class Env_Def:
    coordinate = (0, 0, 0)
    material = ""
    depth = 0
    floor = ""
    dist_floor = 0
    temp = 15
    vis_light = 0
    uv_light = 0
    n2 = 0
    density = 1.01

    def __init__(self, coordinate, floor, floor_depth):
        self.coordinate = coordinate
        self.depth = coordinate[2]
        self.dist_floor = abs(self.depth - floor_depth)
        if self.depth > floor_depth:
            self.material = ''
            return

        self.temp = max(24 - (self.depth * 0.5), 4) + glv.temp_pos
        self.floor = floor
        self.vis_light = max(1 - (0.2 * self.depth), 0)
        self.uv_light = max(1 - (0.3 * self.depth), 0)
        if glv.ozone_set:
            self.uv_light *= 0.1
        if floor == 'vent':
            self.material = 'water'
            self.temp = max(self.temp, 95 - floor_depth*5)
        if floor == 'clay':
            self.temp = max(self.temp, 25 - floor_depth*3)
            if self.dist_floor < 5:
                self.material = 'clay' + str(4-self.dist_floor)
            else:
                self.material = 'water'
        if floor == 'sand':
            if self.dist_floor < 3:
                self.material = 'sand' + str(2-self.dist_floor)
            else:
                self.material = 'water'
        if floor == 'basalt':
            if self.dist_floor < 1:
                self.material = 'basalt'
            else:
                self.material = 'water'
        if floor == 'stone':
            self.material = 'water'

        self.n2 = 0
        self.density = 1.00 + int(self.depth/20)*0.01


class Env_Var:
    high_c = 0
    high_n = 0
    high_e = 0
    low_c = 0
    co2 = 0
    h2s = 0
    so4 = 0
    o2 = 0

    def __init__(self, env_def: Env_Def, preset = (0.0, 0.0, 0.0, 0.0)):
        self.high_c = 0
        self.high_n = 0
        self.high_e = 0
        self.low_c = 0
        self.co2 = 0
        self.h2s = 0
        self.so4 = 0
        self.o2 = 0

        self.so4 = 200000000 * (30 + 0.3 * env_def.temp)
        self.co2 = 50000000 * (200 - env_def.temp)
        if glv.o2_evo:
            self.o2 = 8000000 * max(50 - env_def.temp, 0) * max(50 - env_def.depth, 0)
        else:
            self.o2 = 2000000 * max(50 - env_def.temp, 0) * max(30 - env_def.depth, 0)
        if env_def.floor == 'vent':
            self.h2s = 800000000 * (0.3 ** env_def.dist_floor)
            self.high_c = 800000000 * (0.3 ** env_def.dist_floor)
            self.high_n = 80000000 * (0.3 ** env_def.dist_floor)
            self.high_e = 8000000000 * (0.3 ** env_def.dist_floor)
            self.low_c = 800000000 * (0.3 ** env_def.dist_floor)

        if env_def.floor == 'clay':
            self.h2s = 80000000 * (0.3 ** max(env_def.dist_floor-5, 0))
            self.high_c = 8000000 * (0.1 ** max(env_def.dist_floor-5, 0))
            self.high_n = 800000 * (0.1 ** max(env_def.dist_floor-5, 0))
            self.high_e = 80000000 * (0.1 ** max(env_def.dist_floor-5, 0))
            self.low_c = 80000000 * (0.1 ** max(env_def.dist_floor-5, 0))
            if glv.clay_co2:
                self.high_c *= 5
                self.high_n *= 5
                self.high_e *= 5
                self.low_c *= 5

        if env_def.dist_floor < 1:
            self.high_c += 10000000
            self.high_n += 1000000
            self.high_e += 100000000
            self.low_c += 10000000
            if glv.org_rain:
                self.high_c += 100000000
                self.high_n += 10000000
                self.high_e += 1000000000
                self.low_c += 100000000

        self.high_c *= 20
        self.high_n *= 20
        self.high_e *= 20
        self.low_c *= 20

        self.high_c += preset[0]
        self.high_n += preset[1]
        self.high_e += preset[2]
        self.low_c += preset[3]




class Pop:
    species = ""
    species_id = ""
    population = 0
    high_c = 0
    high_n = 0
    high_e = 0
    low_c = 0
    co2 = 0
    h2s = 0
    so4 = 0
    o2 = 0
    n2 = 0

    def __init__(self, species: Species, species_id: str, population: int, c, n, e):
        self.species = species
        self.species_id = species_id
        self.population = population
        self.high_c = c
        self.high_n = n
        self.high_e = e

    def __str__(self):
        return f"species: {self.species.species_id}\n" \
               f"- {self.population} -\n" \
               f"hic: {self.high_c}\n" \
               f"hin: {self.high_n}\n" \
               f"hie: {self.high_e}\n" \
               f"loc: {self.low_c}\n" \
               f"h2s: {self.h2s}\n" \
               f" o2: {self.o2}\n" \
               f"so4: {self.so4}\n"



class Env_Cell:

    env_pos = (0, 0, 0)
    env_def = None
    env_var = None
    env_pop = []

    def __init__(self, pos, floor, floor_depth):
        self.env_pos = pos
        self.env_def = Env_Def(coordinate=pos, floor=floor, floor_depth=floor_depth)
        self.env_var = Env_Var(self.env_def, (1000000, 100000, 10000000, 100000))
        self.env_pop = []


    def step_interaction(self):

        if len(self.env_pop) < 1:
            return

        max_eating_o2 = sum([pop.species.get_eating_efficiency('o2') * pop.population for pop in self.env_pop]) + Z
        max_eating_so4 = sum([pop.species.get_eating_efficiency('so4') * pop.population for pop in self.env_pop]) + Z
        max_eating_h2s = sum([pop.species.get_eating_efficiency('h2s') * pop.population for pop in self.env_pop]) + Z
        max_eating_high_c = sum([pop.species.get_eating_efficiency('high_c') * pop.population for pop in self.env_pop]) + Z
        max_eating_high_n = sum([pop.species.get_eating_efficiency('high_n') * pop.population for pop in self.env_pop]) + Z
        max_eating_high_e = sum([pop.species.get_eating_efficiency('high_e') * pop.population for pop in self.env_pop]) + Z
        max_eating_low_c = sum([pop.species.get_eating_efficiency('low_c') * pop.population for pop in self.env_pop]) + Z

        efficiency_o2 = min(1, self.env_var.o2 / max_eating_o2)
        efficiency_so4 = min(self.env_var.so4 / max_eating_so4, 1)
        efficiency_h2s = min(self.env_var.h2s / max_eating_h2s, 1)
        efficiency_high_c = min(self.env_var.high_c / max_eating_high_c, 1)
        efficiency_high_n = min(self.env_var.high_n / max_eating_high_n, 1)
        efficiency_high_e = min(self.env_var.high_e / max_eating_high_e, 1)
        efficiency_low_c = min(self.env_var.low_c / max_eating_low_c, 1)

        self.env_var.o2 = max(self.env_var.o2 - max_eating_o2, 0)
        self.env_var.so4 = max(self.env_var.so4 - max_eating_so4, 0)
        self.env_var.h2s = max(self.env_var.h2s - max_eating_h2s, 0)
        self.env_var.high_c = max(self.env_var.high_c - max_eating_high_c, 0)
        self.env_var.high_n = max(self.env_var.high_n - max_eating_high_n, 0)
        self.env_var.high_e = max(self.env_var.high_e - max_eating_high_e, 0)
        self.env_var.low_c = max(self.env_var.low_c - max_eating_low_c, 0)
        # Works same

        for pop in self.env_pop:
            pop.o2 += efficiency_o2 * pop.species.get_eating_efficiency('o2')
            pop.so4 += efficiency_so4 * pop.species.get_eating_efficiency('so4')
            pop.h2s += efficiency_h2s * pop.species.get_eating_efficiency('h2s')
            pop.high_c += efficiency_high_c * pop.species.get_eating_efficiency('high_c')
            pop.high_n += efficiency_high_n * pop.species.get_eating_efficiency('high_n')
            pop.high_e += efficiency_high_e * pop.species.get_eating_efficiency('high_e')
            pop.low_c += efficiency_low_c * pop.species.get_eating_efficiency('low_c')

        # print("-eating")
        # hunting:
        max_hunted = dict()
        for predator in self.env_pop:
            if predator.species.lv_hunt < 1:
                continue
            for prey in self.env_pop:
                if predator.species_id == prey.species_id:
                    continue
                hunt_rate = predator.species.get_hunting_success_rate(prey.species)
                if prey.species_id in max_hunted.keys():
                    max_hunted[prey.species_id] += hunt_rate * predator.population * prey.population
                else:
                    max_hunted[prey.species_id] = hunt_rate * predator.population * prey.population

        efficiency_hunt = dict()
        for prey in self.env_pop:
            if prey.species_id in max_hunted.keys():
                efficiency_hunt[prey.species_id] = min(1, prey.population / max_hunted[prey.species_id])
        for predator in self.env_pop:
            for prey in self.env_pop:
                if predator.species_id == prey.species_id or predator.species.lv_hunt < 1:
                    continue
                hunt_rate = predator.species.get_hunting_success_rate(prey.species)
                hunt_number = hunt_rate * predator.population * prey.population * efficiency_hunt[prey.species_id]

                hunt_benefit = predator.species.get_hunting_benefit_rate(prey.species)

                got_high_c = ((prey.high_c * hunt_number / prey.population) + hunt_number * prey.species.get_needing_energy_to_reproduce() * 0.09)
                got_high_n = ((prey.high_n * hunt_number / prey.population) + hunt_number * prey.species.get_needing_energy_to_reproduce() * 0.009)
                got_high_e = ((prey.high_e * hunt_number / prey.population) + hunt_number * prey.species.get_needing_energy_to_reproduce() * 0.9)
                got_low_c = (prey.low_c * hunt_number / prey.population)
                got_o2 = (prey.o2 * hunt_number / prey.population)
                got_h2s = (prey.h2s * hunt_number / prey.population)
                got_so4 = (prey.so4 * hunt_number / prey.population)

                predator.high_c += hunt_benefit * got_high_c
                predator.high_n += hunt_benefit * got_high_n
                predator.high_e += hunt_benefit * got_high_e
                predator.low_c += hunt_benefit * got_low_c
                predator.o2 += hunt_benefit * got_o2
                predator.h2s += hunt_benefit * got_h2s
                predator.so4 += hunt_benefit * got_so4

                self.env_var.high_c += (1-hunt_benefit) * got_high_c
                self.env_var.high_n += (1-hunt_benefit) * got_high_n
                self.env_var.high_e += (1-hunt_benefit) * got_high_e
                self.env_var.low_c += (1-hunt_benefit) * got_low_c
                self.env_var.o2 += (1-hunt_benefit) * got_o2
                self.env_var.h2s += (1-hunt_benefit) * got_h2s
                self.env_var.so4 += (1-hunt_benefit) * got_so4
        # print("-hunting completed")

        # making
        for pop in self.env_pop:
            pop.high_c += pop.species.get_photosynthesis_max() * self.env_def.vis_light

            mode = 'e'
            c_e = (pop.high_c*10) / pop.high_e
            n_e = (pop.high_n*100) / pop.high_e
            if n_e < 1 and n_e < c_e:
                mode = 'n'
            if c_e < 1 and c_e < n_e:
                mode = 'c'

            if pop.species.lv_o2_hold > 0:
                if mode == 'n':
                    for_e_100_n = (50/(pop.species.get_nitrogen_fix_max() + Z))
                    max_n_energy = (for_e_100_n / (100 + for_e_100_n)) * pop.high_e

                    pop.high_e -= max_n_energy
                    pop.high_n += max_n_energy / (for_e_100_n + Z)
                if mode == 'c':
                    max_o2_burning_h2s = min(pop.o2, pop.h2s * 2)

                    pop.high_e += max_o2_burning_h2s * 18
                    pop.h2s -= max_o2_burning_h2s / 2
                    pop.so4 += max_o2_burning_h2s / 2
                    pop.o2 -= max_o2_burning_h2s

                pop.high_e -= pop.low_c * 2
                pop.high_c += pop.low_c
                pop.low_c = 0
                to_burn = max(pop.high_c - pop.high_e/10, 0)
                if to_burn > 0:
                    max_burn = pop.o2

                    burn = min(to_burn, max_burn, pop.high_c)

                    pop.o2 -= burn
                    pop.high_c -= burn
                    pop.high_e += burn * 25

                    to_burn -= burn

                to_ferment = max(pop.high_c - pop.high_e/10, 0)
                if to_ferment > 0:
                    ferment = min(to_ferment, pop.high_c)

                    pop.high_c -= ferment
                    pop.low_c += ferment
                    pop.high_e += ferment * 2

            else:
                if mode == 'n':
                    # n2 + 3h2 -> high_n (2nh3)
                    h2 = pop.h2s
                    pop.high_n += h2/3
                    pop.h2s = 0
                else:
                    # co2 + h2 + 13E -> high_c + h2o
                    h2 = pop.h2s
                    pop.high_c += min(h2, pop.high_e / 2)
                    pop.high_e -= min(h2*2, pop.high_e)
                    pop.h2s -= min(h2, pop.high_e / 2)

                pop.high_e -= pop.low_c * 2
                pop.high_c += pop.low_c
                pop.low_c = 0
                to_burn = max(pop.high_c - pop.high_e/10, 0)
                if to_burn > 0:
                    max_burn = pop.so4 * 2

                    burn = min(to_burn, max_burn, pop.high_c)

                    pop.so4 -= burn / 2
                    pop.high_c -= burn
                    pop.high_e += burn * 9
                    pop.h2s += burn / 2

                    to_burn -= burn

                to_ferment = max(pop.high_c - pop.high_e/10, 0)
                if to_ferment > 0:
                    ferment = min(to_ferment, pop.high_c)

                    pop.high_c -= ferment
                    pop.low_c += ferment
                    pop.high_e += ferment * 2

            if self.env_def.coordinate[0] % 20 == self.env_def.coordinate[1] % 20 == self.env_def.coordinate[2] % 20 == 10:
                print(pop)
        # print("-making completed")
        # die first.
        for pop in self.env_pop:
            # print(pop)

            self.env_var.o2 += pop.o2
            self.env_var.so4 += pop.so4
            self.env_var.h2s += pop.h2s
            self.env_var.low_c += pop.low_c

            survive_rate = 0.95 * (0.8 ** self.env_def.uv_light) * \
                           pop.species.get_survive_by_temp(self.env_def.temp) * \
                           pop.species.get_survive_by_oxygen(self.env_var.o2)

            death_rate = 1 - survive_rate

            pop.population *= survive_rate
            pop.population = int(pop.population) + 1

            self.env_var.high_c += pop.high_c * death_rate
            self.env_var.high_n += pop.high_n * death_rate
            self.env_var.high_e += pop.high_e * death_rate * 0.8

            pop.high_c *= survive_rate
            pop.high_n *= survive_rate
            pop.high_e *= survive_rate
        # print("-population change completed")

        # reproduce.
        for pop in self.env_pop:

            rep_e = pop.species.get_needing_energy_to_reproduce() + pop.species.get_needing_energy_to_survive() * 4
            rep_c = rep_e / 10
            rep_n = rep_e / 100

            rep_count = min(pop.high_c / rep_c, pop.high_n / rep_n, pop.high_e, rep_e)*0.9 + 0.5
            rep_count = int(rep_count)

            pop.population += rep_count
            pop.high_c -= rep_count * rep_c
            pop.high_n -= rep_count * rep_n
            pop.high_e -= rep_count * rep_e

            if pop.population < 0:
                pop.population = 1

        # env_refresh
        self.env_var = Env_Var(self.env_def,
                               (self.env_var.high_c, self.env_var.high_n, self.env_var.high_e, self.env_var.low_c))


    def get_migration(self, env_def_list: list[Env_Def]):

        density_here = self.env_def.density
        z_here = self.env_def.coordinate[2]

        migration_dict = dict()
        for env_def in env_def_list:
            migration_dict[env_def.coordinate] = []

        for pop in self.env_pop:
            migration_rate = pop.species.get_migration_rate()
            mig_population = int(pop.population * migration_rate + 1)
            mig_high_c = pop.high_c * mig_population / (pop.population + Z)
            mig_high_n = pop.high_n * mig_population / (pop.population + Z)
            mig_high_e = pop.high_e * mig_population / (pop.population + Z)

            for env_def in env_def_list:
                if env_def.material == 'sand1' and pop.species.lv_size > 2:
                    continue
                if env_def.material == 'sand2' and pop.species.lv_size > 0:
                    continue
                if env_def.material == 'clay1' and (pop.species.lv_size > 2 or pop.species.lv_thrust < 1 or pop.species.lv_shell < 0):
                    continue
                if env_def.material == 'clay2' and (pop.species.lv_size > 0 or pop.species.lv_thrust < 1 or pop.species.lv_shell < 1):
                    continue
                if env_def.material == 'clay3' and (pop.species.lv_size > 0 or pop.species.lv_thrust < 2 or pop.species.lv_shell < 1):
                    continue
                if env_def.material == 'clay4' and (pop.species.lv_size > 0 or pop.species.lv_thrust < 4 or pop.species.lv_shell < 1):
                    continue

                if (env_def.coordinate[2] > z_here and pop.species.get_density() < density_here) or \
                        (env_def.coordinate[2] < z_here and pop.species.get_density() > density_here):
                    mig_pop = Pop(pop.species, pop.species_id, mig_population*6, mig_high_c*6, mig_high_n*6, mig_high_e*6)
                    migration_dict[env_def.coordinate].append(mig_pop)
                elif (env_def.coordinate[2] < z_here and pop.species.get_density() < density_here) or \
                        (env_def.coordinate[2] > z_here and pop.species.get_density() > density_here):
                    mig_pop = Pop(pop.species, pop.species_id, int(mig_population/6)+1, mig_high_c/6, mig_high_n/6, mig_high_e/6)
                    migration_dict[env_def.coordinate].append(mig_pop)
                else:
                    mig_pop = Pop(pop.species, pop.species_id, mig_population, mig_high_c, mig_high_n, mig_high_e)
                    migration_dict[env_def.coordinate].append(mig_pop)

        return migration_dict


    def step_migration(self, migration_list: list[Pop]):
        species_dict = dict()
        for i, pop in enumerate(self.env_pop):
            species_dict[pop.species_id] = i

        for mig_pop in migration_list:
            if mig_pop.species_id not in species_dict.keys():
                self.env_pop.append(mig_pop)
                species_dict[mig_pop.species_id] = len(self.env_pop) - 1
            else:
                i = species_dict[mig_pop.species_id]
                self.env_pop[i].population += mig_pop.population
                self.env_pop[i].high_c += mig_pop.high_c
                self.env_pop[i].high_n += mig_pop.high_n
                self.env_pop[i].high_e += mig_pop.high_e

        # print("-migration completed")


class Geography:
    vent_list = []
    depth = dict()
    floor = dict()

    def __init__(self):
        vent_list = []
        depth = dict()
        floor = dict()
