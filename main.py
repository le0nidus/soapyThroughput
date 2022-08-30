# SoapySDR is the API for the hackrf
import SoapySDR
from SoapySDR import Device, SOAPY_SDR_RX, SOAPY_SDR_CF32
# use numpy for buffers
import numpy as np
# use pyplot for plotting
from matplotlib import pyplot as plt
# use time for measuring
import time
# use the defaults from variable file
import configfile


# apply initial settings to HackRF device
def initializeHackRF(fs, f_rx, bw, gain):
    sdr.setSampleRate(SOAPY_SDR_RX, 0, fs)
    sdr.setBandwidth(SOAPY_SDR_RX, 0, bw)
    sdr.setFrequency(SOAPY_SDR_RX, 0, f_rx)
    sdr.setGain(SOAPY_SDR_RX, 0, gain)


# setup a stream (complex floats)
def setStream(sdrDevice):
    stream = sdrDevice.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    print(sdr.getStreamMTU(stream))
    sdrDevice.activateStream(stream)  # start streaming
    return stream


# stop the stream and shutdown
def quitStream(sdrDevice, stream):
    sdrDevice.deactivateStream(stream)  # stop streaming
    sdrDevice.closeStream(stream)


if __name__ == '__main__':

    # show soapySDR devices available
    results = SoapySDR.Device.enumerate()
    print("Available devices:")
    for result in results: print(result)

    # create device instance
    # args can be user defined or from the enumeration result
    args = dict(driver="hackrf")
    sdr = SoapySDR.Device(args)

    print(sdr.getStreamFormats(SOAPY_SDR_RX, 0))

    bandwidth = configfile.BANDWIDTH
    samp_rate = configfile.SAMPLE_RATE
    rx_freq = configfile.RX_FREQ
    RX_gain = configfile.RX_GAIN
    buff_size = configfile.BUFFER_SIZE
    numOfIterations = configfile.ITERATIONS


    initializeHackRF(samp_rate, rx_freq, bandwidth, RX_gain)

    # setup a stream
    rxStream = setStream(sdr)

    print("Current parameters:\nSample rate = " + str(int(samp_rate/1e6)) + "e6\n" +
          "Buffer length = " + str(buff_size) + "\n")

    samples = np.zeros(buff_size, dtype=np.complex64)
    realRates = np.zeros(numOfIterations)
    NumOfAcquiredSamples = np.zeros(numOfIterations)
    # receive samples
    for i in range(numOfIterations):
        start_time = time.time()
        sr = sdr.readStream(rxStream, [samples], buff_size)
        end_time = time.time()
        # the real rate is number of samples acquired / elapsed time
        realRates[i] = sr.ret / (end_time - start_time)
        NumOfAcquiredSamples[i] = sr.ret

    iterVec = np.arange(1,(numOfIterations+1), 1, dtype=int)
    plt.subplots(2,1)
    plt.subplot(211)
    plt.plot(iterVec, realRates)
    plt.subplot(212)
    plt.plot(iterVec, NumOfAcquiredSamples)
    plt.show()
    # shutdown the stream
    quitStream(sdr, rxStream)
