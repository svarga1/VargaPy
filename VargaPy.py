#Python module maintained by Sam Varga
#Contains various functions that I have created



#Module Imports- See ReadMe for dependencies

import numpy as np





#####################
###Thermodynamics###
####################

def SatVapPressure(T, T_units='K', P_units='Pa'):
	#SatVapPressure calculates the saturation vapor pressure at a given temperature

	#T- Input temperature for the saturation vapor pressure
	#T_units: unit of the input temperature, Can be either K or C
	#P_units: Unit of the output saturation vapor pressure, can be hPa or Pa

	#Constants:
	A=2.53*10**11 #Pa
	B=5.42*10**3 #K

	if T_units=='C':
		T=273.15+T #Convert temperature in C to K
	
	e_s=A*exp(-B/T) #Saturation vapor pressure in Pa

	if e_s=='hPa':
		e_s=e_s/100
	
	return e_s


def SatMixingRatio(T, P, T_units='K', P_units='Pa', return_e_s=TRUE):
	#Calculates the saturation mixing ratio at a given temperature and pressure

	#T: input temperature in units T_units
	#P input pressure in units P_units
	#T_units: units of temperature input, can be K or C
	#P_units: units of pressure input, can be Pa or hPa
	#return_e_s: Boolean. If true, SatMixingRatio() returns Saturation mixing ratio and saturation vapor pressure


	#Constants
	R=8.314 #J/(kg*mol)
	M_d=28.97 #Molar mass of dry air; g/mol
	M_w=18.016 #Molar mass of water; g/mol
	R_d=1000*R/M_d #Gas constant for dry air; J/(k*Kg)
	R_v=1000*R/M_w #Gas constant for water vapor; J/(k*kg)
	Epsilon=R_d/R_v

	#Saturation Vapor pressure
	e_s=SatVapPressure(T, T_units, P_units)

	#Saturation Mixing ratio-- returns as a ratio, i.e. not g/kg
	w_s=(Epsilon*e_s)/(P-e_s)

	if return_e_s:
		return w_s, e_s
	else:
		return w_s



####################
####Computation#####
####################

#Check the axes for this

def forward_differencing(X, delta_x, axis=0):

	#Function that calculates the partial derivative of some function F using forward differencing
	#This will not work for the last element of an array

	#X: 2D array of values F(x)
	#delta_x: distance between grid points
	#axis: axis to calculate the derivative along (x=0, y=1)

	#df_dx: array of shape X with approximations of derivative. Either the top or rightmost row will be zeroes


	length=np.shape(X) #Length of array along the dimension axis


	df_dx=np.zeros_like(X)

	i=0 #X
	j=length[0]-1 #Y


	if axis==0:
				
		while i<length[1]-1:
			df_dx[:,i]=(X[:,i+1]-X[:,i])/delta_x
			i+=1
		
	
	elif axis==1:
		while j>0:
			df_dx[j,:]=(X[j-1,:]-X[j,:])/delta_x
			j-=1
			
	return df_dx



def backward_differencing(X, delta_x, axis=0):
	 #Function that calculates the partial derivative of some function F using backward differencing
         #This will not work for the last element of an array

         #X: 2D array of values F(x)
         #delta_x: distance between grid points
         #axis: axis to calculate the derivative along (x=0, y=1)
         #df_dx: array of shape X with approximations of derivative. Either the top or rightmost row will be zeroes


	length=np.shape(X) #Length of array along the dimension axis


	df_dx=np.zeros_like(X)
	i=1 #X
	j=1 #Y


	if axis==0:
		while i<length[1]: #For each column except the first
			df_dx[:,i]=(X[:,i]-X[:,i-1])/delta_x
			i+=1

	elif axis==1:
		while j<length[0]:
			df_dx[j,:]=(X[j,:]-X[j-1,:])/delta_x
			j+=1

	return df_dx



def centered_differencing(X_delta_x, axis=0):
	#Function that calculates the partial derivative of some function F using centered finite differencing
	#Will not work for the boundaries of X

	#X: 2d array of values F(x)
	#Delta_x: distance between grid points
	#Axis: Axis to calculate the derivative along (x=0, y=1)
	#df_dx: array of shape x with approximations of derivative. First/last columns/rows will be zero, depending on axis.

	length=np.shape(X)

	df_dx=np.zeros_like(X)


	i=1 #Index for x, starts at 1 to avoid boundary issues
	j=length[0]-2 #index for y, starts at the second to last index and moves up

	if axis==0:
		while i<length[1]-1:
			df_dx[:,i]=(X[:,i+1]-X[:,i-1])/(2*delta_x)
			i+=1
	if axis==1:
		while j>0:
			df_dx[j,:]=(X[j-1,:]-X[j+1,:])/(2*delta_x)
			j-=1
	return df_dx















