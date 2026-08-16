# Design engine

`generate_initial_layout()` proceeds in fixed stages:

1. Creates the terrain boundary through `geometry.create_rectangle`.
2. Reserves a hard conservation strip, then packs water, recreation, education, rest, meadow and entrance zones without polygon overlap.
3. Builds a pedestrian trunk from the entrance through conservation, recreation, education and rest zones, with secondary and optional bicycle paths.
4. Recommends from a small preliminary plant catalog.
5. Calculates metrics and cost estimate.
6. Applies area, overlap, accessibility, connectivity, conservation, water, slope and budget rules.
7. Scores the validated layout.

The planner never trusts coordinates from an LLM. Future optimizers may propose parameter changes only and must call the same planner and validator.
