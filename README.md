# Space Weather Dashboard 

A desktop app built with Python and Tkinter that pulls live space weather data from NASA's DONKI (Database Of Notifications, Knowledge, Information) API and displays it in a simple, animated dashboard.

## Features

- **Solar Flares** — classification (A/B/C/M/X) and timing of recent flares
- **Geomagnetic Storms** — Kp index and storm intensity over time
- **Coronal Mass Ejections (CMEs)** — speed, type, source location, and Earth-impact notes
- **Solar Energetic Particles (SEP)** — radiation intensity and risk level
- **Coronal Holes** — recent observations and locations
- Animated starfield background
- Automatically pulls the last 10 days of data every time you open a page

## Requirements

- Python 3.8+
- [`requests`](https://pypi.org/project/requests/) library
- Tkinter (usually included with Python; on some Linux distros install via `sudo apt-get install python3-tk`)

Install the dependency:

```bash
pip install requests
```

## Setup

1. Clone the repo:
```bash
   git clone https://github.com/sdmaller12/space_weather.git
   cd space_weather
```

2. Get a free NASA API key at [api.nasa.gov](https://api.nasa.gov) (or use `DEMO_KEY`, which has lower rate limits).

3. Set your API key as an environment variable rather than hardcoding it:
```bash
   export NASA_API_KEY="your_key_here"
```
   (On Windows: `set NASA_API_KEY=your_key_here`)

4. Run the app:
```bash
   python AstronomyFinal.py
```

## Usage

Launch the app and click any category button (Solar Flares, Geomagnetic Storms, CMEs, SEP, Coronal Holes) to fetch and display the most recent NASA DONKI data for that category. Use the **Back** button to return to the main menu.

## Data Source

All space weather data comes from NASA's [DONKI API](https://ccmc.gsfc.nasa.gov/tools/DONKI/), part of the Community Coordinated Modeling Center.

## Notes

- Data refreshes based on a rolling 10-day window ending on the current date.
- Results are cached per session to avoid redundant API calls.

## License

This project is for educational purposes as part of an astronomy course final project.
