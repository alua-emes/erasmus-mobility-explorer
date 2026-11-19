
# Data Sources

## Primary Dataset

**Title:** Mobility of Erasmus+ students in Europe:
Geolocated individual and aggregate mobility flows
from 2014 to 2023.

**Authors:**
- Tuomas Väisänen
- Milad Malekzadeh
- Oula Inkeröinen
- Olle Järv

**Institution:** University of Helsinki,
Digital Geography Lab.

**Publication date:** August 4, 2025

**Version:** 1.1

**Repository:** Zenodo

**DOI:** https://doi.org/10.5281/zenodo.16737523

**Dataset page:** https://zenodo.org/records/16737523

**License:** Creative Commons Attribution 4.0
(CC BY 4.0), as documented in the associated
scientific publication.

## File Used in This Project

Erasmus_2014-2023_aggregate_NUTS.csv

The file contains aggregated student mobility flows
between NUTS regions.

- Temporal coverage: 2014–2023
- Records processed: 588,109
- Total participant count: 2,554,116
- Format: CSV
- Separator: semicolon
- Geographical aggregation: NUTS 3

## Original Data Provider

The geolocated dataset is derived from official
Erasmus+ mobility raw data published by the
European Commission.

Source:
https://data.europa.eu/88u/dataset/erasmus-mobility-raw-data

## Associated Scientific Publication

Väisänen, T., Malekzadeh, M., Inkeröinen, O.,
& Järv, O. (2025).

Mobility of Erasmus+ students in Europe:
Geolocated individual and aggregate mobility flows
from 2014 to 2022.

Scientific Data.

https://doi.org/10.1038/s41597-025-04789-0

Note: The associated scientific publication
describes the earlier 2014–2022 dataset.
This project uses the updated 2014–2023 release.

## Data Acquisition

Download the following file from Zenodo:

Erasmus_2014-2023_aggregate_NUTS.csv

Direct download:

https://zenodo.org/records/16737523/files/Erasmus_2014-2023_aggregate_NUTS.csv?download=1

Place the file in:

data/raw/Erasmus_2014-2023_aggregate_NUTS.csv

Expected MD5 checksum:

048259d0c7fad5e792e13d0642aee0d8

## Data Processing

The project imports five source attributes:

- OD_ID
- ORIGIN
- DESTINATION
- YEAR
- COUNT

Additional geographical indicators are generated
during preprocessing and database initialization.

The original source file is not modified.

## Data Privacy

The project uses aggregated regional mobility data
rather than individual participant records.

No personal or confidential information is processed.
