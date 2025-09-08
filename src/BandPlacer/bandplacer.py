#!/usr/bin/env python3

"""Advancing ringing for the rest of us.

Code to arrange change-ringing learning sessions, using spaced
repetition.
"""

import argparse
import cmd
import collections
import csv
import datetime
import json
import os
import random
import shlex
import sys

STAGE_BELLS = [
    None,
    None,
    None,
    "singles",
    "minimus",
    "doubles",
    "minor",
    "triples",
    "major",
    "caters",
    "royal",
    "cinques",
    "maximus",
    ]

def nbells(method_name: str):
    """Return the number of bells in a method."""
    return STAGE_BELLS.index(method_name.split(' ')[-1].lower())

LARGE_POSITIVE_NUMBER = 1000000000

class Ringer:

    """The data and methods for a ringer."""

    def __init__(self, name: str,
                 email="",
                 learning_status=None,
                 group=None):
        self.name = name
        self.email = email
        # method names to lists of place bell scores:
        self.learning_status = learning_status or {}
        if group:
            group.ringers[name] = self

    def __str__(self):
        return "%s <%s>" % (self.name, self.email)

    def __repr__(self):
        return ("<Ringer %s <%s> with %d methods>"
                % (self.name, self.email, len(self.learning_status)))

    def to_dict(self):
        """Return a JSON-serializable dictionary representing this ringer."""
        return {
            'name': self.name,
            'email': self.email,
            'learning-status': self.learning_status
        }

    def merge_from_dict(self, data):
        """Add some data to a ringer's records."""
        if 'name' in data:
            self.name = data['name']
        if 'email' in data:
            self.email = data['email']
        if 'learning-status' in data:
            for method_name, method_scores in data['learning-status'].items():
                if method_name in self.learning_status:
                    for place, score in enumerate(method_scores):
                        # The incoming data may be from a scoring
                        # system, in which case only one, or only
                        # some, of the place bells may be scored, and
                        # we don't want to disturb those that aren't:
                        if score is not None:
                            self.learning_status[method_name][place] = score
                else:
                    self.learning_status[method_name] = method_scores

    def method_learning_status(self, method):
        """Return this ringer's learning status for the specified method.

        A learning status is a list of numbers, indexed by place bell.

        A negative number indicates that this ringer counts as a
        learner for that place bell, and a positive number indicates
        that they have learnt that place bell, and so count as a
        helper.
        """
        method_name = asMethodName(method)
        if method_name not in self.learning_status:
            self.learning_status[method_name] = [0.0] * nbells(method_name)
        return self.learning_status[method_name]

    def set_method_place_bell_score(self, method, place_bell, score):
        """Set this ringer's score for a place bell of a method."""
        self.method_learning_status(method)[place_bell-1] = score

    def adjust_method_place_bell_score(self, method, place_bell, score_increment):
        """Adjust this ringer's score for a place bell of a method."""
        self.method_learning_status(method)[place_bell-1] += score_increment

class AttendeeGroup:

    """A group of ringers."""

    def __init__(self):
        self.ringers = {}

    def ringer(self, ringer, **kwargs):
        """Return a Ringer object, given a name or a Ringer object.

        If there is already an object for a ringer of that name, that
        existing object is returned.

        This registers the ringer in the attendee group, as a side
        effect.
        """
        return (ringer
                if isinstance(ringer, Ringer)
                else (self.ringers[ringer]
                      if ringer in self.ringers
                      else Ringer(name=ringer, group=self, **kwargs)))

    def add_ringer(self, name, email=""):
        """Add a ringer to the attendee group."""
        # registers by side effect
        self.ringer(name, email=email)

    def list_ringers(self):
        for name in sorted(self.ringers.keys()):
            data = self.ringers[name]
            print("Ringer", name, data.email or "(no email)")
            ringer_learning_status = data.learning_status
            method_names = sorted(ringer_learning_status.keys())
            for methname in method_names:
                print("  ", methname, ringer_learning_status[methname])

class Method:

    """A change-ringing method."""

    def __init__(self, name: str, stage: int or None):
        self.name = name
        self.stage = stage or nbells(name)
        self.place_notation = None
        self.bob = None
        self.single = None
        self._rows = None

    def __str__(self):
        return "<Method %s>" % self.name

def asMethod(method):
    return method if isinstance(method, Method) else Method(method)

def asMethodName(method):
    return method.name if isinstance(method, Method) else method

class Call:

    """Anything that can be called during a touch.

    This will normally be a bob, single, or change of method."""

    pass

class Lead(Call):

    """A call to switch to ringing a specified method."""

    def __init__(self, method: Method):
        self.method = method

class LeadEndVariant(Call):

    """A call, such as a bob or single."""

    def __init__(self, call_type: str):
        self.call_type = call_type

class Touch:

    """A piece of ringing, made up of at least one call."""

    def __init__(self, practice, method_name, ringers=None):
        self.practice = practice
        self.method_name = method_name
        self.ringers = ringers or []

    def _filename(self, number):
        result = os.path.join(self.practice.touch_directory,
                              "%06d.csv" % number)
        print("touch filename is", result)
        return result

    def save(self, number):
        with open(self._filename(number), 'w') as ts:
            writer = csv.DictWriter(ts, fieldnames=['Bell', 'Ringer', 'Score', 'Method'])
            writer.writeheader()
            writer.writerow({'Method': self.method_name})
            for i, ringer in enumerate(self.ringers):
                writer.writerow({'Bell': i+1, 'Ringer': ringer})

    def load(self, number):
        pass # TODO

def worst_lead_except(scores, not_these):
    """Return the worst lead for each ringer in the given scores,
    except the not_these leads.
    scores is a list of scores.
    not_these is a list of indices to skip."""
    worst_v = LARGE_POSITIVE_NUMBER
    worst_i = None
    for i, v in enumerate(scores):
        if (not not_these[i]) and v < worst_v:
            worst_i = i
            worst_v = v
    return worst_i

def worst_leads_except(ringers_scores, not_these):
    """Return the worst lead for each ringer in the given scores,
    except the not_these leads.
    scores is a list of scores.
    not_these is a list of indices to skip."""
    return {ringer: worst_lead_except(scores, not_these)
            for ringer, scores in ringers_scores.items()}

def key_of_lowest_value(dictionary):
    """Return the key corresponding to the lowest value in the dictionary."""
    lowest_k = None
    lowest_v = LARGE_POSITIVE_NUMBER
    for k, v in dictionary.items():
        if v < lowest_v:
            lowest_k = k
            lowest_v = v
    return lowest_k

def _row_methods(row, col_label):
    """Return the method names from a CSV table cell.
    Within the cell, they should be semicolon-separated."""
    if (col_label not in row
        or not row[col_label]):
        return []
    return [name.strip()
            for name in row[col_label].split(';')]

class Practice(cmd.Cmd):

    """A session for practicing ringing."""

    def __init__(self,
                 config_file=None,
                 records_file=None,
                 touch_directory=None,
                 ringers=None,
                 methods=None):
        self.config = {
            'Placing': {
                'Lower': -1,
                'Upper': 1,
            },
            'Scoring': {
                'Increment': 0.5,
                'Decrement': 0.4,
            }
        }
        if config_file:
            if config_file.endswith('.json'):
                with open(config_file) as conf:
                    self.config = json.load(conf)
            elif config_file.endswith('.yaml'):
                with open(config_file) as conf:
                    self.config = yaml.safe_load(conf)
            else:
                print("Don't know how to load config file", config_file)
        self.records = records_file or self.config.get('Files', {}).get('Records')
        self.touch_directory = os.path.expanduser(
            os.path.expandvars(
                touch_directory
                or (self.config.get('Files', {})
                    .get('TouchDirectory', "$HOME/ringing/touches"))))
        os.makedirs(self.touch_directory, exist_ok=True)
        self.attendees = AttendeeGroup()
        self.methods = {name: asMethod(name) for name in methods or []}
        self._by_method = None
        if self.records and os.path.exists(self.records):
            with open(self.records) as recs:
                try:
                    self.from_dict(json.load(recs))
                except json.decoder.JSONDecodeError:
                    print("Could not load records from", self.records)
        self.latest_written_touch_number = None

    def do_save(self, _cmd_str=None):
        if self.records:
            with open(self.records, 'w') as recs:
                json.dump(self.to_dict(), recs, indent=4)

    def from_dict(self, data):
        """Load this practice from a data dictionary as produced by self.to_dict()."""
        for name, data in data.get('records', {}).items():
            ringer = self.attendees.ringer(name)
            ringer.learning_status.update(data['learning-status'])
            ringer.email = data.get('email', '')
        self.latest_written_touch_number = data.get('latest-touch-number', None)

    def to_dict(self):
        """Make a JSON-serializable data dictionary representing this practice."""
        return {
            'timestamp': datetime.datetime.now().isoformat(timespec='seconds'),
            'command': shlex.join(sys.argv),
            'records': {
                name: ringer.to_dict()
                for name, ringer in self.attendees.ringers.items()
            },
            'latest-written-touch-number': self.latest_written_touch_number
            # TODO: perhaps record what was rung at each practice, as
            # a dict keyed by timestamp
        }

    def add_ringer(self, table_row):
        name = table_row['Name']
        self.attendees.add_ringer(name, table_row['Email'])
        for method in _row_methods(table_row, 'Ringing'):
            self.attendees.ringers[name].learning_status[method] = [1] * nbells(method)
        for i, method in enumerate(_row_methods(table_row, 'Learning')):
            self.attendees.ringers[name].learning_status[method] = [-1/(i+1)] * nbells(method)

    def scores_by_method(self):
        """Return the current scores for each method."""
        if not self._by_method:
            self._by_method = collections.defaultdict(lambda: collections.defaultdict(dict))
            for ringer in self.attendees.ringers.values():
                for method, scores in ringer.learning_status.items():
                    self._by_method[method][ringer.name] = scores
        return self._by_method

    def ringers_for_method(self, method):
        return self.scores_by_method()[asMethodName(method)]

    def learners_for_method(self, method):
        """Return a dict binding learner names to their scores.

        A ringer counts as a learner if they have any negative scores
        for that method.
        """
        return {name: scores
                for name, scores in self.ringers_for_method(method).items()
                if any(s < 0 for s in scores)}

    def demand_for_method(self, method):
        """Return how much demand there is for learning a method."""
        return -sum(sum(scores)
                    for scores in self.learners_for_method(method).values())

    def methods_by_demand(self):
        """Return a dict binding method names to the demand for the methods."""
        return {name: self.demand_for_method(name)
                for name in self.scores_by_method().keys()}

    def methods_in_order_of_demand(self):
        demands = self.methods_by_demand()
        return sorted(demands.keys(),
                      key=lambda x: demands[x],
                      reverse=True)

    def methods_with_band_available(self):
        print("scores by method are", self.scores_by_method())
        return set([method_name
                    for method_name, scores in self.scores_by_method().items()
                    if len(scores) >= nbells(method_name)])

    def methods_in_order_of_demand_with_band_available(self):
        possible = self.methods_with_band_available()
        return [method
                for method in self.methods_in_order_of_demand()
                if method in possible]

    def most_demanded_method_with_band_available(self):
        """Return the most demanded method for which enough ringers are available."""
        return self.methods_in_order_of_demand_with_band_available()[0]

    def helpers_for_method(self, method):
        """Return a dict binding helper names to their scores.

        A ringer counts as a helper for a method if all their scores
        for that method are positive.
        """
        return {name: scores
                for name, scores in self.ringers_for_method(method).items()
                if all(s >= 0 for s in scores)}

    def place_band(self, method, lower_threshold=-2, upper_threshold=2):
        """Place a band for a method."""
        band = [None] * nbells(method)
        band_scores = [0] * nbells(method)
        learners = self.learners_for_method(method)
        helpers = self.helpers_for_method(method)
        placing_learners = True
        while not all(band):
            if not learners:
                placing_learners = False
            if placing_learners:
                each_worst_lead = worst_leads_except(learners, band)
                most_needs_practice = key_of_lowest_value(each_worst_lead)
                bell_to_allocate = each_worst_lead[most_needs_practice]
                worst_lead_score = learners[most_needs_practice][bell_to_allocate]
                band[bell_to_allocate] = most_needs_practice
                band_scores[bell_to_allocate] = worst_lead_score
                del learners[most_needs_practice]
            else:
                for i, p in enumerate(band):
                    if not p:
                        # place a helper
                        helper = random.choice(list(helpers.keys()))
                        helper_score = helpers[helper][i]
                        band[i] = helper
                        band_scores[i] = helper_score
                        del helpers[helper]
                        # we place just that one helper here, then go to the outer loop:
                        break
            overall_score = sum(band_scores)
            if overall_score < lower_threshold and helpers:
                placing_learners = False
            elif overall_score > upper_threshold and learners:
                placing_learners = True
        return band

    def do_place(self, method_name):
        """Place a band for a specified method."""
        touch = Touch(practice=self,
                      method_name=method_name,
                      ringers=self.place_band(method=method_name))
        self.latest_written_touch_number = self.next_touch_number()
        touch.save(self.latest_written_touch_number)

    def do_next(self, cmd_str):
        """Choose a method and place a band for the next touch."""
        method_name = self.most_demanded_method_with_band_available()
        touch = Touch(practice=self,
                      method_name=method_name,
                      ringers=self.place_band(method=method_name))
        self.latest_written_touch_number = self.next_touch_number()
        touch.save(self.latest_written_touch_number)

    def score_from_touch(self, touch):
        """Incorporate the scores from a touch file."""
        pass                    # TODO: fill this in

    def do_score(self, touch_number_str):
        """Read the scores from a specified touch file."""
        self.score_from_touch(Touch(practice=self).load(int(touch_number_str)))

    def do_update(self, cmd_str):
        """Read all the scores that have not yet been read."""
        pass                    # TODO fill this in

    def do_step(self, cmd_str):
        """Choose a method, place a band, and read their scores."""
        self.do_next(cmd_str)
        subcmd = self.config.get("RingCommand")
        if subcmd:
            os.system(subcmd % self.latest_written_touch_number)
        self.do_update()

    def do_methods(self, cmd_str):
        """List the methods, with their scores."""
        scores = self.scores_by_method()
        for method_name in sorted(scores.keys()):
            print(method_name)
            data = scores[method_name]
            for ringer in sorted(data.keys()):
                print("  ", ringer, data[ringer])

    def do_for(self, cmd_str):
        print(len(cmd_str), "cmd_str of for are:", cmd_str)
        method_name = cmd_str.strip()
        print("Ringers for", method_name)
        ringers = self.ringers_for_method(method_name)
        for name in sorted(ringers.keys()):
            print("  ", name, ringers[name])
        print("Learners for", method_name)
        learners = self.learners_for_method(method_name)
        for name in sorted(learners.keys()):
            print("  ", name, learners[name])
        print("Total demand for learning", method_name, "is", self.demand_for_method(method_name))
        print("Helpers for", method_name)
        helpers = self.helpers_for_method(method_name)
        for name in sorted(helpers.keys()):
            print("  ", name, helpers[name])

    def next_touch_number(self):
        files = sorted([filename
                        for filename in os.listdir(self.touch_directory)
                        if filename.endswith('.csv')],
                       reverse=True)
        return int(files[0].split('.')[0])+1 if files else 0

    def do_ringers(self, cmd_str):
        self.attendees.list_ringers()

def get_args():
    """Get the command line arguments."""
    parser = argparse.ArgumentParser(
        description="""Program to help run method-learning change-ringing practices.""")
    # Input data:
    parser.add_argument(
        "--config",
        help="""The name of the configuration file to use.""")
    parser.add_argument(
        "--touch-directory", "-t",
        help="The directory to store touch files in.")
    parser.add_argument(
        "--method", "-m",
        action='append',
        help="""Add this method to the methods available to the session.""")
    parser.add_argument(
        "--ringer", "-r",
        action='append',
        nargs=2,
        help="""Add this ringer to the ringers attending the session.""")
    parser.add_argument(
        "--records", "-R",
        help="""The file to load training records from and save them to.""")
    parser.add_argument(
        "--import-record", "--import", "-i",
        action='append',
        help="""Import a ringer's record from a JSON file,
        or multiple entries from a CSV file.""")
    # Commands:
    parser.add_argument(
        "--place", "--place-for", "-p",
        help="""Place a band for a specified method.""")
    parser.add_argument(
        "--next", "-n",
        action='store_true',
        help="""Place a band for the next touch, choosing the method automatically.""")
    parser.add_argument(
        "--list-ringers", action='store_true')
    parser.add_argument(
        "--list-methods", action='store_true')
    parser.add_argument(
        "--ringers-for")
    parser.add_argument(
        "action",
        nargs='*')
    return vars(parser.parse_args())

def practice_main(
        method=None,
        touch_directory=None,
        ringer=None,
        records=None,
        import_record=None,
        place=None,
        next=False,
        list_ringers=False,
        list_methods=False,
        score=None,
        ringers_for=None,
        config=None,
        action=None,
):
    """Run a practice action."""
    practice = Practice(config_file=config,
                        records_file=records,
                        touch_directory=touch_directory)
    for method_name in method or []:
        practice.methods[method_name] = asMethod(method_name)
    for ringer_name, ringer_email in ringer or []:
        practice.attendees.add_ringer(ringer_name, email=ringer_email)
    for record in import_record or []:
        if record and os.path.exists(record):
            if record.endswith(".csv"):
                with open(record) as recstr:
                    for row in csv.DictReader(recstr):
                        print("adding ringer from row", row)
                        practice.add_ringer(row)
            elif record.endswith(".json"):
                with open(record) as recstr:
                    rec_data = json.load(recstr)
                    practice.attendees.ringer(rec_data['name']).merge_from_dict(rec_data)
            else:
                print("Cannot import this type of file:", record)

    # practice actions:
    for action_str in action or []:
        practice.onecmd(action_str)

    # if list_ringers:
    #     practice.list_ringers()
    # if list_methods:
    #     practice.list_methods()
    # if ringers_for:
    #     practice.list_ringers_for_method(ringers_for)
    # if place:
    #     print(practice.place_band(place))
    # if next:
    #     print(practice.place_band(practice.most_demanded_method_with_band_available()))

    # save records:
    practice.do_save()

if __name__ == "__main__":
    practice_main(**get_args())
