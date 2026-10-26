from pathlib import Path

lines = Path(__file__).with_name("boot.log").read_text().splitlines()[1:]
results = []
for line in lines:
    if "Unable to mount root fs" in line:
        result = "root-device-or-filesystem: inspect root=, storage driver, partition and fs support"
    elif "No working init found" in line:
        result = "init-execution: inspect init path, permissions, ELF, interpreter and libraries"
    else:
        result = "unknown: retain full log and last confirmed boot stage"
    results.append(result.split(":")[0])
    print(result)
assert results == ["root-device-or-filesystem", "init-execution", "unknown"]
