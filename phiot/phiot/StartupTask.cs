using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net.Http;
using Windows.ApplicationModel.Background;
using Windows.Devices.Gpio;
using System.Diagnostics;

// The Background Application template is documented at http://go.microsoft.com/fwlink/?LinkID=533884&clcid=0x409

namespace phiot
{
    public sealed class StartupTask : IBackgroundTask
    {
        BackgroundTaskDeferral deferral;
        private const int PIN_PHOTO = 18;
        private const int PIN_RED = 23;
        private const int PIN_BLUE = 24;
        private const int PIN_GREEN = 25;
        private const int LED_RED = 1;
        private const int LED_BLUE = 2;
        private const int LED_GREEN = 4;

        private GpioPin photoPin;
        private List<GpioPin> ledPins;

        public int RcTime()
        {
            /*
             * this code is lifted and ported from: https://www.element14.com/community/community/stem-academy/blog/2014/12/23/reading-a-photo-sensor-with-the-raspberry-pi-b
             * which, in turn, was lifted from adafruit (originally written in Python). It's a workaround for lack of analog inputs on the Pi.
             */
            int reading = 0;

            // set initial state
            photoPin.SetDriveMode(GpioPinDriveMode.Output);
            photoPin.Write(GpioPinValue.Low);

            // can't confirm support for System.Threading.Thread, so using Stopwatch...
            // not sure that Asynch would be appropriate here since we are literally waiting on hardware before switching the pin from output to input
            // see also: https://neosmart.net/blog/2017/system-threading-thread-universal-windows-platform-and-the-fragmentation-of-net-standard/
            Stopwatch sw = new Stopwatch();
            sw.Start();
            bool wait = true;

            while (wait)
            {
                if (sw.ElapsedMilliseconds > 100)
                {
                    wait = false;

                    photoPin.SetDriveMode(GpioPinDriveMode.Input);

                    while(photoPin.Read() == GpioPinValue.Low)
                    {
                        reading++;
                    }
                }
            }

            return reading;
        }


        private void InitGPIO()
        {
            // init LEDs
            ledPins = new List<GpioPin>(){
                GpioController.GetDefault().OpenPin(PIN_RED),
                GpioController.GetDefault().OpenPin(PIN_BLUE),
                GpioController.GetDefault().OpenPin(PIN_GREEN)
            };

            foreach (var pin in ledPins) {
                // designate pins for Output
                pin.SetDriveMode(GpioPinDriveMode.Output);

                // Turn LED off, initially
                pin.Write(GpioPinValue.Low);
            }

            // init Photo cell
            photoPin = GpioController.GetDefault().OpenPin(PIN_PHOTO);
        }


        private void SetLEDs(int mask)
        {
            for (int i = 0; i < ledPins.Count; i++)
            {
                ledPins[i].Write((mask & i) == i ? GpioPinValue.High : GpioPinValue.Low);
            }
        }


        public void Run(IBackgroundTaskInstance taskInstance)
        {
            // 
            // TODO: Insert code to perform background work
            //
            // If you start any asynchronous methods here, prevent the task
            // from closing prematurely by using BackgroundTaskDeferral as
            // described in http://aka.ms/backgroundtaskdeferral
            //

            /*
             * TO DO:
             * 1. Add same physical functionality that we have in Python example (photo sensor, LEDs)
             * 2. ...Plus, add IoT Hub messages...e.g. Light reading, time of day
             * 
             */

            deferral = taskInstance.GetDeferral();
            InitGPIO();

            // generate up to 2 messages per second
            // up to 2000 messages (i.e. 1/4 of daily allocation on free tier)

            int reading;
            while (true)
            {
                reading = RcTime();

                if (reading < 300)
                {
                    SetLEDs(LED_GREEN);
                }

                else if (reading < 900)
                {
                    SetLEDs(LED_BLUE);
                }

                else
                {
                    SetLEDs(LED_RED);
                }
            }
        }
    }
}
