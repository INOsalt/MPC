def Lightingmodel(t, NRoom):
    """
    Calculate the internal gain and power used for lighting in a building.

    Parameters:
    t (int): The current time, assumed to be in hours.
    NRoom (int): The number of rooms in the building.

    Returns:
    tuple: A tuple containing the internal gain (in Watts) and the power used for lighting (in Watts).
    """

    # Example calculation for internal gain:
    # Assuming that internal gain increases during the day and decreases at night
    if 6 <= t < 18:  # Daytime
        internal_gain = 100 * NRoom
    else:  # Nighttime
        internal_gain = 50 * NRoom

    # Example calculation for power used for lighting:
    # Assuming that more lighting is needed at night
    if 6 <= t < 18:  # Daytime
        P_lighting = 50 * NRoom
    else:  # Nighttime
        P_lighting = 100 * NRoom

    return internal_gain, P_lighting


