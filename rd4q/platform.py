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

def create():
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan = channel_map.channels

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
    

    """     # CR SETUP
    crtl_qubit = 3
    target_qubit = 2
    cr_chan_id = "cr_test_channel"
    channels[cr_chan_id] = channels[qubits[crtl_qubit].drive]
    virtual_channel_map[cr_chan_id] = virtual_channel_map[qubits[crtl_qubit].drive] """

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
    #platform.parameters.configs[cr_chan_id] = replace(platform.parameters.configs[qubits[target_qubit].drive])
   
    return platform
