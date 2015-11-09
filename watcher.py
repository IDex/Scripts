#!/bin/env python3
"""
Watch unseen videos in a folder automatically
"""
import os
import re
import json
import subprocess as sp
import argparse

FOLDER = os.path.expanduser('~/new/')


class Watcher:
    """
    Shows unwatched videos in a folder.
    """

    def __init__(self, files, folder, nosave=False):
        self.folder = folder
        self.watched = self.load()
        self.matches = self.find(files)
        self.nosave = nosave
        self.savefile = '/watched.json'

    def save(self):
        if not self.nosave:
            with open(os.path.dirname(os.path.realpath(__file__)) +
                      self.savefile, 'w') as f:
                json.dump(self.watched, f)

    def load(self):
        """
        Load watched videos in the directory and return them.
        """
        watched = []
        try:
            with open(os.path.dirname(os.path.realpath(__file__)) +
                      self.savefile, 'r') as f:
                watched = json.load(f)
        except Exception as e:
            print('{} while loading json'.format(e))
        return watched

    def find(self, files, include_watched=False):
        """Find files from video dir and return them."""
        arg = '.*'.join(files)
        if include_watched:
            matches = [x for x in os.listdir(FOLDER)
                       if re.search(arg, x, re.IGNORECASE)]
        else:
            matches = [x for x in os.listdir(FOLDER)
                       if re.search(arg, x, re.IGNORECASE) and
                       x not in self.watched]
        return matches

    def clear(self, regex):
        """
        Clear files specified by regex from watched or the last one watched.
        """
        if regex:
            to_be_removed = self.find(regex, include_watched=True)
            self.watched = [x for x in self.watched if x not in to_be_removed]
        else:
            self.watched.pop()
        self.save()

    def remove(self):
        """
        Remove watched from watched directory
        """
        for f in self.watched:
            try:
                os.remove(FOLDER + f)
            except FileNotFoundError:
                print('Missing file:', f)

    def playone(self, f=None):
        """Play one file from unwatched"""
        if not f:
            f = sorted(self.matches).pop()
        print('Playing {}'.format(f))
        if sp.call(['mpv', '--fs', self.folder + f], stdout=sp.DEVNULL):
            return
        else:
            self.watched.append(f)
            self.save()

    def playall(self, nonstop=True):
        for f in sorted(self.matches):
            print('Playing {}'.format(f))
            if nonstop:
                if not sp.call(['mpv', '--fs', self.folder + f],
                               stdout=sp.DEVNULL):
                    self.watched.append(f)
                    self.save()
                else:
                    return
            else:
                if self._ask():
                    return

    @staticmethod
    def _ask():
        if 'n' in input('Play next?[Y/n]'):
            return True
        else:
            return False


def main():
    """
    Handle argument interpretation
    """
    parser = argparse.ArgumentParser(
        description=__doc__)
    parser.add_argument('-d', '--directory', default=FOLDER,
                        help='Specify directory for videos')
    parser.add_argument('-a', '--ask', action='count', default=0,
                        help='Watch one file at a time, get asked to continue')
    parser.add_argument('-c', '--clear', action='count',
                        help='Clear last seen/regex from watched.json')
    parser.add_argument('-n', '--nosave', action='store_true', default=False,
                        help="Don't save watched videos")
    parser.add_argument('-r', '--remove', action='store_true', default=False,
                        help='Remove watched files from watched directory')
    parser.add_argument('-l', '--list', action='store_true', default=False,
                        help='List watchable files instead of watching them')
    parser.add_argument('searchwords', nargs='*')
    args = parser.parse_args()
    watcher = Watcher(args.searchwords, args.directory, nosave=args.nosave)
    if args.remove:
        watcher.remove()
    if args.clear:
        watcher.clear(args.searchwords)
        raise SystemExit
    if args.list:
        for f in watcher.matches:
            print(f)
        raise SystemExit
    if args.ask:
        watcher.playall(args.ask)
    else:
        watcher.playall()

if __name__ == '__main__':
    main()
