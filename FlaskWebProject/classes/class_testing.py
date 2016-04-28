from BarnModel import *

import matplotlib.pyplot as plt
from numpy import arange

w2fDeath1 = [0]
w2fDeath2 = [-0.2500, 23.9464, -4.30357143]
w2fDeath3 = [11]
w2fDeath4 = [-526.6290 + 11, 66.8357, -2.03571429]
w2fDeath5 = [-725.9390 + 11, 64.3674, -1.35984848]
w2fDeath6 = [0]

w2fDeath_br = [0, 5, 13.1, 19.1, 27]

finModel = [0, 210.431209, -65.244076, 9.294793, -0.678313, 0.024900, -0.000365]
awgModel = [0.43503557, 2.16250341, -0.09743488, 0.00122924]
awfiModel = [0.90582088, 1.59691733, 0.24820408, -0.01655183, 0.00028117]
awfcModel = [1.1, 0.10728206]
awgAdjust = [273, 0, 24.5]
awfcAdjust = [2.65, 0, 24.5]

feed_cost_br = [2.62141065, 4.12473822, 
				6.29822741, 8.85710311, 11.78041278, 14.48593525,
				17.1341315, 17.63894897, 18.8702043, 20.1224158]

feed_cost_br_wt = [ 20., 30.,
					50., 80., 120., 160.,
            		200., 225., 245., 265.]

priceCutoff = [	0.29438071, 0.18980649, 0.11205248,
				0.09077630, 0.08552250, 0.07965624, 0.07812813,
				0.07665118, 0.07570529, 0.09360718, 0.09719425]

awg_poly = [polynomial(awgModel), polynomial(awgModel) * (1 + (0.089 * 1)), polynomial(awgModel) * (1 + (0.089 * 0.8))]
awg_br = [21., 23.]
awg_br_wt = [245., 265.]
awgModel = PiecePolynomial(awg_poly, awg_br, awg_br_wt)

awfc_poly = [polynomial(awfcModel), polynomial(awfcModel) * (1 - (0.142 * 1)), polynomial(awfcModel) * (1 - (0.142 * 0.8))]
awfc_br = [21., 23.]
awfcModel = PiecePolynomial(awfc_poly, awfc_br)



awgModelAdjust = [275, 0, 18.7 + 6]
awfcModelAdjust = [2.76, 0, 18.7 + 6]
feedCostModel = PiecePolynomial([0.0960], [], [])

gm = PigGrowthModel(awgModel, awfcModel, feedCostModel, awgModelAdjust, awfcModelAdjust, 33)

print gm.awg.shift_x
print gm.feed_cost_total(gm.wt_total.weeks(207))
print gm.wt_total.weeks(207)
print gm.wt_total.weeks(275)

x = arange(0,20)
plt.plot(x, gm.wt_total(x))
plt.show()
