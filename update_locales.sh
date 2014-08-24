#!/bin/bash

pygettext -o po/colors.pot *.py
cd po
for D in $(ls *)
do if [ -d $D ]
   then pushd $D
        msgmerge -U colors.po ../../colors.pot
        popd
   fi
done
