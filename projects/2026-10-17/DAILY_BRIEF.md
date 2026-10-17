# Your first two projects — October 17, 2026

## Catalyst Pricing & Contract Economics

Specialty chemicals | aligned to the supplied Ketjen commercial-finance description.

The synthetic portfolio has 30 customers, three catalyst product families and two annual snapshots. Variable contribution falls by $157,706: volume adds $227,627, mix adds $15,820 and price adds $979,360, while unit-cost changes remove $1,380,513. An exact ordered bridge reconciles the change. SQL customer profitability includes assigned service costs; 135 contract scenarios test pricing, demand response, churn and cost inflation. Read `01-catalyst-commercial-economics/outputs/report.html` and the associated memo and CSVs.

My understanding: I should not assume that selling more or raising prices means the business is becoming more profitable. Here, cost inflation exceeds the favorable price, volume and mix effects. I can use the bridge to explain the change clearly, then use contract scenarios to assess which proposals remain attractive if customers buy less or leave. I would validate the service-cost allocations and demand assumptions before turning those scenarios into real recommendations.

## Credit Card Acquisition: Growth vs Risk-Adjusted Value

Consumer credit cards | aligned to the supplied Wells Fargo business-analyst description.

The simulated randomized campaign includes 12,000 prospects. Conversion rises from 9.57% to 10.46%, a 0.89 percentage-point difference, with an approximate 95% interval from -0.19 to 1.96 points. After standardizing customer-segment weights, the incentive reduces modeled three-year NPV by $2.20 per prospect. Its conditional bootstrap interval is -$10.80 to $5.34, so neither the conversion nor modeled value comparison establishes a reliable positive result. There are 81 credit/funding/retention stress scenarios. Read `02-card-acquisition-economics/outputs/report.html` and its memo and CSVs.

My understanding: A campaign can attract more customers and still produce less value if the incentive and expected costs outweigh the extra contribution. I should distinguish the measured conversion comparison from the assumed three-year economics. In this simulation, I would keep the control strategy while gathering stronger evidence, monitor acquisition cost and seasoned loss performance, and avoid claiming that an uncertain lift justifies scaling.

## Verification and status

All nine unit tests passed, including hand-calculated numerical examples and invalid-input cases. Independent raw-data/SQL/output reconciliations passed. Rebuilding after deleting outputs produced byte-identical artifacts for both projects. Details, hashes and test logs are included. These are three automated verification stages, not three independent human reviews. HTML structure was checked; no browser visual review, live deployment or production integration was performed.

Both projects use Python's standard library and SQL, with Excel-compatible CSVs. No Power BI, Tableau, Java or C++ proficiency is assumed. All operating data, probabilities and financial parameters are synthetic. Industry source links provide context only and do not calibrate the simulation. The portfolio contains no resume, email address or phone number.

Published to Pratattack/analytics-portfolio as reproducible source code. HTML reports are downloadable analytical outputs; no hosted application deployment is claimed.

Projects demonstrate analytical practice; they do not represent employment at Ketjen, Wells Fargo or Oracle or substitute for professional tenure.
