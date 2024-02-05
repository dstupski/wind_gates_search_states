import pandas as pd 
import numpy as np 
import argparse
import h5py
import os
import pynumdiff
import cvxpy
from braid_analysis import braid_filemanager
from braid_analysis import braid_slicing
from braid_analysis import braid_analysis_plots
import zipfile
import pickle



###
#A script meant to take a braidz file and a .hdf5 from a standard windtunnel triggering experiment and performs the appropriate filtering steps, only flies that triggered a flash, flie trajectories of appropriate length, durations that travelled a minimum distance etc.  
#Performs adding a collum that is "unique_id" becuase when many data sets are combine it is possible for the braidobject Id assigning function to give two flies the same id
#creates a "Flash_frame" column that is true if the lights flashed at that time
#creates a "duration" column that assigns the flash duration value to that object id
#creates a "flash_time" column that is the transformed real time either before or after the flash normalized around 0 where the flash occored (i.e. where "Flash frame==True")
#also assigns an orientation 'u' or 'd' (upwind or downwind) based on flight parameters at the time of flashing
#calculates angular velocity and heading, also creates a "time stamp" key that returns the ms relative to the triggering even
#

###

####
#I think the old data preprocessing code was cutting out a lot of useful trajectories
#this is to test different processing parameters on the output of the data using out old
#random intensity data
####

#####
#as a secondary goal I want to implement a reverse kalman filter on the data
#in order to figure out the unnaturally high angular velocity of the saccadic movements
#and correct for the velocity vector during blob detection issue
###

####
#Also wanted to update so the trimmed file comes out inside the same directory as the .braidz file
#to prevent clutter and lost files and to only need one copy of this script tucked away somewhere
####


####
#Setup command line arguments here for taking in a .braidz an .hdf5 file
####

parser = argparse.ArgumentParser()
parser.add_argument('braid_filename', type=str, help="full path to the braid file of interest")
parser.add_argument('trigger_filename', type=str, help= 'full path the the trigger bag hdf5')
args = parser.parse_args()
braid_handle = str(args.braid_filename)
trigger_handle = str(args.trigger_filename)


#Function that can take a hdf5 and convert it into a data frame
def get_pandas_dataframe_from_uncooperative_hdf5(filename, key='first_key'):
    f = h5py.File(filename,'r')
    all_keys = list(f.keys())
    if key == 'first_key':
#         print('Dataset contains these keys: ')
        print(all_keys)
        key = all_keys[0]
#         print('Using only the first key: ', key)
    data = f[key][()]
    dic = {}
    for column_label in data.dtype.fields.keys():
        dic.setdefault(column_label, data[column_label])
    df = pd.DataFrame(dic)
    return df



####
#Try Filtering, for this iteration I want to see how many trajectories creat a trigger event but do not make it to the final 
#data set and why they aren't
####

def get_braid_file(braid_handle, trigger_df):
    braid_df = braid_filemanager.load_filename_as_dataframe_3d(braid_handle)
    braid_df['millis']=(braid_df.frame-braid_df.frame.iloc[0])*10 #add millis before filtering
    braid_df=braid_df[braid_df.obj_id.isin(trigger_df.data_1)] #take only the data with trajectories that create a trigger event
    return braid_df


def do_filtering(df1, trigger_df):
    long_obj_ids1 = braid_slicing.get_long_obj_ids_fast_pandas(df1, length=50)
    df1= df1[df1.obj_id.isin(long_obj_ids1)]
    far1 = braid_slicing.get_trajectories_that_travel_far(df1, xdist_travelled=0.1)
    df1 =df1[df1.obj_id.isin(far1)]
    return df1


####
#Because object ID's can have the same number from one experiment to another
#here we create a function that gives each object in the data frame a truly Unique_id
#so that when data from multiple experiments are combined there's no chance of accidentally having two trajectories
#with the same obj_id
####

def assign_unique_id(braid_df, handle_):
	"""This Function adds a unique ID column to the braid data frame"""
	braid_df['obj_id_unique']=braid_df['obj_id'].apply(lambda x: str(x)+ '_' + handle_)
	return braid_df

####
#Creates a "duration" key- this is only named as such becuase of the original experiments I designed had a random flash duration
#but really the "duration" column holds whatever you annotate as your triggered condition, e.g. for a random intensity experiment it might hold
#100 for 100% blast of red lights or it might hold 50 for a 50% blast of the red lights, this code looks for the "duration" information on the data_4
#column of the hdf5 file.  At some point I should make this modular but Im busy and sleepy and I just ate panda so we don't have much time before I crash
####

def assign_duration_value(braid_df, trigger_df):
	'''Creates two keys in the data frame, one for the 'duration' of the flash (specific for the random flash duration experiments' and one for the Flash_bool, which is True where a flash occured, this is helpful for normalizing the timing of things'''
	braid_df['Flash_bool'] = braid_df['frame'].isin(trigger_df['data_2'].to_list())
	braid_df['duration']= ''
	braid_to_concat =[]
	for i in braid_df['obj_id'].unique():
		dummy_df = braid_df[braid_df['obj_id']==i]
		ind = np.where(trigger_df['data_1']==i)[0][0]
		val = trigger_df['data_4'].iloc[ind]
		dummy_df['duration']=val
		braid_to_concat.append(dummy_df)

	stamped_df = pd.concat(braid_to_concat)
	return stamped_df


'''
takes a raw braidz file, assigns a column 'millis' based on the frames
(which are each 10ms apart), determines when the last real flash was (ignoring shams),
then takes the current millis from the last flash to determine time_since_last_flash
'''
def get_last_flash_time (braid_df, trigger_df):
    frame_trigger_list=trigger_df['data_1'].to_list()
    braid_to_concat =[]
    for i in braid_df['obj_id'].unique():
        unique_df =  braid_df[braid_df['obj_id']==i]
        if (i==frame_trigger_list[0]):
            unique_df['last_flash']=np.nan
        else:
            ind = np.where(braid_df['obj_id']==i)[0][0]
            prior_df = braid_df.iloc[0:(ind-1)]
            prior_df = prior_df[prior_df['Flash_bool']==True]
            prior_df = prior_df.drop_duplicates(subset='frame', keep='first')
            prior_df = prior_df[prior_df['duration']>0]
            if (len(prior_df)==0): ## for scenarios where the first few triggers were all shams
                unique_df['last_flash']=np.nan
            else:
                unique_df['last_flash']=prior_df.millis.iloc[-1]
        braid_to_concat.append(unique_df)
    new_df = pd.concat(braid_to_concat)
    new_df['time_since_flash_millis']=new_df.millis-new_df.last_flash
    new_df['time_since_flash_mins']=new_df['time_since_flash_millis']/60000
    return new_df

####
#Time stamps the frames in ms relative to when the event was triggered, also lumped in assigning upwind and downwind orientations in this function
####
def time_stamp(braid_df):
	"""Create empty list to catch all of the processed individual trajectories"""
	df_catcher=[]
	"""Loop through all of the trajectories one by one"""
	for i in braid_df['obj_id'].unique():
		d_ = braid_df[braid_df['obj_id']==i]
		#d_['orientation']=''
		#print('can i print here')
		try:
			"""find the point in the trajectory where the trigger event happened"""
			ind = np.where(d_['Flash_bool']==True)[0][0]
			#print("can i print this")
			pre_df=d_.iloc[0:ind]
			post_df=d_.iloc[ind:]
			if d_['xvel'].iloc[ind]>0:
				d_['orientation']=['u']*len(d_)
			else:
				d_['orientation']=['d']*len(d_)
			pre_len = len(pre_df)
			#print(' pre length is '+str(pre_len))
			post_len = len(post_df)
			d_['time stamp']=np.linspace(-10*(pre_len), 10*(post_len-1), len(d_))
			#print(len(d_))
			df_catcher.append(d_)
		except:
			pass
	stamped_df=pd.concat(df_catcher)
	return stamped_df



####
#We were having issues with innacurate changes in angular velocity estimates when the flies slow down, the following protocol is used to create an appropriately wrapped and smoothed estimate of the angular velocity of a trajectory
#These parameters worked well when I alligned where the angular velocity peaks were with visually inspected turns
#####

####
#First get the raw angular velocity estimates
####

###function that calculates the heading at any given time, and the angular velocity for a trajectory
def get_angular_velocity(df, time_step):
        d_head_dt_vec =[np.nan]
        df['heading']=np.arctan2(df['yvel'], df['xvel'])
        for i in range(len(df)):
            if i !=0:
                vec_1 =[df['xvel'].iloc[i-1], df['yvel'].iloc[i-1]]
                vec_2 = [df['xvel'].iloc[i], df['yvel'].iloc[i]]
                norm_1 = vec_1/np.linalg.norm(vec_1)
                norm_2 =vec_2/np.linalg.norm(vec_2)
                dot_product = np.dot(norm_1, norm_2)
                d_angle_dt = np.arccos(dot_product)/time_step
                d_head_dt_vec.append(d_angle_dt)
        df['ang vel']= d_head_dt_vec
        return df

###Function that applies it to an entire data set
def get_angular_full_dataset(data_set, time_step):
    df_obj_vec =[]
    for i in data_set['obj_id_unique'].unique():
        d=data_set[data_set['obj_id_unique']==i]
        d_ = get_angular_velocity(d, time_step)
        df_obj_vec.append(d_)
    fdf = pd.concat(df_obj_vec)
    return fdf

###
#Floris's special angular velocity smoothing function
###

##
#helper functions
##
def wrap_angle(a):
    return np.arctan2(np.sin(a), np.cos(a))

def unwrap_angle(z, correction_window_for_2pi=100, n_range=2, plot=False):
    if 0: # option one
        zs = []
        for n in range(-1*n_range, n_range):
            zs.append(z+n*np.pi*2)
        zs = np.vstack(zs)

        smooth_zs = np.array(z[0:2])

        for i in range(2, len(z)):
            first_ix = np.max([0, i-correction_window_for_2pi])
            last_ix = i
            error = np.abs(zs[:,i] - np.mean(smooth_zs[first_ix:last_ix])) 
            smooth_zs = np.hstack(( smooth_zs, [zs[:,i][np.argmin(error)]] ))

        if plot:
            for r in range(zs.shape[0]):
                plt.plot(zs[r,:], '.', markersize=1)
            plt.plot(smooth_zs, '.', color='black', markersize=1)
        
    else: # option two, automatically scales n_range to most recent value, and maybe faster
        smooth_zs = np.array(z[0:2])
        for i in range(2, len(z)):
            first_ix = np.max([0, i-correction_window_for_2pi])
            last_ix = i
            
            nbase = np.round( (smooth_zs[-1] - z[i])/(2*np.pi) )
            
            candidates = []
            for n in range(-1*n_range, n_range):
                candidates.append(n*2*np.pi+nbase*2*np.pi+z[i])
            error = np.abs(candidates - np.mean(smooth_zs[first_ix:last_ix])) 
            smooth_zs = np.hstack(( smooth_zs, [candidates[np.argmin(error)]] ))
        if plot:
            plt.plot(smooth_zs, '.', color='black', markersize=1)
    return smooth_zs

def diff_angle(angles, dt, params, 
               derivative_method='smooth_finite_difference.butterdiff', 
               outlier_max_std=1.5,
               outlier_window_size=500,
               outlier_stride=250,
               correction_window_for_2pi=100):
    '''
    Take a filtered derivative of an angle
    '''
    
    family, method = derivative_method.split('.')

    '''
    angles = interpolate_outliers_angle(angles, outlier_window_size, outlier_stride, outlier_max_std)
    diff_angles = np.diff(angles)
    diff_angles = np.hstack((0, diff_angles, 0))
    wrapped_diff_angle = wrap_angle(diff_angles)
    unwrapped_angle = scipy.integrate.cumtrapz(wrapped_diff_angle)
    
    corrected_unwrapped_angle = [unwrapped_angle[0], unwrapped_angle[1]]
    for i in range(2, len(unwrapped_angle)):
        first_ix = np.max([0, i-correction_window_for_2pi])
        last_ix = i
        error = (unwrapped_angle[i] - mean_angle(corrected_unwrapped_angle[first_ix:last_ix])) / (2*np.pi)
        npi = np.round(error)
        corrected_unwrapped_angle.append(unwrapped_angle[i] - npi*2*np.pi)
    
    offset = mean_angle(angles) - mean_angle(unwrapped_angle)
    unwrapped_angle += offset
    '''
    
    unwrapped_angle = unwrap_angle(angles, correction_window_for_2pi=correction_window_for_2pi, n_range=5)

    if family == 'total_variation_regularization' and method == 'position':
        angles_smooth, angles_dot = diff_tvrp(unwrapped_angle, dt, params)
        return wrap_angle(angles_smooth), angles_dot
    else:
        angles_smooth, angles_dot = pynumdiff.__dict__[family].__dict__[method](unwrapped_angle, dt, params, {})
        return wrap_angle(angles_smooth), angles_dot

###
#function to apply the theta dot smoother to individual trajectories
###
def smoother(d_):
    gamma = 0.01
    dt = .01
    correction_gamma = 10
    theta_meas = d_['heading'].to_numpy()
    tan_theta_cvx = cvxpy.Variable(len(theta_meas))
    vx=d_['xvel'].to_numpy()
    vy= d_['yvel'].to_numpy()
    loss = cvxpy.norm(vx - cvxpy.multiply(tan_theta_cvx, vy), 2) + gamma*cvxpy.tv(tan_theta_cvx) 
    obj = cvxpy.Minimize( loss )
    prob = cvxpy.Problem(obj) 
    prob.solve(solver='MOSEK')
    theta_cvx = np.arctan(tan_theta_cvx.value)
    correction = []
    for i in range(len(theta_cvx)):
        if theta_cvx[i] - theta_meas[i] > 2:
            correction.append(-1)
        elif theta_cvx[i] - theta_meas[i] < -2:
            correction.append(1)
        else:
            correction.append(0)
    correction_cvx = cvxpy.Variable(len(correction))
    loss = cvxpy.norm(correction_cvx - correction, 1) + correction_gamma*cvxpy.tv(correction_cvx) 
    obj = cvxpy.Minimize( loss )
    prob = cvxpy.Problem(obj) 
    prob.solve(solver='MOSEK')
    theta_cvx_corrected = theta_cvx + correction_cvx.value*np.pi
    theta_smooth, thetadot_smooth = diff_angle(theta_cvx_corrected, dt, [1, 0.1],
                                           correction_window_for_2pi=5)
    d_['theta smooth']= theta_smooth
    d_['theta dot smooth']= thetadot_smooth
    return d_
###
#function to apply the smoothed theta dot estimate to an entire data set but also cuts trajectories to look at a wide window (5 seconds before the event to 10 seconds after)
#I added this because on occasion a fly would land on the roof/floor after a triggering event and we'd get several minutes worth of it crawling around so applying this to several minutes worth of data
#took a very long time and became uninformative outside of the couple second window in which we are interested in their behavior
###    

def get_theta_dot_smooth_full_dataset(df):
	df_catcher =[]
	for i in df['obj_id'].unique():
		#try:
		d_=df[df['obj_id']==i]
		d_ = d_[d_['time stamp'].between(-5000, 10000)]		
		smoothed_traj = smoother(d_)
		df_catcher.append(smoothed_traj)
		#except:
		#	pass
	smoothed_df =pd.concat(df_catcher)
	return smoothed_df


#####  
#Put all of the filtering information together and save a trimmed file in the same folder as the .braidz file and its corresponding .hdf5 experimental
#information file
####

    
def compound_it_all(braid_handle, trigger_handle):
    trigger_df = get_pandas_dataframe_from_uncooperative_hdf5(trigger_handle)
    braid_df = get_braid_file(braid_handle, trigger_df)
    newdf = assign_duration_value(braid_df, trigger_df)
    newdf = get_last_flash_time(newdf, trigger_df)
    filtered_df = do_filtering(newdf, trigger_df)
    uniq_id_prefix= braid_handle.split('.')[0]
    save_dir = os.path.split(braid_handle)[0]
    uniq_id_prefix = uniq_id_prefix.split('/')[-1]
    filtered_df = assign_unique_id(filtered_df, uniq_id_prefix)

    filtered_df = time_stamp(filtered_df)
    filtered_df= get_angular_full_dataset(filtered_df, .01)
    filtered_df= get_theta_dot_smooth_full_dataset(filtered_df)
    filtered_df.to_csv(save_dir+'/' + uniq_id_prefix + '_full_trim_protocol.csv')


compound_it_all(braid_handle, trigger_handle)

