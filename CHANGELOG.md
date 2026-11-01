# Changelog

## v1.2.4 — 2026-11-01

- Fixed an s04 labeling issue: corrected 84 `scenario_condition` values and reassigned 49 runs from class 503 to class 502 to match recorded controller settings.
- No raw measurement data changed; updated the labels and regenerated the s04 ZIP archives. Many thanks to Minjae Sung from Seoul National University for reporting the issue.

## v1.2.3 — 2025-07-21

- Fixed a labeling issue in s01, s02, and s03 where `workpiece_usage` was always set to 0 due to an error in the automated CSV label generator.
- Added a supporting feature to the preparation pipeline to improve sampling; raw data was unchanged.

## v1.2.2 — 2025-05-13

- Fixed duplicate data in s03 by removing `003_control-group-3`, which had 86% duplicates compared with class `004_control-group-from-s01` due to a sampling error.

## v1.2.1 — 2025-04-25

- Standardized the Zenodo citation across dataset README files.
- Fixed inconsistent class naming conventions in s05 and s06.
