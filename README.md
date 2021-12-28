# carAccidentsSonification
Sonification of car accident data for the state of San Diego.

Data to sound translations:
    1. Duration of sample playback is mapped to duration of the crash and duration of LPF filter sweep. (longer crash time=longer duration)
    2. Filter cutoff is mapped to the weather condition, (Clear=lowest, Thunder=highest).
    3. Duration of LPF sweep is mapped to distance of the crash. (greater distance=longer attack time)
    4. Reverb gain of inst i99 is mapped to sun position. (Daylight=no reverb, night=reverb).
    5. Pan position of sample is mapped to side of the crash. (Left pan=left side crash)
    6. Pitch of the sample is mapped to severity (higher severity=higher pitch)
    
Soundfont:
    The current soundfont being used is a wood hit. 
    The sharp transient and short duration help illustrate the duration, attack time and reverb gain pfield
    Sounds can be swapped easily by changing filename in line 193
