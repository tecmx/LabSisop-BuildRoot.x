#!/bin/sh

# Copiar configuração de rede
cp $BASE_DIR/../custom-scripts/S41network-config $BASE_DIR/target/etc/init.d
chmod +x $BASE_DIR/target/etc/init.d/S41network-config

# criar modulo iosched 
cp $BASE_DIR/../custom-scripts/S42sstf $BASE_DIR/target/etc/init.d
chmod +x $BASE_DIR/target/etc/init.d/S42sstf

# Copiar e tornar executável o script serverLu.py
cp $BASE_DIR/../custom-scripts/serverLu.py $BASE_DIR/target/usr/bin/
chmod +x $BASE_DIR/target/usr/bin/serverLu.py

make -C $BASE_DIR/../modules/simple_driver/

