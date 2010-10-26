SUBDIRS = its

bin_SCRIPTS = itstool

EXTRA_DIST = ChangeLog COPYING.GPL3

ChangeLog:
	@if test -f $(top_srcdir)/.git/HEAD; then \
	  git log --stat > $@; \
	fi

dist: ChangeLog
.PHONY: ChangeLog
