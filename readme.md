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

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.





