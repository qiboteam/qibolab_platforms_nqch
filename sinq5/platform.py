import keysight.qcs as qcs
import pathlib

from qibolab import ConfigKinds
from qibolab.instruments.keysight_qcs import KeysightQCS, QcsAcquisitionConfig
from qibolab._core.qubits import Qubit
from qibolab._core.components import IqChannel, AcquisitionChannel, DcChannel
from qibolab._core.platform import Platform

ConfigKinds.extend([QcsAcquisitionConfig])

ip_addr = "192.168.0.85"
FOLDER = pathlib.Path(__file__).parent
NUM_QUBITS = 5
NAME = "sinq5"

fastflux_qubits = [0, 2, 3, 4]

connectivity = [
    (0, 2),
    (1, 2), 
    (2, 3), 
    (2, 4), 
]

def create():
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan, qb_flux_chan, tc_flux_chan = channel_map.channels

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

    for qubit_idx, qcs_channel in zip(fastflux_qubits, qb_flux_chan):
        qubit = qubits[qubit_idx]
        channels[qubit.flux] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[qubit.flux] = qcs_channel

    offset_channels = [f"{qb}/flux" for qb in fastflux_qubits]
    for (qb1, qb2), qcs_channel in zip(connectivity, tc_flux_chan):
        chan_name = f"TC {qb1}-{qb2}/flux"
        channels[chan_name] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[chan_name] = qcs_channel
        offset_channels.append(chan_name)

    controller = KeysightQCS(
        address=ip_addr,
        channels=channels,
        qcs_channel_map=channel_map,
        virtual_channel_map=virtual_channel_map,
        offset_channels=offset_channels
    )
    instruments = {
        "qcs": controller
    }
    platform = Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, name=NAME
    )
   
    return platform
