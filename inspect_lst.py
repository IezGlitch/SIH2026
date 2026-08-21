import xarray as xr

ds = xr.open_dataset(r"data\Gaya\gaya_sentinel3_lst_20260524\S3A_SL_2_LST____20260524T154613_20260524T154913_20260526T053838_0179_139_368_0360_PS1_O_NT_005.SEN3\LST_in.nc")
print(ds)