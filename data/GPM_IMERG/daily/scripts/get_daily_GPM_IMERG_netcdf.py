#!/home/nicolasf/anaconda3/envs/climlab/bin/python
# -*- coding: utf-8 -*-
# ==================================================================================
# code get_daily_GPM_IMERG_netcdf.py
# Description: download GPM IMERG version 06 netcdf files for the Pacific region
# TAGS:IMERG:wget:datetime
# created on 2016-07-07 (TRMM)
# updated on 2017-05-23 (TRMM)
# updated on 2020-01-24 (GPM/IMERG)
# Nicolas Fauchereau <Nicolas.Fauchereau@gmail.com>
# ==================================================================================

import os
import argparse
import numpy as np
from datetime import datetime
import pandas as pd
import xarray as xr
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

parser.add_argument('-lonW','--lonmin', dest='lonmin', type=float, default=125., \
help='westernmost longitude for the domain to extract, default is 125.')

parser.add_argument('-lonE','--lonmax', dest='lonmax', type=float, default=240., \
help='eastermost longitude for the domain to extract, default is 240.')

parser.add_argument('-latS','--latmin', dest='latmin', type=float, default=-50., \
help='southermost latitude for the domain to extract, default is -50.')

parser.add_argument('-latN','--latmax', dest='latmax', type=float, default=25., \
help='northermost latitude for the domain to extract, default is 25.')

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

https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDL.06/YYYY/MM/
"""

origin = datetime(1979,1,1,0,0,0)

"""
MAIN LOOP
"""

for date in pd.date_range(start = start_date, end = end_date):

    root_url = "https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDL.06/{:%Y/%m}".format(date)

    fname = "3B-DAY-L.MS.MRG.3IMERG.{:%Y%m%d}-S000000-E235959.V06.nc4".format(date)

    fname_out = 'GPM_IMERG_daily.v06.{:%Y.%m.%d}.nc'.format(date)

    ### ==============================================================================================================
    # build the command
    if proxy:
        cmd = "curl --silent --proxy {} -n -c ~/.urs_cookies -b ~/.urs_cookies -L --url {}/{} -o {}/{}".format(proxy, root_url, fname, opath, fname)
    else:
        cmd = "curl --silent -n -c ~/.urs_cookies -b ~/.urs_cookies -L --url {}/{} -o {}/{}".format(root_url, fname, opath, fname)
        #cmd = "curl --silent -n -L --url {}/{} -o {}/{}".format(root_url, fname, opath, fname)

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

            dset_in = dset_in[['HQprecipitation','precipitationCal']]

            trmm_grid = xr.open_dataset('./trmm_grid_description.nc')

            dset_in_interp = dset_in.interp_like(trmm_grid)

            dset_in_interp = dset_in_interp.transpose('time','lat','lon')

            # roll in the longitudes to go from -180 → 180 to 0 → 360

            dset_in_interp = dset_in_interp.assign_coords(lon=(dset_in_interp.lon % 360)).roll(lon=(dset_in_interp.dims['lon'] // 2), roll_coords=True)

            dset_in_interp = dset_in_interp.sel(lon=slice(*lon_bounds),lat=slice(*lat_bounds))

            dset_in_interp.to_netcdf(os.path.join(opath, fname_out),  unlimited_dims='time')

            os.remove(os.path.join(opath,fname))

            dset_in.close()
            dset_in_interp.close()
            trmm_grid.close()

        else:

            print('\n! file size for {0} does not match, netcdf file {0} probably not available from {1}\n'.format(fname, root_url))
            pass
