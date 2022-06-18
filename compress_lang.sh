#!/bin/sh
cd deb-pkg
for i in *
do
    gzip $i
done
