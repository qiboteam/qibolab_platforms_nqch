import pathlib
import keysight.qcs as qcs

print(qcs.__version__)
FOLDER = pathlib.Path(__file__).parent

n_qubits = 4
connectivity = [(0, 1), (1, 2), (2, 3)]

xy_awgs = qcs.Channels(range(n_qubits), "xy_channels", absolute_phase=False)
digs = qcs.Channels(range(n_qubits), "readout_acquisition", absolute_phase=True)
readout_awgs = qcs.Channels(range(n_qubits), "readout_channels", absolute_phase=True)
cr_awgs = qcs.Channels(range(len(connectivity) * 2), "cr_channels")

readout_awg_address = qcs.Address(1, 15, 1)
xy_awg_address = [qcs.Address(1, 13, 1), qcs.Address(1, 13, 2), qcs.Address(1, 13, 3), qcs.Address(1, 13, 4)]
dig_address = qcs.Address(1, 18, 1)
dnc_address = qcs.Address(1, 17, 1)
cr_awgs_address = [xy_awg_address[idx] for idx in list(sum(connectivity, ()))]

channel_mapper = qcs.ChannelMapper(ip_address="192.168.0.148")

channel_mapper.add_channel_mapping(xy_awgs, xy_awg_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(readout_awgs, [readout_awg_address] * n_qubits, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_channel_mapping(digs, [dig_address] * n_qubits, qcs.InstrumentEnum.M5200Digitizer)
channel_mapper.add_channel_mapping(cr_awgs, cr_awgs_address, qcs.InstrumentEnum.M5300AWG)
channel_mapper.add_downconverters(dig_address, dnc_address)

# order of arguments has changed
channel_mapper.set_lo_frequencies([readout_awg_address, dnc_address], 5.3e9)
channel_mapper.set_lo_frequencies(xy_awg_address, 3.6e9)

# set the digitizer range
dig_channels = channel_mapper.get_physical_channel(dig_address)
#dig_channels.settings.range.value = 0.7
dig_channels.settings.range.value = 0.045

qcs.save(channel_mapper, FOLDER / "chan_map.qcs")
