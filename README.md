## Processes to run to create the various products going into the Island Climate Update bulletin


### 1) update the TRMM rainfall daily data:

+ cd into `~/operational/ICU/ops/data/TRMM/daily/extended_SP/` and note the date of the last netcdf file
+ activate the `pangeo` environment and cd into `~/operational/ICU/ops/data/TRMM/daily/scripts/`
+ run:
```
python get_daily_TRMM_TMPA_netcdf.py -o ../extended_SP -lonW 125 -lonE 240 -latN 25 -latS -50 -s YYYMMDD -e YYYYMMDD
```

where `-s YYYMMDD` indicates the start date (e.g. -s 20190228) and `-e YYYYMMDD` the end date for the download

### 2) update the time-series of TRMM anomalies and categories

+ cd into `~/operational/ICU/ops/TRMM/notebooks/`
+ run `5_get_latest_TRMM_TS_monthly_compare_to_climo.ipynb`: This notebook updates the time series of anomalies for each Island Group, which are saved in the folder `TRMM/outputs/Time_Series/last_6_months`
+ run `6_concat_last_6_months_csv.ipynb`: This notebook concatenates the individual time-series and saves the output (`last_6_months_TRMM_categories.csv`) in the corresponding bulletin folder (e.g. `bulletin/AMJ_2019/`). Do not forget to change the name of the bulletin folder at the beginning of the notebook.

### 3) calculates the water stress from the TRMM anomalies + the CDS forecasts

+ cd into `~/operational/ICU/ops/water_stress/notebooks/`
+ run `prepare_files_for_mapping_and_calculates_stress.ipynb`: do not forget to change the bulletin directory. This notebook reads the copernicus forecasts from the bulletin directory, saves a sanitized version for inclusion in the PPT (e.g. `ICU_forecast_table_for_PPT_AMJ_2019.csv`), reads the last 6 months TRMM anomalies (categories), calculates the Water Stress, and saves both the forecast table for mapping (`ICU_forecast_table_for_mapping.csv`) and the Water Stress for mapping (`ICU_stress_table_for_mapping.csv`).
+ run the notebook `prepare_table_for_Visual_Cortex.ipynb`: do not forget to change the bulletin directory. This notebook reads the copernicus forecasts from the bulletin directory, and saves a file (e.g. `ICU_Rainfall_for_Visual_Cortex_AMJ_2019.csv`) that is used for visualisation using Visual Cortex.
