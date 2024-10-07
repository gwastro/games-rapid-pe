export OMP_NUM_THREADS=1

python ./map.py \
--config-file bank.ini \
--bank-file bank.hdf \
--output-file bns_data_example.hdf \
--psd-file o3psd.txt \
--nprocesses 14 \
--sample-size 50000000
