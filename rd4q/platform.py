import keysight.qcs as qcs
import pathlib

from qibolab import ConfigKinds
from qibolab.instruments.keysight_qcs import KeysightQCS, QcsAcquisitionConfig
from qibolab._core.qubits import Qubit
from qibolab._core.components import IqChannel, AcquisitionChannel
from qibolab._core.platform import Platform
from qibolab._core.serialize import replace

ConfigKinds.extend([QcsAcquisitionConfig])

ip_addr = "192.168.0.148"
FOLDER = pathlib.Path(__file__).parent
NUM_QUBITS = 4
NAME = "rd4q"
connectivity = [(0, 1), (1, 2), (2, 3)]

def create():
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan, cr_awg_chan = channel_map.channels

    qubits = {
        idx: Qubit(
            drive=f"{idx}/drive",
            probe=f"{idx}/probe",
            acquisition=f"{idx}/acquisition",
            flux=f"{idx}/flux"
        ) for idx in range(NUM_QUBITS)
    }

    channels = {}
    virtual_channel_map = {}

    for idx, qubit in qubits.items():
        virtual_channel_map[qubit.drive] = xy_awg_chan[idx]
        channels[qubit.drive] = IqChannel(device="M5300AWG",
                                        path="",
                                        mixer=None,
                                        lo=None)
        

        channels[qubit.probe] = IqChannel(device="M5300AWG",
                                        path="",
                                        mixer=None,
                                        lo=None)
        virtual_channel_map[qubit.probe] = ro_awg_chan[idx]
        channels[qubit.acquisition] = AcquisitionChannel(device="M5200Digitizer",
                                                        path="",
                                                        probe=qubit.probe,
                                                        twpa_pump=None)
        virtual_channel_map[qubit.acquisition] = ro_dig_chan[idx]    
    
    # CR SETUP
    idx = 0
    for qubit_a, qubit_b in connectivity:
        for crtl_qubit_id, tgt_qubit_id in [(qubit_a, qubit_b), (qubit_b, qubit_a)]:
            cr_chan_id = f"CR_{crtl_qubit_id}_{tgt_qubit_id}/drive"
            channels[cr_chan_id] = IqChannel(device="M5300AWG",
                                            path="",
                                            mixer=None,
                                            lo=None)
            virtual_channel_map[cr_chan_id] = cr_awg_chan[idx]
            idx += 1

    controller = KeysightQCS(
        address=ip_addr,
        channels=channels,
        qcs_channel_map=channel_map,
        virtual_channel_map=virtual_channel_map
    )
    instruments = {
        "qcs": controller
    }
    platform = Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, name=NAME
    )
   
    return platform
