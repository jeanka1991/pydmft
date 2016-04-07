# -*- coding: utf-8 -*-
r"""
====================
Study of self energy
====================

"""
# Created Wed Apr  6 08:40:36 2016
# Author: Óscar Nájera

from __future__ import division, absolute_import, print_function

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dmft.plot.triqs_dimer as tdp
import dmft.RKKY_dimer as rt
import dmft.common as gf
import dmft.plot.hf_single_site
import dmft.ipt_imag as ipt


def plot_greenfunct(w, gfunc, title, ylabel, ax=None):
    if ax is None:
        f, ax = plt.subplots(1)
    ax.plot(w, gfunc.real, label=r'$\Re e$' + ylabel)
    ax.plot(w, -gfunc.imag, label=r'$-\Im m$' + ylabel)
    ax.legend(loc=0)
    ax.set_xlabel(r'$\omega$')
    ax.set_ylabel(ylabel + r'$(\omega)$')
    ax.set_title(title)
    ax.set_ylim([-3, 3])
    return ax


def plot_pole_eq(w, gf, sig, title):
    plt.figure()
    plt.plot(w, sig.imag, label=r'$\Im m \Sigma$')
    plt.plot(w, (1 / gf).real, label=r'$\Re e G^{-1}$')
    plt.plot(w, -gf.imag, label='DOS')
    plt.legend(loc=0)
    plt.title(title)
    plt.ylim([-3, 3])


def hiltrans(zeta):
    sqr = np.sqrt(zeta**2 - 1)
    sqr = np.sign(sqr.imag) * sqr
    return 2 * (zeta - sqr)

BETA = 100.
tp = 0.3
w_n = gf.matsubara_freq(100., 300)
w = np.linspace(-5, 20, 1000)
w_set = np.arange(100)
eps_k = np.linspace(-1., 1., 61)
with tdp.HDFArchive('tp03f/DIMER_PM_B100.0_tp0.3.h5') as data:
    for u_str in data:
        giw = tdp.get_giw(data[u_str], slice(-1, -5, -1))

        giw_s = np.squeeze(.5 * (giw['sym_up'].data + giw['sym_dw'].data))
        giw_s = np.squeeze(giw['sym_up'].data)[
            len(giw_s) / 2:len(giw_s) / 2 + 300]

        gs = gf.pade_contination(giw_s, w_n, w, w_set)
        siw_s = 1j * w_n - tp - .25 * giw_s - 1 / giw_s
        ss = gf.pade_contination(siw_s, w_n, w, w_set)
        gst = hiltrans(w - tp - (ss.real - 1j * np.abs(ss.imag)))
        lat_gfs = 1 / np.add.outer(-eps_k, w - tp + 5e-2j - ss)
        Aw = np.clip(-lat_gfs.imag / np.pi, 0, 2)

        U = float(u_str[1:])
        title = r'IPT lattice dimer $U={}$, $t_\perp={}$, $\beta={}$'.format(
            U, tp, BETA)
        ax = plot_greenfunct(w, gs, title, r'$G$')
        plot_greenfunct(w, gst, title, r'$G$', ax)
        plt.savefig('DOS_B100_tp{}_U{}.png'.format(tp, U))

        ax = plot_greenfunct(w, ss, title, r'$\Sigma$')
        plt.savefig('Sigma_B100_tp{}_U{}.png'.format(tp, U))

        plot_pole_eq(w, gst, ss, title)
        plt.savefig('Pole_eq_B100_tp{}_U{}.png'.format(tp, U))
        gf.plot_band_dispersion(w, Aw, title, eps_k)
        plt.savefig('Arpes_eq_B100_tp{}_U{}.png'.format(tp, U))
        plt.savefig('Arpes_den_eq_B100_tp{}_U{}.png'.format(tp, U))
