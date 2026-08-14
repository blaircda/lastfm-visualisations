# lastfm visualisations
searching for structure in my music listening history

running at https://lastfm-visualisations-antiselfdual.streamlit.app/

## instructions

Download data from LastFM to CSV file via https://mainstream.ghan.nl/export.html

In **config.py**
- specify csv file

- specify artists, tracks, albums to exclude

- specify timezone whereabouts e.g. ("2008-01-01", "2015-01-01", "Europe/Dublin")

- specify custom time ranges to focus on e.g. "Undergraduate": ("2008-01-01", "2012-01-01")

Run app:
- streamlit run app.py

## process
- analyses play history for combinations "artist", "track"-"artist" and "album"-"artist"

- shows e.g. calendar yearly, monthly play history, aggregations by month, weekday, (local) hour

- shows play history since first listen of particular items, fits power law plots to these

- shows calendar year record of new vs old plays

## limitations
- the download from LastFM includes MusicBrainz identifiers however with a large number of missing entries I did not use this in favour of just "track"-"artist", "album"-"artist". This means that I do not take into account missing album data, difference between album and live versions of tracks, and similar annoyances

- it's not a fully fledged app allowing other users to upload their music history/access from LastFM directly
