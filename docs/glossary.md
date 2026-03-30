# Glossary of Cloud-Observation Terms

A reference guide for key terms used in the GLOBE Observer Clouds protocol
and this project. Sources are drawn from the
[GLOBE Clouds protocol](https://www.globe.gov/web/atmosphere/protocols/clouds),
[NASA's cloud science resources](https://science.nasa.gov/science-research/earth-science/clouds-in-a-changing-climate/),
and the World Meteorological Organization (WMO) International Cloud Atlas.

---

## Cloud Genera (Types)

| Cloud Type | Altitude | Description |
| --- | --- | --- |
| **Cirrus (Ci)** | High (> 6 km) | Thin, wispy ice-crystal clouds; often indicate fair weather or approaching fronts |
| **Cirrocumulus (Cc)** | High | Small white patches or ripples; sometimes called "mackerel sky" |
| **Cirrostratus (Cs)** | High | Thin, sheet-like veil that often produces halos around the sun or moon |
| **Altocumulus (Ac)** | Mid (2–6 km) | White or grey patches, often in rows; may signal approaching thunderstorms |
| **Altostratus (As)** | Mid | Grey or blue-grey sheets covering the sky; sun visible as through frosted glass |
| **Nimbostratus (Ns)** | Mid–Low | Thick, dark grey layer producing steady rain or snow |
| **Stratocumulus (Sc)** | Low (< 2 km) | Low, lumpy grey or white masses; the most common cloud type globally |
| **Stratus (St)** | Low | Uniform grey layer, like fog that doesn't reach the ground |
| **Cumulus (Cu)** | Low–Mid | Puffy "fair weather" clouds with flat bases and rounded tops |
| **Cumulonimbus (Cb)** | Low to High | Towering thunderstorm clouds; can produce heavy rain, hail, and lightning |

## Sky Conditions (GLOBE Protocol Categories)

| Condition | Approx. Cloud Cover | Description |
| --- | --- | --- |
| **Clear** | 0% | No clouds visible |
| **Few** | ~10–25% | A few clouds scattered across the sky |
| **Isolated** | ~25–30% | Isolated cloud patches |
| **Scattered** | ~30–50% | Clouds scattered across roughly half the sky |
| **Broken** | ~50–90% | More cloud than open sky |
| **Overcast** | ~90–100% | Sky nearly or entirely covered by clouds |
| **Obscured** | 100% | Sky hidden by fog, haze, dust, smoke, or precipitation |

## Cloud Opacity (GLOBE Protocol)

| Level | Description |
| --- | --- |
| **Transparent** | Sun or moon clearly visible through the cloud |
| **Thin** | Sun or moon dimly visible, as through frosted glass |
| **Opaque** | Sun or moon completely hidden by the cloud |

## Additional Terms

**Citizen science:** Scientific research conducted in whole or in part by
non-professional scientists, often through structured protocols like GLOBE.

**Satellite overpass:** The moment a polar-orbiting satellite passes over an
observation location. GLOBE observations made within 15 minutes of an overpass
are especially valuable for ground-truth comparison.

**Satellite match:** When a GLOBE ground observation is paired with
contemporaneous satellite cloud data for the same location. The 2022 challenge
achieved over 49,450 satellite matches — more than double the 20,000 goal.

**GeoJSON:** A standard format for encoding geographic features and their
properties, used by the GLOBE API to return observation data.

**Parquet:** A columnar data storage format optimised for analytical queries,
used in this project for the cleaned dataset.

**GLOBE Observer app:** A free mobile application by NASA that enables
citizen-science data collection for the GLOBE Program. It auto-records
date, time, latitude, longitude, and elevation for each observation.

**CLOUD GAZE:** A Zooniverse-hosted project where volunteers classify cloud
types and other phenomena in photographs taken by GLOBE participants.

---

## References

1. GLOBE Clouds Protocol — https://www.globe.gov/web/atmosphere/protocols/clouds
2. NASA — Clouds in a Changing Climate — https://science.nasa.gov/science-research/earth-science/clouds-in-a-changing-climate/
3. Colón Robles et al. (2020) — GLOBE Observer Data: 2016–2019. *Earth and Space Science*, 7(8). https://doi.org/10.1029/2020EA001175
4. Dodson et al. (2022) — Intense Observation Periods. *Earth and Space Science*, 9(3). https://doi.org/10.1029/2021EA002058
5. WMO International Cloud Atlas — https://cloudatlas.wmo.int/
