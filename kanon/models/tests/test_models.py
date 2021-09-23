import numpy as np

import kanon.models.models as md
import kanon.models.utils as utils


def test_chords_equation_0():
    assert np.allclose(
        [utils.chords_equation_0(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            5.357568053111257,
            8.030070108914645,
            14.0,
            9.899494936611665,
            5.916655664369793,
        ],
    )


def test_long_of_the_tropical_mean_sun():
    assert np.allclose(
        [md.long_of_the_tropical_mean_sun(x, 20) for x in [0, 45, 70, 180, 270, 310]],
        [0, 900, 1400, 3600, 5400, 6200],
    )


def test_equ_of_anomaly_mercury_at_near_dist():
    assert np.allclose(
        [md.equ_of_anomaly_mercury_at_near_dist(x, 47, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            6.013722851349135,
            8.421479511677648,
            1.4019119450127673e-15,
            -9.454431403464346,
            -6.573273264933487,
        ],
    )


def test_equ_of_anomaly_mercury_at_mean_dist():
    assert np.allclose(
        [md.equ_of_anomaly_mercury_at_mean_dist(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            4.358023341886223,
            6.018128036967866,
            9.26735190372531e-16,
            -6.654425046006596,
            -4.752483310369313,
        ],
    )


def test_prod_double():
    assert np.allclose(
        [
            utils.prod_double(x, y, 7)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [0, 0, 14175, 56700, 170100],
    )


def test_shadow_equation_0():
    assert np.allclose(
        [utils.shadow_equation_0(x, 7) for x in [272, 310]],
        [
            -0.24444538644223626,
            -5.873697418240959,
        ],
    )


def test_sin_double():
    assert np.allclose(
        [
            utils.sin_double(x, y, 7)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [
            0.0,
            0.0,
            0.060934671702573724,
            1.0553349599113052e-17,
            -0.12186934340514748,
        ],
    )


def test_sum_double():
    assert np.allclose(
        [
            utils.sum_double(x, y, 7)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [0, 14175, 14490, 15435, 510930],
    )


def test_zero_double_equation_0():
    assert np.allclose(
        [
            utils.zero_double_equation_0(x, y, 7)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [0, 0, 0, 0, 0],
    )


def test_zero_equation_0():
    assert np.allclose(
        [utils.zero_equation_0(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0, 0, 0, 0, 0, 0,
        ],
    )


def test_sine():
    assert np.allclose(
        [md.sine(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            4.949747468305832,
            6.5778483455013586,
            8.572527594031472e-16,
            -7.0,
            -5.362311101832847,
        ],
    )


def test_equ_of_the_sun():
    assert np.allclose(
        [md.equ_of_the_sun(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            4.358023341886223,
            6.018128036967866,
            9.26735190372531e-16,
            -6.654425046006596,
            -4.752483310369313,
        ],
    )


def test_meridian_altitude_of_the_sun():
    assert np.allclose(
        [md.meridian_altitude_of_the_sun(x, 7, 25) for x in [0, 45, 70, 180, 270, 310]],
        [
            65.0,
            69.94357460082693,
            71.57592417363863,
            65.0,
            58.0,
            59.64321825974211,
        ],
    )


def test_declination():
    assert np.allclose(
        [md.declination(x, 7) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            4.9435746008269295,
            6.575924173638629,
            8.551217550772382e-16,
            -7.0,
            -5.356781740257883,
        ],
    )


def test_venus_center_equ():
    assert np.allclose(
        [md.venus_center_equ(x, 18) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            -19.631945709409873,
            -27.962760549542708,
            -6.014322255887037e-15,
            32.168698259696335,
            21.512720465644303,
        ],
    )


def test_mars_center_equ():
    assert np.allclose(
        [md.mars_center_equ(x, 30) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            -28.74845784697243,
            -41.7250944075642,
            -1.4033418597069752e-14,
            49.1066053508691,
            31.60111999186434,
        ],
    )


def test_ascensional_diffs():
    assert np.allclose(
        [md.ascensional_diffs(x, 39, 50) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            36.3126686949605,
            60.92235043062093,
            5.2624957461148764e-15,
            -74.81017282966691,
            -40.97755088038094,
        ],
    )


def test_jupiter_center_equ():
    assert np.allclose(
        [md.jupiter_center_equ(x, 4) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            -5.150279963005815,
            -6.997197151903442,
            -1.0023870426478395e-15,
            7.611378517094657,
            5.600796795434896,
        ],
    )


def test_equ_of_center_of_mercury():
    assert np.allclose(
        [md.equ_of_center_of_mercury(x, 13) for x in [0, 45, 70, 180, 270, 310]],
        [
            -0.0,
            -7.068826378397518,
            -12.457502174422096,
            -1.940791933637306e-15,
            15.92057319077762,
            8.100274156782582,
        ],
    )


def test_equ_of_anomaly_mercury_at_great_dist():
    assert np.allclose(
        [md.equ_of_anomaly_mercury_at_great_dist(x, 35, 2) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            0.48689661908197446,
            0.6498889345943074,
            8.609459262005983e-17,
            -0.6944602875497745,
            -0.5278854950216272,
        ],
    )


def test_moon_anomaly_equ():
    assert np.allclose(
        [
            md.moon_anomaly_equ(x, y, 20, 48)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [-0.0, -0.0, -17.69357669843103, -1.3774202695993336e-14, -40.31554221077259],
    )


def test_moon_center_equ():
    assert np.allclose(
        [md.moon_center_equ(x, 47) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            15.931881505305135,
            31.256925287487654,
            -9.699568736209976e-15,
            -51.566793659149184,
            -18.370446163781168,
        ],
    )


def test_lat_of_the_moon():
    assert np.allclose(
        [md.lat_of_the_moon(x, 23) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            16.038822854808746,
            21.54101431981613,
            2.7416467424977128e-15,
            -23.0,
            -17.41660979279636,
        ],
    )


def test_right_ascension():
    assert np.allclose(
        [md.right_ascension(x, 37) for x in [0, 45, 70, 180, 270, 310]],
        [0.0, 38.612106078037314, 65.49934276693266, 180.0, 270.0, 316.4153398271072],
    )


def test_oblique_ascension():
    assert np.allclose(
        [md.oblique_ascension(x, 45, 26, 20) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            28.449228099847645,
            53.293130468766726,
            180.0,
            280.2253484333922,
            327.33503096973357,
        ],
    )


def test_length_daylight():
    assert np.allclose(
        [md.length_daylight(x, 43, 19, 9) for x in [0, 45, 70, 180, 270, 310]],
        [
            180.0,
            184.2945545567535,
            185.83471368826008,
            180.0,
            173.74751715464697,
            175.324517205095,
        ],
    )


def test_equ_of_times_for_true_sun():
    assert np.allclose(
        [
            md.equ_of_times_for_true_sun(x, 8, 7, 9, 31, 8)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            239.63403654700465,
            281.6984100884974,
            296.2988547308157,
            256.3659634529954,
            195.06472845661438,
            199.87621374043738,
        ],
    )


def test_equ_of_times_for_mean_sun():
    assert np.allclose(
        [
            md.equ_of_times_for_mean_sun(x, 40, 37, 13, 9, 16)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            83.23623857945412,
            442.35400928111915,
            604.4251066678135,
            382.53515096496176,
            -533.1866962409586,
            -317.967463015917,
        ],
    )


def test_planet_double_arg_mercury():
    assert np.allclose(
        [
            md.planet_double_arg_mercury(x, y, 15, 16)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [
            0.0,
            5.5556214031843245,
            -0.6345586630512212,
            11.359784961528892,
            -38.51426497329155,
        ],
    )


def test_venus_lat_incl():
    assert np.allclose(
        [md.venus_lat_incl(x, 23) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            11.499999999999998,
            20.309511095868242,
            3.4494475001222727e-31,
            23.0,
            13.496954043169701,
        ],
    )


def test_venus_lat_deviation():
    assert np.allclose(
        [md.venus_lat_deviation(x, 45, 4) for x in [0, 45, 70, 180, 270, 310]],
        [
            1.7141719840803153,
            1.309461718943569,
            0.7118648187542249,
            -11.73631923492545,
            -4.405148081580671e-16,
            1.2128163576245998,
        ],
    )


def test_venus_lat_slant_approximated():
    assert np.allclose(
        [
            md.venus_lat_slant_approximated(x, 34, 46, 8)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            0.0,
            91.79378698894844,
            138.2241166515225,
            5.276025645629108e-14,
            -169.8479979924591,
            -101.4911700569756,
        ],
    )


def test_venus_lat_slant_geometric():
    assert np.allclose(
        [
            md.venus_lat_slant_geometric(x, 19, 23, 10)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            0.0,
            3.4580387321808126,
            4.99530260665427,
            1.1179062388039683e-15,
            -5.832877880907235,
            -3.798125217361804,
        ],
    )


def test_venus_lat_double_arg():
    assert np.allclose(
        [
            md.venus_lat_double_arg(x, y, 30, 45, 19, 6, 38)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [
            6.307300213455363,
            26.959934751913643,
            27.505063705643845,
            10.367515222675303,
            40.805518235198214,
        ],
    )


def test_venus_equ_anomaly_at_the_max_dist():
    assert np.allclose(
        [md.venus_equ_anomaly_at_the_max_dist(x, 31, 35) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            12.068931332188297,
            17.713683223353296,
            4.385443311584298e-15,
            -21.037511025421818,
            -13.29133059917078,
        ],
    )


def test_venus_equ_anomaly_at_mean_dist():
    assert np.allclose(
        [md.venus_equ_anomaly_at_mean_dist(x, 27) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            13.570940186440264,
            20.125872070977834,
            5.740943971528535e-15,
            -24.227745317954174,
            -14.969532764250934,
        ],
    )


def test_venus_equ_anomaly_at_min_dist():
    assert np.allclose(
        [md.venus_equ_anomaly_at_min_dist(x, 33, 24) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            21.104235641764333,
            32.641395739262315,
            5.613367438827901e-14,
            -41.6335393365702,
            -23.428778642661726,
        ],
    )


def test_venus_equ_proportional_minute():
    assert np.allclose(
        [
            md.venus_equ_proportional_minute(x, y, 3, 34)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270), (180, 120)]
        ],
        [
            0.0,
            0.0,
            15.569356905107423,
            8.459931823896391e-15,
            29.445143547293796,
            9.685667501018142e-15,
        ],
    )


def test_mercury_equ_proportional_minutes():
    assert np.allclose(
        [
            md.mercury_equ_proportional_minutes(x, y, 2, 36)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [0.0, 0.0, 16.083978464093857, 9.499057189984597e-15, 31.818314208131124],
    )


def test_first_stationary_point_of_mercury_by_proportional_minutes():
    assert np.allclose(
        [
            md.first_stationary_point_of_mercury_by_proportional_minutes(x, 15, 39, 48, 4)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            15.0,
            28.343432012622166,
            39.83125441378628,
            45.11308913257944,
            45.09851919048002,
            30.77831329741517,
        ],
    )


def test_first_stationary_point_of_mercury_by_calculation_and_proportional_minutes():
    assert np.allclose(
        [
            md.first_stationary_point_of_mercury_by_calculation_and_proportional_minutes(x, 3, 15, 5)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            145.08550675015084,
            142.72136285175768,
            140.76649653822346,
            140.67404938743098,
            140.67418808913686,
            142.28522655611468,
        ],
    )


def test_mars_equ_anomaly_at_max_dist():
    assert np.allclose(
        [md.mars_equ_anomaly_at_max_dist(x, 25, 48) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            15.926665349431607,
            23.977130078707894,
            9.102758008910109e-15,
            -29.453672726920953,
            -17.608600543417907,
        ],
    )


def test_mars_equ_anomaly_at_mean_dist():
    assert np.allclose(
        [md.mars_equ_anomaly_at_mean_dist(x, 27) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            13.570940186440264,
            20.125872070977834,
            5.740943971528535e-15,
            -24.227745317954174,
            -14.969532764250934,
        ],
    )


def test_mars_equ_anomaly_at_min_dist():
    assert np.allclose(
        [md.mars_equ_anomaly_at_min_dist(x, 12, 15) for x in [0, 45, 70, 180, 270, 310]],
        [
            0.0,
            10.258332179441476,
            14.85820627782239,
            3.1894133175158534e-15,
            -17.35402463626132,
            -11.273899211490654,
        ],
    )


def test_mars_equ_proportional_minutes():
    assert np.allclose(
        [
            md.mars_equ_proportional_minutes(x, y, 14, 15)
            for x, y in [(0, 0), (0, 45), (45, 45), (180, 45), (90, 270)]
        ],
        [0.0, 0.0, 7.323180956335268, 1.8544516524161714e-15, 13.040206043704217],
    )


def test_first_stationary_point_of_venus_by_proportional_minutes():
    assert np.allclose(
        [
            md.first_stationary_point_of_venus_by_proportional_minutes(x, 47, 22, 37, 41)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            47.0,
            46.414290589573,
            44.97039224554984,
            37.0,
            42.10227825549495,
            46.23308136920809,
        ],
    )


def test_first_stationary_point_of_venus_by_calculation_and_proportional_minutes():
    assert np.allclose(
        [
            md.first_stationary_point_of_venus_by_calculation_and_proportional_minutes(x, 35, 20, 42)
            for x in [0, 45, 70, 180, 270, 310]
        ],
        [
            103.77949631704134,
            104.20231461122385,
            105.11114567410759,
            146.69382968660582,
            106.65041325320269,
            104.32514702820028,
        ],
    )
