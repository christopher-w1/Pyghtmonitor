# Pyghtmonitor (Python Lighthouse Monitor)
A simple tool for monitoring the lighthouse controllers' current state. 

## Features
- Live monitoring of most lighthouse metrics
- The chosen metrics for each controller will be mapped to the corresponding window(s) in the graphical lighthouse presentation
- Min/Avg/Max display for current data set
- Settings changed inside the GUI will automatically be saved to "appconfig.json"
- Unresponsive/offline controllers are represented as black windows with red text

## Prequisites
- **Messagepack** v. 1.0.0 or newer
- **websocket-client** v <2
- **PyYaml**
- A recent version of the lampservers config file as **"laserconfig.yaml"**. This is necessary for mapping the data to corresponding windows.

## Todo
- Add a setting for the refresh intervall
- Add a live view mode that streams the content currently displayed on the lighthouse
