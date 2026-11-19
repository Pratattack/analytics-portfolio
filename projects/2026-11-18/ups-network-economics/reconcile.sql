SELECT window, year, scope,
       gaap + COALESCE(network, 0) + other_transformation + impairment
            + asset_gain + divestiture - adjusted AS adjusted_residual
FROM reported ORDER BY scope, window, year;
