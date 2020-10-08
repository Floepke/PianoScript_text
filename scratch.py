from mido import MidiFile

mid = MidiFile('test.mid')
midimsg = []

def translateMIDItoList():
    #### put all needed messages in a list ####
    ### storage 1 ###
    mem1 = 0
    midimsgs = []
    miditempo = []
    ticksperbeat = mid.ticks_per_beat
    msperbeat = 1
   
    # place messages in dict.
    for i in mid:
        midimsgs.append(i.dict())
    # time to tick generator.
    def time2tick(time, ticksperbeat, msperbeat):
        return round((ticksperbeat * (1 / msperbeat) * 1000000 * time), 0)
    for i in midimsgs:
        i['time'] = time2tick(i['time'], ticksperbeat, msperbeat)
        if i['type'] == 'set_tempo':
            msperbeat = i['tempo']       
    # delta to relative time
    for i in midimsgs:
        i['time'] += mem1
        mem1 = i['time']
    # change every note_on with 0 velocity to note_off.
        if i['type'] == 'note_on' and i['velocity'] == 0:
            i['type'] = 'note_off'
    # Add all usable messages in midimsg; the main midimessagelist.
        if i['type'] == 'note_on' or i['type'] == 'note_off':
            midimsg.append([i['type'], i['time'], i['note'], i['velocity'], i['channel']])
        if i['type'] == 'time_signature':
            midimsg.append([i['type'], i['time'], i['numerator'], i['denominator'], i['clocks_per_click'], i['notated_32nd_notes_per_beat']])
        if i['type'] == 'set_tempo':
            midimsg.append( [i['type'], i['time'], (i['tempo'])] )
        if i['type'] == 'track_name':
            midimsg.append([i['type'], i['time'], i['name']])
        if i['type'] == 'end_of_track':
            midimsg.append([i['type'], i['time']])

    for i in midimsg: print(i)
    print(round((ticksperbeat * (1 / 483870) * 1000000 * 0.9677399999999999), 0))
translateMIDItoList()
