import pathlib
import keysight.qcs as qcs

print(qcs.__version__)
FOLDER = pathlib.Path(__file__).parent

n_qubits = 5
n_fastflux_qubits = 4
n_couplers = 4

QubitId = int
ChannelId = int

xy_mapping = [(4, 1), (4, 2), (4, 3), (4, 4), (6, 1)]
tc_mapping = [(3, 1), (3, 2), (3, 3), (3, 4)]
z_mapping  = [(11, 1), (11, 2), (11, 3), (11, 4)]

readout_awg_slot = 6
readout_awg_channel = 2
readout_downconverter_slot = 17
readout_downconverter_channel = 1
readout_digitizer_slot = 18
readout_digitizer_channel = 1

xy_awgs = qcs.Channels(range(n_qubits), "xy_channels", absolute_phase=False)
digs = qcs.Channels(range(n_qubits), "readout_acquisition", absolute_phase=True)
readout_awgs = qcs.Channels(range(n_qubits), "readout_channels", absolute_phase=True)
qubit_flux_awgs = qcs.Channels(range(n_fastflux_qubits), "fastflux_qubit_channels", absolute_phase=False)
tc_flux_awgs = qcs.Channels(range(n_couplers), "fastflux_coupler_channels", absolute_phase=False)

readout_awg_address = [qcs.Address(1, readout_awg_slot, readout_awg_channel) for _ in range(n_qubits)]
xy_awg_address = [qcs.Address(1, slot, channel) for (slot, channel) in xy_mapping]
dig_address = [qcs.Address(1, readout_digitizer_slot, readout_digitizer_channel) for _ in range(n_qubits)]
dnc_address = [qcs.Address(1, readout_downconverter_slot, readout_downconverter_channel) for _ in range(n_qubits)]
qubit_fastflux_address = [qcs.Address(1, slot, channel) for (slot, channel) in z_mapping]
tc_fastflux_address = [qcs.Address(1, slot, channel) for (slot, channel) in tc_mapping]

channel_mapper = qcs.ChannelMapper(ip_address="192.168.0.85")

channel_mapper.add_channel_mapping(xy_awgs, xy_awg_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(readout_awgs, readout_awg_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(digs, dig_address, qcs.InstrumentEnum.M5200Digitizer)
channel_mapper.add_channel_mapping(qubit_flux_awgs, qubit_fastflux_address, qcs.InstrumentEnum.M5301AWG)
channel_mapper.add_channel_mapping(tc_flux_awgs, tc_fastflux_address, qcs.InstrumentEnum.M5301AWG)

channel_mapper.add_downconverters(dig_address, dnc_address)

# order of arguments has changed
channel_mapper.set_lo_frequencies([(1, readout_awg_slot, readout_awg_channel)]
                                  + [(1, readout_downconverter_slot, readout_downconverter_channel)],
                                  5e9)
channel_mapper.set_lo_frequencies(xy_awg_address, 3.9e9)

# set the digitizer range
qcs.save(channel_mapper, FOLDER / "chan_map.qcs")
