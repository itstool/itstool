SUBDIRS = its

bin_SCRIPTS = itstool

man_MANS = itstool.1

EXTRA_DIST =		\
	ChangeLog	\
	COPYING.GPL3	\
	$(bin_SCRIPTS)	\
	itstool.in	\
	$(man_MANS)	\
	itstool.1.in

ChangeLog:
	@if test -f $(top_srcdir)/.git/HEAD; then \
	  git log --stat > $@; \
	fi

dist: ChangeLog
.PHONY: ChangeLog
