import keysight.qcs as qcs
import pathlib

from qibolab._core.instruments.qcs import KeysightQCS
from qibolab._core.qubits import Qubit
from qibolab._core.components import IqChannel, DcChannel, AcquisitionChannel
from qibolab._core.platform import Platform

ip_addr = "192.168.0.80"
FOLDER = pathlib.Path(__file__).parent
NUM_QUBITS = 5
NUM_COUPLERS = 4
NAME = "iqm5q_keysight"

def create():
    # Setup QCS channel mapping and LO configuration
    # TODO: Move channel mapping setup seperately
    channel_map: qcs.ChannelMapper = qcs.load(FOLDER / "chan_map.qcs")
    xy_awg_chan, ro_awg_chan, ro_dig_chan, flux_awg_chan = channel_map.channels

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
            flux=f"C{idx}/flux"
        ) for idx in range(NUM_COUPLERS)
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

    qubit = qubits[0]
    channels[qubit.flux] = DcChannel(device="M5301AWG", path="")
    virtual_channel_map[qubit.flux] = flux_awg_chan

    controller = KeysightQCS(
        address=ip_addr,
        channels=channels,
        qcs_channel_map=channel_map,
        virtual_channel_map=virtual_channel_map
    )
    instruments = {
        "qcs": controller
    }
    return Platform.load(
        path=FOLDER, instruments=instruments, qubits=qubits, couplers=couplers, name=NAME
    )
