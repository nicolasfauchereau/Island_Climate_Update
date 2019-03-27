#!/Users/nicolasf/anaconda3/envs/IOOS/bin/python
# -*- coding: utf-8 -*-
# ==================================================================================
# code get_daily_TRMM_TMPA_netcdf.py
# Description: download TRMM 3B42 RT netcdf files for the Pacific region
# TAGS:3B42:wget:datetime
# created on 2016-07-07
# updated on 2017-05-23
# Nicolas Fauchereau <Nicolas.Fauchereau@gmail.com>
# ==================================================================================

import os
import argparse
import numpy as np
from datetime import datetime
import pandas as pd
import xarray as xr
#from mpl_toolkits.basemap import shiftgrid
from subprocess import call


"""
parse the command line arguments
"""

parser = argparse.ArgumentParser()

parser.add_argument('-s','--start_date', dest='start_date', type=str, default=None, \
help='the start date of the period to retrieve, format YYYYMMDD')

parser.add_argument('-e','--end_date', dest='end_date', type=str, default=None, \
help='the end date of the period to retrieve, format YYYYMMDD')

parser.add_argument('-o','--opath', dest='opath', type=str, default=None, \
help='the path where to save the netcdf files, no default')

parser.add_argument('-p','--proxy', dest='proxy', type=str, default=None, \
help='the proxy settings (url:port), default is None (no proxy)')

parser.add_argument('-lonW','--lonmin', dest='lonmin', type=float, default=135., \
help='westernmost longitude for the domain to extract, default is 135.')

parser.add_argument('-lonE','--lonmax', dest='lonmax', type=float, default=240., \
help='eastermost longitude for the domain to extract, default is 240.')

parser.add_argument('-latS','--latmin', dest='latmin', type=float, default=-50., \
help='southermost latitude for the domain to extract, default is -50.')

parser.add_argument('-latN','--latmax', dest='latmax', type=float, default=10., \
help='northermost latitude for the domain to extract, default is 10.')

vargs = vars(parser.parse_args())

# pop out the arguments

start_date = vargs['start_date']
end_date = vargs['end_date']
opath = vargs['opath']
proxy = vargs['proxy']
lonmin = vargs['lonmin']
lonmax = vargs['lonmax']
latmin = vargs['latmin']
latmax = vargs['latmax']

"""
DOMAIN
"""

### set the domain we want [lonW, lonE, latS, latN]
lon_bounds = [lonmin, lonmax]

lat_bounds = [latmin, latmax]


"""
the root URL

http://disc2.gesdisc.eosdis.nasa.gov/data/TRMM_RT/TRMM_3B42RT_Daily.7/YYYY/MM/
"""

origin = datetime(1979,1,1,0,0,0)

"""
MAIN LOOP
"""

for date in pd.date_range(start = start_date, end = end_date):

    root_url = "http://disc2.gesdisc.eosdis.nasa.gov/data/TRMM_RT/TRMM_3B42RT_Daily.7/{:%Y/%m}".format(date)

    fname =  "3B42RT_Daily.{:%Y%m%d}.7.nc4".format(date)

    fname_out = '3B42RT_daily.{:%Y.%m.%d}.nc'.format(date)

    ### ==============================================================================================================
    # build the command
    if proxy:
        cmd = "curl --silent --proxy {} -n -c ~/.urs_cookies -b ~/.urs_cookies -L --url {}/{} -o {}/{}".format(proxy, root_url, fname, opath, fname)
    else:
        cmd = "curl --silent -n -c ~/.urs_cookies -b ~/.urs_cookies -L --url {}/{} -o {}/{}".format(root_url, fname, opath, fname)

    print(cmd)

    # execute the command
    r = call(cmd, shell=True)

    if r != 0:

        print("download failed for date {:%Y-%m-%d}".format(date))
        pass

    else:

        stat_info = os.stat(os.path.join(opath,fname))

        if stat_info.st_size > 800000:

            dset_in = xr.open_dataset(os.path.join(opath,fname))

            rain = dset_in['precipitation'].data.T

            lon = dset_in.lon.data

            longitude = np.concatenate([lon[(lon.shape[0] // 2):], lon[:(lon.shape[0] // 2)]])

            longitude[longitude < 0] += 360

            rainfall = np.concatenate((rain[:,(lon.shape[0] // 2):], rain[:,:(lon.shape[0] // 2)]), axis=1)

            idays = (date - origin).days

            d = {}
            d['time'] = (('time'), np.array(idays)[[np.newaxis,...]])
            d['lat'] = (('lat'), dset_in.lat.data)
            d['lon'] = (('lon'), longitude)
            d['trmm'] = (('time','lat','lon'), rainfall[np.newaxis,...])

            dset_out = xr.Dataset(d)

            dset_out = dset_out.sel(lon=slice(*lon_bounds),lat=slice(*lat_bounds))

            dset_out.time.attrs['units'] = 'days since 1979-1-1 00:00:0.0'
            dset_out.time.attrs['delta_t'] = '0000-00-01 00:00:00'

            dset_out.lat.attrs['longname'] = 'latitude'
            dset_out.lat.attrs['units'] = 'degrees_north'

            dset_out.lon.attrs['longname'] = 'longitude'
            dset_out.lon.attrs['units'] = 'degrees_east'

            dset_out.trmm.attrs['missing_value'] = -99999.0
            dset_out.trmm.attrs['_FillValue'] = -99999.0

            dset_out.to_netcdf(os.path.join(opath, fname_out),  unlimited_dims='time')

            os.remove(os.path.join(opath,fname))

            dset_in.close()
            dset_out.close()

        else:

            print('\n! file size for {0} does not match, netcdf file {0} probably not available from {1}\n'.format(fname, root_url))
            pass
