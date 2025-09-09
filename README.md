BandPlacer
==========

BandPlacer places bands for learning change-ringing methods one lead
at a time, using spaced repetition.

It originated as part of a plan to arrange intensive method-learning
practices for those whose local practices don't give them the
opportunity to ring more advanced methods, whether because of not
having a band who can ring such methods, or because of their tower
captain not thinking them ready for more methods.

These conditions mean that there might not be expert ringers and
conductors at the intensive practices, so the ringing will be one lead
at a time, to avoid depending on having someone who can put the
ringing right.  In turn, this means that the time from a mistake to
the opportunity to look back at what went wrong will be quite short,
and the mistakes will still be remembered well enough to work out what
happened.

A BandPlacer practice (or course) will typically be for a range of
methods, such as "surprise major methods from the standard eight, core
seven and Horton's four".  Ideally, there should be some participants
who are already confident in the easier methods and are looking for
opportunities to ring the harder ones (and can help with the easier
ones), and some who are learning the easier ones.

Before or at the start of the practice, ringers register for it,
indicating which methods they are learning and which they are already
confident in.

How it works
------------

BandPlacer keeps a score for each participant, for each place bell of
each method.  The scores start as negative for those who are learning
that method, and positive for those who have indicated that they are
already confident in that method.

Before each (one-lead) touch, BandPlacer selects the method with the
most negative total of the negative scores --- that is, the method
with the greatest learning demand.  It then finds the ringer with the
lowest score in any place bell of that method, and places them on that
bell; and then works through successively less negative scores.  It
monitors the total score of the ringers it has placed so far, and if
it drops below a set threshold, switches to placing helpers (ringers
with positive scores for those leads), until it has placed a complete
band.

Then the lead is rung, and the ringers given marks for whether they
have rung that place bell successfully.  This could be done manually,
either by self-assessment or consensus, or automatically with data
from Hawkear or similar if available.

The ringers' scores for the place bells they rang are then adjusted: a
successful lead adds to their score, making it less negative, so they
are less likely to be placed on that place bell of that method again;
an unsuccessful lead makes their score for it more negative, which
will reduce the time before they are placed on it again.  Multiple
successful attempts at a place bell will eventually make the score
for it positive; they will now count as a helper for that lead.

This is meant to focus the learning on the leads (and ringers) that
need it most.

Scores for individual ringers can be exported for them to download, so
the tower doesn't need to keep any information long-term (and the
users can import their data into BandPlanner sessions elsewhere).

Further information
-------------------

 - [Command line manual](doc/command-line-manual.md)
 - [Configuration](doc/configuration.md)
 - [Usage scenarios](doc/scenarios.md)
 