#!/bin/bash

cd palette-editor/share/locale
for D in $(ls -d *)
do if [ -d $D ]
   then pushd $D/LC_MESSAGES/
        echo Building $D
        msgfmt -v -o colors.mo colors.po
        popd
   fi
done
