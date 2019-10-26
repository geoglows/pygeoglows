echo "building geoglows"
$PYTHON setup.py install --single-version-externally-managed --record=record.txt
mkdir $PREFIX/site-packages/
mkdir $PREFIX/site-packages/geoglows
cd $RECIPE_DIR/..
cp -r geoglows/notebooks $PREFIX/site-packages/geoglows
cp -r geoglows/templates $PREFIX/site-packages/geoglows
