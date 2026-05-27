import pathlib
import numpy as np

from qibolab import ConfigKinds
from qibolab._core.pulses import Pulse, Readout, Drag, Acquisition, Rectangular
from qibolab._core.components.configs import IqConfig, DcConfig
from qibolab._core.parameters import Parameters, Settings, NativeGates
from qibolab._core.native import SingleQubitNatives, Native
from qibolab._core.instruments.keysight.components import QcsAcquisitionConfig

ConfigKinds.extend([QcsAcquisitionConfig])
ROOT = pathlib.Path(__file__).parent

readout_frequency_maps = {
    0: 5296988373.986935,
    1: 5120310344.21199,
    2: 5810167789.64958,
    3: 5651451476.68602,
    4: 5464023693.521766,
}

connectivity = [
    (0, 2),
    (1, 2), 
    (2, 3), 
    (2, 4), 
]

config = {}
natives = {}
for qubit_id in range(5):
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
for (qb1, qb2) in connectivity:
    chan_name = f"TC {qb1}-{qb2}/flux"
    config[chan_name] = DcConfig(offset=0)

params = Parameters(
    settings=Settings(relaxation_time=200_000),
    configs=config,
    native_gates=NativeGates(single_qubit=natives)
)

(ROOT / "parameters.json").write_text(params.model_dump_json(indent=4))

