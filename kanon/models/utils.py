import math as m

RAD = m.pi / 180
DEG = 1 / RAD


# # # # # # # # # # # #
#       PLANETS       #
# # # # # # # # # # # #


def planet_anomaly_0(x, R, rho):
    """
    anomaly of the planet or argument equation
    :param x: true argument in degree
    :param R: radius of epicycle
    :param rho distance between earth and epicycle center
    :return anomaly in degree
    """
    return DEG * m.atan(product_sine_0(x, R) / (rho + product_cosine_0(x, R)))


def q_2(x, e):
    """
    Planet center equation except Mercury,
     the function is preceded by a minus sign to agree with Pedersen
    :param x: mean center in degree
    :param e: eccentricity
    :return  center equation in degree
    """
    return -DEG * m.atan(
        2
        * product_sine_0(x, e)
        / (m.sqrt(60 ** 2 - (product_sine_0(x, e)) ** 2) + e * m.cos(x * RAD))
    )


# # # # # # # # # # # #
#      INFERIOR       #
#       PLANETS       #
# # # # # # # # # # # #


# JC FUNCTION
def lat_inf_slant_apo_def_0(x, b3m, pm, R):
    """
    inferior planet latitude at the deferent apogee owing to the
    slant of the epicycle but according
    with Ptolemy CALCULATION
    :param x: true argument in degree
    :param b3m: max of slant latitude  in degree
    :param pm: max of p(0º, av) in degree
    :param R: radius of the epicycle
    :return : part of the latitude  at the deferent apogee in degree
    """
    return planet_anomaly_0(x, R, 60) * b3m / pm


def lat_inf_slant_apo_def_1(x, km, rho, R):
    """
    inferior planet latitude at the deferent apogee owing to the slant of
    the epicycle but according
    with Ptolemy THEORY
    :param x: true argument in degree
    :param km: max of slant  in degree
    :param rho: distance earth-epicycle centre
    :param R: radius of the epicycle
    :return : part of the latitude  at the deferent apogee in degree
    """

    return DEG * m.asin(R * m.sin(RAD * km) * m.sin(RAD * x) / D_1(rho, x, R))


# JC FUNCTION
def lat_inf_devia_asc_node_0(av, jm, R):
    """
    inferior planet latitude at the ascending node owing to the
    deviation of the epicycle
    :param av: true argument in degree
    :jm: deviation max in degree
    :R: radius of the epicycle
    :return: part of the latitude at the ascending node in degree
    """

    return DEG * m.asin(R * m.sin(RAD * jm) * m.cos(RAD * av) / D_0(av, jm, R))


# JC FUNCTION
def lat_inf_incl_0(x, im):
    """
    part of inferior planets latitude owing
    to the inclination of the deferent
    :param x: nodal argument of latitude = angle between ascending node and \
        epicycle center
    :im: inclination max in degree
    """
    return im * (m.sin(RAD * x)) ** 2


def minuta_proportionalia(x, R, e, cm):
    p0 = planet_anomaly_0(x, R, 60)
    p1 = planet_anomaly_0(x, R, 60 + e)
    p2 = planet_anomaly_0(x, R, 60 - e)
    maxp0 = max_equat_anomaly_0(R, 60)
    maxp1 = max_equat_anomaly_0(R, 60 + e)
    maxp2 = max_equat_anomaly_0(R, 60 - e)
    maxp = max_equat_anomaly_0(R, rho_1(cm, e))
    f1 = (maxp - maxp0) / (maxp1 - maxp0)
    f2 = (maxp - maxp0) / (maxp2 - maxp0)
    cm0 = mean_pos_epic_center_0(e)
    if cm > 180:
        cm = 360 - cm
    if 0 <= cm <= cm0:
        p = p0 - (p0 - p1) * f1
    else:
        p = p0 + (p2 - p0) * f2
    return p


# # # # # # # # # # # #
#      SUPERIOR       #
#       PLANETS       #
# # # # # # # # # # # #


# # # # # # # # # # # #
#      LATITUDE       #
#      LONGITUDE      #
# # # # # # # # # # # #

# # # # # # # # # # # #
#      SPHERICAL      #
#     ASTRONOMICAL    #
# # # # # # # # # # # #


def declin_0(x, obl):
    """
    declination of a point of ecliptic
    :param x: longitude of the point in degree
    :param obl: obliquity of the ecliptic in degree
    return declination in degree
    """
    return DEG * m.asin(m.sin(x * RAD) * m.sin(obl * RAD))


def right_asc_0(x, obl):
    """
    Right ascension of a point on ecliptic
    :param x: longitude in degree
    :param eps: inclination of ecliptic in degree
    :param inc: obliquity of the ecliptic
    return right ascension in degree
    define a continue function for x real.
    """
    n = m.floor(x / 180 + 1 / 2)
    ra = 0.0
    if x - (n - 1 / 2) * 180 > 0:
        ra = DEG * m.atan(m.cos(obl * RAD) * m.tan(x * RAD)) + n * 180

    if x == (n - 1 / 2) * 180:
        ra = (n - 1 / 2) * 180

    return ra


def oblique_asc_0(x, oblra, oblad, phi):
    """
    oblique ascension
    :param x: longitude in degree
    :param oblra: obliquity right ascension of the ecliptic in degree
    :param oblad: obliquity ascensional difference of the ecliptic in degree
    :param phi: latitude of observer in degree
    :return: oblique ascension in degree
    """
    return right_asc_0(x, oblra) - DEG * m.asin(
        m.tan(RAD * declin_0(x, oblad)) * m.tan(RAD * phi)
    )


# # # # # # # # # # # #
#         SUN         #
# # # # # # # # # # # #


# # # # # # # # # # # #
#   TRIGONOMETRICAL   #
# # # # # # # # # # # #


def product_sine_0(x, R):
    """
    :param x: angle in degree
    :param R: radius/eccentricity
    """
    return R * m.sin(x * RAD)


def product_cosine_0(x, R):
    """
    :param x: angle in degree
    :param R: factor
    """
    return R * m.cos(x * RAD)


def sin_double(x, y, param_0):
    """
    Sine with double argument
    :param x:
    :param y:
    :param param_0:
    :return:
    """
    return m.sin(RAD * x) * m.sin(RAD * y) * m.sin(RAD * param_0)


def chords_equation_0(x, param_0):
    """
    Chords equation
    :param x:
    :param param_0:
    :return:
    """
    R = param_0
    return 2 * R * m.sin(x * RAD / 2)


def shadow_equation_0(x, param_0):
    """
    Shadow table
    :param x:
    :param param_0:
    :return:
    """
    c = param_0
    return c / m.tan(x * RAD)


# # # # # # # # # # #
#      OTHERS       #
# # # # # # # # # # #


def D_0(av, jm, R):
    """
    Distance from earth to the inferior planet in relation to deviation in latitude
    :param av: true argument in degree
    :param jm: max deviation in degree
    :param R: radius of the epicycle
    """
    return m.sqrt(60 ** 2 + 120 * R * m.cos(RAD * jm) * m.cos(RAD * av) + R ** 2)


def D_1(rho, av, R):
    """
    Distance from earth to the inferior planet in relation to slant in latitude
    :param av: true argument in degree
    :param rho: distance earth-epicycle center
    :param R: radius of the epicycle
    """
    return m.sqrt(rho ** 2 + 2 * rho * R * m.cos(RAD * av) + R ** 2)


def q_0(x, e):
    """
    equation center of the sun  according to Pedersen
    x in degree, return in degree
    """
    return -DEG * m.atan(e * m.sin(RAD * x) / (60 + e * m.cos(RAD * x)))


def rho_0(cm, s, e):
    """
    Alkashi formula  with supplementary angle
    distance Earth-Epicycle centre  for mercury
    cm in degree
    """
    return m.sqrt(s ** 2 + e ** 2 + 2 * e * s * m.cos(RAD * cm))


def rho_1(cm, e):
    """
    distance earth-Epicycle center for venus and planet sup
    cm: mean center in degree
    e:eccentricity
    return: distance
    """
    base = m.sqrt(60 ** 2 - (e * m.sin(RAD * cm)) ** 2) + e * m.cos(RAD * cm)
    return m.sqrt(base ** 2 + (2 * e * m.sin(RAD * cm)) ** 2)


def rho_2(cm, e):
    """
    distance earth-Epicycle center for mercury
    cm: mean center in degree
    e:eccentricity
    return: distance
    """
    return rho_0(cm, s_m_0(cm, e), e)


def s_m_0(cm, e):
    """
    s fonction of mercury, distance equant-epicycle centre
    cm mean centre in degree
    e eccentricity
    """
    s1 = m.sqrt(60 ** 2 - e ** 2 * (m.sin(RAD * cm) + m.sin(RAD * 2 * cm)) ** 2)
    return s1 + e * (m.cos(RAD * cm) + m.cos(RAD * 2 * cm))


def mean_pos_epic_center_0(e):
    """
    mean center of the mean position of the epicycle center
    except Mercury, solution of the equation: rho(cm)=60
    e: eccentricity
    return: angle cm0 in degree
    """
    return 180 - DEG * m.atan(40 * m.sqrt(1 - (e / 120) ** 2) / e)


def mean_pos_epic_center_1(e):
    """
    Mean position of the epicycle centre in the case of mercury
    defined by mean centre cm. This value is called cm0.
    It is the approximate solution of the equation rho(cm)=60,
    with rho the distance between earth and epicycle centre
    return cm0 approximate at 1e-7 in degree
    """
    cm = 0
    eps = 1
    p = 1e-7
    while eps > p:
        while rho_2(cm, e) > 60:
            cm = cm + eps
        cm = cm - eps
        eps = eps / 10
    return cm


def max_equat_anomaly_0(r, rho):
    """
    Maximum of the equation anomaly
    rho:distance earth-epicycle centre
    r: radius of epicycle
    return: angle in degree
    """
    return DEG * m.asin(r / rho)


def q_1(cm, e):
    """
    Center equation of Mercury
    cm:mean centre;
    e:eccentricity
    """
    rho = rho_2(cm, e)
    return -DEG * m.asin(e * m.sin(RAD * cm) / rho)


def variation_of_centre_equation_0(cm, d, e):
    """
    variation_of_centre_equation for mercury
    cm:mean centre in degree
    d:step of the variation in degree
    e:eccentricity
    return variation number without dimension
    """
    return (q_1(cm + d, e) - q_1(cm, e)) / d


def variation_of_centre_equation_1(cm, d, e):
    """
    variation_of_centre_equation for venus and planet sup
    cm:mean centre in degree
    d:step of the variation in degree
    e:eccentricity
    return variation number without dimension
    """
    return (q_2(cm + d, e) - q_2(cm, e)) / d


def first_stationary_point_0(vq, dq, rho, r, e):
    """
    Give the true arg of first station for all planets
    vq:velocity quotient (wa/wt)
    dq:centre equation variation
    rho:distance earth-epicycle centre
    r:radius of epicycle
    e: eccentricity
    return :av(s1) = angle (DCZ) in degree=true argument of first station
    """
    A = (rho + r) * (rho - r)
    B = (1 + dq) / (vq - dq)
    X = m.sqrt(A / (1 + 2 * B))
    Y = 2 * B * X
    TCG = DEG * m.asin((2 * X + Y) / (2 * rho))
    TCZ = DEG * m.asin(Y / (2 * r))
    ZCG = TCG - TCZ
    return 180 - ZCG


def first_stationary_point_mercury_0(cm, vq, r, e):
    """
    True argument of first stationary point of  mercury by calculation in degree
    cm:mean centre in degree
    vq:velocity quotient (wa/wt)
    r:radius of epicycle
    e: eccentricity
    return :av(s1) = angle (DCZ) in degree for mercury
    """

    rho = rho_2(cm, e)
    dq = variation_of_centre_equation_0(cm, 6, e)
    return first_stationary_point_0(vq, dq, rho, r, e)


def first_stationary_point_all_planet_except_mercury_0(cm, vq, r, e):
    """
    True argument of first stationary point of  all planet except mercury
    by calculation in degree
    cm:mean centre in degree
    vq:velocity quotient (wa/wt)
    r:radius of epicycle
    e: eccentricity
    return :av(s1) = angle (DCZ) in degree
    """

    rho = rho_1(cm, e)
    dq = variation_of_centre_equation_1(cm, 6, e)
    return first_stationary_point_0(vq, dq, rho, r, e)


def first_stationary_point_proport_minutes_0(x, e, s0, s1, s2):
    """
    True argument of first stationary point of sup planet or venus (except mercury)
    by proportional minutes in degree
    :param x: mean centre in degree (0<=x<360)
    :param e: planetary eccentricity
    :param s0: first station. true arg. at the apogee (cm=0)
    :param s1: first station. true arg. at the mean position (cm=cm0)
    :param s2: first station. true arg. at the perigee (cm=180)
    :return:true argument of the planet first station in degree
    """

    cm0 = mean_pos_epic_center_0(e)
    R0 = rho_1(0, e)
    R1 = rho_1(cm0, e)
    R2 = rho_1(180, e)
    R = rho_1(x, e)

    cm = x
    if (180 < x) and (x < 360):
        cm = 360 - x
    if (0 <= cm) and (cm < cm0):
        s = s0 + (s1 - s0) * (R - R0) / (R1 - R0)
    if (cm0 <= cm) and (cm <= 180):
        s = s1 + (s2 - s1) * (R - R1) / (R2 - R1)
    return s


def zero_equation_0(x, param_0):
    """
    Zero equation
    :param x:
    :param param_0:
    :return:
    """
    return 0


def zero_double_equation_0(x, y, param_0):
    """
    Zero double argument equation
    :param x:
    :param y:
    :param param_0:
    :return:
    """
    return 0


def prod_double(x, y, param_0):
    """
    Product
    :param x:
    :param y:
    :param param_0:
    :return:
    """
    return x * y * param_0


def sum_double(x, y, param_0):
    """
    Asymmetric sum
    :param x:
    :param y:
    :param param_0:
    :return:
    """
    return (x + y ** 2) * param_0
