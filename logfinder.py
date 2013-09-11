#!/usr/bin/env python

"""
This program takes 2 filenames as arguments.
It will output the lines from file1 where a similar line is not found in file2.
- The files are of syslog format
- date field is ignored in comparisons
- differences in any numeric field are also ignored.

The program works internally by splitting the message on numbers, and storing the
resulting array in a set of tuples.  
The split string serves to mark positions where numbers existed.  
If the non-numeric fragments of strings match in count and value, then the strings are considered equal.
"""
import sys
import re
from sets import Set
import unittest

class SyslogSet():
    reference_objs = Set()

    # public
    def AddLine(self,line):
        array = self.tokenize(line) 
        self.reference_objs.add(tuple(array))

    def LineExists(self,line):
        array = self.tokenize(line)
        return (tuple(array) in self.reference_objs)

    # helpers
    def tokenize(self,line):
        body = self.stripdate(line)
        tokens = self.split(body)
        return tokens

    def stripdate(self,line):
        pattern = re.compile("^[a-zA-Z]{3}\s+?\d\d?\s\d\d:\d\d:\d\d\s+?(?P<body>.*)$")
        m = pattern.search(line)
        if m and m.group('body'):
            return m.group('body')
        raise Exception("invalid syslog/date format")

    def split(self,line):
        tokens = re.split('[0-9]+', line)
        return tokens


class TestSyslogSet(unittest.TestCase): 
    def setUp(self):
        self.sc = SyslogSet()
        self.log = "Aug  31 19:35:34 ubuntu ntpd[7383]: 64.246.132.14 interface 172.16.208.165 -> (none)"

    def test_datehandling(self):
        # test our regex by providing interesting date formats
        self.assertEqual(self.sc.stripdate("Sep 10 07:55:18 two digit day"), "two digit day")
        self.assertEqual(self.sc.stripdate("Sep  9 08:17:10 one digit day"), "one digit day")
        # a broken date
        with self.assertRaisesRegexp(Exception, "invalid syslog/date format"):
            self.sc.stripdate("this is not a date")

    def test_split(self):
        self.assertEqual(self.sc.split("varying size equal 1"), self.sc.split("varying size equal 2000"))
        self.assertEqual(self.sc.split("varying size 1 equal"), self.sc.split("varying size 2000 equal"))
        self.assertNotEqual(self.sc.split(" numbers matter"), self.sc.split("100 numbers matter"))
        self.assertNotEqual(self.sc.split("numbers matter "), self.sc.split("numbers matter 100"))
        self.assertNotEqual(self.sc.split("numbers matter"), self.sc.split("numbers 100 matter"))

    def test_tokenizer(self):
        # visually reviewed:
        self.assertEqual(self.sc.tokenize(self.log), ['ubuntu ntpd[', ']: ', '.', '.', '.', ' interface ', '.', '.', '.', ' -> (none)'])

    def test_mapping(self):
        self.assertFalse(self.sc.LineExists(self.log))
        self.sc.AddLine(self.log)
        self.assertEqual(len(self.sc.reference_objs),1)
        self.assertTrue(self.sc.LineExists(self.log))
        self.sc.AddLine(self.log)
        self.assertEqual(len(self.sc.reference_objs),1)


def main():
    # help and unit-test are overloaded.
    if (len(sys.argv) != 3):
        print "usage: %s file1 file2" % sys.argv[0]
        print "lines from file1 will be output if similar lines do not exist in file2"
        unittest.main()

    file1 = file(sys.argv[1])
    file2 = file(sys.argv[2])
    # the above lines will provide reasnable errors if file cannot be found or opened

    syslogs = SyslogSet()

    for logline in file2:
        syslogs.AddLine(logline)

    for logline in file1:
        if not syslogs.LineExists(logline):
            print logline.rstrip()

if __name__ == "__main__":
    main()
