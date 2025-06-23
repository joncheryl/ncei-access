"""
Test
"""

# %%

import logging
import pandas as pd
from ncei_access import dataType_ref
import ncei_access.ncei_accessor as na

logging.basicConfig(level=logging.DEBUG)
# %%

fdsa = na.NceiAccessor()
station_test = fdsa.find_station('USS0010J52S')  # Greens Basin
# stations_in_boundary_test = fdsa.stations_in_boundary(41,-111,40.5,-110.5)
closest_test = fdsa.find_closest_station(40.629583, -111.626703) # Greens Basin
daily_test = fdsa.get_daily(
    data_types=["TMAX", "TMIN"],
    stations=closest_test.station_id,
    start="1970-04-21",
    end="2025-04-21",
)
# hilow_test = fdsa.get_daily_hilow('USS0010J52S')

# %%
# # id for each station found in
# rewq.data['results'][0]['stations'][0]['id']

# # name
# rewq.data['results'][0]['stations'][0]['name']

# # dataTypes
# pd.DataFrame(rewq.data['results'][0]['stations'][0]['dataTypes'])

# # coordinates
# rewq.data['results'][0]['location']['coordinates']

# Need to get station object to fit nicely into vector like things.
# Need to get date ranges for dataTypes to make sense.

# Test params for _rest_adapter.get for looking for data
params = {
    "dataset": "daily-summaries",
    "dataTypes": ["TMAX", "TMIN"],
    "stations": 'USS0010J52S',
    "startDate": "2024-04-21",
    "endDate": "2025-04-21",
}

temp_test = fdsa._rest_adapter.get(
    endpoint="data/v1/", ep_params=params
)

#%%
# Test paarams for _rest_adapter.get for looking for stations
station_params = {
    "dataset": "daily-summaries",
    "startDate": "2023-03-01",
    "endDate": "2024-03-15",
    "bbox": "41,-111,40,-110",
    "limit": 1000,
}

station_test = fdsa._rest_adapter.get(
    endpoint="search/v1/data", ep_params=station_params
)
# %%
