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

<table class="table table-condensed" style="font-size: 14px; color: black; margin-left: auto; margin-right: auto;">
 <thead>
  <tr>
   <th style="text-align:left;">  </th>
   <th style="text-align:left;">  </th>
  </tr>
 </thead>
<tbody>
  <tr>
   <td style="text-align:left;width: 20em; "> CHAPPIE/ </td>
   <td style="text-align:left;"> Repo contains package info (e.g., pyproject.toml, requirements.txt, demos, etc.) </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 2em;" indentlevel="1"> CHAPPIE/ </td>
   <td style="text-align:left;"> Package contains tests, utils functions, layer querying, parcel querying, and 6 sub-package folders: </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> access/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> OSMnx/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> timeMatrix/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> assets/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> bluespace/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> cultural.py </td>
   <td style="text-align:left;"> Module for cultural assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> education.py </td>
   <td style="text-align:left;"> Module for education assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> emergency.py </td>
   <td style="text-align:left;"> Module for emergency assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> food.py </td>
   <td style="text-align:left;"> Module for food assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> hazard_infrastructure.py </td>
   <td style="text-align:left;"> Module for hazard infrastructure assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> health.py </td>
   <td style="text-align:left;"> Module for health assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> recreation.py </td>
   <td style="text-align:left;"> Module for recreation assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> transit.py </td>
   <td style="text-align:left;"> Module for transit assets </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> eco_services/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> infiltration/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> wq.py </td>
   <td style="text-align:left;"> Module for Get Assessment Total Maximum Daily Load (TMDL) Tracking and Implementation System (ATTAINS) geometry </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> endpoints/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> Health/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> hazards/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> SeaLevelRise/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> StormSurge/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> Tornadoes/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> TropicalCyclones/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> flood.py </td>
   <td style="text-align:left;"> Module for flood hazards </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> technological.py </td>
   <td style="text-align:left;"> Module for technological hazards </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> tornadoes.py </td>
   <td style="text-align:left;"> Module to query and process tornadoes hazards </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> tropical_cyclones.py </td>
   <td style="text-align:left;"> Module to query and process tropical cyclones hazards </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> weather.py </td>
   <td style="text-align:left;"> Get weather related natural hazards data </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 4em;" indentlevel="2"> household/ </td>
   <td style="text-align:left;">  </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> SVI/ </td>
   <td style="text-align:left;"> Folder for module reference materials </td>
  </tr>
  <tr>
   <td style="text-align:left;width: 20em; padding-left: 6em;" indentlevel="3"> svi.py </td>
   <td style="text-align:left;"> Lookups for SVI </td>
  </tr>
</tbody>
</table>

## Disclaimer

The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use. EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA. The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.





