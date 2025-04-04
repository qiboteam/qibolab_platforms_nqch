import keysight.qcs as qcs
import pathlib

from qibolab import ConfigKinds
from qibolab.instruments.keysight_qcs import KeysightQCS, QcsAcquisitionConfig
from qibolab._core.qubits import Qubit
from qibolab._core.components import IqChannel, AcquisitionChannel, DcChannel
from qibolab._core.platform import Platform

ConfigKinds.extend([QcsAcquisitionConfig])

ip_addr = "192.168.0.80"
FOLDER = pathlib.Path(__file__).parent
NUM_QUBITS = 20
NAME = "iqm20q"

# temp workaround
qubits_avail = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 17]

connectivity = {
    0: (7, 12),
    1: (2, 7),
    2: (2, 3),
    3: (12, 13),
    6: (3, 8)
}

def create():
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan, fastflux_chan = channel_map.channels

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

    k = 0
    for idx, qubit in qubits.items():
        if idx not in qubits_avail:
            continue

        virtual_channel_map[qubit.drive] = xy_awg_chan[idx]
        channels[qubit.drive] = IqChannel(device="M5300AWG",
                                        path="",
                                        mixer=None,
                                        lo=None)

        channels[qubit.probe] = IqChannel(device="M5300AWG",
                                        path="",
                                        mixer=None,
                                        lo=None)
        virtual_channel_map[qubit.probe] = ro_awg_chan[k]
        channels[qubit.acquisition] = AcquisitionChannel(device="M5200Digitizer",
                                                        path="",
                                                        probe=qubit.probe,
                                                        twpa_pump=None)
        virtual_channel_map[qubit.acquisition] = ro_dig_chan[k]    
        k += 1

    # Manual mapping, to be removed when full chassis is online
    for qubit_idx, chan_idx in zip([3, 7, 13], [4, 5, 7]):
        qubit = qubits[qubit_idx]
        channels[qubit.flux] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[qubit.flux] = fastflux_chan[chan_idx]

    for chan_idx, (qb1, qb2) in connectivity.items():
        chan_name = f"TC {qb1}-{qb2}/flux"
        channels[chan_name] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[chan_name] = fastflux_chan[chan_idx]

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
