#!/usr/bin/env python3
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType
from time import sleep
import psutil
from typing import Tuple
import color

def initRGB():
	# Getting this script ready to be run as a service. Waiting for the sdk to start.
	while True:
		try:
			print("trying to connect")
			cli = OpenRGBClient()
			break
		except ConnectionRefusedError:
			sleep(5)
			continue

	mb = cli.get_devices_by_type(DeviceType.MOTHERBOARD)[0]
	# try:
	#     gpu = cli.get_devices_by_type(DeviceType.GPU)[0]
	# except IndexError:
	#     gpu = False
	# right_ram, left_ram = cli.get_devices_by_type(DeviceType.DRAM)

	# right_ram.clear()
	# left_ram.clear()


	# To make sure the devices are in the right mode, and to work around a problem
	#   where the gpu won't change colors until switched out of static mode and
	#   then back into static mode.
	if mb:
		mb.set_mode(0)  # Direct mode
	# if gpu:
	#     gpu.set_mode(1)  # Anything would work, this is breathing in my setup
	#     sleep(.1)
	#     gpu.set_mode(0)  # Static mode.  My GPU doesn't have a direct mode.
	#     try:
	#         nvmlInit()
	#         handle = nvmlDeviceGetHandleByIndex(0)
	#     except:
	#         gpu, handle = False, False
	# else:
	# 	handle = False
	return mb

# def temp_to_color(temp: int, min: int, max: int) -> Tuple[int, int]:
# 	multiplier = 240/(max - min)
# 	if temp < min:
# 		return 0, 255
# 	elif temp < max:
# 		return int((temp - min) * multiplier), int((max - temp) * multiplier)
# 	elif temp >= max:
# 		return 255, 0

def blackbody_temp(t):
	T = 1000 + t * 8000
	tscale = .75 + t / 4

	x, y, z = color.spectrum_to_xyz(color.bb_spectrum(T))
	r, g, b = color.xyz_to_rgb(color.SMPTE_SYSTEM, x, y, z)
	r, g, b = color.constrain_rgb(r, g, b)
	r, g, b = color.norm_rgb(r, g, b)
	r, g, b = r * tscale, g * tscale, b * tscale

	return RGBColor(int(r*255), int(g*255), int(b*255))

mb = initRGB()
BLACK = RGBColor(0, 0, 0)

# for temp in range(30 * 8, 100 * 8):
# 	cpu_temp = temp / 8
# 	gpu_temp = 100 - (temp / 8 - 30)

# 	cpu_color = blackbody_temp((cpu_temp - 30) / 70)
# 	gpu_color = blackbody_temp((gpu_temp - 30) / 70)

# 	mb.zones[1].set_colors([cpu_color] * 2 + [BLACK] + [gpu_color] * 2 + [BLACK])

# 	print(cpu_temp, gpu_temp)

# raise SystemExit()

while True:
	try:
		if mb:
			temps = psutil.sensors_temperatures()
			### CPU Temp
			cpu_temp = [t.current for t in temps['zenpower'] if t.label == 'Tdie'][0]
			gpu_temp = [t.current for t in temps['amdgpu'] if t.label == 'edge'][0]

			cpu_color = blackbody_temp((cpu_temp - 30) / 70)
			gpu_color = blackbody_temp((gpu_temp - 30) / 70)

			mb.zones[1].set_colors([cpu_color] * 2 + [BLACK] + [gpu_color] * 2 + [BLACK])

			print(cpu_temp, gpu_temp)

			# red, blue = temp_to_color(temp, 45, 75)
			# cooler.set_color(RGBColor(red, 0, blue))

		# if gpu:
		#     ### GPU Temp
		#     temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
		#     red, blue = temp_to_color(temp, 35, 65)
		#     gpu.set_color(RGBColor(red, 0, blue))
		sleep(.25)
		### RAM Usage
		### Works fine
		# usage = psutil.virtual_memory().percent
		# if usage < 20:
		#     right_ram.set_color(RGBColor(0, 0, 0), end=4)
		#     right_ram.leds[4].set_color(RGBColor(0, 0, int(usage*10)))
		# elif usage < 40:
		#     right_ram.set_color(RGBColor(0, 0, 0), end=3)
		#     right_ram.leds[3].set_color(RGBColor(0, 0, int((usage - 20)*10)))
		#     right_ram.leds[4].set_color(RGBColor(0, 0, 255))
		# elif usage < 60:
		#     right_ram.set_color(RGBColor(0, 0, 0), end=2)
		#     right_ram.leds[2].set_color(RGBColor(0, 0, int((usage - 40)*10)))
		#     right_ram.set_color(RGBColor(0, 0, 255), start=3)
		# elif usage < 80:
		#     right_ram.set_color(RGBColor(0, 0, 255), start=2)
		#     right_ram.leds[0].set_color(RGBColor(0, 0, 0))
		#     right_ram.leds[1].set_color(RGBColor(0, 0, int((usage - 60)*10)))
		# else:
		#     right_ram.set_color(RGBColor(0, 0, 255), start=1)
		#     right_ram.leds[0].set_color(RGBColor(0, 0, int((usage - 80)*10)))
	except (ConnectionResetError, BrokenPipeError, TimeoutError) as e:
		print(str(e) + " during main loop")
		print("Trying to reconnect...")
		mb = initRGB()
