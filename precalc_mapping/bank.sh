export OMP_NUM_THREADS=1
pycbc_brute_bank \
--psd-file o3psd.txt \
--output-file bank.hdf \
--input-config bank.ini \
--minimal-match 0.99 \
--tolerance 0.005 \
--sample-rate 2048 \
--low-frequency-cutoff 20.0 \
--tau0-start 0 \
--tau0-end 1000 \
--tau0-crawl 1000 \
--tau0-threshold 0.5 \
--tau0-cutoff-frequency 15.0 \
--buffer-length 1 \
--verbose
