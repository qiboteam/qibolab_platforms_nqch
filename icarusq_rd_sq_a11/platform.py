import pathlib

from qibolab.platform import Platform
from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.icarusq import *
from qibolab.instruments.icarusqfpga import *
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent

# XY port to DAC channel mapping
cmap_xyline = {
    # RFSoC DAC channel mapping
        "x1": 1,
        "x2": 4,
        "x3": 6,
        "x4": 9,
        "x5": 0,
        "x6": 7,
        "x7": 8,
        "x8": 10
}

# Qubit mapping to readout port, XY port
cmap_qubits = {
    0: ["r1", "x1"],
    1: ["r1", "x2"],
    2: ["r1", "x3"],
    3: ["r1", "x4"],
    4: ["r1", "x5"],
    5: ["r1", "x6"],
    6: ["r1", "x7"],
    7: ["r1", "x8"]
}
# RO port to DAC, ADC channel pair mapping
cmap_roline = {"r1": (2, 6), "r2": (5, 2)}

NAME = "icarusq_rd_sq_a11"
ADDRESS = "192.168.0.132"

def create():
    controller = RFSOC_RO("board2", ADDRESS,
                           delay_samples_offset_dac=0,
                           delay_samples_offset_adc=11)
    attenuator = MCAttenuator("ro_att", "192.168.0.10:100")
    attenuator.attenuation = 20

    channels: Dict[str, Channel] = {}

    # XY channel mapping
    for input_port, dac_channel in cmap_xyline.items():
        port = controller.ports(input_port)
        port.dac = dac_channel

        channels[input_port] = Channel(
            name=input_port,
            port=port
        )

    # RO channel mapping
    for input_port, (dac_channel, adc_channel) in cmap_roline.items():
        port = controller.ports(input_port)
        port.dac = dac_channel
        port.adc = adc_channel
        channels[input_port] = Channel(
            name=input_port,
            port=port
        )
        channels[input_port].attenuator = attenuator

    cmap = ChannelMap(channels)
    
    instruments = {controller.name: controller}
    instruments.update({attenuator.name: attenuator})

    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)
    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)

    # Map qubit to its channels
    for qid, q in qubits.items():
        readout_port, xy_port = cmap_qubits[qid]
        q.drive = cmap[xy_port]
        q.readout = cmap[readout_port]

    return Platform(
        NAME,
        qubits,
        pairs,
        instruments,
        settings,
        resonator_type="2D",
        couplers=couplers,
    )
