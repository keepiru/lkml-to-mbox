# lkml-to-mbox
Import messages from the LKML list archives into an mbox for easy reading.

The Linux Kernel Mailing List (and related sublists) are archived in a git
repo with one message per commit.  This program walks through that history
and converts it into an mbox for easy browsing with a mail client like mutt.
Run it with no arguments to see usage.
