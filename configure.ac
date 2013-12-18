AC_INIT([itstool], [2.0.2], [])
AM_INIT_AUTOMAKE([1.9 no-dist-gzip dist-bzip2])

DATADIR=`(
	case $prefix in
		NONE) prefix=$ac_default_prefix ;;
		*) ;;
	esac
	eval echo $(eval echo $datadir)
)`
AC_SUBST([DATADIR])

AM_PATH_PYTHON([2.6])

py_module=libxml2
AC_MSG_CHECKING(for python module $py_module)
echo "import $py_module" | python - &>/dev/null
if test $? -ne 0; then
	AC_MSG_RESULT(not found)
	AC_MSG_ERROR(Python module $py_module is needed to run this package)
else
	AC_MSG_RESULT(found)
fi

AC_CONFIG_FILES([
Makefile
itstool
itstool.1
its/Makefile
])

AC_OUTPUT
