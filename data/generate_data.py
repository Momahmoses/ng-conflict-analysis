import pandas as pd
import numpy as np
import os

CONFLICT_ZONES = [
    ("Borno", 11.8846, 13.1571, "Insurgency"),
    ("Yobe", 12.2939, 11.4390, "Insurgency"),
    ("Adamawa", 9.3265, 12.3984, "Insurgency"),
    ("Zamfara", 12.1222, 6.2236, "Banditry"),
    ("Sokoto", 13.0059, 5.2476, "Banditry"),
    ("Katsina", 12.9908, 7.6018, "Banditry/Kidnapping"),
    ("Kaduna", 10.5222, 7.4383, "Communal/Banditry"),
    ("Niger", 10.0008, 5.5981, "Banditry"),
    ("Kebbi", 11.4943, 4.2333, "Banditry"),
    ("Plateau", 9.2182, 9.5179, "Farmer-Herder"),
    ("Benue", 7.3369, 8.7404, "Farmer-Herder"),
    ("Taraba", 7.9993, 10.7741, "Farmer-Herder"),
    ("Nassarawa", 8.4994, 8.1997, "Farmer-Herder"),
    ("Kogi", 7.7337, 6.6906, "Armed Robbery"),
    ("Rivers", 4.8156, 7.0498, "Cult Clash"),
    ("Delta", 5.5320, 5.8987, "Cult Clash"),
    ("Ebonyi", 6.2649, 8.0137, "Communal"),
    ("Lagos", 6.5244, 3.3792, "Gang/Cult"),
    ("Anambra", 6.2104, 6.9623, "Unknown Gunmen"),
    ("Imo", 5.4527, 7.0201, "Unknown Gunmen"),
]

INCIDENT_TYPES = [
    "Armed Clash", "Attack on Civilians", "Bombing/Explosion",
    "Kidnapping/Abduction", "Armed Robbery", "Farmer-Herder Clash",
    "Protest/Riot", "Remote Violence", "Strategic Development"
]

ACTORS = [
    "Boko Haram", "ISWAP", "Bandits", "Fulani Herdsmen",
    "Unknown Gunmen", "Cultists", "Criminal Gang", "Military (COIN)", "Police"
]


def generate_conflict_incidents(n: int = 2000) -> pd.DataFrame:
    np.random.seed(42)
    records = []
    base_date = pd.Timestamp("2020-01-01")
    for i in range(n):
        zone_info = CONFLICT_ZONES[np.random.randint(len(CONFLICT_ZONES))]
        state, slat, slon, conflict_type = zone_info
        records.append({
            "event_id": f"NG-{i+1:05d}",
            "date": base_date + pd.Timedelta(days=int(np.random.randint(1460))),
            "state": state, "conflict_type": conflict_type,
            "lat": slat + np.random.uniform(-1.0, 1.0),
            "lon": slon + np.random.uniform(-1.0, 1.0),
            "event_type": np.random.choice(INCIDENT_TYPES,
                          p=[0.20, 0.25, 0.10, 0.15, 0.10, 0.08, 0.05, 0.04, 0.03]),
            "actor1": np.random.choice(ACTORS),
            "actor2": np.random.choice(ACTORS),
            "fatalities": int(np.random.negative_binomial(1, 0.4)),
            "displaced": int(np.random.exponential(500)),
            "is_verified": np.random.choice([True, False], p=[0.80, 0.20]),
            "severity": np.random.choice(["Low", "Medium", "High"], p=[0.45, 0.35, 0.20]),
        })
    return pd.DataFrame(records)


def generate_state_security_index() -> pd.DataFrame:
    np.random.seed(42)
    return pd.DataFrame([
        {"state": state, "lat": slat, "lon": slon,
         "conflict_type": ctype,
         "incidents_2023": int(np.random.randint(10, 500)),
         "fatalities_2023": int(np.random.randint(5, 1500)),
         "displaced_2023": int(np.random.exponential(50000)),
         "security_index": round(np.random.uniform(0.1, 0.9), 3),
         "ag_impact_pct": round(np.random.uniform(5, 65), 1),
        }
        for state, slat, slon, ctype in CONFLICT_ZONES
    ])


def save_all(output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    generate_conflict_incidents().to_csv(f"{output_dir}/incidents.csv", index=False)
    generate_state_security_index().to_csv(f"{output_dir}/security_index.csv", index=False)
    print("Conflict data generated.")


if __name__ == "__main__":
    save_all()
