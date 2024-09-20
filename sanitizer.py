from typing import Dict, List
from dataclasses import dataclass
import datetime
import csv
import re


def is_english(text):
    # Check if the text contains only English alphabet characters and spaces
    return bool(re.match(r"^[A-Za-z\s]*$", text))


def parse_time(time_str):
    if ":" in time_str:
        minutes, seconds = time_str.split(":")
        total_seconds = int(minutes) * 60 + float(seconds)
    else:
        total_seconds = float(time_str)

    return datetime.timedelta(seconds=total_seconds)


NAME_KEY = "Name"
TIMESTAMP_KEY = "חותמת זמן"


@dataclass
class EventResult:
    event: str
    result: datetime.timedelta


@dataclass
class CuberResults:
    name: str
    results: List[EventResult]


def build_comp_results(data: List[Dict[str, str]]) -> List[CuberResults]:
    return [build_cuber_results(row) for row in data]


def build_cuber_results(row: Dict[str, str]) -> CuberResults:
    name = row.pop(NAME_KEY)
    time_stamp = row.pop(TIMESTAMP_KEY)
    event_results = []
    for event, time in row.items():
        if time == "":
            continue
        if event == "Multiblind":
            print("SKIPPING MULTIBLIND")
            continue
        if time == "DNF":
            print("SKIPPING DNF")
            continue
        event_results.append(EventResult(event, parse_time(time)))
    cuber_results = CuberResults(name=name, results=event_results)
    return cuber_results


def read_results() -> List[Dict[str, str]]:
    with open("results.csv", newline="", encoding="utf-8-sig") as data:
        reader = csv.DictReader(data)
        return [row for row in reader]


def sanitize_comp_results(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return [sanitize_cuber_results(result) for result in results]


def sanitize_cuber_results(result: Dict[str, str]) -> Dict[str, str]:
    result[NAME_KEY] = sanitize_name(result[NAME_KEY])
    events = {
        key: value
        for key, value in result.items()
        if key not in [NAME_KEY, TIMESTAMP_KEY]
    }
    for event, time in events.items():
        result[event] = sanitize_time(event, time)
    return result


def sanitize_name(raw_name: str) -> str:
    stripped_string = raw_name.strip()

    if not is_english(stripped_string):
        print(f"error: name '{stripped_string}' is not in English.")
        return f"ERROR: {stripped_string}"
        # stripped_string = input("input the fixed name: ").strip()

    name = " ".join(word.capitalize() for word in stripped_string.split())
    return name


def is_time_duration(raw_time: str) -> bool:
    if raw_time == "":
        return True
    pattern = r"^(?:\d{1,2}\.\d{2}|\d{1,2}:\d{2}\.\d{2})$"
    return bool(re.match(pattern, raw_time))


def is_multiblind_result(input_str: str) -> bool:
    pattern = r"^(\d+)/(\d+) (\S+)$"

    match = re.match(pattern, input_str)
    if not match:
        return False

    solved = int(match.group(1))
    total = int(match.group(2))
    timestamp = match.group(3)

    if solved > total:
        return False

    return is_time_duration(timestamp)


def sanitize_time(event: str, raw_time: str) -> str:
    stripped_string = raw_time.strip()
    if stripped_string == "":
        return ""
    if stripped_string.upper() == "DNF":
        return "DNF"
    event_result_validators = {"Multiblind": is_multiblind_result}
    result_parser = event_result_validators.get(event, is_time_duration)
    if not result_parser(stripped_string):
        print(f"error: time '{stripped_string}' is not a result.")
        return f"ERROR: {stripped_string}"
        # stripped_string = input("input the fixed time: ").strip()
    return stripped_string


def write_sanitized(data: List[Dict[str, str]], filename: str):
    if not data:
        print("the provided list is empty")
        return
    headers = data[0].keys()
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def main():
    raw_results = read_results()
    sanitized = sanitize_comp_results(raw_results)
    write_sanitized(sanitized, "results_sanitized.csv")
    # pprint(sanitized)

    # results = build_comp_results(sanitized)
    # pprint(results)

    # results = []
    # for row in reader:
    #     cuber_results = parse_cuber_results(row)
    #     results.append(cuber_results)
    #
    # return results
    # pprint(read_results())


if __name__ == "__main__":
    main()
