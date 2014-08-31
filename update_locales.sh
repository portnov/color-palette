#!/bin/bash

pygettext -v -o po/colors.pot {.,color,dialogs,matching,palette,widgets}/*.py palette/storage/*.py
cd po
for D in $(ls -d *)
do if [ -d $D ]
   then pushd $D/LC_MESSAGES
        msgmerge -v -U colors.po ../../colors.pot
        popd
   fi
done
