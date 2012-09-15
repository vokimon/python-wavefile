from libsndfilectypes.libsndfile import SndFile, OPEN_MODES, FILE_FORMATS
import numpy as np
if __name__=="__main__":
    with SndFile("LS100673.WAV") as f:
        #print various information
        print f
        #read from 1 to 3 seconds
        data, nbFramesRead = f.readFromTo(1*f.samplerate, 3*f.samplerate, dtype=np.float64)
        print "nb frames read:",nbFramesRead
        
        #get the left channel
        lChannel = data[:,0]
        
        from scipy.signal import butter, lfilter
        cutoffL=200.
        # Low-pass filter on the left channel at 200 Hz
        b,a = butter(3, cutoffL/(f.samplerate/2), btype="low")
        lChannelFiltered = lfilter(b, a, lChannel)
        
        #write the 2 seconds read as an ogg file
        with SndFile("output.ogg", OPEN_MODES.SFM_WRITE,
                     writeFormat=FILE_FORMATS.SF_FORMAT_OGG^FILE_FORMATS.SF_FORMAT_VORBIS) as fo:
            fo.write(data)
        
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(data), dtype=np.float)*1000./f.samplerate, lChannel, label="left channel")
        plt.plot(np.arange(len(data), dtype=np.float)*1000./f.samplerate, lChannelFiltered, label="filtered left channel")
        plt.xlabel("time (ms)")
        plt.ylabel("amplitude (arbitrary unit)")
        plt.title("waveform of filtered and original left channel")
        plt.legend()
        plt.show()