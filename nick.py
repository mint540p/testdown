#!/usr/bin/python
# -*- coding: utf-8 -*-
"""nick.py contains the nick functionality for downloadbooks.py
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

# import all globals from down
import sys

import my_queue as q

try:
	# noinspection PyUnresolvedReferences
	import weechat as w
except ImportError:
	print("This script must be run under WeeChat.")
	print("Get WeeChat now at: http://www.weechat.org/")

import wee_print as wp

import down as d
import weedebug as wdb


def channel_has_nick(fserver, fchannel, fnick):
	"""Check if channel has nick in it."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % fnick, wdb.SHOW_START)
	thisbuffer = w.buffer_search("", "%s.%s" % (fserver, fchannel))
	# check for nick in the buffer
	is_online = bool(w.nicklist_search_nick(thisbuffer, "", fnick))
	if (fnick == "FlipMoran" and not(is_online)):
		is_online = bool(w.nicklist_search_nick(thisbuffer, "","FlipMoran2"))
	return is_online


def check_if_anyone_online__lbinrs():
	"""Check if any nick is online.

	Returns true if yes, false if no notify online.
	"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)
	# check every nick(in NICKLIST) if they are in buffer
	any_nick_online = False
	for tnick in d.NICKLIST:
		check_if_nick_changed_status__lbinrs(tnick)
		if d.NICKLIST[tnick][d.ONLINE]:
			any_nick_online = True

	return any_nick_online


def is_nick_on_channel(this_nick):
	"""Checks if a nick is online."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % this_nick, wdb.SHOW_START)
	return channel_has_nick(d.SERVER, d.CHANNEL, this_nick)


def is_anyone_on_channel__ln():
	"""Checks if any nick in the nicklist is on the server, channel."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)
	status = False
	wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
	with d.NICKLIST_LOCK__L:
		for tnick in d.NICKLIST:
			nick_status = is_nick_on_channel(tnick)
			if nick_status:
				status = True
				break
	wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
	d.QUEUE_RUNNING = status
	return status


def check_if_nick_changed_status__lbinrs(this_nick):
	"""Look if one nick has gone from online to offline or vice versa."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % this_nick, wdb.SHOW_START)
	return_value = False
	if this_nick in d.NICKLIST:
		wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
		with d.NICKLIST_LOCK__L:
			current_status = d.NICKLIST[this_nick][d.ONLINE]
			d.NICKLIST[this_nick][d.ONLINE] = channel_has_nick(d.SERVER, d.CHANNEL, this_nick)
		wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
		if current_status:
			if not d.NICKLIST[this_nick][d.ONLINE]:
				q.clear_queue__lbinrs(this_nick)
				if check_if_nick_done(this_nick):
					remove_nick_from_queue__linrs(this_nick)
				wp.wprint("Nick\t %s changed status to OFFLINE" % this_nick)
				# wp.update_bar__lirs()
				return_value = True
		elif d.NICKLIST[this_nick][d.ONLINE]:
			wp.wprint("NICK\t %s changed status to ONLINE" % this_nick)
			return_value = True
	if return_value:
		wp.update_bar__lirs()
	return return_value


def check_if_nick_done(this_nick):
	"""Check if all books for a nick has been downloaded."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % this_nick, wdb.SHOW_START)

	if this_nick in d.NICKLIST and d.NICKLIST[this_nick][d.NUM_IN_QUEUE] == 0 and \
			d.NICKLIST[this_nick][d.NUM_BOOKS] == 0 and \
			d.NICKLIST[this_nick][d.DOWNLOAD] == 0:
		d.NOTIFY_LIST_CHANGED = True
		return True
	return False


def remove_nick_from_queue__linrs(this_nick):
	"""Remove a nick from NICKLIST.

	IE. no more books to download, alters notify list.
	"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % this_nick, wdb.SHOW_START)
	if this_nick in d.NICKLIST:
		del d.NICKLIST[this_nick]
		wp.wprint("NICK Remove\tRemoved %s from Nicklist" % this_nick)
	d.NOTIFY_LIST_CHANGED = put_nicklist_in_notify()
	pull_nick_from_down_accept(this_nick)
	wp.update_bar__lirs()
	if is_nicklist_empty():
		q.stop__linrs()


def is_nicklist_empty():
	"""Check if NICKLIST is empty, all done."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)

	return not d.NICKLIST  # empty


def pull_nick_from_down_accept(th_nick):
	"""Remove nick from the send list."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % th_nick, wdb.SHOW_START)
	original_xfer_list = w.config_string(w.config_get("xfer.file.auto_accept_nicks"))
	listold = original_xfer_list.split(',')
	if th_nick in listold and check_if_nick_done(th_nick):
		listold.remove(th_nick)
	newlist = ','.join(listold)
	return set_xfer_down_accept(newlist)

	#     w.config_option_set(option_xfer, newlist, 1)
	# if callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED or \
	#         callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_SAME_VALUE:
	#     return True
	# # elif :
	# # ... option set same value
	# # wp.wprint("xfer list not changed=%s." % original_xfer_list)
	# # return True
	# elif callback_return == w.WEECHAT_CONFIG_OPTION_SET_ERROR:
	#     # ... option set error

	#     wp.error_print("ERROR: Option XFER set error, NOT set to %s"
	#                 % original_xfer_list, 2)
	# # wp.error_print("XFER set error")
	# return False


def add_nick_to_send_list(new_list):
	"""Add a nick to the approved nick list for receiving files.

	Prevents just anyone from sending junk to you, must keep the
	xfer.file.auto_accept_files=off.
	"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % new_list, wdb.SHOW_START)
	listnew = new_list.split(',')
	original_xfer_list = w.config_string(w.config_get("xfer.file.auto_accept_nicks"))
	listxfer = original_xfer_list.split(',')
	new_xfer_list = list(sorted(set(listnew + listxfer)))
	new_xfer_str = ""
	empty_list = True
	for item_ in new_xfer_list:
		if not empty_list:
			new_xfer_str += ','
		new_xfer_str += str(item_)
		empty_list = False

	return set_xfer_down_accept(new_xfer_str)


def put_nicklist_in_notify():
	"""Get the nicks from NICKLIST, put in notify configuration setting.

	Puts in the configuration irc.server.'under'.notify.
	"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)
	new_list = ""
	list_new = []
	for nicks in d.NICKLIST:
		list_new.append(nicks)
	list_new = list(sorted(set(list_new)))

	for nicks in list_new:
		if new_list != "":
			new_list += ','
		new_list = new_list + nicks
	return set_under_notify_list(new_list)


def is_nick_online(this_nick):
	"""Return whether or not the NICKLIST thinks the nick is online."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % this_nick, wdb.SHOW_START)
	if this_nick in d.NICKLIST:
		return d.NICKLIST[this_nick][d.ONLINE]
	return False


def set_under_notify_list(new_notify_list):
	"""Change the irc.server.'under'.notify configuration setting.

	To a new list based on either the nicks in NICKLIST or reset back to
	original value.
	"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % new_notify_list, wdb.SHOW_START)
	if add_nick_to_send_list(new_notify_list):
		if d.OPTION_NOTIFY is not None:
			callback_return = w.config_option_set(d.OPTION_NOTIFY,
			                                      new_notify_list, 1)
			if callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED:
				# ... option changed
				# wp.wprint("NOTIFY:: Notify list is now: %s" % new_notify_list)
				d.NOTIFY_LIST_CHANGED = True
				return True
			elif callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_SAME_VALUE:
				return False
			elif callback_return == w.WEECHAT_CONFIG_OPTION_SET_ERROR:
				# ... option set error
				wp.error_print("ERROR: Option set error, NOT set to %s"
				               % new_notify_list, 2)
				return False
			else:
				wp.error_print("ERROR: THIS SHOULD NEVER HAPPEN, WEECHAT RETURNED \
                           INVALID VALUE", 5)
		else:
			wp.error_print("ERROR: under notify list never found or it's option \
                       never saved", 4)
	else:
		wp.error_print("ERROR: xfer list never found or it's option never saved",
		               4)
	return False


def save_under_notify_list():
	"""Save the original irc.server.'under'.notify configuration setting."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)
	# "mangagino,FlipMoran,FlipMoran*,FlipMoran2,Heisenburg,BenHex"
	# save the original notify list in variable ORIGINAL_NOTIFY_LIST
	# "irc.server.under.notify"
	d.OPTION_NOTIFY = w.config_get(d.UNDER_NOTIFY)
	if d.OPTION_NOTIFY:
		d.ORIGINAL_NOTIFY_LIST = w.config_string(d.OPTION_NOTIFY)
		d.NOTIFY_LIST_CHANGED = False
	else:
		wp.error_print("Unable to save the original notify list. Tried to save: %s"
		               % d.UNDER_NOTIFY, 2)


def set_xfer_down_accept(newxferlist):
	"""Set the xfer nick which are automatically accepted."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START : %s" % newxferlist, wdb.SHOW_START)
	option_xfer = w.config_get("xfer.file.auto_accept_nicks")
	if newxferlist:
		callback_return = w.config_option_set(option_xfer, newxferlist, 1)

		if callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED or \
				callback_return == w.WEECHAT_CONFIG_OPTION_SET_OK_SAME_VALUE:
			return True
			# option changed or set same value
		elif callback_return == w.WEECHAT_CONFIG_OPTION_SET_ERROR:
			# ... option set error
			wp.debug(function_name, "ERROR. callback_return = %d" % callback_return, wdb.SHOW_ERROR)
			wp.error_print("ERROR: Option XFER set error, NOT set to %s"
			               % newxferlist, 2)
	# wp.error_print("XFER set error")
	return False


def get_nicks__ln():
	"""Get nick information to put in bar"""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212

	wp.debug(function_name, "START", wdb.SHOW_START)
	total_in_queue = 0
	total_in_bklist = 0
	total_online_nicks = 0
	total_offline_nicks = 0
	total_downloading = 0
	online_nicks = ""
	offline_nicks = ""

	wp.debug(function_name, "Locking NICKLIST", wdb.SHOW_LOCKS)
	with d.NICKLIST_LOCK__L:
		for nick in d.NICKLIST:
			total_in_queue += d.NICKLIST[nick][d.NUM_IN_QUEUE]
			total_in_bklist += d.NICKLIST[nick][d.NUM_BOOKS]
			total_downloading += d.NICKLIST[nick][d.DOWNLOAD]
			if d.NICKLIST[nick][d.ONLINE]:
				total_online_nicks += 1
				online_nicks += (nick + "(%d/%d/%d)," %
				                 (d.NICKLIST[nick][d.NUM_IN_QUEUE], d.NICKLIST[nick][d.DOWNLOAD],
				                  d.NICKLIST[nick][d.NUM_BOOKS]))
			else:
				total_offline_nicks += 1
				offline_nicks += (nick + "(%d)," % d.NICKLIST[nick][d.NUM_BOOKS])
	wp.debug(function_name, "Unlocking NICKLIST", wdb.SHOW_LOCKS)
	if offline_nicks:
		offline_nicks = offline_nicks[:-1]
		# wp.wprint("BAR offline\tAfter cut:%s" % offline_nicks)
	if online_nicks:
		online_nicks = online_nicks[:-1]
	nicks_off = sorted(list(set(offline_nicks.split(","))))
	offline_nicks = ', '.join(nicks_off)
	nicks_on = sorted(list(set(online_nicks.split(","))))
	online_nicks = ', '.join(nicks_on)
	nicks = (offline_nicks, online_nicks)
	totals = (total_downloading, total_in_bklist, total_in_queue, total_offline_nicks,
	          total_online_nicks)
	return nicks, totals


def check_join_again__lj(nick_, times_called):
	"""Restart the joining hook for a nick."""
	# noinspection PyProtectedMember
	function_name = sys._getframe().f_code.co_name  # pylint: disable=W0212
	wp.debug(function_name, "START", wdb.SHOW_START)
	wp.wprint(function_name + "\t " + "%s: called=%d" % (nick_, times_called))
	if times_called > 0:
		times_called *= 2
	else:
		times_called = 4
	wp.debug(function_name, "Locking JOINING_CHRONOLIST", wdb.SHOW_LOCKS)
	with d.JOINING_CHRONOLIST_LOCK__L:
		if nick_ in d.JOINING_CHRONOLIST:
			w.unhook(d.JOINING_CHRONOLIST[nick_])
			del d.JOINING_CHRONOLIST[nick_]
		if times_called < 100:
			d.JOINING_CHRONOLIST[nick_] = w.hook_timer(times_called * d.JOINING_DELAY, 0, 2,
			                                           "cb_joining__lbcijnrs",
			                                           str(times_called) + "," + nick_)
	wp.debug(function_name, "Unlocking JOINING_CHRONOLIST", wdb.SHOW_LOCKS)


def main():
	"""Put in main function for clarity."""
	pass


if __name__ == '__main__':
	main()
