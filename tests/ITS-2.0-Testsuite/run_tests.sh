#!/bin/bash

testdata="
elementswithintext/withintext/withinText
externalresource/externalresource/externalResourceRef
idvalue/idvalue/idValue
localefilter/locale/localeFilter
localizationnote/locnote/locNote
preservespace/preservespace/preserveSpace
translate/translate/translate
"

for datum in $testdata; do
    for format in xml; do
        testdir=`echo $datum | cut -d/ -f1`
        testbase=`echo $datum | cut -d/ -f2`
        testcat=`echo $datum | cut -d/ -f3`
        testpre="inputdata/$testdir/$format/$testbase"
        for testfile in `ls ${testpre}*${format}.${format}`; do
            testnum=`basename ${testfile:${#testpre}} ${format}.${format}`
            skip=0
            #for ex in $exclude; do
            #    if [ "$testbase$testnum$format" = "$ex" ]; then skip=1; break; fi;
            #done
            if [ "$skip" = "0" ]; then
                expected="expected/$testdir/$format/$testbase$testnum${format}output.txt"
                realout="realout/$testdir/$format/$testbase$testnum${format}output.txt"
                mkdir -p "realout/$testdir/$format"
                python ../../itstool.in -n -t $testcat -o $realout $testfile
                if ! cmp "$expected" "$realout"; then
                    echo "$expected";
                    exit 1;
                fi
            fi
        done
    done
done
