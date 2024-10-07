export OMP_NUM_THREADS=1

FILE=bns_data.hdf
if [ -f $FILE ]; then
   echo "Example mapping file already exists"
else
   echo "Example mapping file missing, downloading now"
   bash get.sh
fi

pycbc_create_injections --verbose \
        --config-files injection.ini \
        --ninjections 1 \
        --seed 10 \
        --output-file injection.hdf \
        --variable-params-section variable_params \
        --static-params-section static_params \
        --dist-section prior \
        --force

pycbc_inference --verbose \
--config-files prior.ini \
--output-file test.hdf \
--nprocesses 8 \
--processing-scheme mkl \
--force

pycbc_inference_model_stats --verbose \
--reconstruct-parameters \
--input-file test.hdf \
--output-file test_d.hdf \
--nprocesses 8 \
--force

pycbc_inference_plot_posterior \
--input-file test_d.hdf \
--output-file test1.png \
--parameters '*' ra dec tc distance inclination polarization coa_phase \
--z-arg snr \
--plot-injection-parameters
