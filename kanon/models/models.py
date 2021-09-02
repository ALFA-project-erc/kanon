import math as m

from . import utils
from .meta import dmodel
from .table_types import (
    Jupiter,
    Mars,
    Mercury,
    Moon,
    Spherical,
    Sun,
    Trigonometrical,
    Venus,
)
from .utils import DEG, RAD

# # # # # # # # # # #
#        SUN        #
# # # # # # # # # # #


@dmodel(Sun.equation_sun, 23, 50)
def sun_equation(x: float, e: float) -> float:
    """
    Sun equation
    :param x:
    :param: solar eccentricity
    :return:
    """
    return DEG * m.atan(utils.product_sine_0(x, e) / (60 + e * m.cos(x * RAD)))


@dmodel(Sun.mm_solar_tropical_longitude, 34, 34)
def sun_tropical_longitude(x, val):
    """
    Longitude of the  tropical mean sun
    :param x: value in day
    :param val: value for 1 day
    :return:
    """
    return val * x


# JC VERSION
@dmodel(Sun.equation_time, 51, 25, 26, 27, 28, 29)
def sun_equation_time_true(x, obl, e, ap, epo, hdeg):
    """
    Equation of times for true sun
    :param x: true longitude of the sun in degree
    :param obl: obliquity of the ecliptic in degree
    :param e: solar eccentricity
    :param ap: solar apogee longitude in degree
    :param epo: epoch constant in degree
    :param hdeg: hour conversion rate, deg->h
    :return:
    """

    q = -DEG * m.asin(e * m.sin(RAD * (x - ap)) / 60)

    return hdeg * (x - q - utils.right_asc_0(x, obl) + epo)


# JC VERSION
@dmodel(Sun.equation_time, 52, 25, 26, 27, 28, 29)
def sun_equation_time_mean(x, obl, e, ap, epo, hdeg):
    """
    Equation of times for mean sun
    :param x: mean longitude in degree
    :param obl: obliquity of the ecliptic
    :param e: solar eccentricity
    :param ap: solar apogee longitude
    :param epo: epoch constant
    :param hdeg: hour conversion rate: deg ->h
    :return: equation of time in hour
    """
    q = utils.q_0(x - ap, e)

    return hdeg * (x + epo - utils.right_asc_0(x + q, obl))


# # # # # # # # # # #
#      MERCURY      #
# # # # # # # # # # #


@dmodel(Mercury.equation_anomaly_mean_distance, 32, 104)
def mercury_anomaly_mean_distance(x, R):
    """
    Equation of anomaly Mercury at mean distance
    :param x: true argument in degree
    :param R: radius of the epicycle
    :return: mercury anomalie equation in degree
    """
    return utils.planet_anomaly_0(x, R, 60)


# JC VERSION
@dmodel(Mercury.equation_center, 36, 101)
def mercury_center(x, e):
    """
    Equation of center of Mercury
    :param x: mean centre in degree
    :param e: excenticity
    :return:  centre equation in degree (negative on [0,180º])
    """
    s = m.sqrt(60 ** 2 - (e * (m.sin(x * RAD) + m.sin(2 * x * RAD))) ** 2) + e * (
        m.cos(x * RAD) + m.cos(2 * x * RAD)
    )

    return -DEG * m.atan(utils.product_sine_0(x, e) / (s + e * m.cos(x * RAD)))


# JC VERSION
@dmodel(Mercury.total_equation_double_argument, 53, 124, 125)
def mercury_double_equation(x, y, e, R):
    """
    Planet double argument mercury
    :param x: mean center in degree
    :param y: true argument in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """

    s = utils.s_m_0(x, e)
    rh = utils.rho_0(x, s, e)

    p = utils.planet_anomaly_0(y, R, rh)
    q = utils.q_1(x, e)

    return q + p


# JC FUNCTION
@dmodel(Mercury.equation_anomaly_max_distance, 39, 106, 107)
def mercury_anomaly_max(x, e, R):
    """
    Equation of anomaly Mercury at great distance
    :param x:
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """
    return utils.planet_anomaly_0(x, R, 60 + 3 * e)


# JC FUNCTION
@dmodel(Mercury.equation_anomaly_mean_distance, 33, 104)
def mercury_anomaly_mean(x, R):
    """
    Equation of anomaly Mercury at mean distance
    :param x:
    :param R: radius of the epicycle
    :return:
    """
    return utils.planet_anomaly_0(x, R, 60)


# JC FUNCTION
@dmodel(Mercury.equation_anomaly_min_distance, 40, 109, 110)
def mercury_anomaly_min(x, e, R):
    """
    Equation of anomaly Mercury at near distance
    :param x:
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """
    rho = m.sqrt(60 ** 2 - 180 * e + 3 * e ** 2)
    return utils.planet_anomaly_0(x, R, rho)


@dmodel(Mercury.equation_minuta_proportionalia, 63, 221, 488)
def mercury_minuta_proportionalia(x, y, e, R):
    """
    proportional minutes giving the approximate value of the equation of anomaly
    p(av,cm)in the Mercury case
    :param x: true argument in degree
    :param y: mean center in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """

    p0 = utils.planet_anomaly_0(x, R, 60)
    p1 = utils.planet_anomaly_0(x, R, 60 + 3 * e)
    p2 = utils.planet_anomaly_0(x, R, utils.rho_2(120, e))
    maxp0 = utils.max_equat_anomaly_0(R, 60)
    maxp1 = utils.max_equat_anomaly_0(R, 60 + 3 * e)
    maxp2 = utils.max_equat_anomaly_0(R, utils.rho_2(120, e))
    maxp = utils.max_equat_anomaly_0(R, utils.rho_2(y, e))
    f1 = (maxp - maxp0) / (maxp0 - maxp1)
    f2 = (maxp - maxp0) / (maxp2 - maxp0)
    cm0 = utils.mean_pos_epic_center_1(e)
    cm = y
    if y > 180:
        cm = 360 - y
    if 0 <= cm <= cm0:
        p = p0 + (p0 - p1) * f1
    else:
        p = p0 + (p2 - p0) * f2
    return p


@dmodel(Mercury.planetary_stations, 64, 182, 183, 184, 185)
def mercury_planetary_stations(x, s0, s1, s2, e):
    """
    First stationary point of Mercury by proportional minutes
    :param x: mean centre in degree (0<=x<360)
    :param s0: first station true argument at the apogee in degree (cm=0)
    :param s1: first station true argument at the mean position in degree (cm=cm0)
    :param s2: first station true argument at the perigee in degree(cm=120)
    :param e: planetary eccentricity
    :return: true argument of the mercury first station in degree according x
    """
    cm0 = utils.mean_pos_epic_center_1(e)
    cm = x
    if (180 < x) and (x < 360):
        cm = 360 - x
    R0 = utils.rho_2(0, e)
    R1 = utils.rho_2(cm0, e)
    R2 = utils.rho_2(120, e)
    R = utils.rho_2(cm, e)
    if 0 <= cm <= cm0:
        s = s0 + (s1 - s0) * (R - R0) / (R1 - R0)
    else:
        s = s1 + (s2 - s1) * (R - R1) / (R2 - R1)
    return s


@dmodel(Mercury.planetary_stations, 65, 185, 186, 187)
def mercury_planetary_stations_0(x, e, R, vq):
    """
    First stationary point of Mercury by calculation and proportional minutes
    :param x: mean centre in degree (0<=x<360)
    :param e: planetary eccentricity
    :param R: planetary epicycle radius
    :param vq: velocity quotient
    :return:true argument of the mercury first station in degree
    """

    s0 = utils.first_stationary_point_mercury_0(0, vq, R, e)
    cm0 = utils.mean_pos_epic_center_1(e)
    s1 = utils.first_stationary_point_mercury_0(cm0, vq, R, e)
    s2 = utils.first_stationary_point_mercury_0(120, vq, R, e)
    R0 = utils.rho_2(0, e)
    R1 = utils.rho_2(cm0, e)
    R2 = utils.rho_2(120, e)
    cm = x
    R = utils.rho_2(cm, e)
    if (180 < x) and (x < 360):
        cm = 360 - x
    if 0 <= cm <= cm0:
        s = s0 + (s1 - s0) * (R - R0) / (R1 - R0)
    else:
        s = s1 + (s2 - s1) * (R - R1) / (R2 - R1)
    return s


# # # # # # # # # # #
#       VENUS       #
# # # # # # # # # # #


@dmodel(Venus.latitude_inclination, 54, 288)
def venus_latitude_inclination(x, im):
    """
    component Venus latitude due to inclination
    :param x: nodal argument of latitude = angle between ascending node and epicycle center in degree
    :param im: maximum inclination of the deferent on the ecliptic in degree
    :return: inclination in degree
    """

    return utils.lat_inf_incl_0(x, im)


@dmodel(Venus.latitude_deviation, 55, 296, 298)
def venus_latitude_deviation(x, R, jm):
    """
    component Venus latitude due to  deviation at latitude nodal argument=0
    :param x: true argument in degree
    :param R: radius of the epicycle
    :param jm: maximum deviation of the epicycle
    :return: latitude deviation at latitude nodal argument = 0
    """
    return utils.lat_inf_devia_asc_node_0(x, jm, R)


@dmodel(Venus.latitude_slant, 56, 291, 293, 294)
def venus_latitude_slant_calc(x, R, b3m, pm):
    """
    Venus latitude slant approximated due to the slant of the epicycle at the deferent apogee
    and according ptolemy CALCULATIONS
    :param x: true argument in degree
    :param R: radius of the epicycle
    :param b3m: maximum slant of the epicycle in degree
    :param pm: maximum value of equation of argument p(av, cm) in degree
    :return: slant at the deferene apogee(top) in degree
    """

    return utils.lat_inf_slant_apo_def_0(x, b3m, pm, R)


@dmodel(Venus.latitude_slant, 57, 291, 292, 293)
def venus_latitude_slant_theory(x, R, e, b3m):
    """
    Venus latitude slant geometric due to the slant of the epicycle at the deferent apogee
    and according to the Ptolemy THEORY
    :param x: true argument in degree
    :param R: radius of the epicycle
    :param e: excenticity
    :param b3m: maximum deviation of the epicycle
    :return: venus latitude slant in degree
    """

    return utils.lat_inf_slant_apo_def_1(x, R, 60 + b3m, e)


# JC FUNCTION
@dmodel(Venus.latitude_double_argument, 58, 301, 303, 304, 305, 306)
def venus_latitude_double(x, y, R, im, jm, b3m, pm):
    """
    Venus total latitude double argument
    :param x: true argument in degree
    :param y: nodal argument of latitude=angle between ascending node amd epicycle centre
    :param R: radius of the epicycle
    :param im: inclination of the deferent on the ecliptic in degree
    :param jm: maximum deviation on the epicycle in degree
    :param b3m: maximum latitude due to the slant of the epicycle in degree
    :param pm: maximum value of the equation of the argument
    :return:
    """
    beta_1 = utils.lat_inf_incl_0(y, im)
    beta_2 = utils.lat_inf_devia_asc_node_0(x, jm, R)
    beta_3 = utils.lat_inf_slant_apo_def_0(x, b3m, pm, R)

    return beta_1 + m.sin(RAD * (y + 90)) * beta_2 + m.sin(RAD * y) * beta_3


@dmodel(Venus.equation_center, 29, 90)
def venus_center(x, e):
    """
    Venus center equation
    :param x: mean center in degree
    :param e: excenticity
    :return: center equation in degree
    """
    return utils.q_2(x, e)


@dmodel(Venus.equation_anomaly_max_distance, 59, 95, 96)
def venus_anomaly_max(x, e, R):
    """
    Venus equation anomaly at the maximum distance
    :param x: true argument in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return: equation anomaly in degree:p0(av)=p(av,0º)
    """
    return utils.planet_anomaly_0(x, R, 60 + e)


@dmodel(Venus.equation_anomaly_mean_distance, 60, 93)
def venus_anomaly_mean(x, R):
    """
    Venus equation anomaly at mean distance rho(cm)=60
    :param x: true argument in degree
    :param R: radius of the epicycle
    :return: equation anomaly in degree p(av, cm0)=p0(av)
    """

    return utils.planet_anomaly_0(x, R, 60)


@dmodel(Venus.equation_anomaly_min_distance, 61, 98, 99)
def venus_anomaly_min(x, e, R):
    """
    Venus equation anomaly at minimum distance, rho=60-e
    :param x: true argument in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return: equation anomaly in degree, p2(av)=p(av,180º)
    """
    return utils.planet_anomaly_0(x, R, 60 - e)


@dmodel(Venus.equation_minuta_proportionalia, 62, 266, 489)
def venus_minuta_proportionalia(x, y, e, R):
    """
    Venus equation proportional minute
    :param x: true argument (av) in degree
    :param y: mean center (cm) in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return: minutes proportional in degree
    """

    return utils.minuta_proportionalia(x, R, e, y)


@dmodel(Venus.planetary_stations, 71, 176, 177, 178, 179)
def venus_planetary_stations(x, s0, s1, s2, e):
    """
    First stationary point of Venus by proportional minutes
    :param x: mean center in degree
    :param s0: first station true argument  at apogee  (cm=0) in degree
    :param s1: first station true argument at mean position (cm=cm0) in degree
    :param s2: first station true argument at perigee (cm=180)
    :param e: planetary eccentricity
    :return:
    """
    return utils.first_stationary_point_proport_minutes_0(x, e, s0, s1, s2)


@dmodel(Venus.planetary_stations, 72, 179, 180, 181)
def venus_planetary_stations_0(x, e, R, vq):
    """
    First stationary point of Venus by calculation and proportional minutes
    :param x: mean center in degree
    :param e: planetary eccentricity
    :param R: planetary epicycle radius
    :param vq: velocity quotient
    :return: true argument of the venus first statin in degree
    """
    s0 = utils.first_stationary_point_all_planet_except_mercury_0(0, vq, R, e)
    cm0 = utils.mean_pos_epic_center_0(e)
    s1 = utils.first_stationary_point_all_planet_except_mercury_0(cm0, vq, R, e)
    s2 = utils.first_stationary_point_all_planet_except_mercury_0(180, vq, R, e)
    return utils.first_stationary_point_proport_minutes_0(x, e, s0, s1, s2)


# # # # # # # # # # #
#        MOON       #
# # # # # # # # # # #


# JC VERSION
@dmodel(Moon.equation_anomaly, 41, 54, 55)
def moon_anomaly(x, y, e, R):
    """
    Moon anomaly equation : general formula
    :param x: true argument in degree
    :param y: center or double elongation
    :param e: lunar eccentricity
    :param R: lunar epicycle radius
    :return:
    """

    rho = utils.product_cosine_0(y, e) + m.sqrt(
        60 ** 2 - (utils.product_sine_0(y, e)) ** 2
    )
    return -utils.planet_anomaly_0(x, R, rho)


# JC VERSION
@dmodel(Moon.equation_center, 43, 52)
def moon_center(x, e):
    """
    Moon center equation
    :param x: center or double elongation
    :param e: lunar eccentricity
    :return: moon center equation in degree
    """
    rho = utils.product_cosine_0(x, e) + m.sqrt(
        60 ** 2 - (utils.product_sine_0(x, e)) ** 2
    )
    return utils.planet_anomaly_0(x, e, rho)


@dmodel(Moon.lunar_latitude, 46, 132)
def moon_latitude(x, imax):
    """
    Latitude of the Moon
    :param x: argument of latitude in degree
    :param imax: maximum value
    :return: latitude of the moon in degree
    """

    return DEG * m.asin(m.sin(x * RAD) * m.sin(imax * RAD))


# # # # # # # # # # #
#        MARS       #
# # # # # # # # # # #


@dmodel(Mars.equation_center, 30, 79)
def mars_center(x, e):
    """
    Mars center equation
    :param x:
    :param e: excenticity
    :return:
    """

    return utils.q_2(x, e)


@dmodel(Mars.equation_anomaly_max_distance, 66, 84, 85)
def mars_anomaly_max(x, e, R):
    """
    Mars equation anomaly at maximum distance
    :param x: true argument in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """
    return utils.planet_anomaly_0(x, R, 60 + e)


@dmodel(Mars.equation_anomaly_mean_distance, 68, 82)
def mars_anomaly_mean(x, R):
    """
    Mars equation anomaly at mean distance
    :param x: true argument in degree
    :param R: radius of the epicycle
    :return: equation in degree
    """
    return utils.planet_anomaly_0(x, R, 60)


@dmodel(Mars.equation_anomaly_min_distance, 69, 87, 88)
def mars_anomaly_min(x, e, R):
    """
    Mars equation anomaly at minimum distance
    :param x: true argument in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return: equation in degree
    """

    return utils.planet_anomaly_0(x, R, 60 - e)


@dmodel(Mars.equation_minuta_proportionalia, 70, 311, 490)
def mars_minuta_proportionalia(x, y, e, R):
    """
    Mars equation proportional minutes
    :param x: true argument in degree
    :param y: mean center in degree
    :param e: excenticity
    :param R: radius of the epicycle
    :return:
    """

    return utils.minuta_proportionalia(x, R, e, y)


# # # # # # # # # # #
#      JUPITER      #
# # # # # # # # # # #


@dmodel(Jupiter.equation_center, 35, 68)
def jupiter_center(x, e):
    """
    Jupiter center equation
    :param x:
    :param e: excenticity
    :return:
    """
    return utils.q_2(x, e)


# # # # # # # # # # #
#       SATURN      #
# # # # # # # # # # #


# # # # # # # # # # #
# SPHERICAL ASTRONO #
# # # # # # # # # # #


@dmodel(Spherical.meridian_altitude_sun, 28, 201, 202)
def meridian_altitude_sun(x: float, eps: float, phi: float) -> float:
    """
    Meridian altitude of the sun
    :param x:
    :param eps:
    :param phi:
    :return:
    """

    return 90 - phi + DEG * m.asin(m.sin(x * RAD) * m.sin(eps * RAD))


@dmodel(Spherical.declination, 24, 3)
def declination_sun(x: float, obl: float) -> float:
    """
    declination of the sun
    :param x: longitude of sun in degree
    :param obl: obliquity of the ecliptic in degree
    :return:
    """
    return utils.declin_0(x, obl)


# JC VERSION
@dmodel(Spherical.ascensional_difference, 31, 19, 20)
def ascensional_difference(x, eps, phi):
    """
    Ascenscional differences of a point on ecliptic
    :param x: longitude of this point in degree
    :param eps: inclination of ecliptic in degree
    :param phi: latitude of the observer in degree
    :return: ascensional difference in degree
    """

    return DEG * m.asin(m.tan(utils.declin_0(x, eps) * RAD) * m.tan(phi * RAD))


# JC VERSION
@dmodel(Spherical.right_ascension, 48, 8)
def right_ascension(x, obl):
    """
    Right ascension
    :param x: longitude in degree
    :param obl: obliquity of the ecliptic
    :return: right ascension in degree
    """
    return utils.right_asc_0(x, obl)


# JC VERSION
@dmodel(Spherical.oblique_ascension, 49, 12, 13, 14)
def oblique_ascension(x, oblra, oblad, phi):
    """
    Oblique ascension
    :param x:
    :param oblra: obliquity of the ecliptic (ra)
    :param oblad: obliquity of the ecliptic (ad)
    :param phi: geographical latitude
    :return:oblique ascension in degree
    """

    return utils.oblique_asc_0(x, oblra, oblad, phi)


# JC VERSION
@dmodel(Spherical.length_daylight, 50, 193, 194, 195)
def length_daylight(x, oblra, oblad, phi):
    """
    Length of daylight
    :param x: longitude in degree
    :param oblra: obliquity of the ecliptic (ra) in degree
    :param oblad: obliquity of the ecliptic (ad) in degree
    :param phi: geographical latitude in degree
    :return: Length of the day in DEGREE, divise by 15 to have the result in equinoctial hours
    """
    return utils.oblique_asc_0(x + 180, oblra, oblad, phi) - utils.oblique_asc_0(
        x, oblra, oblad, phi
    )


# # # # # # # # # # #
#   EIGHTH SPHERE   #
# # # # # # # # # # #


# # # # # # # # # # #
#      ECLIPSE      #
# # # # # # # # # # #


# # # # # # # # # # #
#  TRIGONOMETRICAL  #
# # # # # # # # # # #


@dmodel(Trigonometrical.sine, 26, 2)
def sine_product(x: float, R=160) -> float:
    """
    Model for product sinus
    :param x: first argument of sine
    :param R: radius of the circle
    :return: a float
    """
    return utils.product_sine_0(x, R)
