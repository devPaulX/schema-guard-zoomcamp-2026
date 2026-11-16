"""Pure CSV validation rules. Uploaded bytes are never changed or persisted."""

import csv
import io
from dataclasses import dataclass


MAX_CSV_BYTES = 5 * 1024 * 1024


class InvalidCSV(ValueError):
    """The upload cannot be interpreted as a valid UTF-8 CSV dataset."""


@dataclass(frozen=True)
class ValidationResult:
    status: str
    reasons: list[str]


def validate_csv(contents: bytes, required_columns: list[str], threshold: float) -> ValidationResult:
    if not contents:
        raise InvalidCSV("CSV file is empty.")
    if len(contents) > MAX_CSV_BYTES:
        raise InvalidCSV("CSV file exceeds the 5 MiB limit.")
    try:
        decoded = contents.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidCSV("CSV file must be UTF-8 encoded.") from exc
    if "\x00" in decoded:
        raise InvalidCSV("CSV file contains a NUL character.")

    try:
        reader = csv.reader(io.StringIO(decoded, newline=""), strict=True)
        headers = next(reader, None)
        if not headers or any(not name.strip() for name in headers):
            raise InvalidCSV("CSV file must have nonempty headers.")
        if len(headers) != len(set(headers)):
            raise InvalidCSV("CSV file has duplicate headers.")

        indexes = {name: position for position, name in enumerate(headers)}
        missing_counts = {name: 0 for name in required_columns if name in indexes}
        row_count = 0
        for row in reader:
            row_count += 1
            if len(row) != len(headers):
                raise InvalidCSV(
                    f"CSV row {row_count + 1} has {len(row)} columns; expected {len(headers)}."
                )
            for name in missing_counts:
                if not row[indexes[name]].strip():
                    missing_counts[name] += 1
    except csv.Error as exc:
        raise InvalidCSV(f"Malformed CSV: {exc}.") from exc

    if row_count == 0:
        raise InvalidCSV("CSV file must contain at least one data row.")

    reasons = [f"Required column '{name}' is missing." for name in required_columns if name not in indexes]
    for name in required_columns:
        if name in missing_counts:
            count = missing_counts[name]
            percentage = count * 100 / row_count
            if percentage > threshold:
                reasons.append(
                    f"Column '{name}' has {percentage:.2f}% missing values "
                    f"({count}/{row_count}); allowed maximum is {threshold:g}%."
                )
    return ValidationResult("FAIL" if reasons else "PASS", reasons)
