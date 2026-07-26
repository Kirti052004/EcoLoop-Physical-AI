"""
ASHRAE Standard 55 Fanger PMV / PPD Thermal Comfort Calculator
Calculates Predicted Mean Vote (PMV) and Predicted Percentage Dissatisfied (PPD).
"""

import math

def calculate_pmv(ta: float, tr: float = None, vel: float = 0.15, rh: float = 50.0, met: float = 1.2, clo: float = 0.8) -> dict:
    """
    Fanger PMV Calculation.
    :param ta: Air Temperature (°C)
    :param tr: Mean Radiant Temperature (°C). Defaults to ta if None.
    :param vel: Air Velocity (m/s). Default 0.15 m/s.
    :param rh: Relative Humidity (%). Default 50%.
    :param met: Metabolic Rate (met unit). 1 met = 58.15 W/m2 (light office work = 1.2 met).
    :param clo: Clothing Insulation (clo unit). 1 clo = 0.155 m2K/W (light office = 0.8 clo).
    :return: dict with 'pmv', 'ppd', and 'comfort_status'
    """
    if tr is None:
        tr = ta

    pa = rh * 10 * math.exp(16.6536 - 4030.183 / (ta + 235.0)) # Vapor pressure in Pa
    m = met * 58.15 # Metabolic rate in W/m2
    w = 0.0 # External work
    mw = m - w # Internal heat production

    icl = 0.155 * clo # Thermal resistance of clothing

    # Clothing surface temperature iteration
    fcl = 1.05 + 0.64 * icl if icl > 0.078 else 1.00 + 0.2 * icl
    hcf = 12.1 * math.sqrt(vel)

    tcl = ta + (35.5 - ta) / (3.5 * (6.3 + 40.0 * (vel ** 0.5)))
    for _ in range(30):
        hc = 2.38 * abs(tcl - ta)**0.25
        if hc < hcf:
            hc = hcf
        tcl_new = (35.7 - 0.028 * mw - icl * fcl * (3.96 * 10**-8 * ((tcl + 273.0)**4 - (tr + 273.0)**4) + hc * (tcl - ta)))
        if abs(tcl_new - tcl) < 0.001:
            tcl = tcl_new
            break
        tcl = (tcl + tcl_new) / 2.0

    # Heat loss components
    hl1 = 3.05 * 0.001 * (5733.0 - 6.99 * mw - pa)
    hl2 = 0.42 * (mw - 58.15) if mw > 58.15 else 0.0
    hl3 = 1.7 * 10**-5 * m * (5867.0 - pa)
    hl4 = 0.0014 * m * (34.0 - ta)
    hl5 = 3.96 * 10**-8 * fcl * ((tcl + 273.0)**4 - (tr + 273.0)**4)
    hl6 = fcl * hc * (tcl - ta)

    # PMV formula
    ts = 0.303 * math.exp(-0.036 * m) + 0.028
    pmv = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6)

    # PPD formula
    ppd = 100.0 - 95.0 * math.exp(-0.03353 * (pmv**4) - 0.2179 * (pmv**2))

    # Comfort status
    if -0.5 <= pmv <= 0.5:
        status = "Optimal Comfort (ASHRAE 55 Compliant)"
    elif pmv > 0.5:
        status = "Slightly Warm / Warm" if pmv <= 1.5 else "Hot (Cooling Needed)"
    else:
        status = "Slightly Cool / Cool" if pmv >= -1.5 else "Cold (Heating Needed)"

    return {
        "pmv": round(pmv, 3),
        "ppd": round(ppd, 1),
        "comfort_status": status,
        "is_compliant": -0.5 <= pmv <= 0.5
    }

if __name__ == "__main__":
    result = calculate_pmv(23.5, 23.5, 0.15, 45.0)
    print("Test PMV Result:", result)
