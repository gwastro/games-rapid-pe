import h5py, numpy, tqdm, logging, copy, argparse
import pycbc.io
from pycbc.waveform import get_fd_waveform
from pycbc.psd import from_cli, insert_psd_option_group
from pycbc.types.config import InterpolatingConfigParser
from pycbc.distributions import draw_samples_from_config, read_params_from_config
from pycbc.pool import choose_pool


parser = argparse.ArgumentParser()
parser.add_argument('--config-file')
parser.add_argument('--bank-file')
parser.add_argument('--output-file')
parser.add_argument('--sample-size', type=int)
parser.add_argument('--nprocesses', type=int)
insert_psd_option_group(parser, include_data_options=False)
args = parser.parse_args()

# Get the prior to draw samples from
cp = InterpolatingConfigParser([args.config_file])
var, stat = read_params_from_config(cp, vargs_section='variable_params',
                                        sargs_section='static_params')

# Get the template bank
f = h5py.File(args.bank_file, 'r')
minimal_match = f.attrs['minimal_match']
bparams = {b: f[b][:] for b in f.keys()}
num_templates = len(bparams[list(bparams.keys())[0]])
mcb = bparams['mchirp']

# Settings for the match calculation
flow = 20
delta_f = 2

kmin = int(flow / delta_f)
kmax = int(1000 / delta_f)
pred = from_cli(args, kmax+1, 2, flow - 5)

# Pregenerate the bank waveforms
waveforms= []
for i in tqdm.tqdm(range(num_templates)):
    wparam = {k: bparams[k][i] for k in bparams}
    wparam.update(stat)
    hp, hc = get_fd_waveform(delta_f=delta_f, **wparam)

    hp /= (hp.conj()[kmin:kmax] * hp[kmin:kmax] / pred[kmin:kmax]).sum() ** 0.5
    hp[kmin:kmax] /= pred[kmin:kmax]
    waveforms.append(hp[kmin:kmax].numpy())
pred = pred[kmin:kmax].numpy()

samples = draw_samples_from_config(args.config_file, args.sample_size)

def find_match(j):
    s = samples[j]
    mc_dist = abs(s.mchirp - mcb)
    torder = mc_dist.argsort()

    sparam = {k: s[k] for k in s.dtype.names}
    sparam.update(stat)
    hp, hc = get_fd_waveform(delta_f=delta_f, **sparam)
    hp.resize(kmax)
    hp = hp.numpy()[kmin:kmax]
    h_norm = abs((hp.conj() * hp / pred).sum() ** 0.5)

    mmax = 0
    maxi = -1
    for k, i in enumerate(torder):
        wf = waveforms[i]
        m = numpy.vdot(hp, wf)
        m = abs(m) / h_norm

        if m > mmax:
            mmax = m
            maxi = i
        if mmax > minimal_match:
            break
    return mmax, maxi

p = choose_pool(args.nprocesses)
r = list(tqdm.tqdm(p.imap(find_match, range(len(samples))), total=len(samples)))
matches = [a[0] for a in r]
idx = numpy.array([a[1] for a in r])

logging.info('formatting input')
out = h5py.File(args.output_file, 'w')

for b in bparams:
    out['bank/%s' % b] = bparams[b]

dtype = [(k, numpy.float32) for k in var]

for i in tqdm.tqdm(range(len(bparams[b]))):
    select = samples[numpy.where(idx == i)[0]]
    dlist = [select[k] for k in var]
    data = pycbc.io.FieldArray.from_arrays(dlist, dtype=dtype)
    out.create_dataset('map/%i' % i, data=data,
                       compression='gzip', shuffle=True,
                       compression_opts=9)
