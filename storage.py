import os
import pandas as pd


HISTORICAL_FILE = "historical_data.csv"


def save_measurement(measurement):

    new_data = pd.DataFrame([measurement])

    if os.path.exists(HISTORICAL_FILE):

        new_data.to_csv(
            HISTORICAL_FILE,
            mode="a",
            header=False,
            index=False
        )

    else:

        new_data.to_csv(
            HISTORICAL_FILE,
            mode="w",
            header=True,
            index=False
        )