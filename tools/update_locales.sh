#!/bin/bash

cd palette-editor/

pygettext -v -o share/locale/colors.pot {.,bin,color,dialogs,matching,palette,widgets}/*.py palette/storage/*.py
cd share/locale
for D in $(ls -d *)
do if [ -d $D ]
   then pushd $D/LC_MESSAGES
        msgmerge -v -U colors.po ../../colors.pot
        popd
   fi
done
