Configuring BandPlacer
======================

BandPlacer is configured using a JSON or YAML file.

The main sections are `Placing` and `Scoring`.

The `Placing` section controls the placing of ringers in a band,
switching between adding learners and adding helpers.  This is done
using the total score of those placed so far.

`Placing:Lower` is the level below which more helpers should be added
(if available).  Setting this to zero, along with a high setting for
`Placing:Upper`, will force BandPlacer to place only one learner in
each touch.

`Placing:Upper` is the level at which it can switch back from adding
helpers to adding more learners.
