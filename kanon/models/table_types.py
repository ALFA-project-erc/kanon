from .meta import TableType


class Sun(TableType):
    @classmethod
    def astro_id(cls):
        return 1

    equ_of_the_sun = 4
    equ_of_time = 1
    mean_motion_solar_sideral_long = 3
    mean_motion_solar_tropical_long = 2
    revolutions = 86
    solar_velocities = 20


class Mercury(TableType):
    @classmethod
    def astro_id(cls):
        return 2

    equ_anomaly_at_max_dist = 72
    equ_anomaly_at_mean_dist = 27
    equ_anomaly_at_min_dist = 73
    equ_center = 26
    equ_minuta_proportionalia = 91
    first_lat = 96
    lat_deviation = 100
    lat_double_arg = 101
    lat_incl = 98
    lat_slant = 99
    mean_motion_anomaly = 25
    planetary_stations = 30
    second_lat = 97
    total_equ_double_arg_table = 28
    true_position_double_arg = 92
    variable_hypotenuse = 90
    velocity_double_arg = 95
    velocity_eccentricity_component = 93
    velocity_epicycle_component = 94


class Venus(TableType):
    @classmethod
    def astro_id(cls):
        return 3

    equ_anomaly_at_max_dist = 76
    equ_anomaly_at_mean_dist = 33
    equ_anomaly_at_min_dist = 77
    equ_center = 32
    equ_minuta_proportionalia = 103
    first_lat = 108
    lat_deviation = 112
    lat_double_arg = 113
    lat_incl = 110
    lat_slant = 111
    mean_motion_anomaly = 31
    planetary_stations = 36
    second_lat = 109
    total_equ_double_arg_table = 34
    true_position_double_arg = 104
    variable_hypotenuse = 102
    velocity_double_arg = 107
    velocity_eccentricity_component = 105
    velocity_epicycle_component = 106


class Moon(TableType):
    @classmethod
    def astro_id(cls):
        return 4

    equ_anomaly = 47
    equ_anomaly_at_max_dist = 188
    equ_center = 46
    equ_minuta_proportionalia = 89
    equ_variation_of_diameter = 88
    lunar_lat = 48
    lunar_velocities = 23
    mean_arg_of_lat = 87
    mean_motion_double_elongation = 45
    mean_motion_long_plus_lunar_node = 43
    mean_motion_lunar_anomaly = 38
    mean_motion_lunar_elongation = 44
    mean_motion_lunar_long = 37
    mean_motion_lunar_node = 42


class Mars(TableType):
    @classmethod
    def astro_id(cls):
        return 5

    equ_anomaly_at_max_dist = 70
    equ_anomaly_at_mean_dist = 51
    equ_anomaly_at_min_dist = 71
    equ_center = 50
    equ_minuta_proportionalia = 115
    first_lat = 120
    lat_double_arg = 124
    mean_motion_long = 49
    northern_lat = 122
    planetary_stations = 54
    second_lat = 121
    southern_lat = 123
    total_equ_double_arg_table = 52
    true_position_double_arg = 116
    variable_hypotenuse = 114
    velocity_double_arg = 119
    velocity_eccentricity_component = 117
    velocity_epicycle_component = 118


class Jupiter(TableType):
    @classmethod
    def astro_id(cls):
        return 6

    equ_anomaly_at_max_dist = 68
    equ_anomaly_at_mean_dist = 57
    equ_anomaly_at_min_dist = 69
    equ_center = 56
    equ_minuta_proportionalia = 126
    first_lat = 131
    lat_double_arg = 135
    mean_motion_long = 55
    northern_lat = 133
    planetary_stations = 60
    second_lat = 132
    southern_lat = 134
    total_equ_double_arg_table = 58
    true_position_double_arg = 127
    variable_hypotenuse = 125
    velocity_double_arg = 130
    velocity_eccentricity_component = 128
    velocity_epicycle_component = 129


class Saturn(TableType):
    @classmethod
    def astro_id(cls):
        return 7

    equ_anomaly_at_max_dist = 74
    equ_anomaly_at_mean_dist = 63
    equ_anomaly_at_min_dist = 75
    equ_center = 62
    equ_minuta_proportionalia = 137
    first_lat = 142
    lat_double_arg = 146
    mean_motion_long = 61
    northern_lat = 144
    planetary_stations = 66
    second_lat = 143
    southern_lat = 145
    total_equ_double_arg_table = 64
    true_position_double_arg = 138
    variable_hypotenuse = 136
    velocity_double_arg = 141
    velocity_eccentricity_component = 139
    velocity_epicycle_component = 140


class SphericalAstronomical(TableType):
    @classmethod
    def astro_id(cls):
        return 8

    ascensional_diff = 11
    declination = 8
    houses = 79
    length_of_daylight = 78
    length_of_diurnal_seasonal_hour = 12
    meridian_altitude_of_the_sun = 80
    oblique_ascension = 10
    projection_of_rays = 83
    proportion_tables = 84
    right_ascension = 9
    solar_altitude_from_the_time_of_day = 82
    tangent = 85
    time_of_day_from_solar_altitude = 81


class EighthSphere(TableType):
    @classmethod
    def astro_id(cls):
        return 9

    equ_access_and_recess = 148
    mean_motion_access_and_recess = 13
    mean_motion_apogees_and_stars_precessions = 14
    mean_motion_solar_apogee = 17
    trepidation = 147


class Eclipse(TableType):
    @classmethod
    def astro_id(cls):
        return 10

    digit_of_lunar_eclipse_at_great_dist = 163
    digit_of_lunar_eclipse_at_near_dist = 166
    digit_of_solar_eclipse_at_great_dist = 169
    digit_of_solar_eclipse_at_near_dist = 171
    eclipse_interpolation_table = 173
    eclipsed_part_of_the_lunar_disk = 174
    eclipsed_part_of_the_solar_disk = 175
    half_totality_of_lunar_eclipse_at_great_dist = 165
    half_totality_of_lunar_eclipse_at_near_dist = 168
    immersion_of_eclipse_at_near_dist = 172
    immersion_of_lunar_eclipse_at_great_dist = 164
    immersion_of_lunar_eclipse_at_near_dist = 167
    immersion_of_solar_eclipse_at_great_dist = 170
    incl_at_the_beginning_of_lunar_eclipse = 178
    incl_at_the_beginning_of_solar_eclipse = 176
    incl_at_the_beginning_of_totality_for_a_lunar_eclipse = 179
    incl_at_the_end_of_lunar_eclipse = 181
    incl_at_the_end_of_solar_eclipse = 177
    incl_at_the_end_of_totality_for_a_lunar_eclipse = 180
    incl_local_lat_component = 185
    incl_obliquity_component = 186
    lunar_eclipse_half_duration_table = 183
    lunar_eclipse_half_totality_table = 184
    mean_motion_syzygies = 149
    moon_prlx_at_quadrature_and_true_anomaly_at_0deg = 154
    moon_prlx_at_quadrature_and_true_anomaly_at_180deg = 155
    moon_prlx_at_syzygy_and_true_anomaly_at_0deg = 152
    moon_prlx_at_syzygy_and_true_anomaly_at_180deg = 153
    moon_prlx_interpolation_at_quadrature = 157
    moon_prlx_interpolation_at_syzygy = 156
    moon_prlx_interpolation_between_syzygy_and_quadrature = 158
    prlx_lat_component = 151
    prlx_long_component = 150
    radius_of_the_moon = 160
    radius_of_the_shadow = 161
    radius_of_the_sun = 159
    solar_eclipse_half_duration_table = 182
    variation_of_shadow = 162


class Mathematical(TableType):
    @classmethod
    def astro_id(cls):
        return 11

    chords = 5
    cosine = 67
    shadow = 7
    sine = 6
