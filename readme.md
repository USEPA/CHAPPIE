[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
[![test](https://github.com/USEPA/CHAPPIE/actions/workflows/test.yml/badge.svg)](https://github.com/USEPA/CHAPPIE/actions/workflows/test.yml)

## Installation

Once published to pypi (pending) the package can be pip installed
```bash
python3 -m pip install CHAPPIE
```

To install the latest development version of CHAPPIE using pip:

```bash
pip install git+https://github.com/USEPA/CHAPPIE.git
```
## Overview
Community Hazard-scape and Amenity Placement for Providing Improved Endpoints (CHAPPIE) is desgned to characterize household on the hazards they face and ammerities that contribute to their resilience with the aim to identify ways to improve community resilence.

Households - represented spatially by parcel boundaries and generalized by centroids, have on-site characteristics (e.g., placement in flood zones, socio-demographics from ACS, etc.). These households also receive benefits from local amenities (e.g., parks) through a variety of networks (e.g., road networks).   

## Package Structure

| CHAPPIE/ | Repo contains package info (e.g., pyproject.toml, requirements.txt, demos, etc.) |
| :--- | :--- |
| &emsp; CHAPPIE/ | Package contains tests, utils functions, layer querying, parcel querying, and 6 sub-package folders: |
| &emsp; &emsp; access/ | |
| &emsp; &emsp; &emsp; OSMnx/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; timeMatrix/ | Folder for module reference materials |
| &emsp; &emsp; assets/ | |
| &emsp; &emsp; &emsp; bluespace/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; cultural.py | Module for cultural assets |
| &emsp; &emsp; &emsp; education.py | Module for education assets |
| &emsp; &emsp; &emsp; emergency.py | Module for emergency assets |
| &emsp; &emsp; &emsp; food.py | Module for food assets |
| &emsp; &emsp; &emsp; hazard_infrastructure.py &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; &emsp; | Module for hazard infrastructure assets |
| &emsp; &emsp; &emsp; health.py | Module for health assets |
| &emsp; &emsp; &emsp; recreation.py | Module for recreation assets |
| &emsp; &emsp; &emsp; transit.py | Module for transit assets |
| &emsp; &emsp; eco_services/ | |
| &emsp; &emsp; &emsp; infiltration/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; wq.py | Module for Get Assessment Total Maximum Daily Load (TMDL) Tracking and Implementation System (ATTAINS) geometry |
| &emsp; &emsp; endpoints/ | |
| &emsp; &emsp; &emsp; Health/ | Folder for module reference materials |
| &emsp; &emsp; hazards/ | |
| &emsp; &emsp; &emsp; SeaLevelRise/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; StormSurge/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; Tornadoes/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; TropicalCyclones/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; flood.py | Module for flood hazards |
| &emsp; &emsp; &emsp; technological.py | Module for technological hazards |
| &emsp; &emsp; &emsp; tornadoes.py | Module to query and process tornado hazards |
| &emsp; &emsp; &emsp; tropical_cyclones.py | Module to query and process tropical cyclone hazards |
| &emsp; &emsp; &emsp; weather.py | Get weather related natural hazards data |
| &emsp; &emsp; household/ | |
| &emsp; &emsp; &emsp; SVI/ | Folder for module reference materials |
| &emsp; &emsp; &emsp; svi.py | Lookups for SVI |

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.





