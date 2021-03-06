# -*- coding: utf-8 -*-
r"""
Dimer Mott transition
=====================

Follow the spectral function from the correlated metal into the dimer
Mott insulator. The spectral functions is decomposed into the bonding
and anti-bonding contributions to make it explicit that is is a
phenomenon of the quasiparticles opening a band gap.

Using Matsubara frequency solver

.. seealso::
    :ref:`sphx_glr_dimer_lattice_nature_dimer_plot_order_param_transition.py`
"""

# author: Óscar Nájera

from __future__ import division, absolute_import, print_function

import numpy as np
import matplotlib.pyplot as plt

import dmft.common as gf
from dmft import ipt_imag
import dmft.dimer as dimer


def ipt_u_tp(urange, tp, beta, w):

    tau, w_n = gf.tau_wn_setup(dict(BETA=beta, N_MATSUBARA=2**11))
    giw_d, giw_o = dimer.gf_met(w_n, 0., tp, 0.5, 0.)

    w_set = list(np.arange(0, 120, 2))
    w_set = w_set + list(np.arange(120, 512, 8))
    imgss = []

    for u_int in urange:
        giw_d, giw_o, loops = dimer.ipt_dmft_loop(
            beta, u_int, tp, giw_d, giw_o, tau, w_n, 1e-9)
        g0iw_d, g0iw_o = dimer.self_consistency(
            1j * w_n, 1j * giw_d.imag, giw_o.real, 0., tp, 0.25)
        siw_d, siw_o = ipt_imag.dimer_sigma(
            u_int, tp, g0iw_d, g0iw_o, tau, w_n)

        ss = gf.pade_continuation(
            1j * siw_d.imag + siw_o.real, w_n, w + 0.0005j, w_set)  # A-bond

        imgss.append(gf.semi_circle_hiltrans(
            w - tp - (ss.real - 1j * np.abs(ss.imag))))
    return imgss


w = np.linspace(-4, 4, 2**12)
BETA = 512.
tp = 0.3
uranget3 = [0.2, 1., 2., 3., 3.45, 3.5]
imgsst3 = ipt_u_tp(uranget3, tp, BETA, w)

tp = 0.8
uranget8 = [0.2, 1., 1.2, 1.35, 2., 3.]
imgsst8 = ipt_u_tp(uranget8, tp, BETA, w)


def plot_dos(urange, imgss, ax, labelx):
    for i, (U, gss) in enumerate(zip(urange, imgss)):
        imgss = -gss.imag
        imgsa = imgss[::-1]
        ax[i].plot(w, imgsa, 'C0:', lw=0.5)
        ax[i].plot(w, imgss, 'C1-.', lw=0.5)
        ax[i].plot(w, (imgss + imgsa) / 2, 'k', lw=2.5)
        ax[i].text(labelx, 1.7, r"$U={}$".format(U), size=16)
        ax[i].set_yticks(np.arange(3))
        ax[i].set_xticks(np.arange(-3, 4))

    ax[i].set_xlabel(r'$\omega$')
    ax[i].set_xlim([-3.2, 3.2])
    ax[i].set_ylim([0, 2.4])


plt.rcParams['figure.autolayout'] = False
plt.rcParams['axes.labelsize'] = 'medium'
plt.rcParams["axes.grid"] = False
plt.rcParams["ytick.labelsize"] = 'x-small'
plt.rcParams["xtick.labelsize"] = 'x-small'
plt.close()
fig, axes = plt.subplots(6, 2, sharex=True, sharey=True)
plot_dos(uranget3, imgsst3, axes[:, 0], -3)
plot_dos(uranget8, imgsst8, axes[:, 1], 1.)
axes[0, 0].set_title(r'$t_\perp=0.3$')
for ax in axes:
    ax[0].set_ylabel(r'$A(\omega)$')
axes[0, 1].set_title(r'$t_\perp=0.8$')
plt.subplots_adjust(wspace=0.04, hspace=0.09)
# plt.savefig('dimer_transition_spectra.pdf')
# plt.close()
