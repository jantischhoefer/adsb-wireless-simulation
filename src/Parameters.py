import Groundstation
import Plane

# Simulation parameters
sim_timestep = 60 # simulation timestep in seconds. 0.5s recommended to match ADS-B position publishing frequency

# Signal to Noise Ratios
plane_to_satellite_SNRdB = 6.1
satellite_to_groundstation_SNRdB = 6.1
plane_to_groundstation_SNRdB = 12

# Signal Frequencies
sat_freq = 1616000000  # 1616MHz (Iridium Frequency)
adsb_freq = 1090000000  # 1090MHz (ADS-B Frequency)

# Groundstations
ground_station_antenna_range = 370000  # 370km
hanoiAirport = Groundstation.Groundstation("Hanoi_ID", (105.808817, 21.028511), "Hanoi")
saigonAirport = Groundstation.Groundstation("Saigon_ID", (106.660172, 10.762622), "HCMC")
groundstations = [hanoiAirport, saigonAirport]

# Planes
plane1 = Plane.Plane("Plane_ID", callSign="TUAN01", waypoints=[(102.593618, 18.02), (100.593618, 13.741252),  (106.660172, 10.762622)])
plane2 = Plane.Plane("Plane_ID_2", callSign="TUAN02", waypoints=[(108.3, 20.3), (109.670204, 18.427483), (108.9, 15.6), (106.660172, 10.762622)])
planes = [plane1, plane2]