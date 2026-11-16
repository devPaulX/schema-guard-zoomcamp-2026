# SchemaGuard

## Problem
Data teams need a quick way to detect invalid CSV
datasets before downstream processing.

## Solution
SchemaGuard validates CSV files against dataset
contracts and stores validation history.

## Expected behavior
- Create a dataset contract with required columns.
- Specify the maximum allowed missing-value rate.
- Upload a CSV file for validation.
- Display PASS or FAIL with explicit reasons.
- Save and browse historical validation runs.
- Preserve local data across application restarts.

## Scope
Single-user educational application.
No authentication or external AI API required.
