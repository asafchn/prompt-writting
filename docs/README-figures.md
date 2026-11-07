# README figures

The images in `docs/img/` are screenshots of the figures in `readme-visuals.html`. Fonts are bundled in `docs/fonts/`, so the page renders the same offline.

To re-render, from `docs/` (needs `pip install playwright` and Chrome at `/usr/bin/google-chrome`):

```bash
python3 shoot.py readme-visuals.html img                 # all figures
python3 shoot.py readme-visuals.html img results,round2  # only these figure ids
```

Each figure is a `<figure id="...">`. The script captures each one at 2x scale, from a 1220 px-wide viewport, into `img/<id>.png`. To add a figure, give it a new id, then pass that id to the script.
