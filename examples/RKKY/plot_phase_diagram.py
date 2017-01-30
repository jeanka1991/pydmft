# -*- coding: utf-8 -*-
"""
Energy calculation of the Dimer lattice
=======================================

Close to the coexistence region the Energy of the system is calculated.
"""
from math import log
import numpy as np
from scipy.integrate import simps
import matplotlib.pyplot as plt
import dmft.dimer as dimer
import dmft.common as gf
import dmft.ipt_imag as ipt

tpr = np.hstack((np.arange(0, 0.5, 0.02), np.arange(0.5, 1.1, 0.05)))
ur = np.arange(0, 4.5, 0.1)

tpi = 15  # This sets tp in the calculation tpi=15-> tp=0.3

BETARANGE = np.round(
    np.hstack(([768, 512], np.logspace(8, -4.5, 41, base=2))), 2)
temp = 1 / np.array(BETARANGE)
Tux, Ty = np.meshgrid(ur, temp)
tpx, uy = np.meshgrid(tpr, ur)

f, ax = plt.subplots(1, 2, figsize=(18, 7))
fl_d = np.load('disk/dimer_07_2015/Dimer_ipt_metal_seed_FL_DOS_BUt.npy')
fli_d = np.load(
    'disk/dimer_07_2015/Dimer_ipt_insulator_seed_FL_DOS_BUt.npy')

s0 = ax[1].pcolormesh(tpx, uy, fl_d[1], cmap=plt.get_cmap('viridis'))
m = ax[0].pcolormesh(Tux, Ty, fl_d[:, :, tpi], cmap=plt.get_cmap('viridis'))


s0 = ax[1].pcolormesh(tpx, uy, fli_d[1], alpha=0.2,
                      cmap=plt.get_cmap('viridis'))
m = ax[0].pcolormesh(Tux, Ty, fli_d[:, :, tpi], alpha=0.2,
                     cmap=plt.get_cmap('viridis'))

ax[1].axis([tpx.min(), tpx.max(), uy.min(), uy.max()])
ax[0].axis([Tux.min(), Tux.max(), 0, .14])

plt.colorbar(m, ax=ax[0])
plt.colorbar(s0, ax=ax[1])

ax[0].set_ylabel('$T/D$')
ax[0].set_xlabel('U/D')
ax[0].set_title('Phase Diagram $t_\\perp={}$\n'
                'color represents $-\\Im G_{{AA}}(0)$'.format(tpr[tpi]))
ax[1].set_xlabel(r'$t_\perp$')
ax[1].set_ylabel('U/D')
ax[1].set_title('Phase Diagram $\\beta={}$\n'
                'color represents $-\\Im G_{{AA}}(0)$'.format(BETARANGE[1]))

ax[0].axvline(1.8, lw=2, color='r')
ax[0].axvline(2.5, lw=2, color='r')
ax[0].axvline(3.2, lw=2, color='r')
ax[0].axvline(4.0, lw=2, color='r')

ax[1].plot([tpr[tpi]] * 4, [1.8, 2.5, 3.2, 4.0], 'ro', ms=10)


###############################################################################

def loop_beta(u_int, tp, betarange, seed='mott gap'):
    giw_s = []
    sigma_iw = []
    ekin, epot = [], []
    iterations = []
    for beta in betarange:
        tau, w_n = gf.tau_wn_setup(
            dict(BETA=beta, N_MATSUBARA=max(8 * beta, 64)))
        giw_d, giw_o = dimer.gf_met(w_n, 0., 0., 0.5, 0.)
        if seed == 'I':
            giw_d, giw_o = 1 / (1j * w_n - 4j / w_n), np.zeros_like(w_n) + 0j

        giw_d, giw_o, loops = dimer.ipt_dmft_loop(
            beta, u_int, tp, giw_d, giw_o, tau, w_n, 1e-4)
        giw_s.append((giw_d, giw_o))
        iterations.append(loops)
        g0iw_d, g0iw_o = dimer.self_consistency(
            1j * w_n, 1j * giw_d.imag, giw_o.real, 0., tp, 0.25)
        siw_d, siw_o = ipt.dimer_sigma(u_int, tp, g0iw_d, g0iw_o, tau, w_n)
        sigma_iw.append((siw_d.copy(), siw_o.copy()))

        ekin.append(dimer.ekin(giw_d, giw_o, w_n, tp, beta))

        epot.append(dimer.epot(giw_d, w_n, beta, u_int **
                               2 / 4 + tp**2, ekin[-1], u_int))
    # print(np.array(iterations))

    return giw_s, np.array(ekin), np.array(epot)  # , w_n, sigma_iw

BETARANGE = np.hstack((np.around(1 / np.arange(1.e-3, .1, 1.5e-3), decimals=2),
                       np.logspace(3.3, -4.5, 78, base=2)))

temp = 1 / BETARANGE

U_int = [1.8, 2.5, 3.2, 4.0]
start = ['M', 'M', 'I', 'I']
solutions = [loop_beta(u_int, tpr[tpi], BETARANGE, seed)
             for u_int, seed in zip(U_int, start)]

###############################################################################
# Internal Energy
# ---------------
#
# It is very strange as :math:`U` grows into the insulator that there is an
# increase in internal energy as the system is cooled down. It can
# also be seen how the insulator has lower internal energy at :math:`U=3.5`

fig, ax = plt.subplots(2)
colors = ['b', 'g', 'c', 'r', 'y', 'k']
for i, sol in enumerate(solutions):
    u, c = U_int[i], colors[i]
    li = c + '--' if 'I' == start[i] else c + '-'
    ax[0].plot(temp, sol[1] + sol[2], li, label='U={} {}'.format(u, start[i]))
    ax[1].plot(temp, sol[1] + sol[2], li)
ax[0].set_xlim([0, 5])
ax[0].set_ylim([-0.35, 1.5])
ax[1].set_xlim([0, .12])
ax[1].set_ylim([-.35, 0.0])

ax[0].set_title('Internal Energy')
ax[0].set_xlabel('T/D')
ax[0].set_ylabel(r'$\langle  H \rangle$')
ax[0].legend(loc=0)
ax[1].set_xlabel('T/D')
ax[1].set_ylabel(r'$\langle  H \rangle$')


###############################################################################
# Double occupation
# -----------------

fig, ax = plt.subplots(2)
for i, sol in enumerate(solutions):
    u, c = U_int[i], colors[i]
    li = c + '--' if 'I' == start[i] else c + '-'
    ax[0].plot(temp, 2 * sol[2] / 4 / u, li,
               label='U={} {}'.format(u, start[i]))
    ax[1].plot(temp, 2 * sol[2] / 4 / u, li)
ax[0].set_xlim([0, 5])
ax[0].set_ylim([0.0, .25])
ax[1].set_xlim([0, .2])
ax[1].set_ylim([0.0, .15])

ax[0].set_title('Double Occupation')
ax[0].set_xlabel('T/D')
ax[0].set_ylabel(r'$\langle n_\uparrow n_\downarrow \rangle$')
ax[0].legend(loc=0)
ax[1].set_xlabel('T/D')
ax[1].set_ylabel(r'$\langle n_\uparrow n_\downarrow \rangle$')

###############################################################################
# Specific Heat and Entropy
# -------------------------
#

fig_cv, ax_cv = plt.subplots(2)
fig_s, ax_s = plt.subplots(2)

for i, sol in enumerate(solutions):
    u, c = U_int[i], colors[i]
    li = c + '--' if 'I' == start[i] else c + '-'

    H = sol[1] + sol[2]
    CV = (H[1:] - H[:-1]) / (temp[1:] - temp[:-1])

    ax_cv[0].plot(temp[:-1], CV, li, label='U={} {}'.format(u, start[i]))
    ax_cv[1].plot(temp[:-1], CV, li)

    cv_temp = np.hstack((np.clip(CV, 0, 1) / temp[:-1], 0))
    S = np.array([simps(cv_temp[i:], temp[i:], even='last')
                  for i in range(len(temp))]) / 4
    ax_s[0].plot(temp, log(2.) - S, li, label='U={} {}'.format(u, start[i]))
    ax_s[1].plot(temp, log(2.) - S, li)

ax_cv[0].set_xlim([0, 3])
ax_cv[0].set_ylim([-0.08, .83])
ax_cv[1].set_xlim([0, .125])
ax_cv[1].set_ylim([-0.08, 0.83])

ax_cv[0].set_title('Heat Capacity')
ax_cv[0].set_xlabel('T/D')
ax_cv[0].set_ylabel(r'$C_V$')
ax_cv[1].set_xlabel('T/D')
ax_cv[1].set_ylabel(r'$C_V$')
ax_cv[0].legend(loc=0)


ax_s[0].set_xlim([0, 2])
ax_s[0].set_ylim([0.0, log(2)])
ax_s[1].set_xlim([0, .125])
ax_s[1].set_ylim([0., 0.43])

ax_s[0].set_title('Entropy')
ax_s[0].set_xlabel('T/D')
ax_s[0].set_ylabel(r'$S$')
ax_s[1].set_xlabel('T/D')
ax_s[1].set_ylabel(r'$S$')
ax_s[0].legend(loc=0)
ax_s[0].axhline(log(2) / 2, ls=":")
ax_s[1].axhline(log(2) / 2, ls=":")
