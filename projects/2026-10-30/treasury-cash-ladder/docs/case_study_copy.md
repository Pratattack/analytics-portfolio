# Which cash can wait until maturity?

A $1 million cash scenario earns a modeled $6,279 while meeting every payment and reserve constraint. The allocation is driven by when cash is needed, as well as the quoted yield.

## Finding
The reference $1 million scenario earns $6,279 above zero-yield cash after $700,000 of modeled payments, while preserving at least $100,000 of spendable cash at each tested date. It holds $150,000 uninvested so the day-14 stress payment can clear. The result uses indicative October 29 quotes and assumed maturities; it is not an executed return.

## Decision use
A headline yield is insufficient when money is needed before maturity. Use a dated cash forecast to limit what can be invested, then test reserve and fee assumptions before seeking executable prices.

## Methods
Linear programming with explicit capital, payment-date and minimum-cash constraints. Convert bank discount quotes to modeled purchase-to-maturity factors. An independent JavaScript vertex solver checks the Python HiGHS solution. SQL audits capital and the minimum reserve. Test early stress payments, reserve levels and fees.

## Limits
Fixed 28-, 56- and 91-day tenors approximate security dates. No early sale, reinvestment, taxes, lot sizes, bid-ask spread or holiday adjustment is modeled. Treasury bid quotations are not executable offers. The baseline cash yield is assumed zero. No real company cash flow or achieved investment return is claimed.
