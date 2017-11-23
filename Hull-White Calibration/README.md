# Hull-White Calibration
This folder contains some functions and classes that help to calibrate the speed of mean reversion and the constant volatility of the spot rate (a and sigma parameters) in the Hull-White model. The calibration choose those parameters that minimize the sum of squared errors between market cap prices (using Black formulas and the quoted volatilities) and prices obtained using Hull-White analytic formulas, namely \
\begin{align*}
min_{a,\sigma}\sum_i (cap_i^B - cap_i^{HW})/cap_i^B
\end{align*}





