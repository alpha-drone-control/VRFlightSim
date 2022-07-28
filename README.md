# VRFlightSim
<p align="center">
    GUI for Human-drone interaction experiment based on Airsim, support weather adjustment, velocity and angle data visualization.
    <br>
    <a href="https://github.com/alpha-drone-control/VRFlightSim/issues/new">Report bug / Request feature</a>
</p>

##  Table of content

- [VRFlightSim](#vrflightsim)
  - [Table of content](#table-of-content)
  - [Prerequisites](#prerequisites)
  - [User manual](#user-manual)

## Prerequisites

Required environment:

- **Python3.7.12**

- **Requirement installation**:  
`pip install -r requirement.txt`


- **Binary Download Link**:  
 https://hkustconnect-my.sharepoint.com/:u:/g/personal/yhuangdl_connect_ust_hk/Efzi9Gvuu3BBnIA4-qcLoCwBciC74qOrD-OKm5FDPYZ7fA?e=6xLetg

## User manual

-**How to use**:\
Download the binary, and run the `Blocks.exe`  
Clone the code and install the [prerequistes](#prerequistes) above, then use **Python** to run `main.py`

-**Basic manual control**:

**Forward**:  `↑`

**Backward**:  `↓`

**Move left**:  `←`

**Move right**:  `→`

**Move up**:  `w`

**Move down**:  `s`

**Turn left**:  `a`

**Turn right**:  `d`

-**Experiment Instruction**:
1. Input the name and experiment trial.

2. Type the weather ratio in the entry ( **0.0-1.0**  **Type**: `float`).

3. Type the wind speed in the entry ( **x,y,z**  **Type**: `int`).

4. Click on the **Check bottons e.g. Rain** on the application to select weather.

5. Click on the **Check botton 'Start experiment'** to start the experiment and logging the data.

-**Changing experiment path**:
1. Open main.py on editor

2. Change the second argument of "GUI = DroneEnvSettingGUI(depc, u, pp.get_path())" 

3. e.g. changing "pp.get_path()" into "cp.get_path()"


