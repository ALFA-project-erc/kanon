from .meta import TableType


class Sun(TableType):
    @classmethod
    def astro_id(cls):
        return 1

    equation_time = "equation of time"
    solar_velocities = "solar velocities"
    revolutions = "revolutions"
    equation_sun = "equation of the Sun"
    mm_solar_sideral_longitude = "mean motion solar sideral longitude"
    mm_solar_tropical_longitude = "mean motion solar tropical longitude"


class Mercury(TableType):
    @classmethod
    def astro_id(cls):
        return 2

    latitude_deviation = "Mercury latitude deviation"
    velocity_double_argument = "Mercury velocity double argument"
    mm_anomaly = "mean motion anomaly Mercury"
    equation_center = "equation Mercury center"
    equation_anomaly_mean_distance = "equation Mercury anomaly at mean distance"
    total_equation_double_argument = "total equation double-argument table Mercury"
    planetary_stations = "planetary Stations Mercury"
    latitude_inclination = "Mercury latitude inclination"
    latitude_slant = "Mercury latitude slant"
    first_latitude = "Mercury first latitude"
    velocity_epicycle_component = "Mercury velocity epicycle component"
    second_latitude = "Mercury second latitude"
    latitude_double_argument = "Mercury latitude double argument"
    variable_hypothenuse = "variable hypothenuse Mercury"
    equation_minuta_proportionalia = "Mercury equation minuta proportionalia"
    true_position_double_argument = "true position double argument Mercury"
    equation_anomaly_min_distance = "equation Mercury anomaly at minimum distance"
    equation_anomaly_max_distance = "equation Mercury anomaly at maximum distance"
    velocity_eccentricity_component = "Mercury velocity eccentricity component"


class Venus(TableType):
    @classmethod
    def astro_id(cls):
        return 3

    equation_anomaly_max_distance = "equation Venus anomaly at maximum distance"
    latitude_inclination = "Venus latitude inclination"
    second_latitude = "Venus second latitude"
    first_latitude = "Venus first latitude"
    velocity_double_argument = "Venus velocity double argument"
    velocity_eccentricity_component = "Venus velocity eccentricity component"
    true_position_double_argument = "true position double argument Venus"
    equation_minuta_proportionalia = "Venus equation minuta proportionalia"
    variable_hypothenuse = "variable hypothenuse Venus"
    equation_anomaly_min_distance = "equation Venus anomaly at minimum distance"
    latitude_slant = "Venus latitude slant"
    latitude_deviation = "Venus latitude deviation"
    mm_anomaly = "mean motion anomaly Venus"
    total_equation_double_argument = "total equation double-argument table Venus"
    equation_anomaly_mean_distance = "equation Venus anomaly at mean distance"
    equation_center = "equation Venus center"
    latitude_double_argument = "Venus latitude double argument"
    velocity_epicycle_component = "Venus velocity epicycle component"
    planetary_stations = "planetary stations Venus"


class Moon(TableType):
    @classmethod
    def astro_id(cls):
        return 4

    lunar_velocities = "lunar velocities"
    equation_minuta_proportionalia = "Moon equation minuta proportionalia"
    lunar_latitude = "lunar latitude"
    equation_variation_diameter = "Moon equation variation of diameter"
    mean_argument_latitude = "Moon mean argument of latitude"
    mm_double_elongation = "mean motion double elongation"
    mm_lunar_longitude = "mean motion lunar longitude"
    mm_lunar_anomaly = "mean motion lunar anomaly"
    mm_lunar_node = "mean motion lunar node"
    equation_center = "equation Moon center"
    mm_longitude_plus_lunar_node = "mean motion longitude plus lunar node"
    equation_anomaly = "equation Moon anomaly"
    mm_lunar_elongation = "mean motion lunar elongation"


class Mars(TableType):
    @classmethod
    def astro_id(cls):
        return 5

    second_latitude = "Mars second latitude"
    southern_latitude = "Mars southern latitude"
    northern_latitude = "Mars northern latitude"
    first_latitude = "Mars first latitude"
    velocity_epicycle_component = "Mars velocity epicycle component"
    velocity_eccentricity_component = "Mars velocity eccentricity component"
    true_position_double_argument = "true position double argument Mars"
    equation_minuta_proportionalia = "Mars equation minuta proportionalia"
    variable_hypothenuse = "variable hypothenuse Mars"
    velocity_double_argument = "Mars velocity double argument"
    latitude_double_argument = "Mars latitude double argument"
    planetary_stations = "planetary stations Mars"
    total_equation_double_argument = "total equation double-argument table Mars"
    equation_anomaly_mean_distance = "equation Mars anomaly at mean distance"
    equation_center = "equation Mars center"
    equation_anomaly_max_distance = "equation Mars anomaly at maximum distance"
    equation_anomaly_min_distance = "equation Mars anomaly at minimum distance"
    mm_longitude = "mean motion longitude Mars"


class Jupiter(TableType):
    @classmethod
    def astro_id(cls):
        return 6

    equation_center = "equation Jupiter center"
    mm_longitude = "mean motion longitude Jupiter"
    southern_latitude = "Jupiter southern latitude"
    second_latitude = "Jupiter second latitude"
    first_latitude = "Jupiter first latitude"
    equation_anomaly_mean_distance = "equation Jupiter anomaly at mean distance"
    latitude_double_argument = "Jupiter latitude double argument"
    variable_hypothenuse = "variable hypothenuse Jupiter"
    velocity_double_argument = "Jupiter velocity double argument"
    velocity_epicycle_component = "Jupiter velocity epicycle component"
    equation_minuta_proportionalia = "Jupiter equation minuta proportionalia"
    true_position_double_argument = "true position double argument Jupiter"
    velocity_eccentricity_component = "Jupiter velocity eccentricity component"
    total_equation_double_argument = "total equation double-argument table Jupiter"
    planetary_stations = "planetary stations Jupiter"
    northern_latitude = "Jupiter northern latitude"
    equation_anomaly_min_distance = "equation Jupiter anomaly at minimum distance"
    equation_anomaly_max_distance = "equation Jupiter anomaly at maximum distance"


class Saturn(TableType):
    @classmethod
    def astro_id(cls):
        return 7

    equation_anomaly_mean_distance = "equation Saturn anomaly at mean distance"
    first_latitude = "Saturn first latitude"
    equation_center = "equation Saturn center"
    equation_anomaly_max_distance = "equation Saturn anomaly at maximum distance"
    mm_longitude = "mean motion longitude Saturn"
    equation_anomaly_min_distance = "equation Saturn anomaly at minimum distance"
    velocity_double_argument = "Saturn velocity double argument"
    variable_hypothenuse = "variable hypothenuse Saturn"
    equation_minuta_proportionalia = "Saturn equation minuta proportionalia"
    true_position_double_argument = "true position double argument Saturn"
    velocity_eccentricity_component = "Saturn velocity eccentricity component"
    second_latitude = "Saturn second latitude"
    velocity_epicycle_component = "Saturn velocity epicycle component"
    total_equation_double_argument = "total equation double-argument table Saturn"
    planetary_stations = "planetary stations Saturn"
    latitude_double_argument = "Saturn latitude double argument"
    southern_latitude = "Saturn southern latitude"
    northern_latitude = "Saturn northern latitude"


class Spherical(TableType):
    @classmethod
    def astro_id(cls):
        return 8

    tangent = "tangent"
    projection_rays = "projection of rays"
    solar_altitude_from_time_day = "solar altitude from the time of day"
    time_day_from_solar_altitude = "time of day from solar altitude"
    houses = "houses"
    meridian_altitude_sun = "meridian altitude of the Sun"
    proportions = "proportion tables"
    right_ascension = "right ascension"
    oblique_ascension = "oblique ascension"
    ascensional_difference = "ascensional difference"
    length_diurnal_seasonal_hour = "length of diurnal seasonal hour"
    length_daylight = "length of daylight"
    declination = "declination"


class EighthSphere(TableType):
    @classmethod
    def astro_id(cls):
        return 9

    equation_access_and_recess = "equation access and recess"
    trepidation = "trepidation"
    mm_access_and_recess = "mean motion access and recess"
    mm_apogees_and_stars_precessions = "mean motion apogees and stars/precessions"
    mm_solar_apogee = "mean motion solar apogee"


class Eclipse(TableType):
    @classmethod
    def astro_id(cls):
        return 10

    eclipsed_part_solar_disk = "eclipsed part of the solar disk"
    eclipsed_part_lunar_disk = "eclipsed part of the lunar disk"
    eclipse_interpolation = "eclipse interpolation table"
    immersion_eclipse_nearest_distance = "immersion of eclipse at nearest distance"
    digit_solar_eclipse_nearest_distance = "digit of solar eclipse at nearest distance"
    immersion_solar_eclipse_greatest_distance = (
        "immersion of solar eclipse at greatest distance"
    )
    digit_solar_eclipse_greatest_distance = (
        "digit of solar eclipse at greatest distance"
    )
    half_totality_lunar_eclipse_nearest_distance = (
        "half-totality of lunar eclipse at nearest distance"
    )
    immersion_lunar_eclipse_nearest_distance = (
        "immersion of lunar eclipse at nearest distance"
    )
    inclination_begining_solar_eclipse = "inclination at the begining of solar eclipse"
    inclination_end_solar_eclipse = "inclination at the end of solar eclipse"
    inclination_obliquity_component = "inclination obliquity component"
    inclination_local_latitude_component = "inclination local latitude component"
    lunar_eclipse_half_totality = "lunar eclipse half totality table"
    lunar_eclipse_half_duration = "lunar eclipse half duration table"
    solar_eclipse_half_duration = "solar eclipse half duration table"
    inclination_end_lunar_eclipse = "inclination at the end of lunar eclipse"
    inclination_end_totality_lunar_eclipse = (
        "inclination at the end of totality for a lunar eclipse"
    )
    inclination_begining_totality_lunar_eclipse = (
        "inclination at the begining of totality for a lunar eclipse"
    )
    inclination_begining_lunar_eclipse = "inclination at the begining of lunar eclipse"
    digit_lunar_eclipse_nearest_distance = "digit of lunar eclipse at nearest distance"
    half_totality_lunar_eclipse_greatest_distance = (
        "half-totality of lunar eclipse at greatest distance"
    )
    mm_syzygies = "mean motion syzygies"
    parallax_longitude_component = "parallax longitude component"
    parallax_latitude_component = "parallax latitude component"
    moon_prlx_syzygy_true_anomaly_0deg = (
        "Moon parallax at syzygy and true anomaly at 0°"
    )
    moon_prlx_syzygy_true_anomaly_180deg = (
        "Moon parallax at syzygy and true anomaly at 180°"
    )
    moon_prlx_quadrature_true_anomaly_0deg = (
        "Moon parallax at quadrature and true anomaly at 0°"
    )
    moon_prlx_quadrature_true_anomaly_180deg = (
        "Moon parallax at quadrature and true anomaly at 180°"
    )
    moon_prlx_interpolation_syzygy = "Moon parallax interpolation at syzygy"
    moon_prlx_interpolation_quadrature = "Moon parallax interpolation at quadrature"
    immersion_lunar_eclipse_greatest_distance = (
        "immersion of lunar eclipse at greatest distance"
    )
    digit_lunar_eclipse_greatest_distance = (
        "digit of lunar eclipse at greatest distance"
    )
    variation_shadow = "variation of shadow"
    radius_shadow = "radius of the shadow"
    radius_moon = "radius of the Moon"
    radius_sun = "radius of the Sun"
    moon_prlx_interpolation_syzygy_and_quadrature = (
        "Moon parallax interpolation between syzygy and quadrature"
    )


class Trigonometrical(TableType):
    @classmethod
    def astro_id(cls):
        return 11

    cosine = "cosine"
    sine = "sine"
    shadow = "shadow"
    chords = "chords"
