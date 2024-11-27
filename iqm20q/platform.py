import keysight.qcs as qcs
import pathlib

from qibolab import ConfigKinds
from qibolab.instruments.keysight_qcs import KeysightQCS, QcsAcquisitionConfig
from qibolab._core.qubits import Qubit
from qibolab._core.components import IqChannel, DcChannel, AcquisitionChannel
from qibolab._core.platform import Platform

ConfigKinds.extend([QcsAcquisitionConfig])

ip_addr = "192.168.0.80"
FOLDER = pathlib.Path(__file__).parent
NUM_QUBITS = 20
NUM_COUPLERS = 30
NAME = "iqm20q"

fast_flux_qubits = [1, 3, 5, 7, 9, 11, 13, 15, 18]
connectivity_map = [
    (1, 2),
    (1, 4),
    (2, 5),
    (3, 4),
    (3, 8),
    (4, 5),
    (4, 9),
    (5, 6),
    (5, 10),
    (6, 7),
    (6, 11),
    (7, 12),
    (8, 9),
    (8, 13),
    (9, 10),
    (9, 14),
    (10, 11),
    (10, 15),
    (11, 12),
    (11, 16),
    (12, 17),
    (13, 14),
    (14, 15),
    (14, 18),
    (15, 16),
    (15, 19),
    (16, 17),
    (16, 20),
    (18, 19),
    (19, 20),
]

def create():
    # Setup QCS channel mapping and LO configuration
    # TODO: Move channel mapping setup seperately
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan, flux_qubit_chan, flux_coupler_chan = channel_map.channels

    qubits = {
        idx: Qubit(
            drive=f"{idx}/drive",
            probe=f"{idx}/probe",
            acquisition=f"{idx}/acquisition",
            flux=f"{idx}/flux"
        ) for idx in range(NUM_QUBITS)
    }

    couplers = {
        idx: Qubit(
            flux=f"TC{qb1 - 1}-{qb2 - 1}/flux"
        ) for idx, (qb1, qb2) in zip(range(NUM_COUPLERS), connectivity_map)
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

    for qubit_id, qcs_virtual_channel in zip(fast_flux_qubits, flux_qubit_chan):
        qubit = qubits[qubit_id]
        channels[qubit.flux] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[qubit.flux] = qcs_virtual_channel

    for coupler, qcs_virtual_channel in zip(couplers.values(), flux_coupler_chan):
        channels[coupler.flux] = DcChannel(device="M5301AWG", path="")
        virtual_channel_map[qubit.flux] = qcs_virtual_channel

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
        path=FOLDER, instruments=instruments, qubits=qubits, couplers=couplers, name=NAME
    )
   
    return platform
