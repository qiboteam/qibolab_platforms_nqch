import json
import pathlib

ROOT = pathlib.Path(__file__).parent

with open(ROOT / "calibration.json") as r:
    calib = json.load(r)

with open(ROOT / "parameters.json") as r:
    parameters = json.load(r)

for qubit in range(20):
    qb = str(qubit)
    calib["single_qubits"][qb]["resonator"]["dressed_frequency"] = parameters["configs"][f"{qubit}/probe"]["frequency"]

(ROOT / "calibration.json").write_text(json.dumps(calib, indent=4))
