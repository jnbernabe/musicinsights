# Music Insights 🎧

**Music Insights** is a powerful visual analytics dashboard designed to help music lovers understand their Spotify playlists on a deeper level. By analyzing audio features, patterns, and listening habits, it transforms raw data into a beautiful, interactive "Deep Space" themed experience.

## 🚀 Objective

The goal of this project is to provide users with meaningful insights into their music taste that goes beyond simple "Top 10" lists. It answers questions like:
- *"What is the overall 'vibe' of this playlist?"*
- *"Do I prefer high-energy tracks or melancholic ones?"*
- *"Which musical eras dominate my library?"*
- *"Who are my true favorite artists based on listening time, not just play counts?"*

## ✨ Key Features

### 📊 Interactive Dashboard
Upload your Spotify playlist CSV (via [Exportify](https://exportify.net)) to instantly generate a comprehensive dashboard featuring:

*   **Mood Map:** A dynamic scatter plot visualizing the emotional landscape of your music (Energy vs. Positivity).
*   **Audio Profile:** A radar chart breaking down acoustic characteristics (Danceability, Acousticness, etc.).
*   **Tempo Analysis:** See distribution of BPMs to understand if you like it fast or slow.
*   **Era Distribution:** Discover which decades your music taste lives in.
*   **Popularity Trends:** Analyze how mainstream or obscure your library is.
*   **Top Artists & Tracks:** Detailed tables and charts ranking your favorites by both count and duration.

### 🔍 Deep Cuts & Discovery
Uses the Spotify API to unlock **"Essential Deep Cuts"**. The app analyzes your top artists and identifies their popular tracks that are *missing* from your playlist, helping you complete your collection.

### ⚡ Interactive Filtering
Click on charts to filter the entire dashboard!
*   Select a genre to see only tracks from that genre.
*   Click an era bar to travel back in time.
*   All tables and metrics update instantly to reflect your selection.

### 🎨 Deep Space Theme
Built with a premium "Dark Mode" aesthetic featuring glassmorphism, neon accents (Spotify Green, Cyan, Pink), and smooth micro-interactions for a polished user experience.

## 🛠️ How It Works

1.  **Upload:** Drop your `playlist.csv` into the upload zone.
2.  **Analyze:** The backend processes the file, calculating stats and aggregating data locally.
3.  **Explore:** Dive into your personalized dashboard.
4.  **Connect (Optional):** Link Spotify to get song recommendations.

## 💻 Tech Stack

*   **Django** (Python) for robust backend processing.
*   **Pandas** for high-performance data analysis.
*   **Apache ECharts** for stunning, responsive visualizations.
*   **Spotify Web API** for fetching metadata and recommendations.

## Features
- **Upload & parsing** – drop in an Exportify CSV and the `exportify_parser` service normalizes tracks, albums, artists, and playlist entries in SQLite.
- **Snapshot dashboards** – see total track counts plus ranked tables for artists, songs, and playlists along with a Chart.js line graph of additions per month.
- **Personalized nudges** – the recommendation service scans listening streaks (top artists, time of day, biggest playlists) and surfaces actionable suggestions.
- **File history** – every upload is stored so new files can be processed without touching older data.
- **Extensible services** – parsing, stats, and recommendations live in `musicinsights/services/`, making it easy to plug in new heuristics or support JSON inputs later.

## Tech Stack
- Python 3.11+ and Django 5.2.8
- SQLite for local persistence (configurable via `DATABASES` in `musicdata/settings.py`)
- Chart.js over CDN for the dashboard visualization

## Getting Started
1. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. **Install dependencies**  
   The project currently uses core Django only:
   ```bash
   pip install "Django>=5.2,<6.0"
   ```
3. **Apply migrations & run the dev server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
4. Open http://127.0.0.1:8000/ in your browser.

## Usage
1. Export a playlist from Exportify (CSV format).  
2. Visit the upload page (`/`) and submit the CSV file.  
3. You are redirected to `/dashboard/<upload_id>/`, which shows:
   - Total tracks processed
   - Top artists, tracks, and playlists tables
   - Monthly track additions chart
   - Context-aware recommendations list

You can repeat the upload workflow for as many playlists as you like; each file is stored as an `Upload` record so nothing is overwritten.

## Project Layout
```
musicdata-project/
├── manage.py                # Django entry point
├── musicdata/               # Project settings & URL routing
├── musicinsights/           # Core app (models, views, services)
│   ├── models.py            # Upload, Artist, Album, Track, PlaylistEntry
│   ├── services/
│   │   ├── exportify_parser.py
│   │   ├── stats_service.py
│   │   └── recommendation_service.py
│   └── views.py             # Upload form + dashboard views
├── templates/
│   ├── base.html
│   └── musicinsights/
│       ├── upload.html
│       └── dashboard.html
└── media/                   # Stored uploads (via `Upload.original_file`)
```

## Extending the App
- Add new recommendation heuristics in `musicinsights/services/recommendation_service.py`.
- Support additional Exportify fields or alternate formats in `exportify_parser.py`.
- Enhance the dashboard by passing more data through `stats_service.build_dashboard_context`.
- Swap SQLite for Postgres by editing `DATABASES` in `musicdata/settings.py` and updating environment variables.

## Troubleshooting
- If a CSV fails to upload, confirm it ends with `.csv` and matches Exportify’s header names (`Track URI`, `Track Name`, etc.).
- The chart requires JavaScript; make sure the CDN is reachable from your environment.
- When editing locally, restart `runserver` after adding new dependencies or changing settings.

Happy playlist digging!
