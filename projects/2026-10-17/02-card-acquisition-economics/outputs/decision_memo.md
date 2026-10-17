# Credit Card Acquisition: Growth vs Risk-Adjusted Value

SYNTHETIC PORTFOLIO CASE | USD | 2026-10-17

Synthetic randomized campaign: conversion lift 0.89 percentage points; modeled incremental NPV $-2.20 per prospect after standardizing segment mix.

## Decision

Do not scale an incentive based on conversion alone. Retain control pending stronger value evidence; track realized acquisition cost, vintage loss, spend, attrition and complaints before scaling. This conclusion applies only to the simulation.

## Experiment

12,000 randomized prospects. Control 9.57%, treatment 10.46%. Unadjusted approximate 95% lift interval: [-0.19, 1.96] percentage points. Assignment occurs before conversion; intention-to-treat conversion includes all prospects.

## Economics

Three-year acquired-account NPV combines interest, funding, net interchange/rewards, expected loss, servicing and acquisition cost. Treatment adds $70 per acquired account. Standardized modeled value difference $-2.20/prospect; conditional 95% parametric bootstrap interval [$-10.80, $5.34]. Uncertainty covers conversions only, conditional on assumed economics; not full business uncertainty.

## Stress & measurement plan

81 segment scenarios vary PD by 1x/1.5x/2x, funding 4%/5.5%/7.5%, and annual retention 75%/88%/95%. Pre-register a fixed horizon and primary NPV/prospect metric; monitor credit-loss and complaint guardrails. Do not repeatedly peek and stop on significance. No protected characteristics enter the simulation.

## Limitations

All prospects, probabilities and financial parameters are simulated. This is a static exposure approximation, not a lending decision engine or regulatory capital model. PD and LGD are assumptions, not fitted predictions. No revenue recognized on defaulted balances is modeled explicitly. Real rollout requires seasoned vintages, compliance review and credit/finance validation.

## Personal understanding

I can explain why an offer that converts more prospects may still destroy value: additional incentives and expected losses can exceed the extra contribution. Randomization supports a conversion comparison within this simulation, while the profit conclusion remains conditional on the financial assumptions. I would separate observed outcomes from modeled lifetime value in an interview.

## Sources & role alignment

Wells Fargo Business Analyst description supplied by the user: economic models, acquisition, P&L, test plans and post-launch measurement. Context: https://www.federalreserve.gov/Releases/G19/Current/default.htm (reviewed 2026-10-17). No Federal Reserve figures are ingested or used to calibrate assumptions; context only.

