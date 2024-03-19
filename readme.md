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

## How to use
After installing all prequisites, just doubleclick on "main.pyw" if you#re on windows or start it via terminal with "python3 main.pyw" if you're on linux.
Enter your user name and your api token, then click on start monitoring. All available non-empty controller metrics will be added to the first dropdown menu ("Parameter")
once a response from BEACON is received. 

## Todo
- Add a setting for the refresh intervall
- Add a live view mode that streams the content currently displayed on the lighthouse
- Add a console mode
- Add a test option to make a lamp light up with a specific RGB Code
