import pathlib
import keysight.qcs as qcs

print(qcs.__version__)
FOLDER = pathlib.Path(__file__).parent

n_qubits = 20
n_fastflux_qubits = 9
n_couplers = 30

QubitId = int
ChannelId = int
AddressId = tuple[int, int, int]
FridgePort = int

# Maps the qubits to their respective AWG/digitizer channels for readout
# Qubits are 1-indexed to match the datasheet
qubit_readout_line_mapping: dict[QubitId, ChannelId] = {
    1:  1,
    2:  1,
    3:  2,
    4:  2,
    5:  1,
    6:  1,
    7:  1,
    8:  3,
    9:  2,
    10: 2,
    11: 2,
    12: 1,
    13: 3,
    14: 3,
    15: 3,
    16: 2,
    17: 1,
    18: 3,
    19: 3,
    20: 2
}

# This maps the qubit / tunable coupler fastflux ports of the fridge to the corresponding QCS address
fastflux_semiprobe_qcs_address_mapping: dict[FridgePort, AddressId] = {
    10: (2, 18, 1),
    5:  (2, 18, 2),
    21: (2, 18, 3),
    33: (2, 18, 4),
    6:  (2, 17, 1),
    13: (2, 17, 2),
    25: (2, 17, 3),
    37: (2, 17, 4),
    1:  (2, 16, 1),
    17: (2, 16, 2),
    29: (2, 16, 3),
    41: (2, 16, 4),
    14: (2, 15, 1),
    22: (2, 15, 2),
    31: (2, 15, 3),
    38: (2, 15, 4),
    18: (2, 14, 1),
    26: (2, 14, 2),
    34: (2, 14, 3),
    42: (2, 14, 4),
    4:  (2, 13, 1),
    15: (2, 13, 2),
    19: (2, 13, 3),
    35: (2, 13, 4),
    3:  (2, 12, 1),
    11: (2, 12, 2),
    23: (2, 12, 3),
    39: (2, 12, 4),
    12: (2, 11, 1),
    16: (2, 11, 2),    
    27: (2, 11, 3),
    43: (2, 11, 4),

    20: (2, 9, 1),
    24: (2, 9, 2),
    28: (2, 9, 3),
    32: (2, 9, 4),
    36: (2, 8, 2),
    40: (2, 8, 3),
    44: (2, 8, 4)
}

# This maps the qubit flux channels to the fridge fastflux ports
qubit_fastflux_semiprobe_mapping: dict[QubitId, FridgePort] = {
    2:  1,
    4:  24,
    6:  4,
    8:  11,
    10: 25,
    12: 19,
    14: 27,
    16: 38,
    19: 32
}

# This maps the tunable coupler flux channels to the fridge fastflux ports
# This is 1-indexed as well to match the datasheet
tc_fastflux_semiprobe_mapping: dict[str, FridgePort] = {
    'TC1-2':   13,
    'TC1-4':   17, 
    'TC2-5':   3, 
    'TC3-4':   40, 
    'TC3-8':   16, 
    'TC4-5':   22, 
    'TC4-9':   26, 
    'TC5-6':   21, 
    'TC5-10':  43, 
    'TC6-7':   39, 
    'TC6-11':  12, 
    'TC7-12':  20, 
    'TC8-9':   15, 
    'TC8-13':  14, 
    'TC9-10':  29, 
    'TC9-14':  28, 
    'TC10-11': 23, 
    'TC10-15': 37, 
    'TC11-12': 42, 
    'TC11-16': 33,
    'TC12-17': 34,
    'TC13-14': 44,
    'TC14-15': 10, 
    'TC14-18': 35, 
    'TC15-16': 6, 
    'TC15-19': 36, 
    'TC16-17': 5, 
    'TC16-20': 41, 
    'TC18-19': 31, 
    'TC19-20': 18
}

# XY slots are pre-ordered for QB1-QB20
# e.g. Slot 6 Channel 1 connects to QB1 and Slot 15 Channel 4 connects to QB20
xy_slot = [6, 8, 11, 13, 15]

readout_awg_slot = 4
readout_downconverter_slot = 17
readout_digitizer_slot = 18

xy_awgs = qcs.Channels(range(n_qubits), "xy_channels", absolute_phase=False)
digs = qcs.Channels(range(n_qubits), "readout_acquisition", absolute_phase=True)
readout_awgs = qcs.Channels(range(n_qubits), "readout_channels", absolute_phase=True)
qubit_flux_awgs = qcs.Channels(range(n_fastflux_qubits), "fastflux_qubit_channels", absolute_phase=False)
tc_flux_awgs = qcs.Channels(range(n_couplers), "fastflux_coupler_channels", absolute_phase=False)

readout_awg_address = [qcs.Address(1, readout_awg_slot, channel) for channel in qubit_readout_line_mapping.values()]
xy_awg_address = [qcs.Address(1, slot, channel) for slot in xy_slot for channel in range(1, 5)]
dig_address = [qcs.Address(1, readout_digitizer_slot, channel) for channel in qubit_readout_line_mapping.values()]
dnc_address = [qcs.Address(1, readout_downconverter_slot, channel) for channel in qubit_readout_line_mapping.values()]
qubit_fastflux_address = [qcs.Address(*fastflux_semiprobe_qcs_address_mapping[semiprobe_port]) for semiprobe_port in qubit_fastflux_semiprobe_mapping.values()]
tc_fastflux_address = [qcs.Address(*fastflux_semiprobe_qcs_address_mapping[semiprobe_port]) for semiprobe_port in tc_fastflux_semiprobe_mapping.values()]

channel_mapper = qcs.ChannelMapper(ip_address="192.168.0.80")

channel_mapper.add_channel_mapping(xy_awgs, xy_awg_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(readout_awgs, readout_awg_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(digs, dig_address, qcs.InstrumentEnum.M5200Digitizer)
channel_mapper.add_channel_mapping(qubit_flux_awgs, qubit_fastflux_address, qcs.InstrumentEnum.M5301AWG)
channel_mapper.add_channel_mapping(tc_flux_awgs, tc_fastflux_address, qcs.InstrumentEnum.M5301AWG)

channel_mapper.add_downconverters(dig_address, dnc_address)

# order of arguments has changed
# Note that readout downconverter shares common LO across its channels
channel_mapper.set_lo_frequencies([(1, readout_awg_slot, chan) for chan in range(1, 4)]
                                  + [(1, readout_downconverter_slot, chan) for chan in range(1, 4)],
                                  4.93e9)
channel_mapper.set_lo_frequencies(xy_awg_address, 4.2e9)

# set the digitizer range
qcs.save(channel_mapper, FOLDER / "chan_map.qcs")
