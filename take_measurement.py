

class measurementHandler:
	def __init__(self, camera_controller, file_handler):
		self.camera = camera_controller
		self.fileHandler = file_handler

	def take_measurement_series(self, radial_steps, azumuthial_steps, blobCenter_y, blobCenter_x, NOISEimage, totIncidentLight):
		messagebox.showinfo("Message", "Data acquisistion started")
		self.fileHandler.write_text_position(16, "DataBegin")
		self.fileHandler.write_text_position(17, "TIS -num-") #CALCULATE AND ADD TIS VALUE
		
		#Create empty array for data storage with size #radial x #azumuthial
		# ~ BSDF_RAW_data[radial_steps, azumuthuial_steps] = []
		BSDF_RAW_data = [[0 for _ in range(radial_steps)]for _ in range(azumuthial_steps)]
		i = 0
		w = 0
		
		#The file is written as ---->
		#			---->
		#			---->
		# The 'blob' of light used to get data is retrieved at calibration. This step also saves black noise, which is removed below, before data is saved in array. 
		while i < azumuthial_steps:			
			while w < radial_steps:
				self.camera.capture_RAWimage()
				circular_img = self.calibration.pixels_in_circle(self.camera.RAWimage)
				print("data without noise and before exposure adjusting : ", round(np.mean(circular_img) - NOISEimage, 4))
				
				#if the mean value is too low/high we need to change exposure in this step and retake image. Then adjust the data with our regression model, so that the data is comparable to our calibrated 100% data
				while round(np.mean(circular_img) - NOISEimage, 4) > maxMeanGray :
					self.camera.change_exposure(self.camera.setExposure - 50)
					print("lower exposure, new value : ", self.camera.setExposure)
					self.camera.capture_RAWimage()
					circular_img = self.calibration.pixels_in_circle(self.camera.RAWimage)
					print("Decreased exposure ", self.camera.setExposure, " new data value (removed noise) : ", round(np.mean(circular_img) - NOISEimage, 4))
									
				while round(np.mean(circular_img) - NOISEimage, 4) < minMeanGray :
					self.fileHandler.write_text(str(round(np.mean(circular_img) - NOISEimage, 4)))
					self.camera.change_exposure(self.camera.setExposure + 50)
					print("increase exposure, new value : ", self.camera.setExposure)
					self.camera.capture_RAWimage()
					circular_img = self.calibration.pixels_in_circle(self.camera.RAWimage)
					print("Increased exposure ", self.camera.setExposure, " new data value (removed noise) : ", round(np.mean(circular_img) - NOISEimage, 4))

				#For a simpler understanding of the model/coherent relationship I assumed that the relationship between the data points and exposure time are the same, even for lower intensities than what the model is based on.
				#Therefore the model will be adjusted by a factor of original_val / measured_val - this makes the data from any exposure comparable because they are adjusted to the same exposure time. 
				x_var = self.camera.setExposure
				original_val = ((4700052390936943 * x_var) / (9007199254740992)) - ((6038085623309793 * x_var ** 2) / (36893488147419103232)) + (1370615134844229 * x_var ** 3) / (75557863725914323419136) + 6460865974696399 / 70368744177664
				#BRDF = Pr/Pi * Omega_det * cos (theta_det), omdega_det = A/R^2, Pi = totIncidentLight, Pr = round(np.mean(circular_img) - NOISEimage, 4), theta_det = reflection angle from specular
				measured_val = round(np.mean(circular_img) - NOISEimage, 4)
				factor_diff = original_val / measured_val 
				BSDF_RAW_data[i][w] = factor_diff * original_val
				print("saved data : ", BSDF_RAW_data[i][w])
				self.fileHandler.write_text(str(BSDF_RAW_data[i][w]))
				w += 1
			i  += 1
			w = 0
			self.fileHandler.write_text("\n")
			
			
		print("loop ended, size", len(BSDF_RAW_data[0]), "x", len(BSDF_RAW_data))
		self.fileHandler.write_text("DataEnd")
