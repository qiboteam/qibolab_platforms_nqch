import pathlib

from qibolab import ConfigKinds
from qibolab._core.pulses import Pulse, Readout, Drag, Acquisition, Rectangular
from qibolab._core.components.configs import IqConfig, DcConfig
from qibolab._core.parameters import Parameters, Settings, NativeGates
from qibolab._core.native import SingleQubitNatives, Native
from qibolab._core.instruments.keysight.components import QcsAcquisitionConfig

ConfigKinds.extend([QcsAcquisitionConfig])
ROOT = pathlib.Path(__file__).parent

readout_frequency_maps = {
    0: 4.983e9,
    1: 5.1058e9,
    4: 5.272e9,
    5: 5.41e9,
    6: 5.539e9,
    16: 5.723e9,
    11: 5.8355e9,

    2: 4.974e9,
    3: 5.103e9,
    8: 5.2655e9,
    9: 5.415e9,
    10: 5.5589e9,
    19: 5.76275e9,
    15: 5.849e9,

    7: 4.996e9,
    12: 5.1715e9,
    13: 5.330e9,
    17: 5.5315e9,
    14: 5.685e9,
    18: 5.905e9
}


config = {}
natives = {}
for qubit_id in range(20):
    config[f"{qubit_id}/drive"] = IqConfig(frequency=int(4.35e9))
    config[f"{qubit_id}/probe"] = IqConfig(frequency=int(readout_frequency_maps[qubit_id]))
    config[f"{qubit_id}/acquisition"] = QcsAcquisitionConfig(delay=0, smearing=0)
    config[f"{qubit_id}/flux"] = DcConfig(offset=0)
    natives[qubit_id] = SingleQubitNatives(
        RX=Native([
            (f"{qubit_id}/drive", Pulse(duration=50, amplitude=0.5, envelope=Drag(rel_sigma=2, beta=0)))
        ]),
        MZ=Native([
            (f"{qubit_id}/acquisition", Readout(
                acquisition=Acquisition(duration=2000),
                probe=Pulse(duration=2000, amplitude=0.1, envelope=Rectangular())))
        ])
    )
config["qcs/bounds"] = {
    "kind": "bounds",
    "waveforms": 1.0,
    "readout": 1,
    "instructions": 1
}

params = Parameters(
    settings=Settings(relaxation_time=50000),
    configs=config,
    native_gates=NativeGates(single_qubit=natives)
)

(ROOT / "parameters.json").write_text(params.model_dump_json(indent=4))

