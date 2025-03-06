[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18392968)

# Unemployment Insight Hub

A dynamic web application built with Dash that visualizes unemployment trends across different dimensions including gender, regional distribution, and London-specific analysis.

## Features

- Gender-based unemployment analysis
- Regional unemployment comparisons
- London-specific unemployment trends
- Trend comparison tools
- Interactive navigation
- Responsive design

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/unemployment-insight-hub.git

```

2. Install dependencies:

```bash
pip install -e ".[dev]"
```

3. Open your web browser and navigate to `http://localhost:8050`

## Data Structure

The application uses an SQLite database with the following tables:
- `gender_unemployment`: Gender-based unemployment rates by year
- `UnemploymentRateByRegion`: Regional unemployment rates
- `TimePeriod`: Time period reference data
- `Region`: Region reference data

## Development

To set up the development environment:

```bash
pip install -r requirements.txt
```
