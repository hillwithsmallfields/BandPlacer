Using BandPlacer from the command line
======================================

Installation
------------

The main BandPlacer code is in a single Python file,
src/bandplacer.py, for ease of installation.

General
-------

The command line arguments to bandplacer.py include options (given
with `--`) and commands (at the end of the command line).

Configuration is read from a JSON or YAML file specified with
`--config`.

File usage
----------

The progress data for a session is kept in a JSON format file,
referred to as "the records file".  bandplacer.py reads this every
time it starts, and writes back any changes to it when it finishes.

bandplacer.py writes the details of the band for each touch to
numbered CSV files in "the touches directory".  Other software (a text
editor, spreadsheet, or an interface to software such as HawkEar) adds
the scoring of a touch to these files, which bandplacer.py can then
read to integrate into the records file.

Registration
------------

Ringers can be added to the records file individually with the
`ringer` command, which takes a name and an email address as its
arguments; or they can be added collectively using `--import` from a
CSV file, which should include the columns `Name`, `Email`,
`Learning`, and `Ringing`, the latter two being semicolon-delimited
lists of method names.

Details of a ringer can also be imported from a JSON file with
`--import`, these files being produced with `--export`, which allows
ringers to keep their own records and provide them when registering
with another BandPlacer session.

Listing the data
----------------

The data in the records file can be viewed with the commands `ringers`
and `methods`, and the ringers who are learning or can ring a selected
method can be listed with the `for` command, which takes the name of a
method.

Placing ringers
---------------

There are two commands for placing a band: `place`, which takes a
method name, and `--pick`, which chooses the method automatically
according to learning demand.

Both these commands write a numbered CSV file to the touches
directory, with columns `Bell` and `Ringer` filled in, and an empty
`Score` column.  There is also a 'Method' column, which is filled in a
row not containing a ringer placement.

Reading results
---------------

There are two commands for reading the touches files with their
results: `score` to read a specific file, and `update` to read any
files in the touch directoy that have not yet been incorporated into
the records file.

Placing and reading together
----------------------------

The command `next` will pick a method and place a band as for the
command `pick`, then run a program or script specified in
`Commands:RingAndScore` in the configuration, then read any results
that haven't yet been read, as the `update` command does.

When the specified program or script exits, control returns to
bandplacer.py, which will then read the (hopefully updated) touch
file.

The text in `Commands:RingAndScore` should have one `%06d`
substitution in it, to make the touch file filename, which should
correspond to a numbered file in the touches directory.  The program
or script it runs should display the touch file so ringers can see
which bell they're on and what the method is, then modify the file to
include the scores once the touch has been rung.  The file is a CSV
file, so either a spreadsheet program or a text editor should be
suitable.  This script is also where an interface to HawkEar or
similar would be placed.
