[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) [![test](https://github.com/USEPA/CHAPPIE/actions/workflows/test.yml/badge.svg)](https://github.com/USEPA/CHAPPIE/actions/workflows/test.yml)

## Installation

Once published to pypi (pending) the package can be pip installed

``` bash
python3 -m pip install CHAPPIE
```

To install the latest development version of CHAPPIE using pip:

``` bash
pip install git+https://github.com/USEPA/CHAPPIE.git
```

## Overview

Community Hazard-scape and Amenity Placement for Providing Improved Endpoints (CHAPPIE) is designed to characterize household on the hazards they face and ammenities that contribute to their resilience with the aim to identify ways to improve community resilience.

Households - represented spatially by parcel boundaries and generalized by centroids, have on-site characteristics (e.g., placement in flood zones, socio-demographics from ACS, etc.). These households also receive benefits from local amenities (e.g., parks) through a variety of networks (e.g., road networks).

## Package Structure

| CHAPPIE/                       | Repo contains package info (e.g., pyproject.toml, requirements.txt, demos, etc.)                                |
|:-------------------------------------|:-----------------------------------|
|   CHAPPIE/                     | Package contains tests, utils functions, layer querying, parcel querying, and 6 sub-package folders:            |
|     access/                    |                                                                                                                 |
|       OSMnx/                   | Folder for module reference materials                                                                           |
|       timeMatrix/              | Folder for module reference materials                                                                           |
|     assets/                    |                                                                                                                 |
|       bluespace/               | Folder for module reference materials                                                                           |
|       cultural.py              | Module for cultural assets                                                                                      |
|       education.py             | Module for education assets                                                                                     |
|       emergency.py             | Module for emergency assets                                                                                     |
|       food.py                  | Module for food assets                                                                                          |
|       hazard_infrastructure.py | Module for hazard infrastructure assets                                                                         |
|       health.py                | Module for health assets                                                                                        |
|       recreation.py            | Module for recreation assets                                                                                    |
|       transit.py               | Module for transit assets                                                                                       |
|     eco_services/              |                                                                                                                 |
|       infiltration/            | Folder for module reference materials                                                                           |
|       wq.py                    | Module for Get Assessment Total Maximum Daily Load (TMDL) Tracking and Implementation System (ATTAINS) geometry |
|     endpoints/                 |                                                                                                                 |
|       Health/                  | Folder for module reference materials                                                                           |
|     hazards/                   |                                                                                                                 |
|       SeaLevelRise/            | Folder for module reference materials                                                                           |
|       StormSurge/              | Folder for module reference materials                                                                           |
|       Tornadoes/               | Folder for module reference materials                                                                           |
|       TropicalCyclones/        | Folder for module reference materials                                                                           |
|       flood.py                 | Module for flood hazards                                                                                        |
|       technological.py         | Module for technological hazards                                                                                |
|       tornadoes.py             | Module to query and process tornado hazards                                                                     |
|       tropical_cyclones.py     | Module to query and process tropical cyclone hazards                                                            |
|       weather.py               | Get weather related natural hazards data                                                                        |
|     household/                 |                                                                                                                 |
|       SVI/                     | Folder for module reference materials                                                                           |
|       svi.py                   | Lookups for SVI                                                                                                 |

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.
