AC_INIT([itstool], [1.2.0], [])
AM_INIT_AUTOMAKE([1.9 no-dist-gzip dist-bzip2])

DATADIR=`(
	case $prefix in
		NONE) prefix=$ac_default_prefix ;;
		*) ;;
	esac
	eval echo $(eval echo $datadir)
)`
AC_SUBST([DATADIR])

AC_CONFIG_FILES([
Makefile
itstool
itstool.1
its/Makefile
])

AC_OUTPUT
