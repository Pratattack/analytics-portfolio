# Source and role research

Research snapshot and observation cutoff: October 20, 2026. The shared audited planning base is December 31, 2025; the principal filings were published in February 2026. This is a deliberate common annual base, not a claim that October treasury positions or every latest quarter were analyzed.

## Primary sources

- [SEC EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces): public companyfacts and submissions endpoints. The standard-taxonomy companyfacts API excludes company-specific and dimensioned contexts. Therefore it cannot replace original inline-XBRL context review for these cases.
- Each project's `data/source_manifest.json`: exact issuer identities, original document URLs, accessions, filing dates and original HTML hashes. `data/pinned_archives.json` pins the public numeric snapshots.
- [Travelers 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/trv-20251231.htm) and [Q3 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/86312/000008631226000181/trv-20260930.htm): reserve development and catastrophe/underwriting distinctions motivate a diligence challenge. The Q3 report is theme research only; the model uses the separately identified annual triangles.
- [Kimco 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/879101/000119312526060760/kim-20251231.htm): financing, maturity and corporate / joint-venture distinctions. The consolidated unsecured schedule must not be combined with unconsolidated JV mortgage maturities.
- [Regency 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/910606/000119312526051668/reg-20251231.htm): source CIK 910606 identifies the parent, while 1066247 is the operating partnership. The pipeline explicitly corrects this identity distinction.
- [Regency February 2026 fixed-income supplement](https://www.sec.gov/Archives/edgar/data/910606/000119312526039477/reg-ex99_3.htm): actual credit facilities and a pro-rata debt presentation exist, but neither facility availability nor unconsolidated JV funding is assumed in this model. Those are follow-up diligence requirements.
- [Casualty Actuarial Society, Friedland, Estimating Unpaid Claims Using Basic Techniques](https://www.casact.org/abstract/estimating-unpaid-claims-using-basic-techniques), [official text](https://www.casact.org/sites/default/files/database/studynotes_friedland_estimating.pdf): development-method foundation. No actuarial credential, professional reserve certification or formal Mack confidence interval is claimed.
- [SciPy linprog documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html): independent constrained-solution verification using the HiGHS solver; SciPy is a test dependency, not an opaque financial forecast.

## Official employer requirements and portfolio choices

[McKinsey Business Analyst, role 15136](https://www.mckinsey.com/careers/search-jobs/jobs/businessanalyst-15136), checked October 20, 2026, describes owning an analytical workstream, combining research and data analysis, making reasoned decisions and communicating usable outputs. Its listed requirements include an undergraduate degree, organization, clear communication and work-product creation. This supports prioritizing source integrity, a concrete committee decision, a usable workflow and an executive brief. It does not establish recruiting eligibility, work authorization, job availability in a particular office or a guaranteed interview.

The accessible profile supports economics reasoning and Python/SQL analysis. These projects use those tools with an HTML/JavaScript delivery layer; they do not claim Power BI, Tableau, Java/C++ or other unverified resume skills. No inaccessible LinkedIn contents or private resume contact details are published.

## Why these projects are complementary

The insurance case asks how much confidence a finance committee should place in a development-based reserve challenge. Its main risks are disclosure scope, changing settlement behavior and an unobserved loss tail. The REIT case asks which funding constraints fail under a disclosed maturity ladder; its main risks are persistent cash shortfalls, financing costs and unavailable credit. Their empirical sources and decision methods differ from the existing bank attribution and credit-card acquisition projects.
