

class Species:
    species_id = ""

    lv_thrust = 0
    lv_cytosis = 0
    lv_size = 0
    lv_resist_cold = 0
    lv_resist_hot = 0
    lv_density = 0

    lv_hunt = 0
    lv_poison = 0
    lv_shell = 0

    lv_o2_hold = 0
    lv_co2_hold = 0
    lv_photosynthesis = 0
    lv_nitrogen_fix = 0
    lv_hydrogen_usage = 0

    lv_reproduction = 0

    def __str__(self):

        lv_thrust = 0
        lv_cytosis = 0
        lv_size = 0
        lv_resist_cold = 0
        lv_resist_hot = 0
        lv_density = 0

        lv_hunt = 0
        lv_poison = 0
        lv_shell = 0

        lv_o2_hold = 0
        lv_co2_hold = 0
        lv_photosynthesis = 0
        lv_nitrogen_fix = 0
        lv_hydrogen_usage = 0

        lv_reproduction = 0
        return ""

    def __init__(self, df_row):

        self.species_id = df_row.iloc[0]
        self.lv_thrust = df_row.iloc[1]
        self.lv_cytosis = df_row.iloc[2]
        self.lv_size = df_row.iloc[3]
        self.lv_resist_cold = df_row.iloc[4]
        self.lv_resist_hot = df_row.iloc[5]
        self.lv_density = df_row.iloc[6]
        self.lv_hunt = df_row.iloc[7]
        self.lv_poison = df_row.iloc[8]
        self.lv_shell = df_row.iloc[9]
        self.lv_o2_hold = df_row.iloc[10]
        self.lv_co2_hold = df_row.iloc[11]
        self.lv_photosynthesis = df_row.iloc[12]
        self.lv_nitrogen_fix = df_row.iloc[13]
        self.lv_hydrogen_usage = df_row.iloc[14]
        self.lv_reproduction = df_row.iloc[15]



        return

        # with open(file_name, 'r') as file:
        #     self.species_id = file.readline().strip()
        #
        #     self.lv_thrust = int(file.readline())
        #     self.lv_cytosis = int(file.readline())
        #     self.lv_size = int(file.readline())
        #     self.lv_resist_cold = int(file.readline())
        #     self.lv_resist_hot = int(file.readline())
        #     self.lv_density = int(file.readline())
        #
        #     self.lv_hunt = int(file.readline())
        #     self.lv_poison = int(file.readline())
        #     self.lv_shell = int(file.readline())
        #
        #     self.lv_o2_hold = int(file.readline())
        #     self.lv_co2_hold = int(file.readline())
        #     self.lv_photosynthesis = int(file.readline())
        #     self.lv_nitrogen_fix = int(file.readline())
        #     self.lv_hydrogen_usage = int(file.readline())
        #
        #     self.lv_reproduction = int(file.readline())

    def get_genome_size(self):
        a = 0
        a += sum((
            abs(self.lv_thrust),
            abs(self.lv_cytosis),
            abs(self.lv_size),
            abs(self.lv_resist_cold),
            abs(self.lv_resist_hot),
            abs(self.lv_density),
            abs(self.lv_shell),
            abs(self.lv_hunt),
            abs(self.lv_poison),
            abs(self.lv_o2_hold),
            abs(self.lv_co2_hold),
            abs(self.lv_photosynthesis),
            abs(self.lv_nitrogen_fix),
            abs(self.lv_hydrogen_usage),
            abs(self.lv_reproduction))
        )
        return a * (0.95**self.lv_reproduction)

    def get_cell_size(self):
        a = 1
        return a * (1.2**self.lv_size)

    def get_needing_energy_to_reproduce(self):
        genome_size = self.get_genome_size()
        cell_size = self.get_cell_size()

        return 10000 * (cell_size + genome_size * 0.1) * (0.95 ** self.lv_reproduction)

    def get_needing_energy_to_survive(self):
        genome_size = self.get_genome_size()
        cell_size = self.get_cell_size()
        energy_needing_level = self.lv_poison + self.lv_thrust + self.lv_resist_hot + self.lv_resist_cold

        return 100 * (cell_size + genome_size * 0.1) * (0.95 ** self.lv_reproduction) * (1.05 ** energy_needing_level)

    def get_hunting_success_rate(self, other):
        if self.lv_hunt < 1:
            return 0
        hunt = (1 - (2 ** (-self.lv_hunt)))
        a = 1

        a = a * (1.1 ** (self.lv_size/10 + self.lv_thrust -
                         other.lv_size/10 - other.lv_thrust - other.lv_poison/2 - other.lv_shell/2)) * hunt
        return a

    def get_hunting_benefit_rate(self, other):
        a = 0.05
        return min(a * (1.1 ** self.lv_cytosis) * (1.2 ** (self.lv_size - other.lv_size)), 0.95)

    def get_eating_efficiency(self, material_id: str):
        a = 1
        if material_id == 'o2':
            return a * 10 * (1.01 ** self.lv_cytosis) * (8.1 - (2 ** (3 - self.lv_o2_hold))) * self.get_cell_size()
        if material_id == 'so4':
            return a * 10 * (1.1 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'h2s':
            return a * 10 * (1.02 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'low_c':
            return a * 100 * (1.1 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'high_c':
            return a * 100 * (1.1 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'high_n':
            return a * 10 * (1.1 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'high_e':
            return a * 1000 * (1.1 ** self.lv_cytosis) * self.get_cell_size()
        if material_id == 'co2':
            return a * 10 * (1.01 ** self.lv_cytosis) * (8.1 - (2 ** (3 - self.lv_co2_hold))) * self.get_cell_size()
        if material_id == 'n2':
            return a * 10 * (1.01 ** self.lv_cytosis) * self.get_cell_size()

    def get_photosynthesis_max(self):
        if self.lv_photosynthesis < 1:
            return 0
        a = 1 # light max: 1, min: 0 / # co2 is...
        lv = self.lv_photosynthesis + (0.5 * self.lv_co2_hold) - 3
        a = a * ((2 ** lv) / (1 + (2 ** lv)))
        return a

    def get_nitrogen_fix_max(self):
        if self.lv_nitrogen_fix < 1:
            return 0
        a = 1
        lv = self.lv_nitrogen_fix + (0.5 * self.lv_o2_hold) - 2.5
        a = a * ((2 ** lv) / (1 + (2 ** lv)))
        return a

    def get_survive_by_temp(self, temp):

        if temp < 20 - (self.lv_resist_cold * 4):
            return 0.9 ** (20 - (self.lv_resist_cold * 4) - temp)

        if temp > 30 + (self.lv_resist_hot * 7):
            return 0.9 ** (temp - 30 - (self.lv_resist_hot * 7))

        return 1

    def get_survive_by_oxygen(self, oxygen):
        if self.lv_o2_hold > 0:
            return 1
        else:
            return 0.99 ** oxygen

    def get_density(self):
        return 1.02 + ((self.lv_density) * 0.01)

    def get_migration_rate(self):
        a = 0.03
        a /= self.get_cell_size()
        a *= (1.2 ** self.lv_thrust)
        a = min(a, 0.1)
        return a
