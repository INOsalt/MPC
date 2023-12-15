def RCmodel(Tout, Tin, Qsolar, Qven, R):
    """
    Calculate the heat removed by the chiller in a building.

    Parameters:
    Tout (float): Outdoor temperature (in degrees Celsius).
    Tin (float): Indoor temperature (in degrees Celsius).
    Qsolar (float): Solar heat gain (in Watts).
    Qven (float): Heat gain from ventilation (in Watts).
    R (float): Thermal resistance (in °C/W).

    Returns:
    float: Heat removed by the chiller (in Watts).
    """

    # Calculating the heat removed by the chiller
    Qchiller = (Tout - Tin) / R + Qsolar + Qven

    return Qchiller

