#/usr/bin/python3




NICKLIST = {}
ONLINE = 'online'
NUM_IN_QUEUE = 'num_in_queue'
DOWNLOAD = 'downloading'
NUM_BOOKS = 'num_books'



nicks_arr = ['FlipMoran', 'DV8', 'Heisenburg', 'friedeggs', 'Minx', 'BenHex', 'hamsterback', 'Wench', 'Bookworm',
             'Fortunate']


def main():


	print("Generating NICKLIST")
	for nick in nicks_arr:


		NICKLIST [nick] = {ONLINE  : False, NUM_IN_QUEUE: 0,
							                     DOWNLOAD: 0, NUM_BOOKS: 1}
		#	n.put_nicklist_in_notify()

	print("NICKLIST")
	print("%s" % NICKLIST)

	# option_xfer = w.config_get("xfer.file.auto_accept_nicks")
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


	# original_xfer_list = w.config_string(w.config_get("xfer.file.auto_accept_nicks"))
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



	listnew = new_list.split(',')
	# original_xfer_list = w.config_string(w.config_get("xfer.file.auto_accept_nicks"))
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


# These are from notify list only, not the accept nicks list












if __name__ == '__main__':
	main()
