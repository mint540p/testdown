#!/usr/bin/python
# -*- coding: utf-8 -*-
"""down.py stores the global variables for downtest.py(to be changed to downloadbooks.py.

Copyright (c) 2018 by Ben Heisenburg<Heisenburg01@protonmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

    SCRIPT:     downloadbooks.py

See downloadbooks.py(or downtest.py) for directions and meanings for some variables.
"""

import threading

import weechatnick
import weechatvars

########################################################################
# Constants
########################################################################
SCRIPT_NAME = "DownloadBooks"
SCRIPT_AUTHOR = "Ben Heisenburg<Heisenburg01@protonmail.com>"
SCRIPT_VERSION = "0.1.15"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Downloads ebooks from undernet #bookz when you have limited \
        queue for a server nick"

# Title for the buffer to use instead of SCRIPT_NAME
BUFFER_TITLE = 'Download Books'

# From weechatvars.py, SERVER = 'under'  # 'us.undernet.org'
SERVER = weechatvars.IRC_SERVER
# From weechatvars.py, CHANNEL = '#bookz'
CHANNEL = weechatvars.DOWN_CHANNEL
# From weechatvars.py, FILENAME = 'books.txt'
FILENAME = weechatvars.ITEM_FILENAME
# From weechatvars.py, COMPLETEDBOOKS = 'completedBooks.txt'
COMPLETEDBOOKS = weechatvars.COMPLETED_ITEMS
# From weechatvars.py, ERRORBOOKS = 'errorBooks.txt'
ERROR_BOOKS = weechatvars.ERROR_ITEMS

UNDER_NOTIFY = "irc.server." + SERVER + ".notify"

# From weechatvars.py,  DESIREDNICK = weechatvars.MY_NICK, change this variable for your machine
DESIREDNICK = weechatnick.MY_NICK

# new buffer information to move away from weechat core buffer
BUFFER_NAME = 'DownloadBooks'
MY_BUFFER = None
MY_BAR = None

ONLINE = 'online'
NUM_IN_QUEUE = 'num_in_queue'
DOWNLOAD = 'downloading'
NUM_BOOKS = 'num_books'

NICK = 'nick'
TIME = 'time'

# Number of downloads for each bot/nick on channel
QUEUE_MAX = 2

# TIME variables in seconds
SECOND = 1
MINUTE = 60 * SECOND

# delay when starting up script, queue, etc.
TIME_DELAY = 30 * SECOND
# HOUR = 60 * MINUTE
# delay before requesting file after someone joins,
# takes this long to get OmenServe to start__lbcinrs
JOIN_DELAY = 2 * MINUTE + 30 * SECOND  # 355
# TO#DO - check if JOIN_DELAY and REQUEST_DELAY is working right.

# Delay for checking if someone has joined the channel after being on server (in milliseconds).
JOINING_DELAY = 10 * SECOND * 1000

REQUEST_DELAY = 25 * SECOND

T35_MINUTES = 35 * MINUTE
RE_REQUEST_DELAY = T35_MINUTES
SENDING_DELAY = 50 * MINUTE

########################################################################
# Variables
########################################################################


MOVE_HOOK_CHRONOLIST = None

BOOKLIST_LOCK__L = threading.Lock()
CHRONOLIST_LOCK__L = threading.Lock()
INQUEUE_LOCK__L = threading.Lock()
JOINING_CHRONOLIST_LOCK__L = threading.Lock()
NICKLIST_LOCK__L = threading.Lock()
RQ_LOCK__L = threading.Lock()
SENDING_LOCK__L = threading.Lock()

# BKLIST is a dictionary of the form {book:nick}
BKLIST = {}  # book list to download

CHRONOLIST = {}

# INQUEUE = { book: {nick, time} } ; sort of like bklist plus time item added
#  current books being downloaded, potential for download error
INQUEUE = {}  # # type: Dict[book:str, Dict[nick:str, time:time]]

JOINING_CHRONOLIST = {}

# NICKLIST = {nick: {online, num_in_queue, downloading, num_books} }
#  nicks for books to download= nick: {online(true|false)0,num_in_queue,
#  download, num_books}
NICKLIST = {}

# showing the format of  REQUEST_QUEUE = [{book:nick}]
REQUEST_QUEUE = []
# SENDING = { book: {nick, time} } ; moved from INQUEUE, but change the time to
#  when moved to this list; should be re-requested if > 1 hour
SENDING = {}

# current state of program, independent of nicks being online
RUNNING = False

# current state of queue, dependent on nicks being online
QUEUE_RUNNING = False

# nick: number of downloads in the queue
# nicks_in_queue= {}

# whether or not the original file should change, determines whether or not
# to rewrite the books.txt file used for reading additional files
# FILES_CHANGED = False

# whether or not the bklist from books.txt changes since read, used to
# determine if book downloaded
BOOK_LIST_CHANGED = False

# whether or not the notify list has been changed from before
# running the script, actually only changes if enabled
NOTIFY_LIST_CHANGED = False

ORIGINAL_NOTIFY_LIST = ""  # original notify list before starting/enable script

# the string to pointer for the irc.server.under.notify configuration
# option
OPTION_NOTIFY = None

# COMMANDHOOK = None
# hooks for when someone in notify list, joins, back, quit or away
NICK_HOOK_JOIN = None
NICK_HOOK_BACK = None
NICK_HOOK_QUIT = None
NICK_HOOK_AWAY = None

HOOK_MAIN_COMMAND = None

HOOK_XFER_ENDED = None
HOOK_IRC_DCC = None
HOOK_XFER_ADD = None
HOOK_SERVER_DISCONNECTED = None
HOOK_SERVER_CONNECTED = None

HOOK_BOOK_WAIT_TIMER = None
HOOK_TIME_CONNECT = None

HOOK_IRC_303 = None
HOOK_IRC_2JOIN = None
HOOK_IRC_2BACK = None
HOOK_NOTIFY_JOIN = None
HOOK_NOTIFY_QUIT = None
HOOK_NOTIFY_PART = None
HOOK_NOTIFY_AWAY = None
HOOK_NOTIFY_BACK = None
HOOK_IRC_2QUIT = None
HOOK_IRC_2PART = None
HOOK_IRC_2AWAY = None

HOOK_IRC_2PRIVATE_MESSAGE = None
HOOK_IRC_2NOTICE = None

DEBUG_PROGRAM = weechatvars.DEBUG_PRINT

ERRORLINE = "ERROR\t       ERRORErrorERRORErrorERRORErrorERRORErrorERRORError"


def is_int(num_):
    """Test if a string can be converted to an integer."""
    try:
        int(num_)
        return True
    except ValueError:
        return False


def main():
    """Put in main function for clarity."""
    pass


if __name__ == '__main__':
    main()
