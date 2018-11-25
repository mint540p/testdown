#!/usr/bin/python
# -*- coding: utf-8 -*-
"""my-queue.py contains the queue functionality for downloadbooks.py
 designed to download books from undernet irc.

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
"""

########################################################################
# Imports
########################################################################
from __future__ import print_function

import re
import sys
import time

from py2casefold import casefold

# import all globals from down
import down as d
import hooks as h
import my_files as f
import nick as n
import wee_print as wp
import weedebug as wdb

try:
    # noinspection PyUnresolvedReferences
    import weechat as w
except ImportError:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")


def clear_queue__lbinrs(this_nick):
    """Clear the items for a nick out of the queue back to the books list.
    Used when nick quits or stopping queue.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
    wp.debug(function_name, "START: %s" % this_nick, wdb.SHOW_START)
    move_items_inqueue_to_bklist__lbinrs(this_nick)
    wp.update_bar__lirs()
    # write_files()


def move_items_inqueue_to_bklist__lbinrs(nick):
    """For a nick, move book items from INQUEUE back to BKLIST.

    When nick quits or queue is stopped.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % nick, wdb.SHOW_START)

    que_count = 0
    send_count = 0
    wp.debug(function_name, "Locking REQUEST", wdb.SHOW_LOCKS)
    with d.RQ_LOCK__L:
        for book_item in d.REQUEST_QUEUE:
            for bok, nck in book_item.items():
                if nck == nick:
                    wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
                    with d.BOOKLIST_LOCK__L:
                        d.BKLIST[bok] = nck
                    wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)
                    d.REQUEST_QUEUE.remove(book_item)
                    que_count += 1
                    d.BOOK_LIST_CHANGED = True
    wp.debug(function_name, "Unlocking REQUEST", wdb.SHOW_LOCKS)
    wp.debug(function_name, "Locking INQUEUE", wdb.SHOW_LOCKS)
    with d.INQUEUE_LOCK__L:
        for book, info in d.INQUEUE.items():
            if info[d.NICK] == nick:
                del d.INQUEUE[book]
                que_count += 1
                wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
                with d.BOOKLIST_LOCK__L:
                    d.BKLIST[book] = info[d.NICK]
                wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)

                d.BOOK_LIST_CHANGED = True
    wp.debug(function_name, "Unlocking INQUEUE", wdb.SHOW_LOCKS)
    wp.debug(function_name, "Locking SENDING", wdb.SHOW_LOCKS)
    with d.SENDING_LOCK__L:
        for book, info in d.SENDING.items():
            if info[d.NICK] == nick:
                del d.SENDING[book]
                send_count += 1
                wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
                with d.BOOKLIST_LOCK__L:
                    d.BKLIST[book] = info[d.NICK]
                wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)

                wp.print_to_error_list(book)
                d.BOOK_LIST_CHANGED = True
    wp.debug(function_name, "Unlocking SENDING", wdb.SHOW_LOCKS)
    wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
    with d.NICKLIST_LOCK__L:
        if nick in d.NICKLIST:
            d.NICKLIST[nick][d.NUM_IN_QUEUE] -= que_count  # - NICKLIST[nick][DOWNLOAD])
            d.NICKLIST[nick][d.DOWNLOAD] -= send_count
            d.NICKLIST[nick][d.NUM_BOOKS] += que_count + send_count  # total_count
    wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
    # elif total_count > count:
    # else:
    #     wp.error_print("THE NUMBER IN QUEUE FOR %s IS %d AND QUEUE HAS %d."
    #                 % (nick, NICKLIST[nick][NUM_IN_QUEUE], total_count))
    #     NICKLIST[nick][NUM_IN_QUEUE] -= total_count #- NICKLIST[nick][DOWNLOAD])
    #     NICKLIST[nick][DOWNLOAD] = 0
    #     NICKLIST[nick][NUM_BOOKS] += total_count #- NICKLIST[nick][DOWNLOAD])


def move_book_from_queues_to_bklist__lbinrs(book_):
    """Move book from INQUEUE to BKLIST because download failed."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % book_, wdb.SHOW_START)

    q_found, q_to_move, _ = remove_from_queue__lirs(book_)
    s_found, s_to_move, _ = remove_from_sending__lirs(book_)
    lost = True
    if q_found:
        lost = False
        book_add__lbinrs(q_to_move)
    if s_found:
        lost = False
        book_add__lbinrs(s_to_move)
    if lost:
        wp.print_bad_book_name__lis(book_, "INQUEUE to BOOKLIST")


def move_book_from_sending_2_completed__lbirs(book_):
    """Book received and completed; checks if can remove book from INQUEUE."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % book_, wdb.SHOW_START)
    found = False
    bl_found, b_book = remove_from_booklist__lbirs(book_)
    if bl_found:
        wp.print_to_completed_list(b_book)
        found = True
    rq_found, r_book = remove_from_request_queue__lirs(book_)
    if rq_found:
        wp.print_to_completed_list(r_book)
        found = True
    iq_found, q_book, _ = remove_from_queue__lirs(book_)
    if iq_found:
        wp.print_to_completed_list(q_book)
        found = True
    sq_found, s_book, _ = remove_from_sending__lirs(book_)
    if sq_found:
        wp.print_to_completed_list(s_book)
        found = True
    if found:

        d.RUNNING = check_if_books_done()
        if not d.RUNNING:
            d.QUEUE_RUNNING = d.RUNNING
        d.BOOK_LIST_CHANGED = True
    else:
        if book_.startswith("!SearchOok") and book_.endswith(".txt.zip"):
            return
        wp.print_bad_book_name__lis(book_, "SENDING to COMPLETED")
    f.write_files()


def find_in_book_list__lb(book_):
    """Find an item in a dictionary queue for SENDING, INQUEUE, or REQUEST_QUEUE.
    The lock must be made for the appropriate queue before calling this function."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: \n%s" % book_, wdb.SHOW_START)
    book_standard = standardize_string(book_)
    return_1 = False
    return_2 = None
    return_3 = None
    wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
    with d.BOOKLIST_LOCK__L:
        for item in d.BKLIST:
            item_ = standardize_string(item)
            if item_ == book_standard:  # or item_ == book_b_standard:
                return_1 = True
                return_2 = item
                return_3 = d.BKLIST[item]
                break

    wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)
    return return_1, return_2, return_3


def find_in_dictionary(this_queue, book_):
    """Find an item in a dictionary queue for SENDING, INQUEUE, or REQUEST_QUEUE.
    The lock must be made for the appropriate queue before calling this function."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % book_, wdb.SHOW_START)
    book_standard = standardize_string(book_)
    for item in this_queue:
        item_ = standardize_string(item)
        if item_ == book_standard:  # or item_ == book_b_standard:
            return True, item, this_queue[item][d.NICK]  # sending_found, to_remove
    return False, None, None


def find_in_request_queue(book_):
    """Find an item in a dictionary queue for SENDING, INQUEUE, or REQUEST_QUEUE.
    The lock must be made for the appropriate queue before calling this function."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: \n%s" % book_, wdb.SHOW_START)
    book_standard = standardize_string(book_)

    for dict_item in d.REQUEST_QUEUE:
        for item in dict_item:
            item_ = standardize_string(item)
            if item_ == book_standard:  # or item_ == book_b_standard:
                return True, item, item[d.NICK]  # sending_found, to_remove
    return False, None, None


def move_book_from_inqueue_to_sending__linrs(book_):
    """Book received and completed; checks if can remove book from INQUEUE."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % book_, wdb.SHOW_START)
    found, to_remove, the_nick = remove_from_queue__lirs(book_)
    if found:
        put_in_sending__linrs(to_remove, the_nick)

    else:
        if book_.startswith("!SearchOok") and book_.endswith(".txt.zip"):
            return
        wp.wprint("From INQUEUE\t Book not found.")
        wp.print_bad_book_name__lis(book_, "INQUEUE to SENDING")


def check_if_books_done():
    """Check if all books are done, empty lists,queuek."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
    wp.debug(function_name, "START", wdb.SHOW_START)

    done = False
    if not d.BKLIST and not d.INQUEUE and not d.SENDING and not d.REQUEST_QUEUE:
        done = True
    return not done


def move_one_queue_to_downloading__lbcinrs(this_nick):
    """Start receiving a book.

    For a nick, changes 1 from NUM_IN_QUEUE to DOWNLOADING.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START| %s" % this_nick, wdb.SHOW_START)

    if this_nick in d.NICKLIST and add_items__lbcnr(this_nick) > 0:
        # moved these lines to other functions  - remove when working right.9
        # NICKLIST[this_nick][NUM_IN_QUEUE] -= 1
        # NICKLIST[this_nick][DOWNLOAD] += 1

        restart_queue__lirs()


def remove_from_queue__lirs(bkitem):
    """Remove book from IN_QUEUE if there."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % bkitem, wdb.SHOW_START)
    found, to_remove, the_nick = find_in_dictionary(d.INQUEUE, bkitem)
    if found:
        with d.INQUEUE_LOCK__L:
            del d.INQUEUE[to_remove]
            if the_nick in d.NICKLIST:
                d.NICKLIST[the_nick][d.NUM_IN_QUEUE] -= 1
        d.BOOK_LIST_CHANGED = True
        wp.update_bar__lirs()
    return found, to_remove, the_nick


def remove_from_request_queue__lirs(bkitem):
    """Remove book from REQUEST_QUEUE if there."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    found, to_remove, the_nick = find_in_request_queue(bkitem)
    if found:
        wp.debug(function_name, "Locking REQUEST", wdb.SHOW_LOCKS)
        with d.RQ_LOCK__L:
            del d.REQUEST_QUEUE[to_remove]
            if the_nick in d.NICKLIST:
                d.NICKLIST[the_nick][d.NUM_IN_QUEUE] -= 1
        wp.debug(function_name, "Unlocking REQUEST", wdb.SHOW_LOCKS)
        d.BOOK_LIST_CHANGED = True
        wp.update_bar__lirs()
    return found, to_remove


def stop_queue__linrs():
    """Stop the download queue of books."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    d.QUEUE_RUNNING = False
    for nick in d.NICKLIST:
        move_items_inqueue_to_bklist__lbinrs(nick)
        n.pull_nick_from_down_accept(nick)
    # print_queue_status("QUEUE STOPPED")
    wp.update_bar__lirs()
    return False


def remove_from_sending__lirs(book_):
    """Remove book from SENDING when book has been downloaded."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % book_, wdb.SHOW_START)
    found, to_remove, the_nick = find_in_dictionary(d.SENDING, book_)
    if found:
        wp.debug(function_name, "Locking SENDING", wdb.SHOW_LOCKS)
        with d.SENDING_LOCK__L:
            del d.SENDING[to_remove]
            if the_nick in d.NICKLIST:
                d.NICKLIST[the_nick][d.DOWNLOAD] -= 1
        wp.debug(function_name, "Unlocking SENDING", wdb.SHOW_LOCKS)
        d.BOOK_LIST_CHANGED = True
        wp.update_bar__lirs()
    return found, to_remove, the_nick


def standardize_string(my_string):
    """Alter a copy of a sting to a standardized format for comparison."""
    # Removed this debug statement because it produces so much unneeded output.
    # fn = sys._getframe().f_code.co_name
    # wp.debug(fn, "START: %s" % my_string, wdb.SHOW_START)

    str_lower = casefold(my_string.strip().decode('utf-8')).strip()
    return str_lower.replace('_', ' ').strip()


def book_add__lbinrs(th_book):
    """Add book to BKLIST, book list from a line of a search.

    From the original line in a search on UnderNet server, this will remove
    extra info and add the nick, book to the BKLIST.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START : %s" % th_book, wdb.SHOW_START)
    # // check if starts with a '!' following by a nick
    added = 0
    if th_book.startswith("!"):
        # // pull out the ending ::INFO::.*$
        # // remove any extra part to downloading books - from most nick/bots
        book = (re.sub("::INFO::.*$", "", th_book)).strip()
        #  remove the  ---- xx.x KB form other nicks like !new
        # noinspection Annotator
        book = (re.sub(r'\s+-+\s[.\d]+\s[MKG]B', "", book)).strip()
        # // pull out the nick
        nick = (re.findall(r"(?<=^!)\w+", book))[0]
        wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
        with d.BOOKLIST_LOCK__L:
            wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
            with d.NICKLIST_LOCK__L:
                if book not in d.BKLIST:
                    d.BKLIST[book] = nick
                    d.BOOK_LIST_CHANGED = True
                    added = 1
                    if nick in d.NICKLIST:
                        d.NICKLIST[nick][d.NUM_BOOKS] += 1
                    else:
                        d.NICKLIST[nick] = {d.ONLINE: False, d.NUM_IN_QUEUE: 0,
                                            d.DOWNLOAD: 0, d.NUM_BOOKS: 1}
                        n.put_nicklist_in_notify()
            wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
        wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)
        wp.update_bar__lirs()
    return added


# noinspection SpellCheckingInspection
def add_items__lbcnr(this_nick):
    # type: (str) -> int
    """Determines the number of books which can be added for this_nick.  Checks if Nick is online.
    Starts checking if can put items INQUEUE and requests to add can_add items.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    # Find number already in queue for nick and the number of books for nick in list.
    if this_nick in d.NICKLIST:
        thnum_in_queue = d.NICKLIST[this_nick][d.NUM_IN_QUEUE]
        thnum_books = d.NICKLIST[this_nick][d.NUM_BOOKS]
    else:
        # Nick is not in list nicklist, so error, print the error.
        wp.error_print("Nick not in LIST:%s" % this_nick, 3)
        return 0
    # Check if nick is online and if any can be added.  If not, return 0.(last line)
    # wp.wprint("q.add_items\t Nick:%s, Books:%d, Queued:%d" %
    #           (this_nick, thnum_books, thnum_in_queue))
    if n.is_nick_online(this_nick) and thnum_in_queue < d.QUEUE_MAX:
        # Determine how many can be added.  MAX(usually 2) - number currently in queue.
        can_add = d.QUEUE_MAX - thnum_in_queue
        # Check if number of books in list is > number that can be added, otherwise set can be added
        # to the number of books in list.
        if thnum_books < can_add:
            can_add = thnum_books
        wp.wprint("Can add %d Books for %s from list consisting of %d Books, %d Queued, %s is Online" %
                  (can_add, this_nick, thnum_books, thnum_in_queue, this_nick))
        # If books can be added, make sure there is not another hook for added books and add them.
        if can_add > 0:
            if this_nick in d.CHRONOLIST:
                wp.debug(function_name, "Locking CHRONOLIST", wdb.SHOW_LOCKS)
                with d.CHRONOLIST_LOCK__L:
                    w.unhook(d.CHRONOLIST[this_nick])
                    del d.CHRONOLIST[this_nick]
                wp.debug(function_name, "Unlocking CHRONOLIST", wdb.SHOW_LOCKS)
            # Add the books to INQUEUE.
            for _ in range(can_add):
                add_item__lbnr(this_nick)
        # return the number of books added.
        return can_add
    return 0


def remove_from_booklist__lbirs(bkitem):
    """Remove book from BKLIST if there."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    # Find the book in BKLIST.
    found, to_remove, the_nick = find_in_book_list__lb(bkitem)
    # If book is found, then remove it from the BKLIST, indicate the BKLIST has changed, and update
    # the status bar.
    if found:
        wp.debug(function_name, "Locking BOOKLIST", wdb.SHOW_LOCKS)
        with d.BOOKLIST_LOCK__L:
            del d.BKLIST[to_remove]
            if the_nick in d.NICKLIST:
                d.NICKLIST[the_nick][d.NUM_BOOKS] -= 1
        wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)
        d.BOOK_LIST_CHANGED = True
        wp.update_bar__lirs()
    # Return whether the book was found and the name of the book.
    return found, to_remove


def put_in_sending__linrs(to_move, t_nick):
    """Put this book request into the SENDING queue since we started receiving it."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START:to_move=%s, t_nick=%s" % (to_move, t_nick), wdb.SHOW_START)
    wp.debug(function_name, "Locking SENDING", wdb.SHOW_LOCKS)
    with d.SENDING_LOCK__L:
        d.SENDING[to_move] = {d.NICK: t_nick, d.TIME: time.time()}
    wp.debug(function_name, "Unlocking SENDING", wdb.SHOW_LOCKS)
    if t_nick in d.NICKLIST:
        d.NICKLIST[t_nick][d.DOWNLOAD] += 1
    else:
        wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
        with d.NICKLIST_LOCK__L:
            d.NICKLIST[t_nick] = {d.ONLINE: True, d.NUM_IN_QUEUE: 0, d.DOWNLOAD: 1, d.NUM_BOOKS: 0}
        wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)

    d.BOOK_LIST_CHANGED = True
    wp.update_bar__lirs()

    # wp.debug("put in sending\t END:to_move=%s, t_nick=%s" % (to_move, t_nick))


def add_item__lbnr(this_nick):
    """Find a book from a nick and adds to 0 and requests from server."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % this_nick, wdb.SHOW_START)

    book, nick = get_item_from_list(d.BKLIST, this_nick)
    if this_nick == nick:
        dict_item = {book: nick}

        wp.debug(function_name, "Locking REQUEST", wdb.SHOW_LOCKS)
        with d.RQ_LOCK__L:
            d.REQUEST_QUEUE.append(dict_item)
        wp.debug(function_name, "Unlocking REQUEST", wdb.SHOW_LOCKS)
        wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)

        with d.NICKLIST_LOCK__L:
            if this_nick in d.NICKLIST:
                d.NICKLIST[this_nick][d.NUM_IN_QUEUE] += 1
                d.NICKLIST[this_nick][d.NUM_BOOKS] -= 1

        wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
        wp.debug(function_name, "DOWNLOAD %s for %s" % (dict_item, this_nick), wdb.SHOW_INFO)
        wp.wprint("Added to Request\t %s" % book)
        wp.debug(function_name, "locking BOOKLIST", wdb.SHOW_LOCKS)
        with d.BOOKLIST_LOCK__L:
            del d.BKLIST[book]
            d.BOOK_LIST_CHANGED = True
        wp.debug(function_name, "Unlocking BOOKLIST", wdb.SHOW_LOCKS)


def move_request_to_inqueue__lirs():
    """Actual move one item from REQUEST_QUEUE to INQUEUE."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    popitem = {}
    wp.debug(function_name, "Locking REQUEST", wdb.SHOW_LOCKS)
    with d.RQ_LOCK__L:
        if d.REQUEST_QUEUE:
            popitem = d.REQUEST_QUEUE.pop()
    wp.debug(function_name, "Unlocking REQUEST", wdb.SHOW_LOCKS)
    for tbook, tnick in popitem.items():
        request_book__lirs(d.SERVER, d.CHANNEL, tbook)
        with d.INQUEUE_LOCK__L:
            d.INQUEUE[tbook] = {d.NICK: tnick, d.TIME: time.time()}
    wp.update_bar__lirs()


# noinspection SpellCheckingInspection,SpellCheckingInspection
def get_item_from_list(book, nick):
    """Return first book from BkLIST, does not remove."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % nick, wdb.SHOW_START)

    for bkitem, nkitem in book.items():
        if nkitem == nick:
            return bkitem, nkitem
    return None, None


def request_book__lirs(fserver, fchannel, fbook):
    """Request the download of the book from the server.
    fbook is the book out of bklist.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % fbook, wdb.SHOW_START)
    thisbuffer = w.buffer_search("", "%s.%s" % (fserver, fchannel))
    wp.wprint("REQUEST book\t%s" % fbook)
    wp.update_bar__lirs()
    w.command(thisbuffer, fbook)


def request_items__lirs(items_to_request):
    """Request items/books again when in queue to long."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
    wp.debug(function_name, "START, requesting %d items" % len(items_to_request), wdb.SHOW_START)
    for item in items_to_request:
        request_book__lirs(d.SERVER, d.CHANNEL, item)


def adding_books__lbcinrs(argf):
    """Take args(argn) and determining if a filename or a book listing.
    Putting the books into the BKLIST using helper functions.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % argf, wdb.SHOW_START)
    added_books = 0
    wp.wprint("ADD\t Adding an item or file:%s" % argf)
    if argf.startswith('!'):
        # this is a single book item and uses the rest of the line
        # bookitem = argn[1:]
        # and sends the line to S to pull off any extra info
        # and checks if the book was added
        if book_add__lbinrs(argf) == 1:
            wp.wprint("BOOK\t ADDED: %s" % argf)
            d.BOOK_LIST_CHANGED = True
            tnick = re.findall(r"(?<=!)\S*", argf)
            nick = tnick[0].strip()
            n.add_nick_to_send_list(nick)
            added_books = 1
            d.NOTIFY_LIST_CHANGED = n.put_nicklist_in_notify()
            wp.update_bar__lirs()
        # no book was added, print out error statement
        else:
            wp.error_print("UNABLE TO ADD BOOK: %s" % argf)
    # this is a file and sends the file name to read_file__lbn
    else:
        # adding a file
        added_books = f.read_file__lbinrs(argf)
    wp.wprint("%d books added" % added_books)
    # # starts the queue if running and there are any online nicks
    # if d.RUNNING:
    #     d.QUEUE_RUNNING = check_if_anyone_online__linrs()
    #     if d.QUEUE_RUNNING:
    #         start_queue__lbcinrs()


def get_book_list__lirs():
    """Pull list of books and return the string of books to put in bar."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    status = ""
    if d.REQUEST_QUEUE:
        status += "\n  TO REQUEST:"
        wp.debug(function_name, "Locking REQUEST", wdb.SHOW_LOCKS)
        with d.RQ_LOCK__L:

            for item in d.REQUEST_QUEUE:
                for l_book in item.keys():
                    status += "\n" + l_book
        wp.debug(function_name, "Unlocking REQUEST", wdb.SHOW_LOCKS)
    if d.INQUEUE:
        status += "\n  AWAITING:"
        wp.debug(function_name, "Locking INQUEUE", wdb.SHOW_LOCKS)
        with d.INQUEUE_LOCK__L:

            for book in d.INQUEUE:
                status += "\n" + book
        wp.debug(function_name, "Unlocking INQUEUE", wdb.SHOW_LOCKS)
    if d.SENDING:
        status += "\n  RECEIVING:"
        wp.debug(function_name, "Locking SENDING", wdb.SHOW_LOCKS)
        with d.SENDING_LOCK__L:

            for book in d.SENDING:
                status += "\n" + book
        wp.debug(function_name, "Unlocking SENDING", wdb.SHOW_LOCKS)
    return status


def move_book_from_sending_to_queue_bklist__lbcinrs(book_, nick_):
    """Book received and completed; checks if can remove book from INQUEUE."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START: %s" % book_, wdb.SHOW_START)

    found, to_remove, _ = remove_from_sending__lirs(book_)
    if found:
        if book_add__lbinrs(to_remove) > 0 and add_items__lbcnr(nick_):
            restart_queue__lirs()
    else:
        if book_.startswith("!SearchOok") and book_.endswith(".txt.zip"):
            return
        wp.wprint("From SENDING\t Book not found.")
        wp.print_bad_book_name__lis(book_, "SENDING to BKLIST/QUEUE")


def move_items_send_2_bklist(items_to_move):
    """Move items to bklist when in sending to long."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
    wp.debug(function_name, "START, moving %d items" % len(items_to_move), wdb.SHOW_START)
    for item in items_to_move:
        keys_it = item.keys()
        for i_key in keys_it:
            wp.wprint(function_name + "\t Moving item from SENDING to queue: i_key=%s, nick=%s" %
                      (str(i_key), item[i_key]))
            move_book_from_sending_to_queue_bklist__lbcinrs(str(i_key), item[i_key])


# noinspection PyUnusedLocal,PyUnusedFunction
def check_if_book_anywhere__lbirs(bkitem_):
    """Check if book was in sending to long and moved elsewhere.
    :param bkitem_: str
    :return: None
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    remove_from_booklist__lbirs(bkitem_)
    remove_from_request_queue__lirs(bkitem_)
    remove_from_queue__lirs(bkitem_)


# noinspection PyUnusedLocal,PyUnusedFunction
def does_anyone_need_items__ln():
    """Check for any nick needing an item request."""
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    ret_value = False
    if n.is_anyone_on_channel__ln():
        wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
        with d.NICKLIST_LOCK__L:
            for nick_ in d.NICKLIST:
                if d.NICKLIST[nick_][d.NUM_IN_QUEUE] < d.QUEUE_MAX and \
                        d.NICKLIST[nick_][d.NUM_BOOKS] > 0:
                    ret_value = True
                    break
        wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)

    return ret_value


def move_to_queue():
    """Start call_back to move items.

    Items from REQUEST_QUEUE to go to INQUEUE.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)

    if d.MOVE_HOOK_CHRONOLIST:
        w.unhook(d.MOVE_HOOK_CHRONOLIST)
        # wait(3000)
    d.MOVE_HOOK_CHRONOLIST = w.hook_timer(d.REQUEST_DELAY * 1000, 0, len(d.REQUEST_QUEUE),
                                          "cb_move_to_queue__lirs", "")


def restart_queue__lirs():
    """Check if need to move any books to INQUEUE from REQUEST_QUEUE.

    Returns the value for QUEUE_RUNNING
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    num_books_in_request = len(d.REQUEST_QUEUE)
    if num_books_in_request > 0:
        wp.wprint("\t Requesting %d items" % num_books_in_request)
        move_to_queue()
        # wp.wprint("RESTART QUEUE\tEnd returning true")
        d.QUEUE_RUNNING = True
        wp.update_bar__lirs()
        return True
    # wp.wprint("RESTART QUEUE\tEnd returning false")
    return False


def run_queue_if_anyone_online__lbcinrs():
    """Start running requests if any nick online.

    Checks if anyone online, then puts up to MAX_QUEUE in REQUEST_QUEUE
    and then starts requesting each and moving to INQUEUE.
    """
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)

    nicks_online = n.check_if_anyone_online__lbinrs()
    if nicks_online:
        for nick in d.NICKLIST:
            add_items__lbcnr(nick)
    return restart_queue__lirs()


def start_queue__lbcinrs():
    """Start INQUEUE by checking if anyone is online.

    Starts adding items by online nicks.
    """
    # global QUEUE_RUNNING, NICKLIST, RUNNING
    # wp.debug_ print("START\tstart queue")
    # wp.wprint("QUEUE\t STARTING")
    # wp.wprint("START QUEUE\t Begin")
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

    wp.debug(function_name, "START", wdb.SHOW_START)
    if d.RUNNING:
        d.QUEUE_RUNNING = run_queue_if_anyone_online__lbcinrs()
        # print_queue_status("QUEUE STARTING")
        wp.update_bar__lirs()
    # wp.wprint("START QUEUE\tEnd")


def stop__linrs():
    """Stop script; remove notify hooks, stop__linrs queue."""
    # global ORIGINAL_NOTIFY_LIST, NOTIFY_LIST_CHANGED, NICK_HOOKJ, NICK_HOOKB
    # global NICK_HOOKQ, NICK_HOOKA, RUNNING
    # stop__linrs the queue, boolean running means current state of queue
    # noinspection PyProtectedMember
    function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
    wp.debug(function_name, "START", wdb.SHOW_START)
    d.RUNNING = stop_queue__linrs()
    # reset notify list for under to original value
    if d.NOTIFY_LIST_CHANGED:
        n.set_under_notify_list(d.ORIGINAL_NOTIFY_LIST)
        d.NOTIFY_LIST_CHANGED = False
    h.remove_my_hooks()

    h.remove_new_hooks()

    #
    # # Received file send completed
    # = w.hook_signal('xfer_ended', 'cb_XFER_ENDED_SIGNAL', '')
    #
    # # Started receiving the file
    # hooks_list[HOOKS_DCC] = w.hook_signal('irc_DCC', 'cb_DCC', '')
    #
    # # This NEVER happened and the CallBack is missing!!! # CHECK WHY YOU ADDED THIS
    # hooks_list[HOOKS_rISON] = w.hook_hsignal('irc_redirection_%s_ison' % SCRIPT_NAME,
    #  'redirect_ison handler', '')
    #

    #
    # START timed hook every 30 minutes to check if not received book in 35 minutes
    if d.HOOK_BOOK_WAIT_TIMER is not None:
        w.unhook(d.HOOK_BOOK_WAIT_TIMER)
        d.HOOK_BOOK_WAIT_TIMER = None
    #
    # check if anyone is online every 10 minutes
    if d.HOOK_TIME_CONNECT is not None:
        w.unhook(d.HOOK_TIME_CONNECT)
        d.HOOK_TIME_CONNECT = None
    wp.update_bar__lirs()
    wp.wprint("Book Downloads are stopped.")


def main():
    """Put in main function for clarity."""
    pass


if __name__ == '__main__':
    main()
