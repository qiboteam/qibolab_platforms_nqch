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

RUNCARD = pathlib.Path(__file__).parent / "icarusq_iqm_5q.yml"

# XY port to DAC channel mapping
cmap_xyline = {
    # RFSoC DAC channel mapping
        "x1": 1,
        # tc[from][to]
        "tc31": 7,
        "x2": 2,
        "tc32": 7,
        "x3": 4,
        "tc13": 8,
        "tc23": 9,
        "tc43": 10,
        "tc53": 11,
        "x4": 5,
        "tc34": 7,
        "x5": 6,
        "tc35": 7,
}

# Qubit mapping to readout port, XY port
cmap_qubits = {
    0: ["r1", "x1"],
    1: ["r1", "x2"],
    2: ["r1", "x3"],
    3: ["r1", "x4"],
    4: ["r1", "x5"],
}
# RO port to DAC, ADC channel pair mapping
cmap_roline = {"r1": (0, 6)}

NAME = "icarusq_iqm_5q"
ADDRESS = "192.168.0.132"

def create(runcard=RUNCARD):
    controller = RFSOC_RO("board2", ADDRESS)
    attenuator = MCAttenuator("ro_att", "192.168.0.10:100")

    controller.setup(
        dac_sampling_rate=5898.24,
        adc_sampling_rate=1966.08,
        delay_samples_offset_dac=0,
        delay_samples_offset_adc=11,
        adcs_to_read=[9]
    )
    attenuator.setup(9)
    #awg.setup()

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

    runcard = load_runcard(runcard)
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
