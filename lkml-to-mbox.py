#!/usr/bin/python
#
# The Linux Kernel Mailing List (and related sublists) are archived in a git
# repo with one message per commit.  This program walks through that history
# and converts it into an mbox for easy browsing with a mail client like mutt.
# Run it with no arguments to see usage.
#
#  Copyright (C) 2025 Chris Frederick
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


import datetime
import email
import re
import subprocess
import sys

def generate_envelope_from(msg):
    """ Generate a From line in mbox format.
    We don't have the envelope sender and timestamp, so we're going to generate
    them from the From: and Date: headers.  Those aren't guaranteed to be
    present and valid, so we'll just use fake ones if they're missing.

    TODO: The Received: headers are potentially a better source for the date.

    Args:
      msg (email.message.Message): The email message.

    Returns:
      str: a mbox format From line.A
    """

    # Find or fake the sender's address
    from_line = msg.get('From')
    if not from_line:
        from_line = 'From: unknown@example.com'

    # The From: line may contain a raw address, or a name with the address
    # enclosed in angle brackets: John Doe <jdoe@example.com>
    # Strip it down to just the address.
    from_address = re.sub(r'.*<|>.*', '', from_line)

    # Find or fake the time sent
    date_line = msg.get('Date')                                     # 'Sat, 3 Jan 1970 12:34:56 -0800'
    if not date_line:
        date_line = 'Sat, 3 Jan 1970 12:34:56 -0800'                # Fake it if it's missing
    date_tuple = email.utils.parsedate_tz(date_line)                # (1970, 1, 3, 12, 34, 56, 0, 1, -1, -28800)
    timestamp = email.utils.mktime_tz(date_tuple)                   # 246896
    dt = datetime.datetime.fromtimestamp(timestamp)                 # datetime.datetime(1970, 1, 3, 12, 34, 56)
    date_formatted = dt.ctime()                                     # 'Sat Jan  3 12:34:56 1970'

    from_line = f"From {from_address} {date_formatted}"             # From unknown@example.com Sat Jan  3 12:34:56 1970'
    return from_line

def append_msg_to_mbox(message_filename, mbox_filename):
    """ Read a message from a file and append it to an mbox.

    Args:
      message_filename (str): The name of a file containing a single message.
      mbox_filename(str): The name of the output mbox where we will append the message.
    """

    # Read the raw message in.  Ignore utf-8 errors - we're going to
    # copy the message over verbatim.
    with open(message_filename, 'r', errors='ignore') as fh:
        msg = email.message_from_file(fh)

    from_line = generate_envelope_from(msg)

    # Append to the mbox file
    with open(mbox_filename, 'a') as mbox:
        mbox.write(from_line + '\n')
        mbox.write(msg.as_string())  # Append the entire email content
        mbox.write('\n')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <count>")
        print("Import messages from a LKML-style git repo.")
        print("Messages will be read from 'm' (how the LKML does it) and appended to 'mbox'.")
        print("First check out the LAST message you want to read, and then this script will work its way")
        print("back for <count> messages.")
        print("for example, to import the last 1000 messages:")
        print("  $ git checkout origin/master")
        print(f"  $ {sys.argv[0]} 1000")
        sys.exit(1)

    count = int(sys.argv[1])

    for i in range(count):
        sys.stdout.write("%10d\r" % i)  # progress indicator
        append_msg_to_mbox('m', 'mbox')

        # Now try to check out the previous message
        ret = subprocess.call(['git', 'checkout', '-q', 'HEAD^'])
        if ret != 0:
            raise(Exception('git returned nonzero.  Maybe that was the last message?'))

